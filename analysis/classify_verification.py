import json

with open("output/link_check_report.json", "r") as f:
    report = json.load(f)

summary = []
for entry in report:
    good = sum(1 for c in entry["url_checks"] if isinstance(c["status"], int) and c["status"] < 400)
    broken_404_500 = sum(1 for c in entry["url_checks"] if isinstance(c["status"], int) and c["status"] in (404, 500))
    blocked_403 = sum(1 for c in entry["url_checks"] if isinstance(c["status"], int) and c["status"] == 403)
    dns_failed = sum(1 for c in entry["url_checks"] if isinstance(c["status"], str) and "FAILED" in c["status"])
    total = entry["total_urls"]

    if total == 0:
        flag = "no_evidence_provided"
    elif broken_404_500 + dns_failed == total:
        flag = "all_links_dead"
    elif broken_404_500 + dns_failed > 0:
        flag = "some_links_dead"
    elif blocked_403 == total:
        flag = "all_blocked_inconclusive"
    else:
        flag = "looks_clean"

    summary.append({
        "id": entry["id"],
        "app": entry["app"],
        "total_urls": total,
        "working": good,
        "dead_404_500": broken_404_500,
        "dns_failed": dns_failed,
        "blocked_403": blocked_403,
        "flag": flag
    })

with open("output/verification_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

from collections import Counter
flags = Counter(s["flag"] for s in summary)
print("Flag distribution:", flags)
print(f"\nApps needing priority human review (all_links_dead or no_evidence_provided):")
for s in summary:
    if s["flag"] in ("all_links_dead", "no_evidence_provided"):
        print(f"  - {s['app']}")