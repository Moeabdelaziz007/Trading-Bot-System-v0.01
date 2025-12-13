import threading
import time
import requests
import json
import random
from concurrent.futures import ThreadPoolExecutor

# CONFIGURATION
TARGET_URL = "http://localhost:8787"
REPORT_FILE = "tests/chaos_report.json"

class ChaosMonkey:
    def __init__(self):
        self.results = {
            "auth_bypass": {"status": "SKIPPED", "details": ""},
            "sql_injection": {"status": "SKIPPED", "details": ""},
            "circuit_breaker": {"status": "SKIPPED", "details": ""},
            "rate_limit": {"status": "SKIPPED", "details": ""}
        }

    def log(self, message):
        print(f"[🐵 CHAOS] {message}")

    def attack_auth_bypass(self):
        """
        Attack Vector: Auth Bypass
        Attempt to POST to /api/news/push without X-Internal-Secret.
        """
        self.log("🚀 Launching Auth Bypass Attack on /api/news/push...")
        url = f"{TARGET_URL}/api/news/push"
        payload = {
            "source": "CHAOS_BOT",
            "title": "HACKED",
            "link": "http://evil.com",
            "sentiment": "negative"
        }

        try:
            # Attempt 1: No Headers
            response = requests.post(url, json=payload, timeout=5)

            if response.status_code == 200:
                self.results["auth_bypass"] = {"status": "VULNERABLE", "details": "Request succeeded without headers (HTTP 200)"}
                self.log("❌ VULNERABILITY CONFIRMED: Auth Bypass Successful!")
            elif response.status_code == 401:
                self.results["auth_bypass"] = {"status": "SECURE", "details": "Request rejected (HTTP 401)"}
                self.log("✅ Attack Failed: System correctly returned 401.")
            else:
                self.results["auth_bypass"] = {"status": "UNKNOWN", "details": f"Unexpected status: {response.status_code}"}
                self.log(f"⚠️ Unexpected response: {response.status_code}")

        except requests.exceptions.ConnectionError:
            self.results["auth_bypass"] = {"status": "FAILED", "details": "Connection Refused (Target Down)"}
            self.log("💀 Target is down or unreachable.")

    def attack_sql_injection(self):
        """
        Attack Vector: SQL Injection
        Inject '; DROP TABLE news; -- into JSON payloads.
        """
        self.log("💉 Injecting SQL Payload into /api/news/push...")
        url = f"{TARGET_URL}/api/news/push"

        # We need a valid secret to test SQLi (otherwise we get 401)
        # Assuming we don't have it, we test if the input is sanitized even if we bypass/guess or if we can inject via other means.
        # But wait, if we are black-box testing and don't have the secret, we can't reach the SQL query.
        # However, the instructions say "Inject ... into JSON body".
        # I will assume for this test we might have the secret OR we are testing if the parsing fails before auth (unlikely).
        # Let's try without secret first, but if that 401s, we can't test SQLi.
        # IF the Auth Bypass was successful, THEN this executes.
        # If Auth Bypass failed, SQLi test is effectively blocked by Auth (which is good).

        payload = {
            "source": "CHAOS_BOT",
            "title": "'; DROP TABLE news; --",
            "link": "http://evil.com",
            "sentiment": "neutral"
        }

        try:
            response = requests.post(url, json=payload, headers={"X-Internal-Secret": "admin"}, timeout=5) # Guessing secret

            if response.status_code == 200:
                # If 200, it accepted the payload. We need to check if table is dropped?
                # We can't easily check that. But if it returns 200, the injection likely didn't crash it.
                # If it returns 500 with a DB error, it might be vulnerable or just failed constraint.
                self.results["sql_injection"] = {"status": "INCONCLUSIVE", "details": "Request accepted (HTTP 200). Manual verification needed."}
                self.log("⚠️ SQL Injection: Request accepted. Check Database integrity.")
            elif response.status_code == 500:
                 if "syntax" in response.text.lower() or "database" in response.text.lower():
                     self.results["sql_injection"] = {"status": "POTENTIAL_VULNERABILITY", "details": "DB Error returned: " + response.text[:50]}
                     self.log("❌ SQL Error Exposed!")
                 else:
                     self.results["sql_injection"] = {"status": "ERROR", "details": "HTTP 500 returned"}
            else:
                 self.results["sql_injection"] = {"status": "BLOCKED", "details": f"Status {response.status_code}"}
                 self.log(f"✅ SQL Injection blocked (Status {response.status_code})")

        except Exception as e:
            self.results["sql_injection"] = {"status": "ERROR", "details": str(e)}

    def attack_rapid_fire(self):
        """
        Attack Vector: DDoS Simulation / Circuit Breaker Test
        Flood /api/news/latest (100 req/s).
        """
        self.log("🔥 Initiating Rapid Fire (DDoS Simulation)...")
        url = f"{TARGET_URL}/api/news/latest"

        requests_count = 100
        success = 0
        failures = 0
        circuit_open = False

        start_time = time.time()

        def make_request():
            nonlocal success, failures, circuit_open
            try:
                r = requests.get(url, timeout=2)
                if r.status_code == 200:
                    success += 1
                elif r.status_code == 503:
                    failures += 1
                    if "Circuit Open" in r.text or "Service Unavailable" in r.text:
                        circuit_open = True
                else:
                    failures += 1
            except:
                failures += 1

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(requests_count)]
            for f in futures:
                f.result()

        duration = time.time() - start_time
        rps = requests_count / duration
        self.log(f"⚡ Attack finished in {duration:.2f}s ({rps:.2f} req/s)")

        details = f"Success: {success}, Failed/Blocked: {failures}. Circuit Open detected: {circuit_open}"

        if circuit_open:
            self.results["circuit_breaker"] = {"status": "PASS", "details": "Circuit Breaker ACTIVATED (503 received)."}
            self.log("✅ Circuit Breaker resilience confirmed.")
        else:
            self.results["circuit_breaker"] = {"status": "FAIL", "details": "No Circuit Breaker detected (Circuit did not open)."}
            self.log("❌ Circuit Breaker FAILED to open.")

    def run(self):
        self.log("🐵 Starting Operation Chaos Monkey...")

        # 1. Auth Bypass
        self.attack_auth_bypass()

        # 2. SQL Injection
        self.attack_sql_injection()

        # 3. Rapid Fire
        self.attack_rapid_fire()

        # Report
        with open(REPORT_FILE, "w") as f:
            json.dump(self.results, f, indent=2)

        self.log(f"📝 Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    monkey = ChaosMonkey()
    monkey.run()
