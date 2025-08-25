from dataclasses import dataclass
from typing import Optional


@dataclass
class ServiceModel:
    name: Optional[str] = None
    href: Optional[str] = None
    description: Optional[str] = None
    group_name: Optional[str] = None
    icon: Optional[str] = None
