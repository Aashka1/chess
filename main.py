import pygame
import chess
import chess.engine
import os
import sys

# --- Configuration ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800  # Wider screen to accommodate more elements
BOARD_SIZE = 700  # Adjustable board size
SQUARE_SIZE = BOARD_SIZE // 8
SIDEBAR_WIDTH = 300

# Color Palette
COLORS = {
    'LIGHT_SQUARE': (240, 217, 181),  # Warm light brown
    'DARK_SQUARE': (181, 136, 99),    # Warm dark brown
    'BACKGROUND': (50, 50, 50),       # Dark gray background
    'SIDEBAR_BG': (70, 70, 70),       # Slightly lighter dark gray
    'TEXT_COLOR': (220, 220, 220),    # Light gray text
    'HIGHLIGHT_SELECTED': (100, 149, 237, 128),  # Cornflower blue with transparency
    'HIGHLIGHT_LEGAL_MOVE': (34, 139, 34, 100),  # Forest green with transparency
    'HIGHLIGHT_CHECK': (255, 0, 0, 100)  # Transparent red
}

# Piece values for scoring
PIECE_VALUES = {
    'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0
}

class ChessGame:
    def __init__(self, engine_path):
        # Initialize Pygame and game components
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Enhanced Chess")
        
        # Game state
        self.board = chess.Board()
        self.selected_square = None
        self.pending_promotion = None
        self.game_over = False
        
        # Engine setup
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        except Exception as e:
            print(f"Error loading Stockfish: {e}")
            pygame.quit()
            sys.exit(1)
        
        # Load fonts
        self.title_font = pygame.font.Font(None, 36)
        self.info_font = pygame.font.Font(None, 24)
        
        # Load piece images
        self.load_piece_images()
        
        # Game clock
        self.clock = pygame.time.Clock()
        
        # Compute dynamic sizing
        self.compute_layout()
    
    def compute_layout(self):
        """Compute dynamic layout based on screen size"""
        # Adjust board and sidebar sizes based on screen dimensions
        self.board_rect = pygame.Rect(
            (SCREEN_WIDTH - BOARD_SIZE - SIDEBAR_WIDTH) // 2, 
            (SCREEN_HEIGHT - BOARD_SIZE) // 2, 
            BOARD_SIZE, 
            BOARD_SIZE
        )
        self.sidebar_rect = pygame.Rect(
            self.board_rect.right, 
            0, 
            SIDEBAR_WIDTH, 
            SCREEN_HEIGHT
        )
        
        # Recompute square size
        global SQUARE_SIZE
        SQUARE_SIZE = BOARD_SIZE // 8
        
        # Rescale piece images
        self.rescale_piece_images()
    
    def load_piece_images(self):
        """Load piece images with error handling"""
        self.piece_images = {}
        pieces = ['p', 'n', 'b', 'r', 'q', 'k']
        colors = ['w', 'b']
        
        for piece in pieces:
            for color in colors:
                try:
                    path = os.path.join("images", f"{piece}{color}.png")
                    image = pygame.image.load(path)
                    self.piece_images[piece + color] = image
                except Exception as e:
                    print(f"Could not load image {path}: {e}")
        
    def rescale_piece_images(self):
        """Rescale piece images to current square size"""
        self.scaled_piece_images = {}
        for key, image in self.piece_images.items():
            self.scaled_piece_images[key] = pygame.transform.scale(
                image, (SQUARE_SIZE, SQUARE_SIZE)
            )
    
    def draw_board(self):
        """Draw the chessboard with enhanced visuals"""
        # Draw board background
        pygame.draw.rect(self.screen, COLORS['BACKGROUND'], 
                         (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Draw chess board
        for row in range(8):
            for col in range(8):
                color = (COLORS['LIGHT_SQUARE'] if (row + col) % 2 == 0 
                         else COLORS['DARK_SQUARE'])
                rect = pygame.Rect(
                    self.board_rect.x + col * SQUARE_SIZE, 
                    self.board_rect.y + row * SQUARE_SIZE, 
                    SQUARE_SIZE, 
                    SQUARE_SIZE
                )
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLORS['BACKGROUND'], rect, 1)
    
    def draw_pieces(self):
        """Draw chess pieces on the board"""
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square)
                piece_key = piece.symbol().lower() + ('w' if piece.color == chess.WHITE else 'b')
                
                pos = (
                    self.board_rect.x + col * SQUARE_SIZE, 
                    self.board_rect.y + row * SQUARE_SIZE
                )
                
                if piece_key in self.scaled_piece_images:
                    self.screen.blit(self.scaled_piece_images[piece_key], pos)
    
    def draw_sidebar(self):
        """Enhanced sidebar with game information"""
        # Sidebar background
        pygame.draw.rect(self.screen, COLORS['SIDEBAR_BG'], self.sidebar_rect)
        
        # Title
        title = self.title_font.render("Chess Companion", True, COLORS['TEXT_COLOR'])
        title_rect = title.get_rect(centerx=self.sidebar_rect.centerx, top=20)
        self.screen.blit(title, title_rect)
        
        # Game status
        status_text = "White's Turn" if self.board.turn == chess.WHITE else "Black's Turn"
        if self.board.is_check():
            status_text += " (Check!)"
        status = self.info_font.render(status_text, True, COLORS['TEXT_COLOR'])
        status_rect = status.get_rect(centerx=self.sidebar_rect.centerx, top=title_rect.bottom + 20)
        self.screen.blit(status, status_rect)
    
    def handle_events(self):
        """Process game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.VIDEORESIZE:
                # Handle window resizing
                SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                self.compute_layout()
            
            if self.board.turn == chess.WHITE and not self.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.board_rect.collidepoint(mouse_pos):
                        square = self.get_square_under_mouse(mouse_pos)
                        self.handle_square_selection(square)
        
        return True
    
    def get_square_under_mouse(self, mouse_pos):
        """Convert mouse position to chess square"""
        x = (mouse_pos[0] - self.board_rect.x) // SQUARE_SIZE
        y = 7 - ((mouse_pos[1] - self.board_rect.y) // SQUARE_SIZE)
        return chess.square(x, y)
    
    def handle_square_selection(self, square):
        """Handle square selection logic"""
        if self.pending_promotion:
            return
        
        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                self.selected_square = square
        else:
            move = chess.Move(self.selected_square, square)
            
            # Handle promotion
            piece = self.board.piece_at(self.selected_square)
            if piece and piece.piece_type == chess.PAWN:
                target_rank = chess.square_rank(square)
                if (piece.color == chess.WHITE and target_rank == 7) or \
                   (piece.color == chess.BLACK and target_rank == 0):
                    self.pending_promotion = move
                    self.selected_square = None
                    return
            
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None
                
                # Trigger AI move
                self.ai_move()
            else:
                # Reset selection if move is illegal
                self.selected_square = None
    
    def ai_move(self):
        """AI move using Stockfish"""
        if self.board.turn == chess.BLACK and not self.board.is_game_over():
            result = self.engine.play(self.board, chess.engine.Limit(time=0.1))
            self.board.push(result.move)
    
    def draw_highlights(self):
        """Draw board highlights for selected square and legal moves"""
        if self.selected_square is not None:
            # Highlight selected square
            col = chess.square_file(self.selected_square)
            row = 7 - chess.square_rank(self.selected_square)
            
            highlight_rect = pygame.Rect(
                self.board_rect.x + col * SQUARE_SIZE,
                self.board_rect.y + row * SQUARE_SIZE,
                SQUARE_SIZE, SQUARE_SIZE
            )
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill(COLORS['HIGHLIGHT_SELECTED'])
            self.screen.blit(s, highlight_rect)
            
            # Highlight legal moves
            for move in self.board.legal_moves:
                if move.from_square == self.selected_square:
                    col = chess.square_file(move.to_square)
                    row = 7 - chess.square_rank(move.to_square)
                    
                    legal_move_rect = pygame.Rect(
                        self.board_rect.x + col * SQUARE_SIZE,
                        self.board_rect.y + row * SQUARE_SIZE,
                        SQUARE_SIZE, SQUARE_SIZE
                    )
                    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    s.fill(COLORS['HIGHLIGHT_LEGAL_MOVE'])
                    self.screen.blit(s, legal_move_rect)
        
        # Highlight king in check
        if self.board.is_check():
            king_square = self.board.king(self.board.turn)
            if king_square is not None:
                col = chess.square_file(king_square)
                row = 7 - chess.square_rank(king_square)
                
                check_rect = pygame.Rect(
                    self.board_rect.x + col * SQUARE_SIZE,
                    self.board_rect.y + row * SQUARE_SIZE,
                    SQUARE_SIZE, SQUARE_SIZE
                )
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill(COLORS['HIGHLIGHT_CHECK'])
                self.screen.blit(s, check_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            
            # Drawing
            self.screen.fill(COLORS['BACKGROUND'])
            self.draw_board()
            self.draw_pieces()
            self.draw_highlights()
            self.draw_sidebar()
            
            # Game over check
            if self.board.is_game_over():
                self.game_over = True
                result_text = "Draw" if self.board.is_stalemate() else f"{'White' if self.board.turn == chess.BLACK else 'Black'} Wins"
                result_surface = self.title_font.render(result_text, True, COLORS['TEXT_COLOR'])
                result_rect = result_surface.get_rect(
                    centerx=self.screen.get_width() // 2, 
                    centery=self.screen.get_height() // 2
                )
                self.screen.blit(result_surface, result_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        # Clean up
        self.engine.quit()
        pygame.quit()

def main():
    # Update this path to your Stockfish engine location
    engine_path = "/path/to/stockfish"  # Replace with actual path
    
    try:
        game = ChessGame(engine_path)
        game.run()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
