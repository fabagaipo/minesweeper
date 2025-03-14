import tkinter as tk
from tkinter import messagebox, ttk
import random
from datetime import datetime
import json
import os

DIFFICULTY = {
    'Beginner': {'rows': 9, 'cols': 9, 'mines': 10},
    'Intermediate': {'rows': 16, 'cols': 16, 'mines': 40},
    'Expert': {'rows': 16, 'cols': 30, 'mines': 99}
}

class Minesweeper:
    def __init__(self, master, difficulty, high_scores, start_screen):
        self.master = master
        self.master.title("Minesweeper")
        self.difficulty = difficulty
        self.high_scores = high_scores
        self.start_screen = start_screen
        self.refresh_button = None
        self.message_label = None
        self.timer_label = None
        self.mine_counter_label = None
        self.start_time = None
        self.timer_running = False
        self.elapsed_time = 0
        self.game_over = False
        self.board = None
        self.buttons = {}
        self.revealed = None  # Will be initialized in new_game
        self.flagged = None   # Will be initialized in new_game
        self.flags_placed = 0
        self.info_frame = None
        self.button_frame = None
        
        # Load images
        self.images = {}
        self.load_images()
        
        # Create game layout
        self.create_menu()
        self.create_info_frame()
        self.new_game()
        
        # Configure window
        self.master.resizable(False, False)
        self.master.update_idletasks()
        
        # Center the window
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'+{x}+{y}')
        
        # Ensure window is visible and focused
        self.master.lift()
        self.master.focus_force()

    def add_high_score(self, time):
        if self.difficulty not in self.high_scores:
            self.high_scores[self.difficulty] = []
        scores = self.high_scores[self.difficulty]
        scores.append(time)
        scores.sort()
        self.high_scores[self.difficulty] = scores[:10]  # Keep only top 10
        self.save_high_scores()
        
    def save_high_scores(self):
        try:
            with open('highscores.json', 'w') as f:
                json.dump(self.high_scores, f)
        except Exception as e:
            print(f"Error saving high scores: {e}")

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def show_high_scores(self):
        # Get the parent window (either game window or start screen)
        parent = self.master
        
        scores_window = tk.Toplevel(parent)
        scores_window.title("High Scores")
        scores_window.transient(parent)
        scores_window.grab_set()
        scores_window.geometry("300x400")
        scores_window.resizable(False, False)

        # Style configuration
        style = ttk.Style()
        style.configure('Scores.TNotebook', background='#f0f0f0')
        style.configure('Scores.TFrame', background='#f0f0f0')

        notebook = ttk.Notebook(scores_window, style='Scores.TNotebook')
        notebook.pack(padx=10, pady=10, expand=True, fill='both')

        for difficulty in DIFFICULTY.keys():
            frame = ttk.Frame(notebook, style='Scores.TFrame')
            notebook.add(frame, text=difficulty)
            frame.configure(padding=10)

            scores = self.high_scores.get(difficulty, [])
            if not scores:
                ttk.Label(frame, text="No scores yet!", 
                         font=("Arial", 11)).pack(pady=20)
            else:
                # Sort scores and take top 10
                sorted_scores = sorted(scores)[:10]
                for i, score in enumerate(sorted_scores, 1):
                    formatted_time = self.format_time(score)
                    ttk.Label(frame, text=f"{i}. {formatted_time}", 
                             font=("Arial", 11)).pack(pady=2)

        close_button = ttk.Button(scores_window, text="Close", 
                                 command=scores_window.destroy)
        close_button.pack(pady=10)

        # Center the scores window
        scores_window.update_idletasks()
        width = scores_window.winfo_width()
        height = scores_window.winfo_height()
        x = (parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2))
        y = (parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2))
        scores_window.geometry(f'+{x}+{y}')
        
        # Ensure the window is visible and focused
        scores_window.lift()
        scores_window.focus_force()

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=self.new_game)
        game_menu.add_command(label="High Scores", command=self.show_high_scores)
        game_menu.add_command(label="Return to Menu", 
                            command=lambda: self.master.destroy())
        game_menu.add_separator()
        
        difficulty_menu = tk.Menu(game_menu, tearoff=0)
        game_menu.add_cascade(label="Difficulty", menu=difficulty_menu)
        for diff in DIFFICULTY.keys():
            difficulty_menu.add_command(label=diff, 
                                      command=lambda d=diff: self.change_difficulty(d))
        
        game_menu.add_separator()
        game_menu.add_command(label="Exit", 
                            command=lambda: self.quit_game())
    
    def create_info_frame(self):
        self.info_frame = tk.Frame(self.master)
        self.info_frame.grid(row=0, column=0, columnspan=DIFFICULTY[self.difficulty]['cols'], sticky='ew', pady=5)
        
        self.mine_counter_label = tk.Label(self.info_frame, text=f"Mines: {DIFFICULTY[self.difficulty]['mines']}", 
                                          font=("Arial", 12))
        self.mine_counter_label.pack(side=tk.LEFT, padx=10)
        
        self.timer_label = tk.Label(self.info_frame, text="Time: 00:00", font=("Arial", 12))
        self.timer_label.pack(side=tk.RIGHT, padx=10)
    
    def update_timer(self):
        if self.timer_running and not self.game_over:
            try:
                self.elapsed_time = int((datetime.now() - self.start_time).total_seconds())
                self.timer_label.config(text=f"Time: {self.format_time(self.elapsed_time)}")
                self.master.after(1000, self.update_timer)
            except:
                self.timer_running = False
    
    def change_difficulty(self, difficulty):
        self.difficulty = difficulty
        if self.timer_running:
            self.timer_running = False
        self.master.title(f"Minesweeper - {difficulty}")
        self.new_game()
        
    def quit_game(self):
        if messagebox.askokcancel("Quit", "Do you want to exit Minesweeper?"):
            if self.start_screen:
                self.start_screen.master.destroy()
            else:
                self.master.destroy()
    
    def new_game(self):
        rows = DIFFICULTY[self.difficulty]['rows']
        cols = DIFFICULTY[self.difficulty]['cols']
        
        # Update window title
        self.master.title(f"Minesweeper - {self.difficulty}")
        
        # Initialize game state
        self.board = self.initialize_board()
        self.buttons = {}
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]
        self.flagged = [[False for _ in range(cols)] for _ in range(rows)]
        self.game_over = False
        self.flags_placed = 0
        self.start_time = None
        self.timer_running = False
        self.elapsed_time = 0
        
        # Clear existing game grid
        if self.button_frame:
            self.button_frame.destroy()
        if self.info_frame:
            self.info_frame.destroy()
        
        # Create new game layout
        self.create_info_frame()
        self.create_buttons()
        self.place_mines()
        self.calculate_numbers()
        
        # Update display
        self.mine_counter_label.config(text=f"Mines: {DIFFICULTY[self.difficulty]['mines'] - self.flags_placed}")
        self.timer_label.config(text="Time: 00:00")
        
        # Update window size and position
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'+{x}+{y}')

    def initialize_board(self):
        rows, cols = DIFFICULTY[self.difficulty]['rows'], DIFFICULTY[self.difficulty]['cols']
        return [[' ' for _ in range(cols)] for _ in range(rows)]
    
    def place_mines(self):
        rows, cols = DIFFICULTY[self.difficulty]['rows'], DIFFICULTY[self.difficulty]['cols']
        mines = DIFFICULTY[self.difficulty]['mines']
        mines_placed = 0
        while mines_placed < mines:
            row = random.randint(0, rows - 1)
            col = random.randint(0, cols - 1)
            if self.board[row][col] != '*':
                self.board[row][col] = '*'
                mines_placed += 1

    def calculate_numbers(self):
        rows, cols = DIFFICULTY[self.difficulty]['rows'], DIFFICULTY[self.difficulty]['cols']
        for row in range(rows):
            for col in range(cols):
                if self.board[row][col] == '*':
                    continue
                mine_count = 0
                for r in range(row - 1, row + 2):
                    for c in range(col - 1, col + 2):
                        if 0 <= r < rows and 0 <= c < cols and self.board[r][c] == '*':
                            mine_count += 1
                if mine_count > 0:
                    self.board[row][col] = str(mine_count)
    
    def load_images(self):
        # Load all game images
        try:
            self.images['covered'] = tk.PhotoImage(file='assets/cell_covered.gif')
            self.images['uncovered'] = tk.PhotoImage(file='assets/cell_uncovered.gif')
            self.images['mine'] = tk.PhotoImage(file='assets/mine.gif')
            self.images['flag'] = tk.PhotoImage(file='assets/flag.gif')
            self.images['wrong'] = tk.PhotoImage(file='assets/wrong_mine.gif')
            
            # Load number images
            for i in range(1, 9):
                self.images[str(i)] = tk.PhotoImage(file=f'assets/number_{i}.gif')
        except Exception as e:
            print(f"Error loading images: {e}")
            messagebox.showerror("Error", "Failed to load game images. Using text mode.")
    
    def create_buttons(self):
        rows, cols = DIFFICULTY[self.difficulty]['rows'], DIFFICULTY[self.difficulty]['cols']
        self.button_frame = tk.Frame(self.master)
        self.button_frame.grid(row=1, column=0, columnspan=cols)
        
        for row in range(rows):
            for col in range(cols):
                button = tk.Button(self.button_frame, image=self.images['covered'],
                                 width=35, height=35,
                                 command=lambda r=row, c=col: self.reveal_cell(r, c))
                button.grid(row=row, column=col, padx=0, pady=0)
                button.bind('<Button-3>', lambda e, r=row, c=col: self.toggle_flag(r, c))
                self.buttons[(row, col)] = button

    def toggle_flag(self, row, col):
        if self.game_over or self.revealed[row][col]:
            return
        
        if not self.flagged[row][col]:
            if self.flags_placed < DIFFICULTY[self.difficulty]['mines']:
                self.flagged[row][col] = True
                self.flags_placed += 1
                self.buttons[(row, col)].config(image=self.images['flag'])
        else:
            self.flagged[row][col] = False
            self.flags_placed -= 1
            self.buttons[(row, col)].config(image=self.images['covered'])
        
        self.mine_counter_label.config(text=f"Mines: {DIFFICULTY[self.difficulty]['mines'] - self.flags_placed}")
        
    def reveal_cell(self, row, col):
        if self.game_over or self.revealed[row][col] or self.flagged[row][col]:
            return
        
        if not self.start_time:
            self.start_time = datetime.now()
            self.timer_running = True
            self.update_timer()
        
        self.revealed[row][col] = True

        if self.board[row][col] == '*':
            self.buttons[(row, col)].config(image=self.images['mine'], state='disabled')
            self.game_over = True
            self.timer_running = False
            self.reveal_all_mines()
            messagebox.showinfo("Game Over", "Better luck next time!")
            self.disable_all_buttons()
            return
        
        cell_value = self.board[row][col]
        if cell_value == ' ':
            self.buttons[(row, col)].config(image=self.images['uncovered'], state='disabled')
        else:
            self.buttons[(row, col)].config(image=self.images[cell_value], state='disabled')
        if self.board[row][col] == ' ':
            for r in range(row - 1, row + 2):
                for c in range (col - 1, col + 2):
                    if 0 <= r < ROW and 0 <= c < COL and not self.revealed[r][c]:
                        self.reveal_cell(r, c)

        if self.check_win():
            self.game_over = True
            self.timer_running = False
            self.add_high_score(self.elapsed_time)
            messagebox.showinfo("Congratulations!", f"You've won the game in {self.format_time(self.elapsed_time)}!\nCheck the high scores to see if you made it to the top 10!")
            self.disable_all_buttons()

    def disable_all_buttons(self):
        for button in self.buttons.values():
            button.config(state='disabled')

    def reveal_all_mines(self):
        rows, cols = DIFFICULTY[self.difficulty]['rows'], DIFFICULTY[self.difficulty]['cols']
        for row in range(rows):
            for col in range(cols):
                if self.board[row][col] == '*' and not self.flagged[row][col]:
                    self.buttons[(row, col)].config(image=self.images['mine'])
                elif self.flagged[row][col] and self.board[row][col] != '*':
                    self.buttons[(row, col)].config(image=self.images['wrong'])
    
    def check_win(self):
        rows, cols = DIFFICULTY[self.difficulty]['rows'], DIFFICULTY[self.difficulty]['cols']
        for row in range(rows):
            for col in range(cols):
                if self.board[row][col] != '*' and not self.revealed[row][col]:
                    return False
        return True



