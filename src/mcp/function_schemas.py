# JSON function definitions for model function-calling (OpenAI-style).
# Models that support function calling need a list of function descriptors (name, description, parameters schema).
# These are intentionally small and generic; extend to match your toolset.

FUNCTION_DEFINITIONS = [
    {
        "name": "search_documents",
        "description": "Search MCP-indexed documents for relevant sources to answer a user query. Returns a list of candidate MCP metadata.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The user's natural-language query"},
                "k": {"type": "integer", "description": "Number of documents to return", "default": 3, "minimum": 1, "maximum": 20}
            },
            "required": ["query"]
        },
    },
    {
        "name": "compute_drhash",
        "description": "Compute sha256 drhash for a given canonical_text (used to verify integrity).",
        "parameters": {
            "type": "object",
            "properties": {
                "canonical_text": {"type": "string", "description": "The canonicalized text to hash"}
            },
            "required": ["canonical_text"]
        },
    },
    {
        "name": "request_human_review",
        "description": "Create a human review ticket for a particular job or result when model indicates INSUFFICIENT_CONFIDENCE or disagreement.",
        "parameters": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "Optional job identifier in storage"},
                "reason": {"type": "string", "description": "Reason why human review was requested"},
                "meta": {"type": "object", "description": "Optional metadata for the ticket"}
            },
            "required": ["reason"]
        },
    },
]
