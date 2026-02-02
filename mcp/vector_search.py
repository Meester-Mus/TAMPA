"""
Stub module for vector search functionality.
This will be implemented later with FAISS support.
"""


def build_index(data_root, model_name, force=False):
    """
    Build FAISS index from data directory.
    
    Args:
        data_root: Path to data directory
        model_name: Name of sentence transformer model
        force: Force rebuild of index
        
    Returns:
        dict with doc_count
    """
    # Stub implementation
    return {"doc_count": 0}


def search(query, k, data_root):
    """
    Search FAISS index for similar documents.
    
    Args:
        query: Search query string
        k: Number of results to return
        data_root: Path to data directory
        
    Returns:
        dict with results list
    """
    # Stub implementation
    return {"results": []}
