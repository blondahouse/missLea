"""Trusted Operator Control Plane v1. No secrets on disk, prompts, or return payloads.

This module is a portability prototype: it must be hosted in a separately protected
operator-owned execution environment before any real master credentials are attached.
"""
from __future__ import annotations
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

KEY = re.compile(r"^[A-Z][A-Z0-9_]{2,79}$")
WORKER = re.compile(r"^misslea-[a-z0-9-]{2,56}$")
TOKEN_ID = re.compile(r"^[a-zA-Z0-9_-]{8,96}$")


class OperatorError(Exception):
    pass


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class HTTP:
    def __init__(self, opener=None):
        self._opener = opener or build_opener(_NoRedirect())

    def send(self, method, url, *, headers=None, body=None):
        parsed = urlsplit(url)
        # Endpoint pinning: no arbitrary URL fetching, no private IP or userinfo.
        if parsed.scheme != "https" or parsed.hostname not in {
            "api.cloudflare.com", "oauth2.googleapis.com",
            "gmail.googleapis.com", "eu.infisical.com", "us.infisical.com",
            "app.infisical.com",
        } or parsed.username or parsed.password or parsed.port:
            raise OperatorError("provider_endpoint_not_allowed")
        request = Request(url, method=method, data=body,
                          headers=headers or {})
        try:
            with self._opener.open(request, timeout=20) as response:
                if not 200 <= response.status < 300:
                    raise OperatorError("provider_operation_failed")
                payload = response.read(1024 * 1024)
            return json.loads(payload)
        except (HTTPError, URLError, TimeoutError, OSError,
                json.JSONDecodeError, UnicodeError):
            # Never output HTTP response bodies, credentials, headers or redirect URLs.
            raise OperatorError("provider_operation_failed") from None


class InfisicalVault:
    """Credential resolution from two **separately authenticated** Infisical projects.

    Do not print, serialize, save, log, or return a resolved secret to a caller.
    """
    def __init__(self, http, environ=None):
        self.http = http
        self.env = environ if environ is not None else os.environ
        region = self.env.get("MISSLEA_INFISICAL_REGION", "eu")
        if region not in ("eu", "us", "legacy"):
            raise OperatorError("invalid_vault_region")
        self.base = {"eu":"https://eu.infisical.com",
                     "us":"https://us.infisical.com",
                     "legacy":"https://app.infisical.com"}[region]

    def _identity(self, tier):
        if tier not in ("OPS", "ROOT"):
            raise OperatorError("invalid_vault_tier")
        prefix = "MISSLEA_" + tier + "_INFISICAL_"
        values = [self.env.get(prefix + name, "")
                  for name in ("CLIENT_ID", "CLIENT_SECRET", "PROJECT_ID")]
        if any(not v for v in values):
            raise OperatorError("vault_identity_not_configured")
        return values

    def _token(self, tier):
        client_id, client_secret, _ = self._identity(tier)
        body = urlencode({"clientId":client_id,"clientSecret":client_secret}).encode()
        answer = self.http.send("POST", self.base + "/api/v1/auth/universal-auth/login",
                                headers={"Content-Type":"application/x-www-form-urlencoded"},
                                body=body)
        token = answer.get("accessToken")
        if not isinstance(token, str) or not token:
            raise OperatorError("vault_auth_failed")
        return token

    def get(self, tier, key):
        if not KEY.fullmatch(key):
            raise OperatorError("invalid_secret_handle")
        _client, _secret, project = self._identity(tier)
        token = self._token(tier)
        params = urlencode({"projectId":project,"environment":"prod",
                            "secretPath":"/"})
        url = self.base + "/api/v4/secrets/" + quote(key) + "?" + params
        obj = self.http.send("GET", url, headers={"Authorization":"Bearer "+token})
        value = (obj.get("secret") or {}).get("secretValue")
        if not isinstance(value,str) or not value:
            raise OperatorError("secret_unavailable")
        return value

    def put_operational(self, key, value):
        """Root identity must be granted write access to the operations project."""
        if not KEY.fullmatch(key) or not isinstance(value,str) or not value:
            raise OperatorError("invalid_secret")
        project = self.env.get("MISSLEA_OPS_INFISICAL_PROJECT_ID", "")
        if not project:
            raise OperatorError("ops_project_not_configured")
        token = self._token("ROOT")
        payload = json.dumps({"projectId":project,"environment":"prod",
                              "secretPath":"/","secretValue":value}).encode()
        obj = self.http.send("POST",
            self.base + "/api/v4/secrets/" + quote(key),
            headers={"Authorization":"Bearer "+token,
                     "Content-Type":"application/json"},body=payload)
        if "secret" not in obj:
            raise OperatorError("secret_write_unconfirmed")
        return True


