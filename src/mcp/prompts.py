"""
MCP prompt templates for model interactions.
"""

SYSTEM_PROMPT = """You are a TAMPA verification assistant. You analyze MCP payloads containing canonical text and provenance data.
Your task is to verify claims against the provided evidence and return structured responses.
When uncertain or when confidence is low, you should request human review."""

USER_TEMPLATE = """MCP Payload:
{mcp_json}

User Question: {question}

Please analyze the provided MCP data and answer the question based on the evidence."""