class StartScreen:
    def __init__(self, master):
        self.master = master
        self.master.title("Minesweeper - Main Menu")
        self.master.geometry("400x500")
        self.master.resizable(False, False)
        self.master.configure(bg='#f0f0f0')  # Light gray background
        
        # Initialize high scores
        self.high_scores = {diff: [] for diff in DIFFICULTY.keys()}
        try:
            with open('highscores.json', 'r') as f:
                self.high_scores.update(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            self.save_high_scores()
        
        # Title
        title_frame = tk.Frame(master, pady=30, bg='#f0f0f0')
        title_frame.pack(fill='x')
        title_label = tk.Label(title_frame, text="MINESWEEPER", 
                              font=("Arial", 24, "bold"),
                              bg='#f0f0f0', fg='#333333')
        title_label.pack()
        
        # Main buttons frame
        button_frame = tk.Frame(master, bg='#f0f0f0')
        button_frame.pack(expand=True, fill='both', padx=50)
        
        # Difficulty frame
        diff_frame = tk.LabelFrame(button_frame, text="Select Difficulty", 
                                  font=("Arial", 12), bg='#f0f0f0')
        diff_frame.pack(fill='x', pady=20)
        
        self.difficulty = tk.StringVar()
        self.difficulty.set("Intermediate")  # Set default difficulty
        
        for diff in DIFFICULTY.keys():
            tk.Radiobutton(diff_frame, text=diff, variable=self.difficulty, 
                          value=diff, font=("Arial", 11), bg='#f0f0f0').pack(pady=5)
        
        # Action buttons
        style = ttk.Style()
        style.configure('Large.TButton', font=("Arial", 12), padding=10)
        style.configure('TButton', font=("Arial", 10))
        
        ttk.Button(button_frame, text="New Game", style='Large.TButton',
                   command=self.start_game).pack(fill='x', pady=10)
        ttk.Button(button_frame, text="High Scores", style='Large.TButton',
                   command=self.show_high_scores).pack(fill='x', pady=10)
        ttk.Button(button_frame, text="Exit", style='Large.TButton',
                   command=self.on_game_close).pack(fill='x', pady=10)
        
        # Center the window
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'+{x}+{y}')
    
    def load_high_scores(self):
        try:
            with open('highscores.json', 'r') as f:
                self.high_scores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.high_scores = {diff: [] for diff in DIFFICULTY.keys()}
            self.save_high_scores()
    
    def save_high_scores(self):
        with open('highscores.json', 'w') as f:
            json.dump(self.high_scores, f)
    
    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def show_high_scores(self):
        # Get the parent window (either game window or start screen)
        parent = self.master
        
        scores_window = tk.Toplevel(parent)
        scores_window.title("High Scores")
        scores_window.transient(parent)
        scores_window.grab_set()
        scores_window.geometry("300x400")
        scores_window.resizable(False, False)

        # Style configuration
        style = ttk.Style()
        style.configure('Scores.TNotebook', background='#f0f0f0')
        style.configure('Scores.TFrame', background='#f0f0f0')

        notebook = ttk.Notebook(scores_window, style='Scores.TNotebook')
        notebook.pack(padx=10, pady=10, expand=True, fill='both')

        for difficulty in DIFFICULTY.keys():
            frame = ttk.Frame(notebook, style='Scores.TFrame')
            notebook.add(frame, text=difficulty)
            frame.configure(padding=10)

            scores = self.high_scores.get(difficulty, [])
            if not scores:
                ttk.Label(frame, text="No scores yet!", 
                         font=("Arial", 11)).pack(pady=20)
            else:
                # Sort scores and take top 10
                sorted_scores = sorted(scores)[:10]
                for i, score in enumerate(sorted_scores, 1):
                    formatted_time = self.format_time(score)
                    ttk.Label(frame, text=f"{i}. {formatted_time}", 
                             font=("Arial", 11)).pack(pady=2)

        close_button = ttk.Button(scores_window, text="Close", 
                                 command=scores_window.destroy)
        close_button.pack(pady=10)

        # Center the scores window
        scores_window.update_idletasks()
        width = scores_window.winfo_width()
        height = scores_window.winfo_height()
        x = (parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2))
        y = (parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2))
        scores_window.geometry(f'+{x}+{y}')
        
        # Ensure the window is visible and focused
        scores_window.lift()
        scores_window.focus_force()
    
    def start_game(self):
        try:
            difficulty = self.difficulty.get()
            
            # Create and configure game window
            game_window = tk.Toplevel(self.master)
            game_window.title(f"Minesweeper - {difficulty}")
            game_window.resizable(False, False)
            
            # Create the game instance
            game = Minesweeper(game_window, difficulty, 
                             self.high_scores, self)
            
            # Configure window closing
            def on_game_close():
                if game.timer_running:
                    game.timer_running = False
                game_window.destroy()
                self.master.deiconify()
            
            game_window.protocol("WM_DELETE_WINDOW", on_game_close)
            
            # Hide the start screen
            self.master.withdraw()
            
        except Exception as e:
            import traceback
            error_msg = f"Failed to start game: {str(e)}"
            print(f"{error_msg}\n{traceback.format_exc()}")
            messagebox.showerror("Error", error_msg)
            if 'game_window' in locals():
                game_window.destroy()
            self.master.deiconify()
    
    def on_game_close(self):
        if messagebox.askokcancel("Quit", "Do you want to exit Minesweeper?"):
            self.master.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    start_screen = StartScreen(root)
    root.mainloop()
