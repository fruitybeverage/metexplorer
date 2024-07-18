import os
import webbrowser
from urllib.parse import urlparse

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QFrame, QHBoxLayout, QSizePolicy, QFileDialog

import config


def clear_layout(layout):
    """Clears layout when a new search is performed."""
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

def get_art_info(data, field, default="Unknown"):
    """Retrieve artwork information."""
    return data.get(field, default) or default

def create_result_frame(data, parent):
    """Creates a layout for search results."""
    frame = QFrame()
    frame.setFrameShape(QFrame.StyledPanel)
    frame_layout = QHBoxLayout()

    # Work description
    text = (
        f"Title: {get_art_info(data, 'title')}\n"
        f"Artist: {get_art_info(data, 'artistDisplayName')}\n"
        f"Date: {get_art_info(data, 'objectDate')}\n"
        f"Medium: {get_art_info(data, 'medium')}\n"
        f"Classification: {get_art_info(data, 'classification')}\n"
    )
    label = QLabel(text)
    label.setWordWrap(True)
    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    label.setMaximumWidth(800)

    # Create layout for image or placeholder "Loading..."
    frame_layout.addWidget(label)
    image_label = QLabel()
    image_label.setAlignment(Qt.AlignCenter)
    image_label.setFixedSize(config.THUMBNAIL_MAX_WIDTH, config.THUMBNAIL_MAX_HEIGHT)
    loading_label = QLabel("Loading...")
    loading_label.setAlignment(Qt.AlignCenter)
    loading_label.setFixedSize(config.THUMBNAIL_MAX_WIDTH, config.THUMBNAIL_MAX_HEIGHT)

    # Add Loading or No Image Found label while downloading the image (if there is one).
    if "primaryImage" in data and data["primaryImage"]:
        frame_layout.addWidget(loading_label, alignment=Qt.AlignRight)
        parent.download_image(
            data["primaryImage"],
            frame_layout,
            loading_label,
            data["primaryImage"],
            data.get("objectURL"),
        )
    else:
        image_label.setText("No Image Found")
        frame_layout.addWidget(image_label, alignment=Qt.AlignRight)

    frame.setLayout(frame_layout)

    return frame


def open_object_url(object_url):
    """Open object URL (MET's URL for the work) in the default web browser."""
    webbrowser.open(object_url)


def download_image_to_local(pixmap, image_url):
    """Save image locally."""
    default_download_path = os.path.join(os.path.expanduser("~"), "Downloads")
    image_name = os.path.basename(urlparse(image_url).path)
    default_filename = os.path.join(default_download_path, image_name)
    file_path, _ = QFileDialog.getSaveFileName(
        None,
        "Save Image",
        default_filename,
        "Images (*.png *.xpm *.jpg *.jpeg *.bmp)",
    )
    if file_path:
        pixmap.save(file_path)
