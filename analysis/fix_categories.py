import json

with open("data/apps_list.json", "r") as f:
    apps = json.load(f)
apps_by_id = {a["id"]: a for a in apps}

with open("output/results_v1_groq.json", "r") as f:
    results = json.load(f)

for r in results:
    if "category" not in r or not r["category"]:
        app_id = r.get("id")
        if app_id in apps_by_id:
            r["category"] = apps_by_id[app_id]["category"]

with open("output/results_v1_groq.json", "w") as f:
    json.dump(results, f, indent=2)

print("Backfilled category field for all apps.")