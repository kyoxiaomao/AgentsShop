import re


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _split_key_results(text: str) -> list[str]:
    parts = re.split(r"(?:。|；|;|\n|，并|, and )", text)
    results: list[str] = []
    seen: set[str] = set()
    for part in parts:
        item = _normalize_text(part)
        if len(item) < 2:
            continue
        if item in seen:
            continue
        seen.add(item)
        results.append(item)
    if not results:
        return ["完成任务执行并输出可复用结果"]
    return results[:5]


def decompose_task_text(user_content: str) -> dict:
    cleaned = _normalize_text(user_content)
    objective = cleaned
    if not objective:
        objective = "完成用户任务并给出可验证结果"
    elif not objective.startswith("完成"):
        objective = f"完成任务：{objective[:120]}"
    key_results = _split_key_results(cleaned)
    return {"objective": objective, "key_results": key_results}

