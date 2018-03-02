## How to run Bamboo Scanner
1. Download the latest version from the [releases section](https://github.com/BambooAGM/bamboo-scanner/releases).
2. Decompress the downloaded file.
3. Run "BambooScanner.exe"

# Developer Installation

## Requirements
* Python 3.6
* Pycharm (recommended)
* virtualenv (recommended)

## Setup project
1. Clone this repository to your machine.
2. Create a virtualenv called "venv" inside the project directory.
3. With the virtualenv active, run `pip install -r requirements.txt`

## Generate distributable package
1. Make sure the project is setup correctly.
2. Install the [Windows 10 SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk) needed for the Universal C Runtime.
3. With the virtualenv active, run `pyinstaller BambooScanner.spec`
4. If successful, package sits inside the "dist" directory.

## Project structure
* assets/ - Image files, and such resources.
* backend/ - Controller modules for BPC, BSC, and Arduino.
* gui/ - Tkinter classes that make up the GUI.
    * bpc/ - The pages of the BPC tool.
    * bsc/ - The pages of the BSC tool.
    * widgets/ - Custom widgets and helper functions for the GUI.
* main.py - Main script / Root Tk widget. Initializes GUI and provides global functions.
* requirements.txt - pip dependencies
* BambooScanner.spec - PyInstaller configuration file to generate distributable package.