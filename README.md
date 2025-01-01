# connectx
Connect X (Enhanced)
A Connect X game built in Python using Tkinter. Features include:

Adjustable Board Size (rows/columns) and Connect Target (4 by default).
Single Player (with AI) or Two Players.
AI Difficulty Levels: Easy (random), Medium (minimax depth=2), Hard (minimax depth=4).
Color Themes for the interface.
Timers: Each player starts with 10 minutes; each move adds 15 seconds.
If a player’s time runs out, they lose.
Animated Piece Drop and Blinking Win Highlight.
Undo functionality:
Two-player: undo the last move.
Single-player: undo both the AI’s and the human’s last move.
Table of Contents
Installation
Usage
Features
How It Works
Contributing
License
Installation
Clone this repository or download the ZIP and extract it.
Ensure you have Python 3.7+ installed on your system.
(Optional) Create and activate a virtual environment:
bash
Copy code
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
Install any required packages (typically just tkinter, which is usually included by default with Python on most systems).
Usage
Open a terminal (or command prompt) in the project directory.

Run the main file:

bash
Copy code
python conn.py
(Replace conn.py with the name of your main file, if different.)

A Main Menu appears, offering:

Start Game: Launches the Connect X game.
Options: Configure rows, columns, connect target, color theme, difficulty, and timer.
Exit: Closes the application.
Once you start the game:

If you chose Single Player, the AI will move after you place a piece.
If Two Players, each click places a piece for the current player, then switches turns.
Undo:
In Two Players, undo the last move.
In Single Player, undo the last two moves (AI + human).
Timers count down for the current player; each move adds a 15-second increment.
Features
Board Customization
Set any board size (minimum 4×4) and choose your “connect” goal (3+).

Two Game Modes

Single Player with AI
3 difficulty levels (Easy, Medium, Hard).
Two Players (local play).
Color Themes
Select from various background colors (blue, green, gray, black, white).

Time Control

Both players start with 10 minutes (by default).
Each move adds 15 seconds.
If a player’s timer hits 0, they lose on time.
Animated Drops
Pieces “fall” smoothly into place rather than appearing instantly.

Blinking Win Highlight
When a player connects the required number in a row, those winning pieces flash green, then the game announces the winner.

Undo Moves

For Two Players: Undo the last move.
For Single Player: Undo both your and the AI’s last move (restoring the turn to you).
How It Works
Tkinter UI
The game uses a single window with two main screens:

Main Menu (Start, Options, Exit)
Game Window (canvas for the board, timers, and control buttons).
Minimax AI

Easy: Random valid column.
Medium: Minimax with depth=2.
Hard: Minimax with depth=4 (alpha-beta pruning).
Timers

Using time.time() to track elapsed seconds for the current player.
A small loop (self.master.after(...)) updates the displayed times every 200 ms.
Each move triggers an increment of 15 seconds for the current player’s clock.
Undo Stack

Each move is pushed onto a move_stack as (row, col, piece).
Pressing Undo pops the moves off the stack and clears them from the board.
Contributing
Fork this repository.
Create a new branch for your feature or bug fix.
Commit your changes, push your branch, and open a pull request describing what you changed and why.
