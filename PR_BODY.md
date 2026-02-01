# feat(mcp): add function-calling stubs and examples

## Summary
This PR adds function-calling support for MCP integration, enabling models to call server-side tools for document search, drhash computation, and human review requests.

## Files Added

### Core MCP Function-Calling Files
1. **src/mcp/function_schemas.py** - OpenAI-style function definitions for three tools:
   - `search_documents`: Search MCP-indexed documents by query
   - `compute_drhash`: Compute SHA256 hash for canonical text verification
   - `request_human_review`: Create human review tickets for low-confidence cases

2. **src/mcp/functions.py** - Server-side implementations:
   - Minimal stubs that can be extended with real integrations
   - Local file-based search implementation
   - SHA256 drhash computation
   - JSON-based ticket creation system

3. **examples/mcp_fncall_example.py** - Illustration of function-calling flow:
   - Shows how to provide functions to the model
   - Demonstrates executing server-side functions
   - Returns results to model for continuation

4. **tests/test_mcp_functions.py** - Unit tests:
   - Validates drhash computation matches canonicalizer
   - Tests human review ticket creation

### Supporting Files
5. **src/mcp/adapter.py** - MCP payload builder stub
6. **src/mcp/prompts.py** - System and user prompt templates
7. **src/datanet/canonicalize_v1.py** - HTML canonicalization stub
8. **requirements.txt** - Added pytest and pydantic dependencies
9. **.gitignore** - Excludes Python cache and build artifacts

## Updated Files
- **README.md** - Added "MCP integration" section with function calling documentation

## Run/Test Instructions

### Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Tests
```bash
pytest tests/test_mcp_functions.py -q
```

Expected output: 2 tests passed

### Run Example
```bash
PYTHONPATH=src python examples/mcp_fncall_example.py
```

This demonstrates the function-calling flow with simulated model interactions.

## Security Note: Do Not Trust Model-Supplied drhashes

⚠️ **IMPORTANT SECURITY CONSIDERATION**

**Never trust drhash values provided by the model.** Models can:
- Fabricate plausible-looking hashes
- Hallucinate matching hashes for non-existent content
- Be manipulated to return specific hash values

**Always compute drhashes server-side:**
1. Receive canonical_text from model
2. Compute drhash using `compute_drhash()` function server-side
3. Compare with stored/expected values
4. Treat any model-supplied drhash as untrusted metadata only

The `compute_drhash` function in this PR demonstrates the correct server-side approach for integrity verification.

## Pattern
1. Provide `functions` list to the model (SDK param)
2. If model returns `function_call`, execute the named function server-side
3. Return function output to model as a `function` role message for continuation

## Next Steps
- Replace stub implementations with production services (vector DB, ticketing system)
- Add authentication and authorization for function calls
- Implement rate limiting and abuse prevention
- Add comprehensive logging and monitoring
