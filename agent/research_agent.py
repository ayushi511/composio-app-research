import os
import json
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "openai/gpt-oss-20b"

with open("data/apps_list.json", "r") as f:
    apps = json.load(f)

with open("schema/app_schema.json", "r") as f:
    schema = json.load(f)



def build_prompt(app):
    return f"""Research this app's public developer/API documentation from what you know:

App: {app['app']}
Category: {app['category']}
Hint: {app['hint']}

Return ONLY a single JSON object (no markdown, no backticks, no extra text) with this exact structure:

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
        return {
            "id": app["id"],
            "app": app["app"],
            "error": str(e),
            "raw_response": text
        }


results = []
for i, app in enumerate(apps):
    print(f"[{i+1}/{len(apps)}] Researching {app['app']}...")
    result = research_app(app)
    results.append(result)
    time.sleep(1)

with open("output/results_v1_groq.json", "w") as f:
    json.dump(results, f, indent=2)

print("Done. Saved to output/results_v1_groq.json")