#!/usr/bin/env python3
"""Build the TF-IDF index for MCP documents under data/ and save it to data/mcp_index.joblib"""
from mcp.searcher import build_index

if __name__ == "__main__":
    print(build_index(data_root="data"))
