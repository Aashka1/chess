import pygame
import chess
import os
import chess.engine  # For using an external chess engine

# --- Initialize Stockfish Engine ---
# Make sure to update the path below to point to your Stockfish binary.
engine_path = "path/to/stockfish"  # e.g., "C:/path/to/stockfish.exe" on Windows
engine = chess.engine.SimpleEngine.popen_uci(engine_path)

# --- Constants and Setup ---

# Increase the width to allow a sidebar scoreboard
BOARD_WIDTH, BOARD_HEIGHT = 800, 800
SIDEBAR_WIDTH = 200
WIDTH, HEIGHT = BOARD_WIDTH + SIDEBAR_WIDTH, BOARD_HEIGHT

SQUARE_SIZE = BOARD_WIDTH // 8

# Colors
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
SIDEBAR_BG = (200, 200, 200)  # light gray for sidebar background

# Piece values for scoring (king value set to 0)
piece_values = {
    'p': 1,
    'n': 3,
    'b': 3,
    'r': 5,
    'q': 9,
    'k': 0
}

# Initial piece counts for a standard chess game
initial_counts = {
    chess.WHITE: {'p': 8, 'n': 2, 'b': 2, 'r': 2, 'q': 1, 'k': 1},
    chess.BLACK: {'p': 8, 'n': 2, 'b': 2, 'r': 2, 'q': 1, 'k': 1}
}

# Designate which side is controlled by AI:
# For example, human plays White, AI plays Black.
ai_color = chess.BLACK

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game with Stockfish AI and Scoreboard")

# Set working directory to script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- Load Piece Images ---
IMAGES = {}
pieces = ['p', 'n', 'b', 'r', 'q', 'k']
for piece in pieces:
    for color in ['w', 'b']:
        image_path = os.path.join("images", f"{piece}{color}.png")
        try:
            image = pygame.image.load(image_path)
            image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
            IMAGES[piece + color] = image
            print(f"Loaded image for {piece + color} from {image_path}")
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")

print("Loaded image keys:", list(IMAGES.keys()))

# --- Drawing Functions ---

def draw_board(screen):
    # Draw the 8x8 board in the left portion of the window
    for row in range(8):
        for col in range(8):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

def draw_pieces(screen, board):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
            # Construct the key for the image (e.g., 'rw' for white rook)
            piece_key = piece.symbol().lower() + ('w' if piece.color == chess.WHITE else 'b')
            if piece_key in IMAGES:
                screen.blit(IMAGES[piece_key],
                            pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE,
                                        SQUARE_SIZE, SQUARE_SIZE))
            else:
                print(f"KeyError: No image found for key '{piece_key}'")

