# Python-UnoLevelTracker

A simple python app to track the players scores while playing the card game Uno.
Uses pygame for everything GUI related.

This app is designed to be used on a ~16:9 touchscreen device, but can also be controlled via mouse and keyboard and supports any screen resolution.

## Features

* Track players drawn cards and wins
* Create, save and load games using the GUI
* Saved games are stored under `%APPDATA%\Uno` (Win), `~/.uno` (Linux) and `~/Library/Application Support/Uno` (Mac OS)
* Statistics
* Undo button
* Track play time
* Automatic pause after 5 min

## How to use

The GUI launches on the screen, the mouse cursor is currently on.

After launching, start a new game and supply the players names. Confirm each name by pressing the return key.

To confirm the player selection, press enter a second time.

Use <kbd>Q</kbd> or the `Back`-Button to quit the game. The game is automatically saved after every action.

## How to use the code

* Clone or download this repository

* Install pygame using  
`pip install pygame`  
or  
`pip install -r requirements.txt`

* Execute `run.pyw` or start a run script suitable for your operating system or just run the uno folder as python module.

## Screenshots

Coming soon

## How to build

For bundeling the scripts as exe, the python library `pyinstaller` is required, which can be installed using the following command:

`pip install pyinstaller`

Run `pyinstaller run.spec` to build a single exe file inside a subdirectory called `dist`

## Todos

* Some polishing, cleanup
* Fix undo button

## License

This app is distributed under GNU GPL version 3.0, which can be found in the file `LICENSE`.
