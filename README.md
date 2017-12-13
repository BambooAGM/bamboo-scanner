## Requirements
* Python 3.6
* Pycharm
* virtualenv (recommended)

## How to get it running
1. Clone this repository to your machine.
2. Create a virtualenv and activate it.
3. With the virtualenv active, run `pip install -r requirements.txt`
4. Open project in Pycharm.
5. Run main.py

## Project structure

* assets/ - Image files, and such resources.
* backend/ - Controller modules for BPC, BSC, and Arduino.
* gui/ - Tkinter classes that make up the GUI.
    * bpc/ - The pages of the BPC tool.
    * bsc/ - The pages of the BSC tool.
    * widgets/ - Custom widgets and helper functions for the GUI.
* main.py - Main script / Root Tk widget. Initializes GUI and provides global functions.
* requirements.txt - pip dependencies