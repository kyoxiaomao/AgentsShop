import datetime
import json
import logging
import os
import re
from typing import Dict, List

from .models import AgentProfile, AgentStatus


logger = logging.getLogger("datacenter")

BASE_DIR = os.path.dirname(__file__)
REGISTRY_FILE = os.path.join(BASE_DIR, "registry.json")
STATUS_FILE = os.path.join(BASE_DIR, "status.json")
SNAPSHOT_FILE = os.path.join(BASE_DIR, "ui_snapshot.json")
AGENTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "agents")


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


def _discover_agents_from_files() -> List[AgentProfile]:
    if not os.path.isdir(AGENTS_DIR):
        return []
    result: List[AgentProfile] = []
    name_pattern = re.compile(r"name\s*:\s*str\s*=\s*[\"']([^\"']+)[\"']")
    fallback_name_pattern = re.compile(r"name\s*=\s*[\"']([^\"']+)[\"']")
    cn_pattern = re.compile(r"cn_name\s*=\s*[\"']([^\"']+)[\"']")
    seen: set[str] = set()
    for root, _dirs, files in os.walk(AGENTS_DIR):
        for filename in files:
            if not filename.endswith(".py") or filename.startswith("__"):
                continue
            path = os.path.join(root, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                logger.error("read agent file failed %s %s", path, e)
                continue
            if "BaseAgent" not in content:
                continue
            name_match = name_pattern.search(content) or fallback_name_pattern.search(content)
            if not name_match:
                continue
            agent_id = name_match.group(1)
            if agent_id in seen:
                continue
            cn_match = cn_pattern.search(content)
            cn_name = cn_match.group(1) if cn_match else agent_id
            result.append(AgentProfile(id=agent_id, name=agent_id, cn_name=cn_name, enabled=True))
            seen.add(agent_id)
    return result


def _read_registry_agents() -> List[AgentProfile]:
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


def get_agents() -> List[AgentProfile]:
    agents = _discover_agents_from_files()
    if agents:
        return agents
    return _read_registry_agents()


def get_status_map() -> Dict[str, AgentStatus]:
    data = _read_json(STATUS_FILE, {})
    result: Dict[str, AgentStatus] = {}
    now = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
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
