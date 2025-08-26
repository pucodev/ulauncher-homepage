from os import makedirs
from os.path import join
from typing import List

import requests
from ulauncher.api.client.EventListener import EventListener

from src.db.db import run_migrations, save_service
from src.models.ServiceModel import ServiceModel
from src.utils.logger import logger
from src.utils.media import get_service_icon_folder_path
from src.utils.notification import Notification
from src.utils.utils import plural_text


class SyncEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()

        if data and data.get("action") == "sync":
            self.fetch_data(extension)

    def clean_icon_name(self, icon):
        return icon.replace(".png", "").replace(".svg", "")

    def download_icon(self, icon_name) -> str:
        filename = f"{self.clean_icon_name(icon_name)}.png"
        url = f"https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/{filename}"
        makedirs(get_service_icon_folder_path(), exist_ok=True)
        file_path = join(get_service_icon_folder_path(), filename)
        logger.debug("---------- DOWNLOAD ICON ----------")
        logger.debug(f"Download icon: {url}")
        logger.debug(f"Save icon to: {file_path}")
        logger.debug("-----------------------------------")

        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(r.content)

        return str(file_path)

    def _save_db(self, items: List[ServiceModel]):
        run_migrations()
        save_service(items, True)

    def fetch_data(self, extension):
        notification = Notification()
        notification.show(title="Syncing services", body="Please wait")

        try:
            items = self._get_services(extension)

            self._save_db(items)

            self._show_sync_result(notification, items)
        except (requests.RequestException, ValueError) as e:
            logger.error(f"Error: {e}")
            notification.show(
                title="Error",
                body="There was an unexpected error, please try again",
            )

    def _get_services(self, extension) -> List[ServiceModel]:
        url = extension.preferences.get("api_url")
        response = requests.get(f"{url}/api/services", timeout=30)
        response.raise_for_status()
        data = response.json()

        items: List[ServiceModel] = []
        for group in data:
            group_name = group.get("name")
            services = group.get("services") or []
            for service in filter(lambda s: s.get("name") and s.get("href"), services):
                icon = service.get("icon")
                if icon:
                    icon = self.clean_icon_name(icon)
                    self.download_icon(icon)

                items.append(
                    ServiceModel(
                        icon=icon,
                        name=service["name"],
                        description=service.get("description"),
                        href=service["href"],
                        group_name=group_name,
                    )
                )
        return items

    def _show_sync_result(self, notification, items):
        count = len(items)
        notification.show(
            title="Services synchronized",
            body=plural_text(
                "No services synchronized",
                "1 service synchronized",
                f"{count} services synchronized",
                count,
            ),
        )
