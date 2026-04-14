from __future__ import annotations

import argparse
import json
import sys
import traceback
from typing import Any


class Worker:
    def __init__(self, *, model_name: str, max_length: int, instruction: str) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.model_name = model_name
        self.max_length = max_length
        self.instruction = instruction
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        device_map = "auto" if torch.cuda.is_available() else None
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            dtype=dtype,
            device_map=device_map,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        ).eval()
        self.token_false_id = self.tokenizer.convert_tokens_to_ids("no")
        self.token_true_id = self.tokenizer.convert_tokens_to_ids("yes")
        prefix = (
            '<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct '
            'provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n'
        )
        suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        self.prefix_tokens = self.tokenizer.encode(prefix, add_special_tokens=False)
        self.suffix_tokens = self.tokenizer.encode(suffix, add_special_tokens=False)

    def rerank(self, query: str, documents: list[str]) -> list[float]:
        torch = self.torch
        if not documents:
            return []
        pairs = [
            f"<Instruct>: {self.instruction}\n<Query>: {query}\n<Document>: {document}"
            for document in documents
        ]
        batch_size = 2 if torch.cuda.is_available() else 1
        scores: list[float] = []
        with torch.no_grad():
            for start in range(0, len(pairs), batch_size):
                batch_pairs = pairs[start : start + batch_size]
                inputs = self.tokenizer(
                    batch_pairs,
                    padding=False,
                    truncation="longest_first",
                    return_attention_mask=False,
                    max_length=self.max_length - len(self.prefix_tokens) - len(self.suffix_tokens),
                )
                for index, value in enumerate(inputs["input_ids"]):
                    inputs["input_ids"][index] = self.prefix_tokens + value + self.suffix_tokens
                inputs = self.tokenizer.pad(inputs, padding=True, return_tensors="pt", max_length=self.max_length)
                inputs = {key: value.to(self.model.device) for key, value in inputs.items()}
                logits = self.model(**inputs).logits[:, -1, :]
                true_vector = logits[:, self.token_true_id]
                false_vector = logits[:, self.token_false_id]
                stacked = torch.stack([false_vector, true_vector], dim=1)
                stacked = torch.nn.functional.log_softmax(stacked, dim=1)
                batch_scores = stacked[:, 1].exp().detach().cpu().tolist()
                scores.extend(batch_scores)
        return scores


def _write(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--max-length", type=int, default=4096)
    parser.add_argument(
        "--instruction",
        default="Given a research query, retrieve relevant passages that answer the query.",
    )
    args = parser.parse_args()

    try:
        worker = Worker(model_name=args.model, max_length=args.max_length, instruction=args.instruction)
        _write({"status": "ready", "model": args.model})
    except Exception as exc:  # noqa: BLE001
        _write({"status": "error", "message": str(exc), "traceback": traceback.format_exc()})
        raise SystemExit(1)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            if request.get("action") == "rerank":
                scores = worker.rerank(request.get("query") or "", request.get("documents") or [])
                _write({"status": "ok", "scores": scores})
            elif request.get("action") == "ping":
                _write({"status": "ok", "message": "pong"})
            else:
                _write({"status": "error", "message": "unsupported action"})
        except Exception as exc:  # noqa: BLE001
            _write({"status": "error", "message": str(exc), "traceback": traceback.format_exc()})


if __name__ == "__main__":
    main()
