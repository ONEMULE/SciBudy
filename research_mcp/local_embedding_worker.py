from __future__ import annotations

import argparse
import json
import sys
import traceback
from typing import Any


def _last_token_pool(last_hidden_states, attention_mask):
    left_padding = attention_mask[:, -1].sum() == attention_mask.shape[0]
    if left_padding:
        return last_hidden_states[:, -1]
    sequence_lengths = attention_mask.sum(dim=1) - 1
    batch_size = last_hidden_states.shape[0]
    return last_hidden_states[range(batch_size), sequence_lengths]


class Worker:
    def __init__(self, *, model_name: str, output_dim: int, max_length: int, query_instruction: str) -> None:
        import torch
        import torch.nn.functional as F
        from transformers import AutoModel, AutoTokenizer

        self.torch = torch
        self.F = F
        self.model_name = model_name
        self.output_dim = output_dim
        self.max_length = max_length
        self.query_instruction = query_instruction
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        device_map = "auto" if torch.cuda.is_available() else None
        self.model = AutoModel.from_pretrained(
            model_name,
            dtype=dtype,
            device_map=device_map,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        )
        self.model.eval()

    def _prepare_texts(self, texts: list[str], input_type: str) -> list[str]:
        if input_type != "query":
            return texts
        prefix = f"Instruct: {self.query_instruction}\nQuery: "
        return [prefix + text for text in texts]

    def embed(self, texts: list[str], *, input_type: str) -> list[list[float]]:
        torch = self.torch
        prepared = self._prepare_texts(texts, input_type)
        outputs: list[list[float]] = []
        batch_size = 4 if torch.cuda.is_available() else 2
        with torch.no_grad():
            for start in range(0, len(prepared), batch_size):
                batch = prepared[start : start + batch_size]
                encoded = self.tokenizer(
                    batch,
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt",
                )
                encoded = {key: value.to(self.model.device) for key, value in encoded.items()}
                model_out = self.model(**encoded)
                embeddings = _last_token_pool(model_out.last_hidden_state, encoded["attention_mask"])
                embeddings = self.F.normalize(embeddings, p=2, dim=1)
                if self.output_dim and self.output_dim < embeddings.shape[1]:
                    embeddings = embeddings[:, : self.output_dim]
                    embeddings = self.F.normalize(embeddings, p=2, dim=1)
                outputs.extend(embeddings.detach().cpu().tolist())
        return outputs


def _write(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output-dim", type=int, default=2560)
    parser.add_argument("--max-length", type=int, default=4096)
    parser.add_argument(
        "--query-instruction",
        default="Given a research query, retrieve relevant passages that answer the query.",
    )
    args = parser.parse_args()

    try:
        worker = Worker(
            model_name=args.model,
            output_dim=args.output_dim,
            max_length=args.max_length,
            query_instruction=args.query_instruction,
        )
        _write({"status": "ready", "model": args.model, "output_dim": args.output_dim})
    except Exception as exc:  # noqa: BLE001
        _write({"status": "error", "message": str(exc), "traceback": traceback.format_exc()})
        raise SystemExit(1)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            if request.get("action") == "embed":
                vectors = worker.embed(request.get("texts") or [], input_type=request.get("input_type") or "passage")
                _write({"status": "ok", "vectors": vectors})
            elif request.get("action") == "ping":
                _write({"status": "ok", "message": "pong"})
            else:
                _write({"status": "error", "message": "unsupported action"})
        except Exception as exc:  # noqa: BLE001
            _write({"status": "error", "message": str(exc), "traceback": traceback.format_exc()})


if __name__ == "__main__":
    main()
