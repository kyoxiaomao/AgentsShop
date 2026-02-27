import datetime
import json
import logging
import os
from typing import Dict, List

from .models import AgentProfile, AgentStatus


logger = logging.getLogger("datacenter")

BASE_DIR = os.path.dirname(__file__)
REGISTRY_FILE = os.path.join(BASE_DIR, "registry.json")
STATUS_FILE = os.path.join(BASE_DIR, "status.json")
SNAPSHOT_FILE = os.path.join(BASE_DIR, "ui_snapshot.json")


def _read_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("missing file %s", path)
        return default
    except Exception as e:
        logger.error("read json failed %s %s", path, e)
        return default


def _write_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_agents() -> List[AgentProfile]:
    data = _read_json(REGISTRY_FILE, {"agents": []})
    result: List[AgentProfile] = []
    for item in data.get("agents", []):
        try:
            result.append(
                AgentProfile(
                    id=item["id"],
                    name=item.get("name", item["id"]),
                    cn_name=item.get("cn_name", item["id"]),
                    enabled=bool(item.get("enabled", True)),
                )
            )
        except Exception as e:
            logger.error("invalid agent item %s %s", item, e)
    return result


def get_status_map() -> Dict[str, AgentStatus]:
    data = _read_json(STATUS_FILE, {})
    result: Dict[str, AgentStatus] = {}
    now = datetime.datetime.utcnow().isoformat() + "Z"
    for aid in data.keys():
        v = data[aid]
        status = v.get("status", "offline")
        updated = v.get("updated_at", now)
        result[aid] = AgentStatus(id=aid, status=status, updated_at=updated)
    return result


def build_ui_snapshot() -> str:
    agents = get_agents()
    status_map = get_status_map()
    out = {
        "version": 1,
        "agents": [{"id": a.id, "name": a.name, "cn_name": a.cn_name, "enabled": a.enabled} for a in agents],
        "status": {k: {"status": v.status, "updated_at": v.updated_at} for k, v in status_map.items()},
    }
    _write_json(SNAPSHOT_FILE, out)
    return SNAPSHOT_FILE


def snapshot_path() -> str:
    return SNAPSHOT_FILE
