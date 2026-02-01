#!/bin/bash
#
# GPG Detached Signature Helper for Decision Records
#
# Usage: ./sign_decision.sh <decision_record.json> [key_id]
#

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <decision_record.json> [key_id]"
    exit 1
fi

DECISION_FILE="$1"
KEY_ID="${2:-}"

if [ ! -f "$DECISION_FILE" ]; then
    echo "Error: File not found: $DECISION_FILE"
    exit 1
fi

OUTPUT_FILE="${DECISION_FILE}.asc"

if [ -n "$KEY_ID" ]; then
    echo "Signing with key: $KEY_ID"
    gpg --detach-sign --armor --local-user "$KEY_ID" --output "$OUTPUT_FILE" "$DECISION_FILE"
else
    echo "Signing with default key"
    gpg --detach-sign --armor --output "$OUTPUT_FILE" "$DECISION_FILE"
fi

if [ $? -eq 0 ]; then
    echo "✓ Signature created: $OUTPUT_FILE"
    echo ""
    echo "To verify:"
    echo "  gpg --verify $OUTPUT_FILE $DECISION_FILE"
else
    echo "✗ Signature failed"
    exit 1
fi
