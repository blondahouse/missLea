"""Command-line entry for an isolated trusted runner, not for agent-executed code."""
import argparse
import json
import sys
from pathlib import Path
from .operator import HTTP, InfisicalVault, OperatorError, execute
from .registry import validate_manifest, public_account_index


def main(argv=None):
    parser=argparse.ArgumentParser(description="Miss Lea trusted operator (no secrets on stdout)")
    parser.add_argument("--manifest",default="labs/operator_control/accounts.example.json")
    parser.add_argument("--command-file",help="Path to non-secret JSON command; privileged runner only")
    parser.add_argument("--list-accounts",action="store_true")
    args=parser.parse_args(argv)
    try:
        if args.list_accounts:
            data=validate_manifest(json.loads(Path(args.manifest).read_text()))
            result={"accounts":public_account_index(data)}
        else:
            if not args.command_file:
                raise OperatorError("missing_command")
            command=json.loads(Path(args.command_file).read_text())
            http=HTTP()
            result=execute(command,http=http,vault=InfisicalVault(http))
        print(json.dumps({"status":"ok","result":result},ensure_ascii=False))
        return 0
    except (ValueError, OSError, json.JSONDecodeError, OperatorError) as error:
        # Deliberately no input echo, HTTP body, vault contents or Python traceback.
        code=str(error) if isinstance(error,OperatorError) else "invalid_operator_input"
        print(json.dumps({"status":"error","code":code}),file=sys.stderr)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
