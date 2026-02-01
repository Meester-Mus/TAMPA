# Local TAMPA runner stub used for tests or local runs
from . import validate_tampa, canonicalize_v1

def run_local(snapshot_html):
    canonical = canonicalize_v1.canonicalize_html(snapshot_html)
    # For scaffold: return an empty NO_MATCH Tampa
    return {
        'verdict_hint': 'NO_MATCH',
        'matched_spans': [],
        'provenanceConfidence': 0.0,
        'provenance_breakdown': {'match_base': 0.0, 'main_content_bonus': 0.0, 'integrity_adjust': 0.0, 'multisource_bonus': 0.0, 'authority_boost': 0.0, 'final': 0.0},
        'internal': {'drhash': canonical['drhash'], 'canonical_sample': canonical['canonical_sample'], 'canonicalize_version': 'canonicalize_v1'},
        'runtime_ms': 0,
        'sigma_trace': [],
        'tampa_sigma': 0
    }
