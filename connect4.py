import tkinter as tk
from tkinter import simpledialog, messagebox
import random

# Timing parameters (milliseconds)
AI_DELAY_MS = 500
ANIMATION_DELAY_MS = 20

class EnhancedConnectGame:
    def __init__(self, master):
        self.master = master
        master.title("Enhanced Connect Game")

        # Ask user for board configuration
        self.rows = simpledialog.askinteger(
            "Board Rows",
            "Enter number of rows (e.g., 6, 10):",
            parent=master,
            minvalue=4
        )
        if not self.rows:
            self.rows = 6  # default

        self.cols = simpledialog.askinteger(
            "Board Columns",
            "Enter number of columns (e.g., 7, 10):",
            parent=master,
            minvalue=4
        )
        if not self.cols:
            self.cols = 7  # default

        self.connect_target = simpledialog.askinteger(
            "Connect Target",
            "Enter target in-a-row (e.g., 4 or 5):",
            parent=master,
            minvalue=3
        )
        if not self.connect_target:
            self.connect_target = 4  # default

        # Ask for single or two-player mode
        self.game_mode = simpledialog.askstring(
            "Game Mode",
            "Enter '1' for Single Player or '2' for Two Players:",
            parent=master
        )
        if self.game_mode not in ["1", "2"]:
            self.game_mode = "2"

        # If single player, ask for difficulty
        self.difficulty = None
        if self.game_mode == "1":
            self.difficulty = simpledialog.askinteger(
                "Difficulty",
                "Select AI Difficulty Level (1=Easy, 2=Medium, 3=Hard):",
                parent=master,
                minvalue=1, maxvalue=3
            )
            if self.difficulty not in [1, 2, 3]:
                self.difficulty = 1

        # Core game state
        self.board = self.create_board()
        self.current_player = 1  # 1 -> Red, 2 -> Yellow
        self.piece_map = {1: "R", 2: "Y"}
        self.move_stack = []  # stack of (row, col, piece)

        # UI sizing
        self.cell_size = 80
        self.padding = 10

        # Create UI
        self.create_ui()
        self.draw_board()

    # -------------------------------------------------------
    #                   Setup & UI
    # -------------------------------------------------------
    def create_board(self):
        """Creates an empty board."""
        return [["_"] * self.cols for _ in range(self.rows)]

    def create_ui(self):
        """Sets up the Canvas and the Undo button."""
        # Frame for canvas
        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.pack(side=tk.TOP)

        self.canvas_width = self.cols * (self.cell_size + self.padding) + self.padding
        self.canvas_height = self.rows * (self.cell_size + self.padding) + self.padding

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="blue"
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)

        # Frame for buttons
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(side=tk.BOTTOM, pady=10)

        self.undo_button = tk.Button(
            self.button_frame,
            text="Undo",
            command=self.undo_move
        )
        self.undo_button.pack()

    def draw_board(self):
        """Renders the current board state on the canvas."""
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = self.padding + c * (self.cell_size + self.padding)
                y1 = self.padding + r * (self.cell_size + self.padding)
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                cell_val = self.board[r][c]
                if cell_val == "R":
                    color = "red"
                elif cell_val == "Y":
                    color = "black"
                else:
                    color = "white"

                self.canvas.create_oval(
                    x1, y1, x2, y2,
                    fill=color, outline="yellow", width=2
                )

    # -------------------------------------------------------
    #                   Event Handlers
    # -------------------------------------------------------
    def handle_click(self, event):
        """Handles human clicks on the board (player 1 if single-player or whichever player's turn in 2-player)."""
        # If single-player & it's AI's turn, ignore
        if self.game_mode == "1" and self.current_player == 2:
            return

        col = (event.x - self.padding) // (self.cell_size + self.padding)
        if not (0 <= col < self.cols):
            return  # invalid click

        piece = self.piece_map[self.current_player]

        # Attempt to drop
        if not self.drop_piece_animated(col, piece):
            return  # column full

        if self.check_and_handle_win_or_tie(piece):
            return

        # Switch player
        self.current_player = 2 if self.current_player == 1 else 1

        # AI move if single-player
        if self.game_mode == "1" and self.current_player == 2:
            self.master.after(AI_DELAY_MS, self.computer_move)

    def computer_move(self):
        """Executes the AI's turn (if single player)."""
        piece = self.piece_map[2]  # Yellow

        # AI column selection
        if self.difficulty == 1:
            # Easy: random
            valid_cols = [c for c in range(self.cols) if self.board[0][c] == "_"]
            col = random.choice(valid_cols)
        else:
            depth = 2 if self.difficulty == 2 else 4
            col, _ = self.minimax(self.board, depth, True, float("-inf"), float("inf"))

        # Drop piece
        if col is not None:
            self.drop_piece_animated(col, piece)

        if self.check_and_handle_win_or_tie(piece):
            return

        # Switch back to player
        self.current_player = 1

    def undo_move(self):
        """
        Undo the last move(s):
          - Two-player mode: Undo the last single move.
          - Single-player mode: Undo the last two moves (the AI's move & the human's move)
        """
        if self.game_mode == "2":
            # Undo one move
            if not self.move_stack:
                return
            row, col, piece = self.move_stack.pop()
            self.board[row][col] = "_"
            # Set current_player based on undone piece
            self.current_player = 1 if piece == "R" else 2

        else:
            # Single-player => Undo two moves if available
            if len(self.move_stack) < 2:
                return
            # Undo AI move
            row_ai, col_ai, piece_ai = self.move_stack.pop()
            self.board[row_ai][col_ai] = "_"

            # Undo human move
            row_hu, col_hu, piece_hu = self.move_stack.pop()
            self.board[row_hu][col_hu] = "_"

            # After undoing both, it's human's turn
            self.current_player = 1

        self.draw_board()

    # -------------------------------------------------------
    #            Piece Drop & Animation
    # -------------------------------------------------------
    def drop_piece_animated(self, col, piece):
        """Animates a piece dropping in the given column. Returns False if column is full."""
        if self.board[0][col] != "_":
            return False

        # Find target row
        target_row = None
        for r in range(self.rows-1, -1, -1):
            if self.board[r][col] == "_":
                target_row = r
                break

        if target_row is None:
            return False

        # Animate
        start_row = -1
        x1 = self.padding + col * (self.cell_size + self.padding)
        x2 = x1 + self.cell_size
        piece_id = None
        current_row = start_row

        while current_row < target_row:
            if piece_id is not None:
                self.canvas.delete(piece_id)
            current_row += 1

            y1 = self.padding + current_row * (self.cell_size + self.padding)
            y2 = y1 + self.cell_size
            color = "red" if piece == "R" else "black"

            piece_id = self.canvas.create_oval(
                x1, y1, x2, y2,
                fill=color, outline="black", width=2
            )
            self.canvas.update()
            self.master.after(ANIMATION_DELAY_MS)

        if piece_id is not None:
            self.canvas.delete(piece_id)

        # Place on board
        self.board[target_row][col] = piece
        self.move_stack.append((target_row, col, piece))
        self.draw_board()
        return True

    # -------------------------------------------------------
    #               Game End Checks
    # -------------------------------------------------------
    def check_and_handle_win_or_tie(self, piece):
        """Check for win or tie, handle blinking if needed, return True if game ended."""
        win_positions = self.check_win(piece)
        if win_positions:
            self.blink_winning_pieces(win_positions)
            return True

        if self.check_tie():
            messagebox.showinfo("Game Over", "It's a tie!")
            self.reset_game()
            return True

        return False

    def check_win(self, piece):
        """
        Checks if 'piece' has a connect of length 'self.connect_target'.
        Returns list of positions if found, otherwise None.
        """
        return self.check_piece_win(self.board, piece, self.connect_target)

    def check_piece_win(self, board, piece, target):
        """Check if 'piece' has 'target' in a row in 'board'. Return positions or None."""
        # Horizontal
        for r in range(self.rows):
            for c in range(self.cols - (target - 1)):
                if all(board[r][c + k] == piece for k in range(target)):
                    return [(r, c + k) for k in range(target)]
        # Vertical
        for r in range(self.rows - (target - 1)):
            for c in range(self.cols):
                if all(board[r + k][c] == piece for k in range(target)):
                    return [(r + k, c) for k in range(target)]
        # Diagonal (down-right)
        for r in range(self.rows - (target - 1)):
            for c in range(self.cols - (target - 1)):
                if all(board[r + k][c + k] == piece for k in range(target)):
                    return [(r + k, c + k) for k in range(target)]
        # Diagonal (down-left)
        for r in range(self.rows - (target - 1)):
            for c in range(target - 1, self.cols):
                if all(board[r + k][c - k] == piece for k in range(target)):
                    return [(r + k, c - k) for k in range(target)]
        return None

    def check_tie(self):
        """If the top row has no '_' -> board is full."""
        return "_" not in self.board[0]

    def reset_game(self):
        """Reset the board and move stack. Player 1 starts."""
        self.board = self.create_board()
        self.move_stack = []
        self.current_player = 1
        self.draw_board()

    # -------------------------------------------------------
    #           Blinking Win Highlight
    # -------------------------------------------------------
    def blink_winning_pieces(self, positions, highlight_color="green", blink_count=6):
        """Blink the winning positions, then show 'Game Over' and reset."""
        def toggle(step=0):
            self.canvas.delete("all")
            use_highlight = (step % 2 == 1)

            for r in range(self.rows):
                for c in range(self.cols):
                    x1 = self.padding + c * (self.cell_size + self.padding)
                    y1 = self.padding + r * (self.cell_size + self.padding)
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size

                    val = self.board[r][c]
                    if val == "R":
                        color = "red"
                    elif val == "Y":
                        color = "black"
                    else:
                        color = "white"

                    if (r, c) in positions and use_highlight:
                        color = highlight_color

                    self.canvas.create_oval(
                        x1, y1, x2, y2,
                        fill=color, outline="yellow", width=2
                    )

            if step < blink_count:
                self.master.after(300, toggle, step + 1)
            else:
                # Done blinking, declare winner
                winner_piece = self.board[positions[0][0]][positions[0][1]]
                winner_player = 1 if winner_piece == "R" else 2
                messagebox.showinfo("Game Over", f"Player {winner_player} ({winner_piece}) wins!")
                self.reset_game()

        toggle(0)

    # -------------------------------------------------------
    #                     AI Logic
    # -------------------------------------------------------
    def minimax(self, board, depth, maximizing_player, alpha, beta):
        """Return (best_col, best_score) for the AI (piece_map[2]) using minimax."""
        valid_cols = [c for c in range(self.cols) if board[0][c] == "_"]
        terminal = self.is_terminal_node(board)
        if depth == 0 or terminal:
            if terminal:
                # Check who won
                if self.check_piece_win(board, self.piece_map[2], self.connect_target):
                    return (None, float("inf"))
                elif self.check_piece_win(board, self.piece_map[1], self.connect_target):
                    return (None, float("-inf"))
                else:
                    return (None, 0)  # tie
            else:
                return (None, self.evaluate_board(board, self.piece_map[2]))

        if maximizing_player:
            best_score = float("-inf")
            best_col = random.choice(valid_cols)
            for col in valid_cols:
                row = self.get_next_open_row(board, col)
                temp_board = self.copy_board(board)
                temp_board[row][col] = self.piece_map[2]
                _, score = self.minimax(temp_board, depth - 1, False, alpha, beta)
                if score > best_score:
                    best_score = score
                    best_col = col
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break
            return (best_col, best_score)
        else:
            best_score = float("inf")
            best_col = random.choice(valid_cols)
            for col in valid_cols:
                row = self.get_next_open_row(board, col)
                temp_board = self.copy_board(board)
                temp_board[row][col] = self.piece_map[1]
                _, score = self.minimax(temp_board, depth - 1, True, alpha, beta)
                if score < best_score:
                    best_score = score
                    best_col = col
                beta = min(beta, best_score)
                if alpha >= beta:
                    break
            return (best_col, best_score)

    def is_terminal_node(self, board):
        """Check if the board is in a terminal state (win for R, win for Y, or tie)."""
        if self.check_piece_win(board, self.piece_map[1], self.connect_target):
            return True
        if self.check_piece_win(board, self.piece_map[2], self.connect_target):
            return True
        if "_" not in board[0]:
            return True
        return False

    def evaluate_board(self, board, ai_piece):
        """A simple heuristic that counts center preference + 2/3 in-a-row opportunities, etc."""
        human_piece = self.piece_map[1]
        center_weight = 3
        (ai2, ai3) = self.count_n_in_a_rows(board, ai_piece)
        (hu2, hu3) = self.count_n_in_a_rows(board, human_piece)

        # Weights
        w2 = 5
        w3 = 50
        b2 = 4
        b3 = 40

        score = 0
        # Center preference
        center_col = self.cols // 2
        center_array = [board[r][center_col] for r in range(self.rows)]
        center_count = center_array.count(ai_piece)
        score += center_count * center_weight

        # 2/3 in-a-rows
        score += ai2 * w2
        score += ai3 * w3
        score -= hu2 * b2
        score -= hu3 * b3
        return score

    def count_n_in_a_rows(self, board, piece):
        """Return (# of 2-in-a-rows, # of 3-in-a-rows) that are not blocked by the opponent."""
        count2 = 0
        count3 = 0
        directions = [(1,0), (0,1), (1,1), (1,-1)]

        for r in range(self.rows):
            for c in range(self.cols):
                if board[r][c] == piece:
                    for dr, dc in directions:
                        sequence = []
                        blocked = False
                        # We only go up to connect_target length
                        for k in range(self.connect_target):
                            rr = r + k*dr
                            cc = c + k*dc
                            if rr < 0 or rr >= self.rows or cc < 0 or cc >= self.cols:
                                blocked = True
                                break
                            if board[rr][cc] not in [piece, "_"]:
                                blocked = True
                                break
                            sequence.append(board[rr][cc])
                        if not blocked:
                            pc = sequence.count(piece)
                            empty = sequence.count("_")
                            # e.g. for connect_target=4, if pc=2 and empty=2 => 2 in a row
                            if pc == 2 and empty == (self.connect_target - 2):
                                count2 += 1
                            if pc == 3 and empty == (self.connect_target - 3):
                                count3 += 1

        return (count2, count3)

    def get_next_open_row(self, board, col):
        """Get the next open row in 'col' or None."""
        for r in range(self.rows-1, -1, -1):
            if board[r][col] == "_":
                return r
        return None

    def copy_board(self, board):
        """Return a deep copy of 'board'."""
        return [row[:] for row in board]


def main():
    root = tk.Tk()
    EnhancedConnectGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
