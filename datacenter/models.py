from dataclasses import dataclass
from typing import Literal


StatusLiteral = Literal["offline", "idle", "busy"]


@dataclass
class AgentProfile:
    id: str
    name: str
    cn_name: str
    enabled: bool = True


@dataclass
class AgentStatus:
    id: str
    status: StatusLiteral
    updated_at: str
