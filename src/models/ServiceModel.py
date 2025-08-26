from dataclasses import dataclass
from os.path import join
from typing import Optional

from src.utils.media import get_icon_path, get_service_icon_folder_path


@dataclass
class ServiceModel:
    name: Optional[str] = None
    href: Optional[str] = None
    description: Optional[str] = None
    group_name: Optional[str] = None
    icon: Optional[str] = None

    def get_icon_path(self):
        if self.icon:
            return f"{join(get_service_icon_folder_path(), self.icon)}.png"

        return get_icon_path()

    def get_full_description(self):
        return f"{self.group_name}: {self.description}"
