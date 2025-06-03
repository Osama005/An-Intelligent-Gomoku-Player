import tkinter as tk
from tkinter import messagebox
import math
import copy

class GomokuGUI:
  def __init__(self, master):
      self.master = master
      self.master.title("Gomoku Game")
      self.default_board_size = 15  
      self.cell_size = 50  
      self.margin = self.cell_size // 2  
      self.current_player = 'X'  # Start with player 'X'
      self.board_size = self.default_board_size  
      self.grid_size = self.board_size + 1  
      self.board = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
      self.difficulty = "Medium"
      self.game_started = False 

      # Control Frame for inputs
      self.control_frame = tk.Frame(self.master)
      self.control_frame.pack(pady=10)

      # Board size input
      self.board_size_label = tk.Label(self.control_frame, text="Enter Board Size (5-20):")
      self.board_size_label.pack(side="left")
      self.board_size_entry = tk.Entry(self.control_frame, width=5)
      self.board_size_entry.insert(0, str(self.default_board_size))
      self.board_size_entry.pack(side="left", padx=(5, 20))

      # Difficulty selection
      self.difficulty_label = tk.Label(self.control_frame, text="Select Difficulty:")
      self.difficulty_label.pack(side="left")
      self.difficulty_var = tk.StringVar(value=self.difficulty)
      self.difficulty_menu = tk.OptionMenu(self.control_frame, self.difficulty_var, "Easy", "Medium", "Hard")
      self.difficulty_menu.pack(side="left", padx=(5, 20))

      # Start game button
      self.start_button = tk.Button(self.control_frame, text="Start Game", command=self.start_game)
      self.start_button.pack(side="left")

      # Canvas for the board
      self.canvas = tk.Canvas(
          self.master,
          width=2 * self.margin + self.board_size * self.cell_size,
          height=2 * self.margin + self.board_size * self.cell_size,
          bg="saddlebrown" 
      )
      self.canvas.pack(pady=10)

      # Bind click event
      self.canvas.bind("<Button-1>", self.handle_click)

      # Initially draw the grid
      self.draw_grid()

  def start_game(self):
      try:
          board_size_input = self.board_size_entry.get()
          if not board_size_input:
              raise ValueError("Board size cannot be empty")
          board_size = int(board_size_input)
          if not (5 <= board_size <= 20):
              raise ValueError("Board size must be between 5 and 20")

          self.board_size = board_size
          self.grid_size = self.board_size + 1  # Update grid size
          self.difficulty = self.difficulty_var.get()

          # Update margins and canvas size based on new board size
          self.margin = self.cell_size // 2
          self.canvas.config(
              width=2 * self.margin + self.board_size * self.cell_size,
              height=2 * self.margin + self.board_size * self.cell_size
          )

          # Reset the game
          self.board = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
          self.canvas.delete("all")
          self.draw_grid()

          self.current_player = 'X'  
          self.game_started = True  
      except ValueError as e:
          messagebox.showerror("Invalid Input", str(e))
  
  def difficulty_depth(self):
        if self.difficulty == "Easy":
            return 2
        elif self.difficulty == "Medium":
            return 3
        elif self.difficulty == "Hard":
            return 4

  def draw_grid(self):
      # Draw horizontal and vertical lines
      for i in range(self.grid_size):
          # Horizontal lines
          y = self.margin + i * self.cell_size
          self.canvas.create_line(
              self.margin,
              y,
              self.margin + self.board_size * self.cell_size,
              y
          )
          # Vertical lines
          x = self.margin + i * self.cell_size
          self.canvas.create_line(
              x,
              self.margin,
              x,
              self.margin + self.board_size * self.cell_size
          )

  def handle_click(self, event):
      if not self.game_started:
          return

      x_click = event.x
      y_click = event.y

      col = round((x_click - self.margin) / self.cell_size)
      row = round((y_click - self.margin) / self.cell_size)

      if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
          exact_x = self.margin + col * self.cell_size
          exact_y = self.margin + row * self.cell_size
          distance = ((x_click - exact_x) ** 2 + (y_click - exact_y) ** 2) ** 0.5
          threshold = self.cell_size / 2

          if distance <= threshold:
              if self.board[row][col] is None:
                  self.board[row][col] = 'X'
                  self.draw_move(row, col, 'X')
                  if self.check_win(row, col):
                      messagebox.showinfo("Game Over", "Human wins!")
                      self.reset_game()
                  elif self.is_board_full():
                      messagebox.showinfo("Game Over", "It's a draw!")
                      self.reset_game()
                  else:
                      self.switch_player()
                      self.ai_move()

  def draw_move(self, row, col, player):
      x = self.margin + col * self.cell_size
      y = self.margin + row * self.cell_size
      radius = self.cell_size // 2 - 8  # Adjust radius for better fit
      color = "black" if player == 'X' else "white"
      outline = "black" if player == 'X' else "gray"
      self.canvas.create_oval(
          x - radius, y - radius,
          x + radius, y + radius,
          fill=color,
          outline=outline
      )

  def switch_player(self):
      self.current_player = 'O' if self.current_player == 'X' else 'X'

  def check_win_condition(self, board):
      for player in ['O', 'X']:
          lines = self.get_all_lines(board)
          target = [player] * 5
          for line in lines:
              for i in range(len(line) - 4):
                  if line[i:i+5] == target:
                      return True
      return False

  def check_win(self, row, col):
      return self.check_win_condition(self.board)

  def get_all_lines(self, board):
      lines = []
      # Rows
      for row in board:
          lines.append(row)
      # Columns
      for col in zip(*board):
          lines.append(list(col))
      # Diagonals
      for p in range(2 * self.grid_size - 1):
          diag1 = []
          diag2 = []
          for q in range(max(p - self.grid_size + 1, 0), min(p + 1, self.grid_size)):
              diag1.append(board[q][p - q])
              diag2.append(board[self.grid_size - 1 - q][p - q])
          lines.append(diag1)
          lines.append(diag2)
      return lines

  def get_possible_moves(self, board):
    moves = set()
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for row in range(self.grid_size):
      for col in range(self.grid_size):
        if board[row][col] is not None:
          for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < self.grid_size and 0 <= c < self.grid_size and board[r][c] is None:
              moves.add((r, c))
    if not moves:
      center = self.grid_size // 2
      return [(center, center)]
    return list(moves)

  def simple_heuristic(self, board):
      score = 0
      # Check all rows, columns, and both diagonals
      lines = self.get_all_lines(board)
      for line in lines:
          if line.count('O') > 0 and line.count('X') == 0:
              score += line.count('O')
          elif line.count('X') > 0 and line.count('O') == 0:
              score -= 2 * line.count('X')
      return score

  def weighted_heuristic(self, board):
    score = 0
    # Define weights for different patterns
    # Offense patterns
    patterns_offense = {
        "five": 100000,
        "open_four": 10000,
        "four": 1000,
        "open_three": 1000,
        "three": 100,
        "open_two": 100,
        "two": 10
    }
    
    # Defense patterns (higher weights to prioritize blocking)
    patterns_defense = {
        "five": 100000,        # Block opponent's five
        "open_four": 15000,    # Block opponent's open four (higher priority)
        "four": 12000,         # Block opponent's four
        "open_three": 8000,    # Block opponent's open three
        "three": 5000,         # Block opponent's three
        "open_two": 2000,      # Block opponent's open two
        "two": 1000            # Block opponent's two
    }
    
    lines = self.get_all_lines(board)
    for line in lines:
        # Offensive evaluation
        score += self.evaluate_line(line, 'O', patterns_offense)
        # Defensive evaluation
        score -= self.evaluate_line(line, 'X', patterns_defense)
    return score


  def evaluate_line(self, line, player, patterns):
      score = 0
      opponent = 'X' if player == 'O' else 'O'
      
      # Convert player symbols to numeric values for pattern matching
      player_val = 2 if player == 'O' else 1
      opponent_val = 1 if player == 'O' else 2
      
      # Transform the line to numeric representation
      transformed_line = [
          player_val if cell == player else 
          opponent_val if cell == opponent else 
          0 for cell in line
      ]
      
      # Define pattern list in order of priority
      pattern_list = [
          ("five", patterns["five"]),
          ("open_four", patterns["open_four"]),
          ("four", patterns["four"]),
          ("open_three", patterns["open_three"]),
          ("three", patterns["three"]),
          ("open_two", patterns["open_two"]),
          ("two", patterns["two"])
      ]
      
      for pattern_name, pattern_score in pattern_list:
          pattern = self.get_pattern(pattern_name, player_val)
          if self._contains_pattern(transformed_line, pattern):
              score += pattern_score
              # Once a pattern is matched, do not count smaller patterns within it
              break
      
      return score

  def get_pattern(self, pattern_name, player_val):
      """Retrieve the numeric pattern based on the pattern name and player value."""
      patterns_numeric = {
          "five": [player_val] * 5,
          "open_four": [0, player_val, player_val, player_val, player_val, 0],
          "four": [player_val, player_val, player_val, player_val],
          "open_three": [0, player_val, player_val, player_val, 0],
          "three": [player_val, player_val, player_val],
          "open_two": [0, player_val, player_val, 0],
          "two": [player_val, player_val]
      }
      return patterns_numeric.get(pattern_name, [])

  def _contains_pattern(self, transformed_line, pattern):
      """Check if the transformed line contains the exact pattern."""
      pattern_length = len(pattern)
      for i in range(len(transformed_line) - pattern_length + 1):
          if transformed_line[i:i + pattern_length] == pattern:
              return True
      return False


  def minimax(self, board, depth, alpha, beta, maximizingPlayer, heuristic):
      if depth == 0 or self.check_win_condition(board):
          return heuristic(board), None

      if maximizingPlayer:
          maxEval = -math.inf
          best_move = None
          for move in self.get_possible_moves(board):
              new_board = copy.deepcopy(board)
              new_board[move[0]][move[1]] = 'O'
              eval, _ = self.minimax(new_board, depth - 1, alpha, beta, False, heuristic)
              if eval > maxEval:
                  maxEval = eval
                  best_move = move
              alpha = max(alpha, eval)
              if beta <= alpha:
                  break
          return maxEval, best_move
      else:
          minEval = math.inf
          best_move = None
          for move in self.get_possible_moves(board):
              new_board = copy.deepcopy(board)
              new_board[move[0]][move[1]] = 'X'
              eval, _ = self.minimax(new_board, depth - 1, alpha, beta, True, heuristic)
              if eval < minEval:
                  minEval = eval
                  best_move = move
              beta = min(beta, eval)
              if beta <= alpha:
                  break
          return minEval, best_move
      
  def is_board_full(self):
    for row in self.board:
      if None in row:
        return False
    return True
  
  def ai_move(self):
      # Choose heuristic: simple_heuristic or weighted_heuristic
      heuristic = self.weighted_heuristic  # Change to self.simple_heuristic if preferred

      # Run minimax to get the best move
      _, move = self.minimax(self.board, depth=self.difficulty_depth(), alpha=-math.inf , beta=math.inf, maximizingPlayer=True, heuristic=heuristic)
      
      if move:
          row, col = move
          self.board[row][col] = 'O'
          self.draw_move(row, col, 'O')
          if self.check_win(row, col):
              messagebox.showinfo("Game Over", "AI (O) wins!")
              self.reset_game()
          elif self.is_board_full():
              messagebox.showinfo("Game Over", "It's a draw!")
              self.reset_game()
          else:
              self.switch_player()

  def reset_game(self):
      self.board = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
      self.canvas.delete("all")
      self.draw_grid()
      self.current_player = 'X'  # Reset to player 'X'

def main():
  root = tk.Tk()
  game = GomokuGUI(root)
  root.mainloop()

if __name__ == "__main__":
  main()

