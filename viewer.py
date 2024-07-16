import requests
from urllib.parse import urlparse
from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QSizePolicy,
    QPushButton,
    QFileDialog,
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, Signal
import config
import utils


class FullImageViewer(QMainWindow):
    """A viewer to display full sized image and option to download it."""

    closed = Signal()

    def __init__(self, image_url, object_url=None):
        """Initialize the viewer with full size image and sets up the UI."""
        super().__init__()
        self.setWindowTitle("Full Image Viewer")
        self.resize(config.VIEWER_DEFAULT_WIDTH, config.VIEWER_DEFAULT_HEIGHT)
        self.setMinimumSize(config.VIEWER_MIN_WIDTH, config.VIEWER_MIN_HEIGHT)
        self.image_url = image_url
        self.object_url = object_url
        self.original_pixmap = None
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add Learn More button
        self.learn_more_button = QPushButton("Learn More")
        if self.object_url:
            self.learn_more_button.clicked.connect(
                lambda: utils.open_object_url(self.object_url)
            )
        else:
            self.learn_more_button.setDisabled(True)

        # Add Download Image button
        self.download_button = QPushButton("Download Image")
        self.download_button.clicked.connect(
            lambda: utils.download_image_to_local(self.original_pixmap, self.image_url)
        )

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.learn_more_button)
        buttons_layout.addWidget(self.download_button)
        layout.addLayout(buttons_layout)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.download_viewer_image(self.image_url)

    def download_viewer_image(self, image_url):
        """Downloads the image and refreshes the viewer."""
        response = requests.get(image_url)
        if response.status_code == 200:
            image = QImage()
            image.loadFromData(response.content)
            self.original_pixmap = QPixmap(image)
            self.update_pixmap()
        else:
            self.image_label.setText("Failed to load image")

    def update_pixmap(self):
        """Refreshes the displayed image based on window size update."""
        if self.original_pixmap:
            available_size = self.centralWidget().size()
            scaled_pixmap = self.original_pixmap.scaled(
                available_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        self.update_pixmap()
        super().resizeEvent(event)

    def update_image(self, image_url, object_url=None):
        """Updates the image in viewer with new URL."""
        self.image_url = image_url
        self.download_viewer_image(self.image_url)
        self.object_url = object_url

        # Enable Learn More button if there is a URL
        if self.object_url:
            self.learn_more_button.setDisabled(False)
            self.learn_more_button.clicked.connect(
                lambda: utils.open_object_url(self.object_url)
            )
        else:
            self.learn_more_button.setDisabled(True)

    def closeEvent(self, event):
        """Send a signal when viewer is closed."""
        self.closed.emit()
        super().closeEvent(event)
