import json
import unittest
from labs.operator_control.operator import (CloudflareAdapter, InfisicalVault, OperatorError, execute)
from labs.operator_control.registry import validate_manifest, public_account_index

class FakeHTTP:
    def __init__(self):
        self.calls=[]
        self.fail_vault_write=False
        self.fail_revoke=False
    def send(self, method, url, *, headers=None, body=None):
        self.calls.append((method,url,headers,body))
        if url.endswith("/api/v1/auth/universal-auth/login"):
            return {"accessToken":"test-vault-session"}
        if "/api/v4/secrets/" in url:
            if method=="GET":
                key=url.split("/api/v4/secrets/")[1].split("?")[0]
                values={"CLOUDFLARE_ACCOUNT_ID":"a"*32,
                    "CLOUDFLARE_WORKERS_ADMIN_TOKEN":"ops-only-fake-token",
                    "CLOUDFLARE_PROVISIONING_TOKEN":"root-only-fake-token",
                    "GOOGLE_OAUTH_CLIENT_ID":"gmail-client-id",
                    "GOOGLE_OAUTH_CLIENT_SECRET":"gmail-client-secret",
                    "GMAIL_REFRESH_TOKEN":"refresh-secret"}
                return {"secret":{"secretValue":values[key]}}
            if method=="POST":
                if self.fail_vault_write:
                    return {"approval":{"id":"pending"}}
                return {"secret":{"id":"stored"}}
        if url.endswith("/workers/scripts") and method=="GET":
            return {"success":True,"result":[{"id":"misslea-existing"}]}
        if method=="PUT" and "/workers/scripts/" in url:
            return {"success":True,"result":{"id":"misslea-new"}}
        if method=="POST" and url.endswith("/tokens"):
            return {"success":True,"result":{"id":"token-id-1234","value":"issued-secret-never-shown"}}
        if method=="DELETE" and "/tokens/" in url:
            return {"success":not self.fail_revoke}
        if url=="https://oauth2.googleapis.com/token":
            return {"access_token":"oauth-access-secret"}
        if url.endswith("/gmail/v1/users/me/profile"):
            return {"emailAddress":"missLea931@gmail.com","messagesTotal":0}
        raise AssertionError((method,url))

ENV={
"MISSLEA_INFISICAL_REGION":"eu",
"MISSLEA_OPS_INFISICAL_CLIENT_ID":"ops-id",
"MISSLEA_OPS_INFISICAL_CLIENT_SECRET":"ops-client-secret",
"MISSLEA_OPS_INFISICAL_PROJECT_ID":"ops-project",
"MISSLEA_ROOT_INFISICAL_CLIENT_ID":"root-id",
"MISSLEA_ROOT_INFISICAL_CLIENT_SECRET":"root-client-secret",
"MISSLEA_ROOT_INFISICAL_PROJECT_ID":"root-project"
}
class OperatorTests(unittest.TestCase):
    def setUp(self):
        self.http=FakeHTTP()
        self.vault=InfisicalVault(self.http,ENV)

    def test_separate_machine_identity_and_vault_scope(self):
        self.assertEqual(self.vault.get("OPS","CLOUDFLARE_ACCOUNT_ID"),"a"*32)
        self.assertEqual(self.vault.get("ROOT","CLOUDFLARE_PROVISIONING_TOKEN"),"root-only-fake-token")
        sessions=[x for x in self.http.calls if x[1].endswith("universal-auth/login")]
        self.assertIn(b"ops-client-secret",sessions[0][3])
        self.assertIn(b"root-client-secret",sessions[1][3])
        for invalid in ("../../passwd","BAD KEY",""):
            with self.assertRaises(OperatorError):
                self.vault.get("OPS",invalid)

    def test_cloudflare_list_and_create_only_prefixed_nonexisting(self):
        self.assertEqual(execute({"operation":"cloudflare.workers.list"},http=self.http,vault=self.vault),
                         {"workers":["misslea-existing"]})
        with self.assertRaisesRegex(OperatorError,"invalid_worker_name"):
            execute({"operation":"cloudflare.worker.create","name":"foreign-worker"},http=self.http,vault=self.vault)
        with self.assertRaisesRegex(OperatorError,"worker_already_exists"):
            execute({"operation":"cloudflare.worker.create","name":"misslea-existing"},http=self.http,vault=self.vault)
        result=execute({"operation":"cloudflare.worker.create","name":"misslea-new"},http=self.http,vault=self.vault)
        self.assertEqual(result,{"worker":"misslea-new","created":True})
        self.assertTrue(any(x[0]=="PUT" for x in self.http.calls))

    def test_root_token_minted_and_written_directly_to_operational_vault(self):
        cmd={"operation":"cloudflare.token.issue","name":"Lab Worker Editor",
            "permission_group_id":"a"*32,
            "resource_scope":"com.cloudflare.api.account."+"a"*32,
            "secret_name":"CLOUDFLARE_NEW_WORKER_TOKEN"}
        result=execute(cmd,http=self.http,vault=self.vault)
        self.assertEqual(result["credential_handle"],"CLOUDFLARE_NEW_WORKER_TOKEN")
        encoded=json.dumps(result)
        self.assertNotIn("issued-secret",encoded)
        writes=[c for c in self.http.calls if c[0]=="POST" and "/api/v4/secrets/" in c[1]]
        self.assertEqual(len(writes),1)
        self.assertIn(b"issued-secret-never-shown",writes[0][3])
        self.assertEqual(len([c for c in self.http.calls if c[0]=="DELETE"]),0)

    def test_failed_secret_storage_revokes_and_fails_closed(self):
        self.http.fail_vault_write=True
        cmd={"operation":"cloudflare.token.issue","name":"Lab Worker Editor",
            "permission_group_id":"a"*32,
            "resource_scope":"com.cloudflare.api.account."+"a"*32,
            "secret_name":"CLOUDFLARE_NEW_WORKER_TOKEN"}
        with self.assertRaisesRegex(OperatorError,"token_storage_failed_revoked"):
            execute(cmd,http=self.http,vault=self.vault)
        self.assertEqual(len([c for c in self.http.calls if c[0]=="DELETE"]),1)
        self.http.fail_revoke=True
        with self.assertRaisesRegex(OperatorError,"token_storage_failed_revocation_unknown"):
            execute(cmd,http=self.http,vault=self.vault)

    def test_gmail_oauth_profile_not_direct_chatgpt_connector(self):
        obj=execute({"operation":"gmail.profile"},http=self.http,vault=self.vault)
        self.assertEqual(obj["emailAddress"],"missLea931@gmail.com")
        self.assertNotIn("oauth-access-secret",json.dumps(obj))

    def test_invalid_commands_fail_without_provider_calls(self):
        for cmd in ({"operation":"fetch","url":"https://evil.com"},
                    {"operation":"cloudflare.worker.create","name":"../../etc"},
                    {"operation":"gmail.profile","token":"exfil"}):
            with self.assertRaises(OperatorError):
                execute(cmd,http=self.http,vault=self.vault)
        self.assertEqual(self.http.calls,[])

    def test_manifest_is_metadata_only(self):
        from pathlib import Path
        obj=json.loads(Path("labs/operator_control/accounts.example.json").read_text())
        validate_manifest(obj)
        self.assertEqual(len(public_account_index(obj)),2)
        obj["accounts"][0]["root_ref"]="not-a-vault-ref"
        with self.assertRaises(ValueError):
            validate_manifest(obj)

if __name__=="__main__":
    unittest.main()
