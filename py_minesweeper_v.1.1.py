import tkinter as tk
import random
import json
import os

class Minesweeper:
    def __init__(self, root, rows=9, cols=9, mines=10):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = []
        self.buttons = []
        self.game_over = False
        self.mine_count = mines
        self.save_file = "minesweeper_save.json"

        self.setup_game()

    def setup_game(self):
        if self.load_game():
            return
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.place_mines()
        self.calculate_numbers()
        self.create_buttons()
        self.create_ui()

    def place_mines(self):
        mine_positions = random.sample(range(self.rows * self.cols), self.mines)
        for pos in mine_positions:
            r, c = divmod(pos, self.cols)
            self.board[r][c] = -1

    def calculate_numbers(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == -1:
                    continue
                self.board[r][c] = self.count_adjacent_mines(r, c)

    def count_adjacent_mines(self, r, c):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and self.board[nr][nc] == -1:
                    count += 1
        return count

    def create_buttons(self):
        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(self.root, width=2, height=1, font=("Arial", 12, "bold"),
                                command=lambda r=r, c=c: self.reveal_cell(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.flag_cell(r, c))
                btn.grid(row=r, column=c)
                self.buttons[r][c] = btn

    def create_ui(self):
        self.mine_label = tk.Label(self.root, text=f"Mines: {self.mine_count}", font=("Arial", 12))
        self.mine_label.grid(row=self.rows, column=0, columnspan=self.cols // 2, sticky="w")

        self.timer_label = tk.Label(self.root, text="Time: 0", font=("Arial", 12))
        self.timer_label.grid(row=self.rows, column=self.cols // 2, columnspan=self.cols // 2, sticky="e")

        reset_button = tk.Button(self.root, text="Reset Level", command=self.reset_level, font=("Arial", 10))
        reset_button.grid(row=self.rows + 1, column=0, columnspan=self.cols, pady=5)

        self.timer = 0
        self.update_timer()

    def update_timer(self):
        if not self.game_over:
            self.timer += 1
            self.timer_label.config(text=f"Time: {self.timer}")
            self.root.after(1000, self.update_timer)

    def reveal_cell(self, r, c):
        if self.game_over or self.buttons[r][c]["state"] == "disabled":
            return

        if self.board[r][c] == -1:
            self.buttons[r][c].config(text="M", bg="red")
            self.game_over = True
            self.reveal_all()
            self.show_message("Game Over! You clicked on a mine.")
            return

        self.buttons[r][c].config(text=str(self.board[r][c]) if self.board[r][c] > 0 else "", state="disabled", relief=tk.SUNKEN, bg="lightgrey")

        if self.board[r][c] == 0:
            self.reveal_adjacent_cells(r, c)

        if self.check_win():
            self.game_over = True
            self.show_message("Congratulations! You Win!")

    def reveal_adjacent_cells(self, r, c):
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and self.buttons[nr][nc]["state"] != "disabled":
                    self.reveal_cell(nr, nc)

    def flag_cell(self, r, c):
        if self.game_over or self.buttons[r][c]["state"] == "disabled":
            return

        current_text = self.buttons[r][c].cget("text")
        if current_text == "F":
            self.buttons[r][c].config(text="")
            self.mine_count += 1
        else:
            self.buttons[r][c].config(text="F", fg="orange")
            self.mine_count -= 1
        self.mine_label.config(text=f"Mines: {self.mine_count}")

    def reveal_all(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == -1:
                    self.buttons[r][c].config(text="M", bg="red")
                elif self.buttons[r][c]["state"] != "disabled":
                    self.buttons[r][c].config(text=str(self.board[r][c]) if self.board[r][c] > 0 else "", state="disabled", bg="lightgrey")

    def check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != -1 and self.buttons[r][c]["state"] != "disabled":
                    return False
        return True

    def show_message(self, message):
        popup = tk.Toplevel(self.root)
        popup.title("Game Over")
        label = tk.Label(popup, text=message, font=("Arial", 14))
        label.pack(pady=10)
        restart_button = tk.Button(popup, text="Restart", command=self.restart_game)
        restart_button.pack(pady=5)
        save_button = tk.Button(popup, text="Save Game", command=self.save_game)
        save_button.pack(pady=5)

    def restart_game(self):
        self.root.destroy()
        main()

    def reset_level(self):
        if os.path.exists(self.save_file):
            os.remove(self.save_file)
        self.root.destroy()
        main()

    def save_game(self):
        game_state = {
            "board": self.board,
            "mine_count": self.mine_count,
            "timer": self.timer,
            "game_over": self.game_over,
            "buttons": [[self.buttons[r][c].cget("text") for c in range(self.cols)] for r in range(self.rows)]
        }
        with open(self.save_file, "w") as file:
            json.dump(game_state, file)

    def load_game(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as file:
                game_state = json.load(file)
            self.board = game_state["board"]
            self.mine_count = game_state["mine_count"]
            self.timer = game_state["timer"]
            self.game_over = game_state["game_over"]

            self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
            for r in range(self.rows):
                for c in range(self.cols):
                    btn = tk.Button(self.root, width=2, height=1, font=("Arial", 12, "bold"),
                                    text=game_state["buttons"][r][c],
                                    command=lambda r=r, c=c: self.reveal_cell(r, c))
                    btn.bind("<Button-3>", lambda e, r=r, c=c: self.flag_cell(r, c))
                    btn.grid(row=r, column=c)
                    self.buttons[r][c] = btn

            self.create_ui()
            return True
        return False

if __name__ == "__main__":
    def main():
        root = tk.Tk()
        root.title("Minesweeper")
        game = Minesweeper(root)
        root.mainloop()

    main()