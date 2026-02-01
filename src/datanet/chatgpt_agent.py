import os

def run_chatgpt_tampa(canonical_text, canonical_sample, drhash):
    # Stub: if OPENAI_API_KEY not set, return an error-like dict to be saved as raw
    if not os.getenv('OPENAI_API_KEY'):
        return {'error': 'OPENAI_API_KEY not set', 'canonical_sample': canonical_sample}
    # In real usage this function should call the remote model and return parsed JSON
    raise RuntimeError('chatgpt_agent not implemented in scaffold')
