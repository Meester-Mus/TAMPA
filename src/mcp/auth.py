from os import environ
from typing import List, Optional, Dict, Any

MCP_API_KEYS_ENV = "MCP_API_KEYS"  # comma-separated list of valid keys

def _load_api_keys() -> List[str]:
    v = environ.get(MCP_API_KEYS_ENV, "")
    if not v:
        return []
    return [k.strip() for k in v.split(",") if k.strip()]

def is_auth_enabled() -> bool:
    return len(_load_api_keys()) > 0

def validate_api_key(key: Optional[str]) -> bool:
    """
    Return True when key is allowed. If no keys are configured, validation passes (auth disabled).
    """
    allowed = _load_api_keys()
    if not allowed:
        return True
    if not key:
        return False
    return key in allowed

def get_api_key_from_headers(headers: Dict[str, Any]) -> Optional[str]:
    """
    Simple header extractor: looks for 'Authorization: Bearer <key>' or 'X-API-Key'.
    """
    auth = headers.get("Authorization") or headers.get("authorization")
    if auth and isinstance(auth, str) and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    x = headers.get("X-API-Key") or headers.get("x-api-key")
    if x:
        return x
    return None

# Simple argument validation to reduce attack surface / huge payloads.
def validate_function_args(args: Dict[str, Any], allowed_keys: Optional[List[str]] = None, max_total_size: int = 200_000) -> None:
    """
    - allowed_keys: if provided, ensure args only contains those keys.
    - max_total_size: approximate limit on serialized size of args to avoid huge payloads.
    Raises ValueError on invalid input.
    """
    if allowed_keys is not None:
        extra = set(args.keys()) - set(allowed_keys)
        if extra:
            raise ValueError(f"Unexpected argument keys: {sorted(list(extra))}")
    # Simple size check
    try:
        import json
        s = json.dumps(args)
        if len(s) > max_total_size:
            raise ValueError("Function arguments exceed max allowed size")
    except ValueError:
        # Re-raise our own ValueError as-is
        raise
    except Exception as e:
        # If serialization fails, reject with context
        raise ValueError(f"Invalid function arguments: {type(e).__name__}") from e
