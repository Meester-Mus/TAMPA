"""
Signing Helpers

Wrapper utilities for GPG detached signatures and JWS signing.
"""

import subprocess
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class GPGSigner:
    """GPG signing helper."""
    
    def __init__(self, key_id: Optional[str] = None, gpg_home: Optional[str] = None):
        """
        Initialize GPG signer.
        
        Args:
            key_id: GPG key ID to use for signing
            gpg_home: GPG home directory
        """
        self.key_id = key_id
        self.gpg_home = gpg_home
    
    def sign_detached(self, data: str, output_path: Optional[Path] = None) -> Optional[str]:
        """
        Create detached GPG signature.
        
        Args:
            data: Data to sign
            output_path: Optional path to write signature
            
        Returns:
            Signature string or None on failure
        """
        try:
            cmd = ["gpg", "--detach-sign", "--armor"]
            
            if self.key_id:
                cmd.extend(["--local-user", self.key_id])
            
            if self.gpg_home:
                cmd.extend(["--homedir", self.gpg_home])
            
            if output_path:
                cmd.extend(["--output", str(output_path)])
            
            result = subprocess.run(
                cmd,
                input=data.encode('utf-8'),
                capture_output=True,
                check=True
            )
            
            if output_path:
                logger.info(f"Signature written to {output_path}")
                return output_path.read_text()
            else:
                return result.stdout.decode('utf-8')
        
        except subprocess.CalledProcessError as e:
            logger.error(f"GPG signing failed: {e.stderr.decode('utf-8')}")
            return None
        except Exception as e:
            logger.error(f"GPG signing error: {e}")
            return None
    
    def verify_signature(self, data: str, signature: str) -> bool:
        """
        Verify detached GPG signature.
        
        Args:
            data: Original data
            signature: Detached signature
            
        Returns:
            True if signature is valid
        """
        try:
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as data_file:
                data_file.write(data)
                data_path = data_file.name
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as sig_file:
                sig_file.write(signature)
                sig_path = sig_file.name
            
            cmd = ["gpg", "--verify", sig_path, data_path]
            
            if self.gpg_home:
                cmd.extend(["--homedir", self.gpg_home])
            
            result = subprocess.run(cmd, capture_output=True)
            
            # Clean up temp files
            Path(data_path).unlink()
            Path(sig_path).unlink()
            
            return result.returncode == 0
        
        except Exception as e:
            logger.error(f"GPG verification error: {e}")
            return False


class JWSSigner:
    """JWS (JSON Web Signature) signing helper."""
    
    def __init__(self, private_key: Optional[str] = None, algorithm: str = "RS256"):
        """
        Initialize JWS signer.
        
        Args:
            private_key: Private key for signing (PEM format)
            algorithm: Signature algorithm
        """
        self.private_key = private_key
        self.algorithm = algorithm
    
    def sign(self, payload: Dict[str, Any]) -> Optional[str]:
        """
        Create JWS signature.
        
        Args:
            payload: Data to sign
            
        Returns:
            JWS token or None on failure
        """
        try:
            from jose import jws
            import json
            
            if not self.private_key:
                logger.error("No private key configured")
                return None
            
            payload_json = json.dumps(payload)
            token = jws.sign(
                payload_json,
                self.private_key,
                algorithm=self.algorithm
            )
            
            return token
        
        except ImportError:
            logger.error("python-jose not installed")
            return None
        except Exception as e:
            logger.error(f"JWS signing error: {e}")
            return None
    
    def verify(self, token: str, public_key: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWS signature.
        
        Args:
            token: JWS token
            public_key: Public key for verification
            
        Returns:
            Verified payload or None on failure
        """
        try:
            from jose import jws
            import json
            
            payload_json = jws.verify(
                token,
                public_key,
                algorithms=[self.algorithm]
            )
            
            return json.loads(payload_json)
        
        except ImportError:
            logger.error("python-jose not installed")
            return None
        except Exception as e:
            logger.error(f"JWS verification error: {e}")
            return None


def sign_decision_record(record_json: str, signer_type: str = "gpg", **kwargs) -> Optional[str]:
    """
    Sign a decision record.
    
    Args:
        record_json: Canonical JSON of decision record
        signer_type: Type of signer ('gpg' or 'jws')
        **kwargs: Signer-specific arguments
        
    Returns:
        Signature string or None on failure
    """
    if signer_type == "gpg":
        signer = GPGSigner(
            key_id=kwargs.get("key_id"),
            gpg_home=kwargs.get("gpg_home")
        )
        return signer.sign_detached(record_json)
    elif signer_type == "jws":
        import json
        signer = JWSSigner(
            private_key=kwargs.get("private_key"),
            algorithm=kwargs.get("algorithm", "RS256")
        )
        payload = json.loads(record_json)
        return signer.sign(payload)
    else:
        logger.error(f"Unknown signer type: {signer_type}")
        return None
