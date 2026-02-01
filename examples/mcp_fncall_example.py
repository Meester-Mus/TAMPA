"""
Illustration of function-calling flow with a model.
This pseudocode demonstrates providing function schemas to the model, receiving a function_call,
executing the function server-side, and sending the result back to the model for finalization.
(Adapt to your LLM SDK.)
"""
import json
import os
from datanet.canonicalize_v1 import canonicalize_html
from mcp.adapter import build_mcp_payload
from mcp.prompts import SYSTEM_PROMPT, USER_TEMPLATE
from mcp.function_schemas import FUNCTION_DEFINITIONS
from mcp.functions import compute_drhash, search_documents, request_human_review

# NOTE: replace with your model client (OpenAI or other). This is illustrative pseudocode.

def run_with_model(question: str):
    html = "<html><body><p>Example: Alice said X and Bob said Y.</p></body></html>"
    canonical = canonicalize_html(html)
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
    mcp = build_mcp_payload(canonical["canonical_text"], provenance, matched_spans=[])
    mcp_json = json.dumps(mcp, ensure_ascii=False)

    system = {"role": "system", "content": SYSTEM_PROMPT}
    user = {"role": "user", "content": USER_TEMPLATE.format(mcp_json=mcp_json, question=question)}

    # Example using OpenAI-style function calling (pseudocode):
    # resp = client.chat.completions.create(
    #   model="gpt-4o-mini",
    #   messages=[system, user],
    #   functions=FUNCTION_DEFINITIONS,
    #   function_call="auto"
    # )
    #
    # If the response includes a function_call:
    #    fn_name = resp.choices[0].message.function_call.name
    #    fn_args = json.loads(resp.choices[0].message.function_call.arguments)
    #
    # Call the local implementation:
    #    if fn_name == "compute_drhash": result = compute_drhash(**fn_args)
    #    elif fn_name == "search_documents": result = search_documents(**fn_args)
    #    elif fn_name == "request_human_review": result = request_human_review(**fn_args)
    #
    # Then send the function result back to the model:
    #    followup = {"role":"function", "name": fn_name, "content": json.dumps(result)}
    #    final = client.chat.completions.create(model="gpt-4o-mini", messages=[system, user, followup])
    #
    # Print placeholders to show flow:
    print("Would call model with FUNCTIONS:", [f["name"] for f in FUNCTION_DEFINITIONS])
    print("Example MCP payload drhash:", mcp["source"]["drhash"])
    # Simulate a compute_drhash call:
    print("Simulated compute_drhash result:", compute_drhash(mcp["canonical_text"]))
    # Simulate search_documents:
    print("Simulated search_documents result:", search_documents("Alice", k=2))

if __name__ == "__main__":
    run_with_model("What did Alice say?")
