import random
import tkinter as tk
from tkinter import ttk
import time
import threading

# Constants
EMPTY = " "
X = "X"
O = "O"

class TicTacToe:
    def __init__(self):
        self.reset_game()
        
    def reset_game(self):
        self.board = [[EMPTY for _ in range(3)] for _ in range(3)]
        self.game_over = False
        self.winner = None
        
    def get_available_moves(self):
        """Return a list of available moves as (row, col) tuples."""
        moves = []
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == EMPTY:
                    moves.append((row, col))
        return moves
    
    def is_valid_move(self, move):
        """Check if the move is valid."""
        if not move:
            return False
        row, col = move
        if row < 0 or row > 2 or col < 0 or col > 2:
            return False
        return self.board[row][col] == EMPTY
    
    def get_current_player(self):
        """Determine whose turn it is based on the board state."""
        x_count = sum(row.count(X) for row in self.board)
        o_count = sum(row.count(O) for row in self.board)
        return O if x_count > o_count else X
    
    def apply_move(self, move):
        """Apply a move to the board. Return True if successful."""
        if self.is_valid_move(move):
            row, col = move
            player = self.get_current_player()
            self.board[row][col] = player
            self.check_game_state()
            return True
        return False
    
    def check_game_state(self):
        """Check if the game is over and determine the winner."""
        result = self._get_winner()
        if result is not None:
            self.game_over = True
            self.winner = result
        elif not self.get_available_moves():
            self.game_over = True
    
    def _get_winner(self):
        """Check if there's a winner and return X, O, or None."""
        # Check rows
        for row in self.board:
            if row.count(X) == 3:
                return X
            if row.count(O) == 3:
                return O
        
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] == X:
                return X
            if self.board[0][col] == self.board[1][col] == self.board[2][col] == O:
                return O
        
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != EMPTY:
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != EMPTY:
            return self.board[0][2]
        
        return None
    
    def get_winner_value(self):
        """Return numerical value for the winner (1 for X, -1 for O, 0 for draw)."""
        if not self.game_over:
            return None
        if self.winner == X:
            return 1
        elif self.winner == O:
            return -1
        else:
            return 0

class TicTacToeAI:
    def __init__(self, learning_rate=0.5, exploration_rate=0.1, train_games=10000):
        self.q_values = {}  # Dictionary to store Q-values: {(board_state, move): q_value}
        self.learning_rate = learning_rate
        self.exploration_rate = exploration_rate
        self.train_games = train_games
        self.training_progress = 0
        self.stop_training = False
        self.game_count = 0
        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0
    
    def get_q_value(self, game, move):
        """Get the Q-value for a given game state and move."""
        return self.q_values.get((str(game.board), move), 0)
    
    def update_q_value(self, state, move, new_state, reward):
        """Update Q-value using the Q-learning formula."""
        old_q = self.q_values.get((str(state), move), 0)
        # Simplified Q-learning formula
        self.q_values[(str(state), move)] = old_q + self.learning_rate * (reward - old_q)
    
    def get_best_move(self, game):
        """Get the best move based on Q-values."""
        moves = game.get_available_moves()
        if not moves:
            return None
            
        # Use exploration during training
        if random.random() < self.exploration_rate:
            return random.choice(moves)
        
        best_move = moves[0]
        best_q = float('-inf')
        
        for move in moves:
            q_value = self.get_q_value(game, move)
            if q_value > best_q:
                best_q = q_value
                best_move = move
                
        return best_move
    
    def train(self, callback=None, visual_callback=None):
        """Train the AI by playing games against itself with visual feedback."""
        self.game_count = 0
        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0
        self.stop_training = False
        
        while self.game_count < self.train_games and not self.stop_training:
            game = TicTacToe()
            
            # For visual simulation of gameplay
            if visual_callback and self.game_count % 10 == 0:  # Show every 10th game
                visual_callback(game.board, None, None, reset=True)
                
            game_history = []  # Store moves for this game
            
            while not game.game_over and not self.stop_training:
                current_state = [row[:] for row in game.board]  # Deep copy current board state
                current_player = game.get_current_player()
                
                # Get and apply move
                move = self.get_best_move(game)
                if not move:
                    break
                    
                game_history.append((current_state, move, current_player))
                game.apply_move(move)
                
                # Show move in UI if requested
                if visual_callback and self.game_count % 10 == 0:
                    visual_callback(game.board, move, current_player)
            
            # If training was stopped, don't process the last game
            if self.stop_training:
                break
                
            # Game is over - update Q-values based on outcome
            winner_value = game.get_winner_value()
            
            # Update statistics
            if winner_value == 1:
                self.x_wins += 1
            elif winner_value == -1:
                self.o_wins += 1
            else:
                self.draws += 1
            
            # Assign rewards based on game outcome
            for i, (state, move, player) in enumerate(game_history):
                # Calculate reward based on game result and player
                if winner_value == 0:  # Draw
                    reward = 0.5
                elif (winner_value == 1 and player == X) or (winner_value == -1 and player == O):
                    # Player won - higher reward for moves closer to the end
                    reward = 1.0 - 0.9 * (len(game_history) - i - 1) / len(game_history)
                else:
                    # Player lost - negative reward
                    reward = -1.0
                
                # Update Q-value
                self.update_q_value(state, move, game.board, reward)
            
            # Update progress
            self.game_count += 1
            self.training_progress = (self.game_count) / self.train_games * 100
            
            if callback and self.game_count % 10 == 0:
                callback(self.training_progress, self.x_wins, self.o_wins, self.draws)
        
        # Final update
        if callback:
            callback(self.training_progress, self.x_wins, self.o_wins, self.draws)
            
        return not self.stop_training  # Return True if completed, False if stopped


class TicTacToeUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe with Visual Training")
        self.root.resizable(False, False)
        
        self.game = TicTacToe()
        self.ai = TicTacToeAI(train_games=1000)  # Reduced default for faster training
        
        # Training visualization speed control
        self.speed_var = tk.DoubleVar(value=0.3)  # Default delay between moves
        
        # Training state
        self.training_running = False
        self.training_thread = None
        
        self.create_widgets()
        self.create_game_board()
        
    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Title
        ttk.Label(self.main_frame, text="Tic Tac Toe with Visual Training", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=10)
        
        # Game board frame
        self.board_frame = ttk.Frame(self.main_frame, padding="5")
        self.board_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Start a new game or train the AI")
        status_label = ttk.Label(self.main_frame, textvariable=self.status_var, font=("Arial", 10))
        status_label.grid(row=2, column=0, columnspan=3, pady=5)
        
        # Controls frame
        controls_frame = ttk.Frame(self.main_frame, padding="5")
        controls_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        # New Game button
        new_game_btn = ttk.Button(controls_frame, text="New Game", command=self.new_game)
        new_game_btn.grid(row=0, column=0, padx=5)
        
        # Train AI button (will toggle to Stop Training)
        self.train_btn_text = tk.StringVar(value="Train AI")
        self.train_btn = ttk.Button(controls_frame, textvariable=self.train_btn_text, command=self.toggle_training)
        self.train_btn.grid(row=0, column=1, padx=5)
        
        # AI First button
        self.ai_first_btn = ttk.Button(controls_frame, text="AI Goes First", command=self.ai_move_first)
        self.ai_first_btn.grid(row=0, column=2, padx=5)
        
        # Training settings frame
        settings_frame = ttk.Frame(self.main_frame, padding="5")
        settings_frame.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Game count input
        ttk.Label(settings_frame, text="Games:").grid(row=0, column=0, padx=5)
        self.games_var = tk.StringVar(value="1000")
        games_entry = ttk.Entry(settings_frame, textvariable=self.games_var, width=8)
        games_entry.grid(row=0, column=1, padx=5)
        
        # Animation speed slider
        ttk.Label(settings_frame, text="Animation Speed:").grid(row=0, column=2, padx=5)
        speed_slider = ttk.Scale(settings_frame, from_=0.01, to=1.0, orient="horizontal", 
                               variable=self.speed_var, length=100)
        speed_slider.grid(row=0, column=3, padx=5)
        
        # Training progress frame
        training_frame = ttk.Frame(self.main_frame, padding="5")
        training_frame.grid(row=5, column=0, columnspan=3, pady=5)
        
        ttk.Label(training_frame, text="Training Progress:").grid(row=0, column=0, padx=5, sticky="w")
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(training_frame, variable=self.progress_var, length=300, mode="determinate")
        self.progress_bar.grid(row=0, column=1, padx=5)
        
        # Game counter
        self.games_count_var = tk.StringVar(value="0/0 games")
        ttk.Label(training_frame, textvariable=self.games_count_var).grid(row=0, column=2, padx=5)
        
        # Training stats
        self.stats_frame = ttk.Frame(self.main_frame, padding="5")
        self.stats_frame.grid(row=6, column=0, columnspan=3, pady=5)
        
        self.x_wins_var = tk.StringVar(value="X Wins: 0")
        self.o_wins_var = tk.StringVar(value="O Wins: 0")
        self.draws_var = tk.StringVar(value="Draws: 0")
        
        ttk.Label(self.stats_frame, textvariable=self.x_wins_var).grid(row=0, column=0, padx=15)
        ttk.Label(self.stats_frame, textvariable=self.o_wins_var).grid(row=0, column=1, padx=15)
        ttk.Label(self.stats_frame, textvariable=self.draws_var).grid(row=0, column=2, padx=15)
        
        # Current game info
        self.player_var = tk.StringVar(value="Current player: X")
        self.player_label = ttk.Label(self.main_frame, textvariable=self.player_var, font=("Arial", 12))
        self.player_label.grid(row=7, column=0, columnspan=3, pady=5)
    
    def create_game_board(self):
        """Create the 3x3 game board buttons."""
        self.buttons = []
        
        for i in range(3):
            row_buttons = []
            for j in range(3):
                btn = tk.Button(
                    self.board_frame,
                    text=EMPTY,
                    font=("Arial", 20, "bold"),
                    width=5,
                    height=2,
                    command=lambda r=i, c=j: self.make_move(r, c)
                )
                btn.grid(row=i, column=j, padx=2, pady=2)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
    
    def update_board(self, board=None):
        """Update the UI board to match the game state."""
        if board is None:
            board = self.game.board
            
        for i in range(3):
            for j in range(3):
                self.buttons[i][j]["text"] = board[i][j]
        
        # Update player indicator
        if not self.game.game_over:
            self.player_var.set(f"Current player: {self.game.get_current_player()}")
        else:
            if self.game.winner:
                self.player_var.set(f"Winner: {self.game.winner}")
            else:
                self.player_var.set("Game ended in a draw")
    
    def make_move(self, row, col):
        """Handle player move."""
        if self.game.game_over or self.training_running:
            return
        
        if self.game.apply_move((row, col)):
            self.update_board()
            
            if not self.game.game_over:
                self.root.after(100, self.ai_move)
            else:
                self.show_game_result()
    
    def ai_move(self):
        """Let the AI make a move."""
        if self.game.game_over:
            return
        
        move = self.ai.get_best_move(self.game)
        if move and self.game.apply_move(move):
            self.update_board()
            
            if self.game.game_over:
                self.show_game_result()
    
    def ai_move_first(self):
        """Start a new game with AI going first."""
        if not self.training_running:
            self.new_game()
            self.ai_move()
    
    def show_game_result(self):
        """Display the game result."""
        if self.game.winner == X:
            self.status_var.set("X wins!")
        elif self.game.winner == O:
            self.status_var.set("O wins!")
        else:
            self.status_var.set("Game ended in a draw!")
    
    def new_game(self):
        """Reset the game."""
        if not self.training_running:
            self.game.reset_game()
            self.update_board()
            self.status_var.set("Game started! Your turn (X)")
            self.player_var.set(f"Current player: {self.game.get_current_player()}")
    
    def toggle_training(self):
        """Toggle between starting and stopping training."""
        if not self.training_running:
            # Start training
            self.start_training()
        else:
            # Stop training
            self.stop_training()
    
    def start_training(self):
        """Start the AI training process with visual simulation."""
        try:
            train_games = int(self.games_var.get())
            
            self.ai = TicTacToeAI(train_games=train_games)
            self.status_var.set(f"Training AI with {train_games} games...")
            
            # Change button text to "Stop Training"
            self.train_btn_text.set("Stop Training")
            self.training_running = True
            
            # Disable other buttons during training
            self.ai_first_btn["state"] = "disabled"
            
            # Start training in a separate thread
            self.training_thread = threading.Thread(target=self.train_ai_thread)
            self.training_thread.daemon = True
            self.training_thread.start()
            
        except ValueError:
            self.status_var.set("Please enter a valid number of games")
    
    def stop_training(self):
        """Stop the training process."""
        if self.training_running:
            self.ai.stop_training = True
            self.status_var.set("Stopping training...")
            
            # Button will be reset to "Train AI" when the thread finishes
    
    def train_ai_thread(self):
        """Run training in a separate thread."""
        completed = self.train_ai()
        
        # Update UI after training is complete or stopped
        self.root.after(0, self.training_completed, completed)
    
    def training_completed(self, completed):
        """Handle completion of training."""
        self.training_running = False
        self.train_btn_text.set("Train AI")
        self.ai_first_btn["state"] = "normal"
        
        if completed:
            self.status_var.set("Training completed successfully!")
        else:
            self.status_var.set("Training stopped.")
    
    def train_ai(self):
        """Train the AI with visual simulation."""
        # Update progress callback
        def update_progress(progress, x_wins, o_wins, draws):
            self.progress_var.set(progress)
            self.games_count_var.set(f"{self.ai.game_count}/{self.ai.train_games} games")
            
            # Update statistics
            self.x_wins_var.set(f"X Wins: {x_wins}")
            self.o_wins_var.set(f"O Wins: {o_wins}")
            self.draws_var.set(f"Draws: {draws}")
            
            # Update UI
            self.root.update_idletasks()
        
        # Visual simulation callback
        def visual_update(board, move, player, reset=False):
            if reset:
                # Clear the board for a new game
                self.update_board([[EMPTY for _ in range(3)] for _ in range(3)])
                return
                
            # Show move on board
            self.update_board(board)
            
            # Add delay for visualization
            self.root.update_idletasks()
            time.sleep(self.speed_var.get())  # Adjustable delay
        
        # Start training with callbacks
        return self.ai.train(callback=update_progress, visual_callback=visual_update)


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeUI(root)
    root.mainloop()