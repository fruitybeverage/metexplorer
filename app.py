import requests
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap, QAction, QImage
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QPushButton,
    QScrollArea,
    QMenu,
)

import config
import utils
from downloader import ImageDownloaderThread
from fetch import FetchDataThread
from viewer import FullImageViewer


class App(QWidget):
    """An application for criteria based browsing of the MET Collection."""

    def __init__(self):
        """
        The metexplorer application main UI.
        User enters search requirements.
        metexplorer returns thumbnails and information of the work."""

        super().__init__()
        self.results = None  # Search results
        self.has_images = None  # Filter for result with images
        self.query = None  # Search term field
        self.order = None  # Sort order value
        self.classification = None  # Artwork classification value
        self.results_layout = None  # Search results layout
        self.scroll_area = None  # Scroll area for results
        self.loading_label = None  # Placeholder label for image downloading
        self.full_image_viewer = None  # Full sized image viewer

        self.setWindowTitle("MET Collection Explorer")
        self.resize(config.APPLICATION_DEFAULT_WIDTH, config.APPLICATION_DEFAULT_HEIGHT)
        self.init_ui()

        self.fetch_threads = []  # Threaded queries
        self.image_threads = []  # Threaded image search

    def init_ui(self):
        """Sets up the user interface with the layouts."""
        layout = QVBoxLayout()
        layout.addLayout(self.create_form_layout())
        self.create_scroll_area(layout)
        self.create_loading_label(layout)
        self.setLayout(layout)

    def create_form_layout(self):
        """Creates the layout for user search input including search field,
         classification dropdown, image requirement and date sorting option."""
        form_layout = QHBoxLayout()

        # Search field
        form_layout.addWidget(QLabel("Search:"))
        self.query = QLineEdit()
        self.query.setMinimumWidth(100)
        form_layout.addWidget(self.query)

        # Modifiable Classification dropdown.  Displays top 50 classifications.
        form_layout.addWidget(QLabel("Classification:"))
        self.classification = QComboBox()
        self.classification.setMinimumWidth(265)
        self.classification.setEditable(True)
        self.classification.addItems(config.CLASSIFICATION_OPTIONS)
        form_layout.addWidget(self.classification)

        # Filter for entries which have images.
        self.has_images = QCheckBox("Has Images")
        self.has_images.setChecked(True)
        form_layout.addWidget(self.has_images)

        # Sort by ascending or descending work date.
        form_layout.addWidget(QLabel("Order By Date:"))
        self.order = QComboBox()
        self.order.addItems([config.ORDER_ASCENDING, config.ORDER_DESCENDING])
        self.order.currentIndexChanged.connect(self.sort_results)
        form_layout.addWidget(self.order)

        # Launch search.
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        form_layout.addWidget(search_button)
        return form_layout

    def create_scroll_area(self, layout):
        """Creates the scroll area to display search results."""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_layout = QVBoxLayout()
        results_widget = QWidget()
        results_widget.setLayout(self.results_layout)
        self.scroll_area.setWidget(results_widget)
        layout.addWidget(self.scroll_area)

    def create_loading_label(self, layout):
        """Displays a "Loading..." label in the image area while data fetching."""
        self.loading_label = QLabel("Loading...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.loading_label)
        self.loading_label.hide()

    def search(self):
        """Performs the search operation by clearing the existing results, and starting a new fetch."""
        utils.clear_layout(self.results_layout)
        self.loading_label.show()
        self.terminate_threads()
        fetch_thread = FetchDataThread(
            self.query.text(),
            self.has_images.isChecked(),
            self.classification.currentText(),
        )
        fetch_thread.result_ready.connect(self.add_results)
        fetch_thread.no_results.connect(self.show_no_results)
        fetch_thread.finished.connect(lambda: self.loading_label.hide())
        self.fetch_threads.append(fetch_thread)
        fetch_thread.start()

    def terminate_threads(self):
        """Terminates all fetch and image download threads."""
        for thread in self.fetch_threads + self.image_threads:
            thread.stop()
            thread.quit()
            thread.wait()
        self.fetch_threads.clear()
        self.image_threads.clear()

    @Slot(list)
    def add_results(self, results):
        """Add a new frame for each search result."""
        self.results = results
        self.sort_results()

    def sort_results(self):
        """Sort search results by work end date then filter results if user requires an image."""
        if hasattr(self, "results"):
            sorted_results = sorted(
                self.results,
                key=lambda x: x.get("objectEndDate", 0),
                reverse=self.order.currentText() == config.ORDER_DESCENDING,
            )
            utils.clear_layout(self.results_layout)
            filtered_results = []

            # Display entries which contain an image if "Has Images" is checked.
            # Otherwise, display all results.
            for data in sorted_results:
                has_primary_image_sm = bool(data.get("primaryImageSmall"))

                if self.has_images.isChecked() and has_primary_image_sm:
                    filtered_results.append(data)
                elif not self.has_images.isChecked():
                    filtered_results.append(data)
            if not filtered_results:
                self.show_no_results()
            else:
                for data in filtered_results:
                    self.add_result(data)

    @Slot()
    def show_no_results(self):
        """Display a message if no results found."""
        self.loading_label.hide()
        no_results_label = QLabel("No results found.")
        no_results_label.setAlignment(Qt.AlignCenter)
        self.results_layout.addWidget(no_results_label)

    def add_result(self, data):
        """Add a frame for every result entry."""
        frame = utils.create_result_frame(data, self)
        self.results_layout.addWidget(frame)
        self.add_context_menu(frame, data)

    def download_large_image(self, image_url):
        """Fetch image for local download."""
        response = requests.get(image_url)
        if response.status_code == 200:
            image = QImage()
            image.loadFromData(response.content)
            pixmap = QPixmap(image)
            utils.download_image_to_local(pixmap, image_url)

    def add_context_menu(self, frame, data):
        """Create a right click menu to search results."""
        menu = QMenu()

        # Learn More option to launch MET information link on work
        learn_more_action = QAction("Learn More", self)
        learn_more_action.triggered.connect(
            lambda: utils.open_object_url(data.get("objectURL"))
        )
        menu.addAction(learn_more_action)

        # Download Image option
        if "primaryImage" in data and data["primaryImage"]:
            download_image_action = QAction("Download Image", self)
            download_image_action.triggered.connect(
                lambda: self.download_large_image(data["primaryImage"])
            )
            menu.addAction(download_image_action)

        frame.setContextMenuPolicy(Qt.CustomContextMenu)
        frame.customContextMenuRequested.connect(
            lambda pos: menu.exec_(frame.mapToGlobal(pos))
        )

    def download_image(
        self, url, layout, loading_label, full_image_url, object_url=None
    ):
        """Starts a image download thread for every result entry."""
        image_thread = ImageDownloaderThread(url, layout, loading_label)
        image_thread.image_ready.connect(
            lambda pixmap, l=layout: self.add_image(
                pixmap, l, loading_label, full_image_url, object_url
            )
        )
        image_thread.error_occurred.connect(
            lambda l=layout: self.show_error(l, loading_label)
        )
        self.image_threads.append(image_thread)
        image_thread.start()

    @Slot(QPixmap, QHBoxLayout)
    def add_image(self, pixmap, layout, loading_label, full_image_url, object_url=None):
        """Add image to search results layout."""
        layout.removeWidget(loading_label)
        loading_label.deleteLater()
        label = QLabel()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.mousePressEvent = (
            lambda event, url=full_image_url, obj_url=object_url: self.show_full_image(
                url, obj_url
            )
        )
        layout.addWidget(label, alignment=Qt.AlignRight)

    @Slot(QHBoxLayout)
    def show_error(self, layout, loading_label):
        """Display error if image fails to load."""
        layout.removeWidget(loading_label)
        loading_label.deleteLater()
        error_label = QLabel("Image failed to load")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setFixedSize(
            config.THUMBNAIL_MAX_WIDTH, config.THUMBNAIL_MAX_HEIGHT
        )
        layout.addWidget(error_label, alignment=Qt.AlignRight)

    def closeEvent(self, event):
        """Close application and terminates all threads."""
        self.terminate_threads()
        super().closeEvent(event)

    def show_full_image(self, image_url, object_url=None):
        """Opens a new window to display the full sized image"""
        # Opens a new image viewer with full size image.
        if not self.full_image_viewer:
            self.full_image_viewer = FullImageViewer(image_url, object_url)
            self.full_image_viewer.closed.connect(self.full_image_viewer_closed)
            self.full_image_viewer.show()

        # Refresh existing image viewer with new full size image if there is one existing
        else:
            if not self.full_image_viewer.isVisible():
                self.full_image_viewer = FullImageViewer(image_url, object_url)
                self.full_image_viewer.closed.connect(self.full_image_viewer_closed)
                self.full_image_viewer.show()
            else:
                self.full_image_viewer.update_image(image_url, object_url)

    @Slot()
    def full_image_viewer_closed(self):
        """Sets full image viewer checker to None."""
        self.full_image_viewer = None
