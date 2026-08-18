import json
from collections import Counter, defaultdict

with open("output/results_v1_groq.json", "r") as f:
    data = json.load(f)

# Filter out any remaining errors
data = [d for d in data if "error" not in d]
print(f"Analyzing {len(data)} apps\n")

# 1. Auth method distribution
auth_counter = Counter()
for d in data:
    for method in d.get("auth_methods", []):
        auth_counter[method] += 1

print("=== AUTH METHOD DISTRIBUTION ===")
for method, count in auth_counter.most_common():
    pct = count / len(data) * 100
    print(f"  {method}: {count} ({pct:.0f}%)")

# 2. Access model distribution
access_counter = Counter(d.get("access", "unclear") for d in data)
print("\n=== ACCESS MODEL DISTRIBUTION ===")
for access, count in access_counter.most_common():
    pct = count / len(data) * 100
    print(f"  {access}: {count} ({pct:.0f}%)")

# 3. Buildability distribution
build_counter = Counter(d.get("buildability", "unknown") for d in data)
print("\n=== BUILDABILITY DISTRIBUTION ===")
for status, count in build_counter.most_common():
    pct = count / len(data) * 100
    print(f"  {status}: {count} ({pct:.0f}%)")

# 4. Access model BY category (cross-tab)
category_access = defaultdict(lambda: Counter())
for d in data:
    category_access[d.get("category", "unknown")][d.get("access", "unclear")] += 1

print("\n=== ACCESS MODEL BY CATEGORY ===")
for category, counter in category_access.items():
    total = sum(counter.values())
    breakdown = ", ".join(f"{k}: {v}" for k, v in counter.most_common())
    print(f"  {category} ({total} apps): {breakdown}")

# 5. Most common blockers (non-empty only)
blocker_counter = Counter(d.get("blocker", "").strip().lower() for d in data if d.get("blocker"))
print("\n=== MOST COMMON BLOCKERS ===")
if blocker_counter:
    for blocker, count in blocker_counter.most_common(10):
        print(f"  {blocker}: {count}")
else:
    print("  (most apps reported no blocker / blocker field mostly empty)")

# 6. MCP existence
mcp_counter = Counter()
for d in data:
    surface = d.get("api_surface", {})
    exists = surface.get("mcp_exists")
    source = surface.get("mcp_source", "none")
    key = f"{'has MCP' if exists else 'no MCP'} ({source})" if exists else "no MCP"
    mcp_counter[key] += 1

print("\n=== MCP EXISTENCE ===")
for key, count in mcp_counter.most_common():
    pct = count / len(data) * 100
    print(f"  {key}: {count} ({pct:.0f}%)")

# 7. Easy wins vs needs outreach
easy_wins = [d["app"] for d in data if d.get("access") == "self_serve" and d.get("buildability") == "ready"]
needs_outreach = [d["app"] for d in data if d.get("access") in ("gated_approval", "gated_partnership")]

print(f"\n=== EASY WINS (self-serve + ready): {len(easy_wins)} apps ===")
print(f"  {', '.join(easy_wins[:15])}{'...' if len(easy_wins) > 15 else ''}")

print(f"\n=== NEEDS OUTREACH (approval/partnership gated): {len(needs_outreach)} apps ===")
print(f"  {', '.join(needs_outreach) if needs_outreach else '(none found)'}")

# Save full structured summary for the HTML page to consume
summary = {
    "total_apps": len(data),
    "auth_distribution": dict(auth_counter),
    "access_distribution": dict(access_counter),
    "buildability_distribution": dict(build_counter),
    "access_by_category": {k: dict(v) for k, v in category_access.items()},
    "top_blockers": dict(blocker_counter.most_common(10)),
    "mcp_distribution": dict(mcp_counter),
    "easy_wins": easy_wins,
    "needs_outreach": needs_outreach
}

with open("output/pattern_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\nSaved structured summary to output/pattern_summary.json")