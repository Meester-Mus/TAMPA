from datanet import canonicalize_v1
from datanet import validate_tampa


def test_validate_basics():
    html = '<p>Hello world</p>'
    canonical = canonicalize_v1.canonicalize_html(html)
    # build a minimal tampa that matches drhash
    tampa = {'verdict_hint': 'NO_MATCH', 'matched_spans': [], 'internal': {'drhash': canonical['drhash']}}
    ok, reason = validate_tampa.validate_tampa_output(tampa, canonical['canonical_text'])
    assert ok, reason
