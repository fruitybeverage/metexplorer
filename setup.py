from setuptools import setup

# PURPOSE: Sets up application bundle with py2app.

# Main application file
APP = ["main.py"]

# Additional files required by MET Explorer
DATA_FILES = []

# Configuration options for the application bundle including packages, excluded modules and icons.
OPTIONS = {
    "includes": [
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtCore",
        "requests",
    ],
    "packages": [
        "PySide6",
    ],
    "excludes": [
        "Carbon",
        "PyQt5",
        "tkinter",
    ],
    "optimize": 2,
    "compressed": True,
    "iconfile": "resources/ApplicationIcon.icns",
    "plist": {
        "CFBundleName": "MET Collection Explorer",
        "CFBundleDisplayName": "MET Collection Explorer",
        "CFBundleIdentifier": "com.lydialam.metcollectionexplorer",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
