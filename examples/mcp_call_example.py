"""
Example: build an MCP payload from canonicalize_v1 and call OpenAI chat completion.
This script is a template — do not commit secrets. Use environment OPENAI_API_KEY when running locally.
"""
import json
import os
from datanet.canonicalize_v1 import canonicalize_html
from mcp.adapter import build_mcp_payload
from mcp.prompts import SYSTEM_PROMPT, USER_TEMPLATE

# Example HTML
HTML = "<html><body><p>Example content: Alice said X and Bob said Y.</p></body></html>"

def example_run(question: str):
    canonical = canonicalize_html(HTML)
    provenance = {
        "provenanceConfidence": 0.87,
        "provenance_breakdown": {
            "match_base": 0.70,
            "main_content_bonus": 0.10,
            "integrity_adjust": 0.05,
            "multisource_bonus": 0.02,
            "authority_boost": 0.00,
            "final": 0.87,
        },
    }
    mcp = build_mcp_payload(canonical, provenance, matched_spans=[])
    mcp_json = json.dumps(mcp, ensure_ascii=False)

    system = {"role": "system", "content": SYSTEM_PROMPT}
    user = {"role": "user", "content": USER_TEMPLATE.format(mcp_json=mcp_json, question=question)}

    # Example using OpenAI chat completion (pseudocode)
    # from openai import OpenAI
    # client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    # resp = client.chat.completions.create(model="gpt-4o-mini", messages=[system, user], max_tokens=400)
    # print(resp.choices[0].message.content)

    print("SYSTEM PROMPT:\n", SYSTEM_PROMPT)
    print("USER MESSAGE (truncated):\n", user["content"][:1000])
    print("\n[Run the model client locally with your API key as shown in comments]")
