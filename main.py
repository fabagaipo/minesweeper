import tkinter as tk
import random

# TODO: Add difficulty levels
# Traditionally, a 16x16 grid contains 40 mines
ROW = 16
COL = 16
MINES = 40

#TODO: Add flagging feature and replace * with actual mine image/icon
class Minesweeper:
    def __init__(self, master):
        self.master = master
        self.master.title("Minesweeper")
        self.refresh_button = None
        self.message_label = None
        self.new_game()

    def new_game(self):
        self.board = self.initialize_board()
        self.buttons = {}
        self.revealed = [[False for _ in range(COL)] for _ in range(ROW)]
        self.game_over = False

        self.create_buttons()
        self.place_mines()
        self.calculate_numbers()

        if self.refresh_button:
            self.refresh_button.grid_forget()

        if self.message_label:
            self.message_label.grid_forget()
            self.message_label = None

    def initialize_board(self):
        return [[' ' for _ in range(COL)] for _ in range(ROW)]
    
    def place_mines(self):
        mines_placed = 0
        while mines_placed < MINES:
            row = random.randint(0, ROW - 1)
            col = random.randint(0, COL - 1)
            if self.board[row][col] != '*':
                self.board[row][col] = '*'
                mines_placed += 1

    def calculate_numbers(self):
        for row in range(ROW):
            for col in range(COL):
                if self.board[row][col] == '*':
                    continue
                mine_count = 0
                for r in range(row - 1, row + 2):
                    for c in range(col - 1, col + 2):
                        if 0 <= r < ROW and 0 <= c < COL and self.board[r][c] == '*':
                            mine_count += 1
                if mine_count > 0:
                    self.board[row][col] = str(mine_count)
    
    def create_buttons(self):
        for row in range(ROW):
            for col in range(COL):
                button = tk.Button(self.master, text=' ', width=4, height=2,
                                   command=lambda r=row, c=col: self.reveal_cell(r, c))
                button.grid(row=row, column=col)
                self.buttons[(row, col)] = button

    def reveal_cell(self, row, col):
        if self.game_over or self.revealed[row][col]:
            return
        
        self.revealed[row][col] = True
        self.buttons[(row, col)].config(state='disabled')

        if self.board[row][col] == '*':
            self.buttons[(row, col)].config(text='*', bg='red')
            self.game_over = True
            self.show_game_over_message("Boohoo. Do better")
            self.disable_all_buttons()
            self.show_refresh_button()
            return
        
        number_colors = {
            '1': 'blue',
            '2': 'green',
            '3': 'red',
            '4': 'purple',
        }
        
        cell_value = self.board[row][col]
        color = number_colors.get(cell_value, 'black')
        self.buttons[(row, col)].config(
            text=cell_value,
            bg='#c0c0c0',
            disabledforeground=color,
            state='disabled'
        )
        if self.board[row][col] == ' ':
            for r in range(row - 1, row + 2):
                for c in range (col - 1, col + 2):
                    if 0 <= r < ROW and 0 <= c < COL and not self.revealed[r][c]:
                        self.reveal_cell(r, c)

        if self.check_win():
            self.game_over = True
            self.show_game_over_message("I guess you won. Congrats?")
            self.disable_all_buttons()
            self.show_refresh_button()

    def disable_all_buttons(self):
        for button in self.buttons.values():
            button.config(state='disabled')

    def show_game_over_message(self, message):
        self.message_label = tk.Label(self.master, text=message, font=("Arial", 16))
        self.message_label.grid(row=ROW + 1, column=0, columnspan=COL)

    def check_win(self):
        for row in range(ROW):
            for col in range(COL):
                if self.board[row][col] != '*' and not self.revealed[row][col]:
                    return False
        return True

    def show_refresh_button(self):
        if not self.refresh_button:
            self.refresh_button = tk.Button(self.master, text="New Game", command=self.new_game, width=15, height=2)
            self.refresh_button.grid(row=ROW + 2, column=0, columnspan=COL)

if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()