def draw_sidebar(screen, board, font):
    """Draw the scoreboard sidebar showing captured pieces and scores."""
    # Draw sidebar background
    sidebar_rect = pygame.Rect(BOARD_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT)
    pygame.draw.rect(screen, SIDEBAR_BG, sidebar_rect)

    # Compute current piece counts for both sides
    current_counts = {
        chess.WHITE: {'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0},
        chess.BLACK: {'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0}
    }
    for piece in board.piece_map().values():
        key = piece.symbol().lower()
        side = chess.WHITE if piece.color == chess.WHITE else chess.BLACK
        current_counts[side][key] += 1

    # Compute captured pieces for each side
    captured = {chess.WHITE: {}, chess.BLACK: {}}
    scores = {chess.WHITE: 0, chess.BLACK: 0}
    for side in [chess.WHITE, chess.BLACK]:
        for key in initial_counts[side]:
            lost = initial_counts[side][key] - current_counts[side][key]
            captured[side][key] = lost
            scores[side] += lost * piece_values[key]

    # Display the scoreboard.
    x_text = BOARD_WIDTH + 10  # padding from left edge of sidebar
    y_text = 20
    line_spacing = 30

    # Title
    title = font.render("Scoreboard", True, (0, 0, 0))
    screen.blit(title, (x_text, y_text))
    y_text += line_spacing * 2

    # Display for White:
    white_title = font.render("White Lost:", True, (0, 0, 0))
    screen.blit(white_title, (x_text, y_text))
    y_text += line_spacing
    for key, count in captured[chess.WHITE].items():
        if count > 0:
            text = font.render(f"{key.upper()}: {count}", True, (0, 0, 0))
            screen.blit(text, (x_text, y_text))
            y_text += line_spacing
    white_score_text = font.render(f"Score: {scores[chess.WHITE]}", True, (0, 0, 0))
    screen.blit(white_score_text, (x_text, y_text))
    y_text += line_spacing * 2

    # Display for Black:
    black_title = font.render("Black Lost:", True, (0, 0, 0))
    screen.blit(black_title, (x_text, y_text))
    y_text += line_spacing
    for key, count in captured[chess.BLACK].items():
        if count > 0:
            text = font.render(f"{key.upper()}: {count}", True, (0, 0, 0))
            screen.blit(text, (x_text, y_text))
            y_text += line_spacing
    black_score_text = font.render(f"Score: {scores[chess.BLACK]}", True, (0, 0, 0))
    screen.blit(black_score_text, (x_text, y_text))

def get_square_under_mouse():
    x, y = pygame.mouse.get_pos()
    if x < BOARD_WIDTH and y < BOARD_HEIGHT:
        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE
        return chess.square(col, 7 - row)
    return None

# --- Main Game Loop ---

def main():
    clock = pygame.time.Clock()
    board = chess.Board()  # starting position
    selected_square = None
    pending_promotion = None
    font = pygame.font.SysFont("Arial", 20)

    while True:
        # Process events for human moves only when it's not AI's turn.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            # Only process human input if it's human's turn (not AI's turn)
            if board.turn != ai_color:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pending_promotion:
                        continue  # ignore clicks during promotion
                    square = get_square_under_mouse()
                    if square is not None:
                        if selected_square == square:
                            selected_square = None  # deselect if clicking same square
                        elif selected_square is not None:
                            move = chess.Move(selected_square, square)
                            piece = board.piece_at(selected_square)
                            # Check for pawn promotion conditions:
                            if piece and piece.piece_type == chess.PAWN:
                                target_rank = chess.square_rank(square)
                                if (piece.color == chess.WHITE and target_rank == 7) or \
                                   (piece.color == chess.BLACK and target_rank == 0):
                                    pending_promotion = move
                                    selected_square = None
                                    continue
                            if move in board.legal_moves:
                                board.push(move)
                                selected_square = None
                        else:
                            piece = board.piece_at(square)
                            if piece and piece.color == board.turn:
                                selected_square = square

                elif event.type == pygame.KEYDOWN and pending_promotion:
                    promotion_piece = None
                    if event.key == pygame.K_q:
                        promotion_piece = chess.QUEEN
                    elif event.key == pygame.K_r:
                        promotion_piece = chess.ROOK
                    elif event.key == pygame.K_b:
                        promotion_piece = chess.BISHOP
                    elif event.key == pygame.K_n:
                        promotion_piece = chess.KNIGHT
                    if promotion_piece:
                        move = pending_promotion
                        move.promotion = promotion_piece
                        if move in board.legal_moves:
                            board.push(move)
                        pending_promotion = None

        # --- AI Move ---
        # If it's the AI's turn, let Stockfish choose and play a move.
        if board.turn == ai_color and not board.is_game_over() and not pending_promotion:
            # Optional: add a short delay to simulate "thinking"
            pygame.time.delay(500)
            # Use the engine to get the best move; adjust the time limit as needed.
            result = engine.play(board, chess.engine.Limit(time=0.1))
            board.push(result.move)
            # Reset any selection (in case human had selected a piece)
            selected_square = None

        # --- Drawing ---
        # Clear screen
        screen.fill((255, 255, 255))
        # Draw the board and pieces
        draw_board(screen)
        draw_pieces(screen, board)

        # Highlight selected square and legal moves (only for human moves)
        if selected_square is not None:
            col = chess.square_file(selected_square)
            row = 7 - chess.square_rank(selected_square)
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(pygame.Color("blue"))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            for move in board.legal_moves:
                if move.from_square == selected_square:
                    col = chess.square_file(move.to_square)
                    row = 7 - chess.square_rank(move.to_square)
                    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                    s.set_alpha(100)
                    s.fill(pygame.Color("green"))
                    screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        # Highlight king in check
        if board.is_check():
            king_square = board.king(board.turn)
            if king_square is not None:
                col = chess.square_file(king_square)
                row = 7 - chess.square_rank(king_square)
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                s.set_alpha(100)
                s.fill(pygame.Color("red"))
                screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        # Show promotion prompt if needed
        if pending_promotion:
            promo_text = font.render("Select promotion: Q, R, B, N", True, (0, 0, 0))
            text_rect = promo_text.get_rect(center=(BOARD_WIDTH // 2, BOARD_HEIGHT // 2))
            screen.blit(promo_text, text_rect)

        # Draw game over message if needed
        if board.is_game_over():
            result_text = "1/2-1/2" if board.is_stalemate() else board.result()
            game_over_text = font.render(f"Game Over: {result_text}", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(BOARD_WIDTH // 2, BOARD_HEIGHT // 2))
            screen.blit(game_over_text, text_rect)

        # Draw the scoreboard sidebar
        draw_sidebar(screen, board, font)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    try:
        main()
    finally:
        # Shut down the engine when the game is closed.
        engine.quit()
        pygame.quit()
