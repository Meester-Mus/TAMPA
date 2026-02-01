# Extended JSON function definitions for model function-calling (OpenAI-style).
# Adds higher-level functions used by agents: fetch_full_mcp, annotate_span, export_result.

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
    {
        "name": "fetch_full_mcp",
        "description": "Fetch the full MCP payload (meta + snapshot) for a job id so the model can inspect full context.",
        "parameters": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "The job id for the MCP payload to fetch"}
            },
            "required": ["job_id"]
        }
    },
    {
        "name": "annotate_span",
        "description": "Attach an annotation to a matched span in a job's metadata (for human review or downstream signals).",
        "parameters": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "Job id where the span lives"},
                "drhash": {"type": "string", "description": "Document hash for the canonical text"},
                "start": {"type": "integer", "description": "Span start offset"},
                "end": {"type": "integer", "description": "Span end offset"},
                "note": {"type": "string", "description": "Annotation note or label"}
            },
            "required": ["job_id", "drhash", "start", "end", "note"]
        }
    },
    {
        "name": "export_result",
        "description": "Export a job result to a specified format and return a pointer/URL to the exported artifact.",
        "parameters": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "Job id to export"},
                "format": {"type": "string", "enum": ["json", "text"], "description": "Export format"}
            },
            "required": ["job_id", "format"]
        }
    }
]
