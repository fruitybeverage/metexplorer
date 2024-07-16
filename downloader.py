import requests
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
import config


class ImageDownloaderThread(QThread):
    """Download images asynchronously."""

    image_ready = Signal(QPixmap, object)
    error_occurred = Signal(object)

    def __init__(self, url, layout, loading_label):
        """Download and return images from URL."""
        super().__init__()
        self.url = url
        self.layout = layout
        self.loading_label = loading_label
        self._is_running = True

    def run(self):
        """Downloads the image from URL.  Emits a signal with the downloaded image or error."""
        if self._is_running:
            try:
                response = requests.get(self.url)
                if response.status_code == 200 and self._is_running:
                    image = QImage()
                    image.loadFromData(response.content)
                    pixmap = QPixmap(image).scaled(
                        config.THUMBNAIL_MAX_WIDTH,
                        config.THUMBNAIL_MAX_HEIGHT,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                    self.image_ready.emit(pixmap, self.layout)
                else:
                    self.error_occurred.emit(self.layout)
            except Exception as e:
                self.error_occurred.emit(self.layout)

    def stop(self):
        """Terminates download thread."""
        self._is_running = False
