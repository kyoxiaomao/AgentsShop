import json
import os

from datacenter.service import build_ui_snapshot, snapshot_path


def main() -> None:
    out = build_ui_snapshot()
    assert os.path.exists(out)
    with open(out, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "agents" in data
    assert isinstance(data["agents"], list)
    assert any(a.get("id") == "seraAgent" for a in data["agents"])
    assert "status" in data
    assert "seraAgent" in data["status"]
    print(out)


if __name__ == "__main__":
    main()
