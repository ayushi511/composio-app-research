import os
import json
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "openai/gpt-oss-20b"

with open("data/apps_list.json", "r") as f:
    all_apps = json.load(f)

with open("output/results_v1_groq.json", "r") as f:
    existing_results = json.load(f)

existing_by_id = {r["id"]: r for r in existing_results}
apps_by_id = {a["id"]: a for a in all_apps}

to_retry = [apps_by_id[app_id] for app_id, r in existing_by_id.items() if "error" in r]
print(f"Retrying {len(to_retry)} apps: {[a['app'] for a in to_retry]}")


def build_prompt(app):
    return f"""Research this app's public developer/API documentation from what you know:

App: {app['app']}
Category: {app['category']}
Hint: {app['hint']}

Return ONLY a single JSON object (no markdown, no backticks, no extra text, do not call any tools) with this exact structure:

{{
  "one_liner": "one sentence description",
  "auth_methods": ["OAuth2" or "API key" or "Basic" or "token" or "other"],
  "access": "self_serve | trial_then_paid | gated_paid | gated_approval | gated_partnership | unclear",
  "api_surface": {{
    "type": "REST | GraphQL | REST+GraphQL | SOAP | none_public",
    "breadth": "narrow | moderate | broad",
    "mcp_exists": true or false,
    "mcp_source": "official | community | none"
  }},
  "buildability": "ready | buildable_with_caveats | blocked",
  "blocker": "short string, empty if none",
  "evidence_urls": ["url1", "url2"],
  "confidence": "high | medium | low",
  "agent_notes": "1-2 sentences explaining your answer"
}}

Rules:
- Never invent a URL. Only include URLs you are confident are real documentation pages.
- Use "low" confidence if you're not sure, rather than guessing.
- Do not attempt to browse or search the web. Answer from what you already know.
"""


def research_app(app):
    prompt = build_prompt(app)
    text = None
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        data["id"] = app["id"]
        data["app"] = app["app"]
        return data
    except Exception as e:
        return {"id": app["id"], "app": app["app"], "error": str(e), "raw_response": text}


for i, app in enumerate(to_retry):
    print(f"[{i+1}/{len(to_retry)}] Retrying {app['app']}...")
    result = research_app(app)
    existing_by_id[app["id"]] = result
    time.sleep(3)

merged = [existing_by_id[a["id"]] for a in all_apps]
with open("output/results_v1_groq.json", "w") as f:
    json.dump(merged, f, indent=2)

print("Done. Merged results saved.")