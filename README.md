# Python-UnoLevelTracker

A simple python app to track the players scores while playing the card game Uno.
Uses pygame for everything GUI related.

This app is designed to be used on a ~16:9 touchscreen device, but can also be controlled via mouse and keyboard and supports any screen resolution.

## Features

* Track players score
* Highlights highest and lowest players
* Create, save and load games using the GUI
* Saved games are stored under `%APPDATA%\Uno` (Win), `~/.uno` (Linux) and `~/Library/Application Support/Uno` (Mac OS)

## How to use

The GUI launches on the screen, the mouse cursor is currently on.

After launching, start a new game and supply the players names. Confirm each name by pressing the return key.

To confirm the player selection, press enter a second time.

Use the keys <kbd>1</kbd> - <kbd>9</kbd> or tap the upper half of the screen to increase a players score.

To decrease it, tap the lower half or use <kbd>Shift</kbd>+<kbd>Number-Key</kbd>.

Use <kbd>Q</kbd> or the `Back`-Button to quit the game. The game is automatically saved after every action.

## How to use the code

* Clone or download this repository

* Install pygame using  
`pip install pygame`  
or  
`pip install -r requirements.txt`

* Execute `run.pyw` or start a run script suitable for your operating system or just run the uno folder as python module.

## Screenshots

### Main menu while entering player names

![image](https://user-images.githubusercontent.com/1323131/164507094-0754f855-89b8-4ff3-81b5-af8ec8079367.png)

### Menu for loading previously played games

![image](https://user-images.githubusercontent.com/1323131/164507323-7a4ef7dd-91ab-4181-b3c3-be7db2f27063.png)

### In game screen

![image](https://user-images.githubusercontent.com/1323131/164507552-a2a04d07-9538-4176-9854-4b7605bd2b96.png)

### Statistics screen

![image](https://user-images.githubusercontent.com/1323131/164508457-4d6ba036-e11e-460f-8ead-fb5a93be05b3.png)

The numbers below are in minutes

## How to build

For bundeling the scripts as exe, the python library `pyinstaller` is required, which can be installed using the following command:

`pip install pyinstaller`

Run `pyinstaller run.spec` to build a single exe file inside a subdirectory called `dist`

## Todos

An undo button to prevent oneself from messing up the statistics in the end..

## License

This app is distributed under GNU GPL version 3.0, which can be found in the file `LICENSE`.
