# GPG Signing Guide

## Overview

TAMPA Datanet Agent supports GPG detached signatures for decision records.
This ensures cryptographic verification of canonical changes and acceptance decisions.

## Prerequisites

- GPG installed (`gpg --version`)
- GPG key pair generated

## Generating a GPG Key

If you don't have a GPG key:

```bash
# Generate new key
gpg --full-generate-key

# Follow prompts:
# - Select RSA and RSA (default)
# - Key size: 4096 bits
# - Expiration: choose appropriate time
# - Name and email: your identity
# - Passphrase: choose strong passphrase
```

## Listing Keys

```bash
# List public keys
gpg --list-keys

# List secret keys
gpg --list-secret-keys

# Example output:
# pub   rsa4096 2024-01-01 [SC]
#       ABCD1234ABCD1234ABCD1234ABCD1234ABCD1234
# uid           [ultimate] Your Name <you@example.com>
```

## Signing a Decision Record

### Method 1: Using the Helper Script

```bash
# Sign with default key
./scripts/sign_decision.sh decision_record.json

# Sign with specific key
./scripts/sign_decision.sh decision_record.json ABCD1234ABCD1234
```

This creates `decision_record.json.asc` with the detached signature.

### Method 2: Using GPG Directly

```bash
# Create detached signature
gpg --detach-sign --armor \
    --local-user YOUR_KEY_ID \
    --output decision.json.asc \
    decision.json
```

### Method 3: Using Python Helper

```python
from src.datanet.sign_helpers import GPGSigner

signer = GPGSigner(key_id="YOUR_KEY_ID")
signature = signer.sign_detached(decision_json_string)
print(signature)
```

## Verifying a Signature

```bash
# Verify detached signature
gpg --verify decision.json.asc decision.json

# Expected output on success:
# gpg: Signature made ...
# gpg: Good signature from "Your Name <you@example.com>"
```

## Exporting Public Key

To allow others to verify your signatures:

```bash
# Export public key
gpg --armor --export YOUR_KEY_ID > pubkey.asc

# Import someone's public key
gpg --import their_pubkey.asc
```

## Configuration

### Setting Default Key

Edit `~/.gnupg/gpg.conf`:

```
default-key YOUR_KEY_ID
```

### Configure in TAMPA

Edit `configs/authority_v1.json`:

```json
{
  "signing": {
    "default_method": "gpg",
    "gpg_key_id": "YOUR_KEY_ID",
    "require_detached_signature": true
  }
}
```

## Workflow Example

### 1. Create Decision Record

```python
from src.datanet.decision_composer import DecisionComposer

composer = DecisionComposer()
record = composer.compose_canon_proposal(
    current_canon={"version": "v1"},
    proposed_change={"version": "v2"},
    rationale="Update for new features",
    author="alice@example.com"
)

# Get canonical JSON
canonical_json = record.to_canonical_json()

# Save to file
with open("decision.json", "w") as f:
    f.write(canonical_json)
```

### 2. Sign the Record

```bash
./scripts/sign_decision.sh decision.json YOUR_KEY_ID
```

### 3. Verify and Store

```bash
# Verify signature
gpg --verify decision.json.asc decision.json

# Store both files
# - decision.json (canonical record)
# - decision.json.asc (detached signature)
```

## JWS Alternative

For environments without GPG:

```python
from src.datanet.sign_helpers import JWSSigner

# Load your private key (PEM format)
with open("private_key.pem") as f:
    private_key = f.read()

signer = JWSSigner(private_key=private_key, algorithm="RS256")
token = signer.sign({"decision": "data"})
print(token)

# Verify with public key
with open("public_key.pem") as f:
    public_key = f.read()

verified = signer.verify(token, public_key)
print(verified)
```

## Security Best Practices

1. **Protect Private Keys**: Never commit private keys to version control
2. **Use Strong Passphrases**: Protect GPG keys with strong passphrases
3. **Key Rotation**: Regularly rotate signing keys
4. **Backup Keys**: Securely backup private keys
5. **Verify Imports**: Always verify fingerprints when importing public keys
6. **Revocation Certificate**: Generate revocation certificate when creating keys

## Common Issues

### "No secret key" Error

```bash
# You need to import or generate your secret key
gpg --list-secret-keys
```

### Permission Denied

```bash
# Fix GPG directory permissions
chmod 700 ~/.gnupg
chmod 600 ~/.gnupg/*
```

### "Inappropriate ioctl for device"

```bash
# Set GPG_TTY for terminal
export GPG_TTY=$(tty)

# Add to ~/.bashrc or ~/.zshrc
echo 'export GPG_TTY=$(tty)' >> ~/.bashrc
```

## References

- [GnuPG Manual](https://gnupg.org/documentation/)
- [GPG Best Practices](https://riseup.net/en/security/message-security/openpgp/gpg-best-practices)
- [JSON Web Signature (JWS) RFC](https://tools.ietf.org/html/rfc7515)
