import datetime
import json
import os
from threading import Lock
from typing import Any


class OkrasService:
    def __init__(self, *, storage_dir: str) -> None:
        self._storage_dir = storage_dir
        self._write_lock = Lock()

    def _ensure_dir(self) -> None:
        os.makedirs(self._storage_dir, exist_ok=True)

    def resolve_okras_daily_file(self, now: datetime.datetime | None = None) -> str:
        current = now or datetime.datetime.now()
        name = current.strftime("okras-%Y-%m-%d.jsonl")
        return os.path.join(self._storage_dir, name)

    def validate_okras_record(self, record: dict[str, Any]) -> None:
        required = [
            "o_id",
            "k_id",
            "O",
            "K",
            "R",
            "A",
            "S",
            "status",
            "session_id",
            "source_mode",
            "created_at",
            "updated_at",
        ]
        for key in required:
            if key not in record:
                raise ValueError(f"missing_field:{key}")
        result = record.get("R")
        if not isinstance(result, dict):
            raise ValueError("invalid_result")
        result_type = result.get("type")
        if result_type not in {"text", "file"}:
            raise ValueError("invalid_result_type")
        if result_type == "file" and not str(result.get("path") or "").strip():
            raise ValueError("missing_result_file_path")
        score = record.get("S")
        if not isinstance(score, dict):
            raise ValueError("invalid_score")
        score_value = score.get("score")
        if not isinstance(score_value, (int, float)):
            raise ValueError("invalid_score_value")
        if score_value < 0 or score_value > 100:
            raise ValueError("score_out_of_range")

    def append_okras_records(self, records: list[dict[str, Any]]) -> str:
        if not records:
            raise ValueError("empty_records")
        for record in records:
            self.validate_okras_record(record)
        self._ensure_dir()
        path = self.resolve_okras_daily_file()
        with self._write_lock:
            with open(path, "a", encoding="utf-8") as f:
                for record in records:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return path

