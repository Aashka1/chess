# Chess Game with Pygame and Stockfish

## Overview
This project is a chess game built using **Pygame** and **python-chess**, integrating the **Stockfish chess engine** for AI gameplay. It features an interactive chessboard, highlights legal moves, detects check/checkmate, and provides a visually appealing user interface with dynamic resizing.

## Features
- **Interactive Chessboard**: Click to select and move pieces.
- **Stockfish AI Integration**: Play against an AI opponent.
- **Dynamic Resizing**: Adjusts board size when the window is resized.
- **Move Highlighting**: Indicates selected squares, legal moves, and check positions.
- **Sidebar Information**: Displays game status and turn information.
- **Basic Error Handling**: Handles missing engine files and image loading errors.

## Installation
### Prerequisites
Ensure you have **Python 3.x** installed along with the following dependencies:
```sh
pip install pygame chess
```

### Stockfish Chess Engine
Stockfish is required for AI moves. Download it from:
- [Stockfish Official Website](https://stockfishchess.org/download/)

Extract the engine and note its path for configuration.

## Running the Game
1. Update the `engine_path` variable in `main()` with the correct path to the Stockfish executable.
2. Run the script:
```sh
python chess_game.py
```

## How to Play
- Click on a piece to select it.
- Click on a highlighted square to move the selected piece.
- The AI will automatically make a move for Black.
- The game ends when checkmate or stalemate occurs.

## File Structure
```
chess_game/
│── images/                # Folder containing chess piece images
│── chess_game.py          # Main script
│── README.md              # Project documentation
```

## Key Components
- **ChessGame Class**: Manages the game logic, rendering, and AI integration.
- **load_piece_images()**: Loads and scales chess piece images.
- **draw_board()**: Draws the chessboard and highlights.
- **handle_events()**: Handles user interactions.
- **ai_move()**: Calls Stockfish to generate AI moves.

## Future Improvements
- Add timer functionality for timed matches.
- Implement undo/redo functionality.
- Enable saving and loading game states.

## Acknowledgments
- **Pygame** for GUI rendering.
- **python-chess** for game logic.
- **Stockfish** for AI opponent.

---
Enjoy playing Chess! ♟️
