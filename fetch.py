import requests
from PySide6.QtCore import QThread, Signal
from concurrent.futures import as_completed, ThreadPoolExecutor

import config


class FetchDataThread(QThread):
    """Fetching search results from MET API thread."""

    result_ready = Signal(list)
    no_results = Signal()

    def __init__(self, query, has_images, classification):
        """Queries the MET API for artworks based in user input."""

        super().__init__()
        self.query = query
        self.has_images = has_images
        self.classification = classification
        self._is_running = True

    def run(self):
        """Query and fetch object data from MET API."""
        # ISSUES:
        # 1) has_images does not return the correct results:
        #       https://github.com/metmuseum/openaccess/issues/52
        # 2) Different results given diff query order
        #       https://github.com/metmuseum/openaccess/issues/51

        if self.has_images:
            params = {
                "hasImages": str(self.has_images).lower(),
            }
        else:
            params = {}

        if self.query:
            params["q"] = self.query
        else:
            params["q"] = self.classification

        response = requests.get(f"{config.API_URL}/search", params=params)
        if response.status_code == 200 and self._is_running:
            object_ids = response.json().get("objectIDs")
            if object_ids:
                object_ids = object_ids[: config.MAX_RESULTS]
                objects_data = self.fetch_objects_data(object_ids)
                if self._is_running:
                    # Filter results by classification if provided
                    if self.classification:
                        objects_data = [
                            obj
                            for obj in objects_data
                            if obj.get("classification").lower()
                            == self.classification.lower()
                        ]
                    if objects_data:
                        self.result_ready.emit(objects_data)
                    else:
                        self.no_results.emit()
            else:
                self.no_results.emit()

    def fetch_objects_data(self, object_ids):
        """Fetch object details concurrently."""
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.fetch_object_data, object_id)
                for object_id in object_ids
            ]
            return [
                result
                for future in as_completed(futures)
                if self._is_running and (result := future.result())
            ]

    @staticmethod
    def fetch_object_data(object_id):
        """Fetch data for a single object."""
        try:
            url = f"{config.API_URL}/objects/{object_id}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                data["url"] = url
                return data
        except Exception as e:
            print(f"Error fetching object data: {e}")
        return None

    def stop(self):
        """Terminate a thread."""
        self._is_running = False