class CloudflareAdapter:
    def __init__(self, http, vault):
        self.http, self.vault = http, vault

    def _credentials(self, root=False):
        tier = "ROOT" if root else "OPS"
        token = self.vault.get(tier, "CLOUDFLARE_PROVISIONING_TOKEN" if root else "CLOUDFLARE_WORKERS_ADMIN_TOKEN")
        account_id = self.vault.get("OPS", "CLOUDFLARE_ACCOUNT_ID")
        if not re.fullmatch(r"[0-9a-f]{32}", account_id):
            raise OperatorError("invalid_cloudflare_account_id")
        return token, account_id

    def list_workers(self):
        token, account = self._credentials()
        result = self.http.send("GET", f"https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts",
                                headers={"Authorization":"Bearer "+token})
        if result.get("success") is not True or not isinstance(result.get("result"),list):
            raise OperatorError("cloudflare_response_invalid")
        return {"workers":sorted(x["id"] for x in result["result"]
                                  if isinstance(x,dict) and isinstance(x.get("id"),str))}

    def create_synthetic_worker(self, name):
        """Provision an intentionally inert new Worker, never replace existing scripts."""
        if not isinstance(name,str) or not WORKER.fullmatch(name):
            raise OperatorError("invalid_worker_name")
        token, account = self._credentials()
        existing = self.list_workers()["workers"]
        if name in existing:
            raise OperatorError("worker_already_exists")
        # Cloudflare ES module multipart upload; no arbitrary caller-provided code.
        boundary = "MissLeaOperatorV1"
        module = 'export default { async fetch() { return Response.json({status:"ready",lab:true}); } };'
        body = (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"metadata\"\r\n"
            "Content-Type: application/json\r\n\r\n"
            '{"main_module":"worker.mjs","compatibility_date":"2026-11-16"}'
            f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"worker.mjs\"; filename=\"worker.mjs\"\r\n"
            "Content-Type: application/javascript+module\r\n\r\n"
            + module + f"\r\n--{boundary}--\r\n"
        ).encode()
        obj = self.http.send("PUT",f"https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/{name}",
              headers={"Authorization":"Bearer "+token,
                       "Content-Type":"multipart/form-data; boundary="+boundary},body=body)
        if obj.get("success") is not True:
            raise OperatorError("cloudflare_create_unconfirmed")
        return {"worker":name,"created":True}

    def issue_token(self, *, name, permission_group_id, resource_scope, secret_name):
        """Root-only privilege used to MINT a narrow credential, store it in OPS vault.

        The issued token is never returned. On failed vault persistence, attempt revoke.
        """
        if not isinstance(name,str) or not re.fullmatch(r"[a-zA-Z0-9_. -]{3,80}", name):
            raise OperatorError("invalid_token_name")
        if not isinstance(permission_group_id,str) or not re.fullmatch(r"[0-9a-f]{32}",permission_group_id):
            raise OperatorError("invalid_permission_group")
        if not isinstance(resource_scope,str) or not re.fullmatch(r"com\.cloudflare\.api\.account\.[0-9a-f]{32}",resource_scope):
            raise OperatorError("invalid_resource_scope")
        if not KEY.fullmatch(secret_name):
            raise OperatorError("invalid_secret_handle")
        token, account = self._credentials(root=True)
        body = json.dumps({"name":name,"policies":[{
            "effect":"allow","permission_groups":[{"id":permission_group_id}],
            "resources":{resource_scope:"*"}
        }]}).encode()
        obj = self.http.send("POST",f"https://api.cloudflare.com/client/v4/accounts/{account}/tokens",
            headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"},body=body)
        result = obj.get("result") if obj.get("success") is True else None
        if not isinstance(result,dict) or not result.get("value") or not result.get("id"):
            raise OperatorError("token_issuance_unconfirmed")
        try:
            self.vault.put_operational(secret_name,result["value"])
        except (OperatorError, RuntimeError):
            # Do not leave an orphan privileged token silently in the provider.
            try:
                self.http.send("DELETE",f"https://api.cloudflare.com/client/v4/accounts/{account}/tokens/{quote(str(result['id']))}",
                   headers={"Authorization":"Bearer "+token})
            except Exception:
                raise OperatorError("token_storage_failed_revocation_unknown") from None
            raise OperatorError("token_storage_failed_revoked") from None
        return {"created":True,"credential_handle":secret_name,"token_id":result["id"]}


class GmailAdapter:
    def __init__(self,http,vault):
        self.http, self.vault = http,vault

    def profile(self):
        client_id=self.vault.get("OPS","GOOGLE_OAUTH_CLIENT_ID")
        client_secret=self.vault.get("OPS","GOOGLE_OAUTH_CLIENT_SECRET")
        refresh_token=self.vault.get("OPS","GMAIL_REFRESH_TOKEN")
        payload=urlencode({"client_id":client_id,"client_secret":client_secret,
                           "refresh_token":refresh_token,"grant_type":"refresh_token"}).encode()
        auth=self.http.send("POST","https://oauth2.googleapis.com/token",
            headers={"Content-Type":"application/x-www-form-urlencoded"},body=payload)
        access=auth.get("access_token")
        if not isinstance(access,str) or not access:
            raise OperatorError("gmail_authorization_failed")
        data=self.http.send("GET","https://gmail.googleapis.com/gmail/v1/users/me/profile",
            headers={"Authorization":"Bearer "+access})
        return {"emailAddress":data.get("emailAddress"),"messagesTotal":data.get("messagesTotal")}


def execute(command, *, http, vault):
    """Private trusted operator entrypoint: never accept arbitrary URL, code or secret reads."""
    if not isinstance(command,dict) or set(command)-{"operation","name","permission_group_id","resource_scope","secret_name"}:
        raise OperatorError("invalid_command")
    op=command.get("operation")
    cf=CloudflareAdapter(http,vault)
    if op=="cloudflare.workers.list" and len(command)==1:
        return cf.list_workers()
    if op=="cloudflare.worker.create" and set(command)=={"operation","name"}:
        return cf.create_synthetic_worker(command["name"])
    if op=="cloudflare.token.issue" and set(command)=={
        "operation","name","permission_group_id","resource_scope","secret_name"
    }:
        return cf.issue_token(name=command["name"],
            permission_group_id=command["permission_group_id"],
            resource_scope=command["resource_scope"],
            secret_name=command["secret_name"])
    if op=="gmail.profile" and len(command)==1:
        return GmailAdapter(http,vault).profile()
    raise OperatorError("operation_not_implemented")
