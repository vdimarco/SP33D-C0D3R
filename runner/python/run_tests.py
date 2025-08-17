import json, os, subprocess, sys, time, requests

API = os.getenv("API_URL", "http://api:8000")
run_id = sys.argv[1]

def _run(cmd):
    start = time.time()
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode == 0, time.time() - start, p.stdout

ok_pub, dt_pub, log_pub = _run(["pytest", "-q", "tests_public", "--maxfail=1", "--disable-warnings"])
ok_hid, dt_hid, log_hid = _run(["pytest", "-q", "tests_hidden", "--maxfail=1", "--disable-warnings"])

passed = ok_pub and ok_hid
payload = {
    "passed": passed,
    "public_ok": ok_pub,
    "hidden_ok": ok_hid,
    "logs": {
        "public": log_pub[-4000:],
        "hidden": (log_hid[-4000:] if passed else "redacted until pass"),
    },
}
try:
    requests.post(f"{API}/runs/{run_id}/result", json=payload, timeout=5)
except Exception as e:
    print("warn: result post failed", e)
