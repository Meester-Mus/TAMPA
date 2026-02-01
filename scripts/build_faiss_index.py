#!/usr/bin/env python3
"""Build the FAISS index for MCP documents under data/ and save it to data/faiss_index.faiss"""
from mcp.vector_search import build_index
import sys
import argparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", default="data")
    p.add_argument("--index-path", default=None)
    p.add_argument("--model", default="all-MiniLM-L6-v2")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    try:
        res = build_index(data_root=args.data_root, index_path=args.index_path, model_name=args.model, force=args.force)
        print(res)
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
