import os
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
from src.utils.utils import get_homepage_url, is_valid_homepage_url, plural_text


class SyncEnterEventListener(EventListener):

    def on_event(self, event, extension):
        data = event.get_data()

        if data and data.get("action") == "sync":
            self.fetch_data(extension)

    def clean_icon_name(self, icon_filename: str) -> str:
        """Get the name of the icon without the extension."""
        return os.path.splitext(icon_filename)[0]

    def download_icon(self, icon_name: str) -> str:
        """Downloads an icon and returns the path if successful, otherwise an empty string."""
        filename = f"{icon_name}.png"
        url = f"https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/{filename}"
        makedirs(get_service_icon_folder_path(), exist_ok=True)
        file_path = join(get_service_icon_folder_path(), filename)

        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()  # Raise an exception for bad status codes
            with open(file_path, "wb") as f:
                f.write(r.content)

            logger.debug(f"Successfully downloaded icon to {file_path}")
            return str(file_path)
        except requests.RequestException as e:
            logger.error(f"Failed to download icon '{icon_name}': {e}")
            return ""

    def _save_db(self, items: List[ServiceModel]):
        run_migrations()
        save_service(items, True)

    def fetch_data(self, extension):
        notification = Notification()

        if not is_valid_homepage_url(extension):
            notification.show(
                title="Error: Homepage url",
                body="Please enter the homepage URL in the extension configuration",
            )
            return

        notification.show(title="Syncing services", body="Please wait...")

        try:
            items = self._get_services(extension)
            self._save_db(items)
            self._show_sync_result(notification, items)
        except (requests.RequestException, ValueError) as e:
            logger.error(f"Error fetching data: {e}")
            notification.show(
                title="Error",
                body="An unexpected error occurred, please try again",
            )

    def _get_services(self, extension) -> List[ServiceModel]:
        url = get_homepage_url(extension)
        response = requests.get(f"{url}/api/services", timeout=30)
        response.raise_for_status()
        data = response.json()

        items: List[ServiceModel] = []
        for group in data:
            group_name = group.get("name")
            services = group.get("services") or []
            for service in filter(lambda s: s.get("name") and s.get("href"), services):
                icon_name = None
                raw_icon = service.get("icon")
                if raw_icon:
                    cleaned_icon_name = self.clean_icon_name(raw_icon)
                    if self.download_icon(cleaned_icon_name):
                        icon_name = cleaned_icon_name

                items.append(
                    ServiceModel(
                        icon=icon_name,
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
