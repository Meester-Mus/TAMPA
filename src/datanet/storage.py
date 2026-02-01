"""
Storage Abstraction

Simple storage layer for job results, decisions, and canonical data.
Supports local filesystem and MinIO S3-compatible storage.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class StorageBackend:
    """Base class for storage backends."""
    
    def store(self, key: str, data: Any) -> bool:
        """Store data with given key."""
        raise NotImplementedError
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data by key."""
        raise NotImplementedError
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with optional prefix."""
        raise NotImplementedError
    
    def delete(self, key: str) -> bool:
        """Delete data by key."""
        raise NotImplementedError


class LocalStorage(StorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, base_path: str = "./data"):
        """
        Initialize local storage.
        
        Args:
            base_path: Base directory for storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_path(self, key: str) -> Path:
        """Get full path for a key."""
        return self.base_path / f"{key}.json"
    
    def store(self, key: str, data: Any) -> bool:
        """Store data to local file."""
        try:
            path = self._get_path(key)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Stored data to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to store {key}: {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from local file."""
        try:
            path = self._get_path(key)
            if not path.exists():
                return None
            
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to retrieve {key}: {e}")
            return None
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with prefix."""
        try:
            pattern = f"{prefix}*.json" if prefix else "*.json"
            files = self.base_path.glob(pattern)
            return [f.stem for f in files]
        except Exception as e:
            logger.error(f"Failed to list keys: {e}")
            return []
    
    def delete(self, key: str) -> bool:
        """Delete data file."""
        try:
            path = self._get_path(key)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete {key}: {e}")
            return False


class MinIOStorage(StorageBackend):
    """MinIO S3-compatible storage backend."""
    
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str = "tampa-data",
        secure: bool = False
    ):
        """
        Initialize MinIO storage.
        
        Args:
            endpoint: MinIO endpoint (e.g., 'localhost:9000')
            access_key: Access key
            secret_key: Secret key
            bucket: Bucket name
            secure: Use HTTPS
        """
        try:
            from minio import Minio
            
            self.client = Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )
            self.bucket = bucket
            
            # Create bucket if it doesn't exist
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                logger.info(f"Created bucket: {bucket}")
        except ImportError:
            logger.error("minio package not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize MinIO: {e}")
            raise
    
    def store(self, key: str, data: Any) -> bool:
        """Store data to MinIO."""
        try:
            import io
            
            json_data = json.dumps(data, indent=2)
            data_bytes = json_data.encode('utf-8')
            
            self.client.put_object(
                self.bucket,
                f"{key}.json",
                io.BytesIO(data_bytes),
                len(data_bytes),
                content_type="application/json"
            )
            
            logger.info(f"Stored data to MinIO: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store {key}: {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from MinIO."""
        try:
            response = self.client.get_object(self.bucket, f"{key}.json")
            data = response.read()
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to retrieve {key}: {e}")
            return None
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with prefix."""
        try:
            objects = self.client.list_objects(self.bucket, prefix=prefix)
            return [obj.object_name.replace('.json', '') for obj in objects]
        except Exception as e:
            logger.error(f"Failed to list keys: {e}")
            return []
    
    def delete(self, key: str) -> bool:
        """Delete object from MinIO."""
        try:
            self.client.remove_object(self.bucket, f"{key}.json")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {key}: {e}")
            return False


def get_storage(storage_type: str = "local", **kwargs) -> StorageBackend:
    """
    Get storage backend instance.
    
    Args:
        storage_type: Type of storage ('local' or 'minio')
        **kwargs: Storage-specific configuration
        
    Returns:
        StorageBackend instance
    """
    if storage_type == "local":
        return LocalStorage(kwargs.get("base_path", "./data"))
    elif storage_type == "minio":
        return MinIOStorage(
            endpoint=kwargs.get("endpoint", "localhost:9000"),
            access_key=kwargs.get("access_key", "minioadmin"),
            secret_key=kwargs.get("secret_key", "minioadmin"),
            bucket=kwargs.get("bucket", "tampa-data"),
            secure=kwargs.get("secure", False)
        )
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")
