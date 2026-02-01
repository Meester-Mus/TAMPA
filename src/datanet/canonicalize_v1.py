import hashlib

def canonicalize_html(html: str):
    # Minimal placeholder canonicalizer: strip tags naive and normalize whitespace
    import re
    text = re.sub(r'&lt;[^&gt;]+&gt;', ' ', html)
    text = ' '.join(text.split())
    drhash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    sample = text[:200]
    return {'canonical_text': text, 'canonical_sample': sample, 'drhash': drhash}
