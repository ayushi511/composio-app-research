import json
import requests
import time

with open("output/results_v1_groq.json", "r") as f:
    results = json.load(f)

def check_url(url):
    try:
        resp = requests.head(url, timeout=8, allow_redirects=True,
                              headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code >= 400:
            resp = requests.get(url, timeout=8, allow_redirects=True,
                                 headers={"User-Agent": "Mozilla/5.0"})
        return resp.status_code
    except Exception as e:
        return f"FAILED: {e}"

verification_report = []

for entry in results:
    if "error" in entry:
        continue
    app_name = entry.get("app", "unknown")
    urls = entry.get("evidence_urls", [])
    url_checks = []
    for url in urls:
        status = check_url(url)
        url_checks.append({"url": url, "status": status})
        time.sleep(0.5)
    broken = [u for u in url_checks if not (isinstance(u["status"], int) and u["status"] < 400)]
    verification_report.append({
        "id": entry.get("id"),
        "app": app_name,
        "total_urls": len(urls),
        "broken_urls": len(broken),
        "url_checks": url_checks
    })
    print(f"Checked {app_name}: {len(urls)-len(broken)}/{len(urls)} URLs OK")

with open("output/link_check_report.json", "w") as f:
    json.dump(verification_report, f, indent=2)

print("Done. Saved to output/link_check_report.json")