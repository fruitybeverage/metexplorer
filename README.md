# MET Collection Explorer

MET Collection Explorer is a PySide6-based application that allows users to explore the MET (Metropolitan Museum of Art) collection. Users can search for artworks, filter results, and view images in full size.

## Features

- Search for artworks from the MET collection
- Filter results by classification and availability of images
- Sort results by date
- View thumbnails and full-size images
- Download full-size images
- Learn more about the artwork

## Requirements

- Python 3.7+
- PySide6
- Requests

## Note
**This Application has only been tested on macOS Sonoma**

### Create a virtual environment

1. **Clone the repository:**

   ```sh
   git clone https://github.com/fruitybeverage/metexplorer.git
   cd metexplorer
   ```
2. **Create a virtual environment:**
   ```sh
   python -m venv .venv
   ```
### Activate the virtual environment and install requirements

1. **Activate the virtual environment:**
   - On Windows
       ```sh
       .venv\Scripts\activate
       ```
   - On macOS and Linux
       ```sh
       source .venv/bin/activate
       ```
2. **Install the requirements:**
    ```sh
    pip install -r requirements.txt
    ```
   
### Running the Application
1. **Activate the virtual environment (if not already activated):**
   - On Windows
       ```sh
       .venv\Scripts\activate
       ```
   - On macOS and Linux
       ```sh
       source .venv/bin/activate
       ```
2. **Run the application:**
    ```sh
    python main.py
    ```
### Building the Application (macOS)
To build the application on macOS using py2app, follow these steps:
1. **pip install py2app**
    ```sh
    pip install py2app
    ```
2. **Run the setup script to build the application:**
    ```sh
   python setup.py py2app
   ```
3. **The built application will be in the `dist` directory.**



## Project Structure
- app.py: Main application logic and UI.
- config.py: Configuration settings for the application.
- downloader.py: Image downloader thread implementation.
- fetch.py: Data fetcher thread implementation.
- main.py: Entry point for the application.
- utils.py: Utility functions.
- viewer.py: Full image viewer window.
- requirements.txt: List of required Python packages.

## Application Bundle Location
A zipped version of the application exists here:
    
https://drive.google.com/drive/folders/1PM3F9SExKv8ai-MZY9o1z0s27UCYLxdt?usp=sharing
