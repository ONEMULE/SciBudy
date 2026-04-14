from __future__ import annotations

import argparse

from huggingface_hub import snapshot_download


def warm(repo_id: str) -> None:
    print(f"warming {repo_id}", flush=True)
    snapshot_download(
        repo_id=repo_id,
        resume_download=True,
    )
    print(f"ready {repo_id}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--embedding-model", default="Qwen/Qwen3-Embedding-4B")
    parser.add_argument("--reranker-model", default="Qwen/Qwen3-Reranker-4B")
    parser.add_argument("--skip-embedding", action="store_true")
    parser.add_argument("--skip-reranker", action="store_true")
    args = parser.parse_args()

    if not args.skip_embedding:
        warm(args.embedding_model)
    if not args.skip_reranker:
        warm(args.reranker_model)


if __name__ == "__main__":
    main()
