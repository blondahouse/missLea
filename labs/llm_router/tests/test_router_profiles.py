"""Static safety checks for the gateway's deterministic synthetic configuration."""
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RouterProfilesTests(unittest.TestCase):
    def test_bifrost_uses_only_three_loopback_fixtures(self):
        data = json.loads((ROOT / "profiles/bifrost.json").read_text())
        providers = data["providers"]
        self.assertEqual(set(providers), {"lab-primary", "lab-backup", "lab-paid"})
        for name, port in [("lab-primary", 19100), ("lab-backup", 19101), ("lab-paid", 19102)]:
            self.assertEqual(
                providers[name]["network_config"]["base_url"],
                f"http://127.0.0.1:{port}",
            )
            self.assertEqual(providers[name]["keys"][0]["value"], "sk-lab-synthetic-only")
        self.assertIs(data["config_store"]["enabled"], True)
        self.assertTrue(data["client"]["enforce_auth_on_inference"])
        self.assertTrue(data["governance"]["auth_config"]["is_enabled"])
        self.assertEqual(len(data["governance"]["virtual_keys"]), 2)

    def test_no_provider_secrets_in_profiles(self):
        config = (ROOT / "profiles/bifrost.json").read_text()
        self.assertNotIn("env.OPENAI_API_KEY", config)
        self.assertNotIn("api.openai.com", config)


if __name__ == "__main__":
    unittest.main()
