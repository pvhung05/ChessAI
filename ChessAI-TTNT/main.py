import pygame
import board
import pieces
import ai
from move import Move
import math

# Khởi tạo Pygame
pygame.init()

# Thiết lập cửa sổ
WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 8
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()

# Màu sắc
YELLOW = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (125, 125, 125)
GREEN = (0, 255, 0)

# Tạo surface cho quân cờ
piece_images = {
    'WP': pygame.image.load('images/WP.png'), 
    'WR': pygame.image.load('images/WR.png'),  
    'WN': pygame.image.load('images/WN.png'),  
    'WB': pygame.image.load('images/WB.png'),  
    'WQ': pygame.image.load('images/WQ.png'), 
    'WK': pygame.image.load('images/WK.png'), 
    'BP': pygame.image.load('images/BP.png'),  
    'BR': pygame.image.load('images/BR.png'),  
    'BN': pygame.image.load('images/BN.png'), 
    'BB': pygame.image.load('images/BB.png'),  
    'BQ': pygame.image.load('images/BQ.png'), 
    'BK': pygame.image.load('images/BK.png')  
}

# Scale ảnh
for key in piece_images:
    piece_images[key] = pygame.transform.scale(piece_images[key], (SQUARE_SIZE, SQUARE_SIZE))

# Hàm kiểm tra xem vua còn trên bàn cờ không
def is_king_captured(chessboard, color):
    for row in chessboard.chesspieces:
        for piece in row:
            if piece != 0 and piece.color == color and piece.piece_type == 'K':
                return False
    return True

# Hàm vẽ bàn cờ và quân cờ với khả năng bỏ qua quân cờ đang di chuyển
def draw_board(chessboard, selected=None, possible_moves=None, moving_piece_pos=None):
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else GRAY
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = chessboard.chesspieces[col][row]
            # Bỏ qua vẽ quân cờ nếu nó đang di chuyển
            if piece != 0 and (moving_piece_pos is None or (col != moving_piece_pos[0] or row != moving_piece_pos[1])):
                key = piece.color + piece.piece_type
                screen.blit(piece_images[key], (col * SQUARE_SIZE, row * SQUARE_SIZE))
    
    if selected:
        pygame.draw.rect(screen, GREEN, (selected[0] * SQUARE_SIZE, selected[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
    
    if possible_moves:
        for move in possible_moves:
            pygame.draw.rect(screen, YELLOW, (move.xto * SQUARE_SIZE, move.yto * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

# Hàm animate_move sửa lại để tránh lỗi
def animate_move(chessboard, move, piece):
    frames = 30
    piece_image = piece_images[piece.color + piece.piece_type]
    x_start, y_start = move.xfrom * SQUARE_SIZE, move.yfrom * SQUARE_SIZE
    x_end, y_end = move.xto * SQUARE_SIZE, move.yto * SQUARE_SIZE

    for i in range(frames + 1):
        t = i / frames
        eased_t = t * t * (3 - 2 * t)  # Ease in-out

        x = x_start + (x_end - x_start) * eased_t
        y = y_start + (y_end - y_start) * eased_t

        screen.fill(BLACK)
        # Không vẽ quân cờ ở vị trí ban đầu trong quá trình di chuyển
        draw_board(chessboard, moving_piece_pos=(move.xfrom, move.yfrom))
        screen.blit(piece_image, (x, y))  # Vẽ quân cờ đang di chuyển
        pygame.display.flip()
        clock.tick(FPS)

    # Sau khi animation hoàn tất, thực hiện nước đi
    try:
        chessboard.perform_move(move)
    except Exception as e:
        print(f"Error in perform_move: {e}")
        raise

# Hàm main
def main():
    chessboard = board.Board.new()
    running = True
    selected = None
    possible_moves = None
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                col, row = x // SQUARE_SIZE, y // SQUARE_SIZE
                print(f"Clicked at ({col}, {row})")
                
                if selected is None:
                    piece = chessboard.get_piece(col, row)
                    if piece != 0 and piece.color == pieces.Piece.WHITE:
                        selected = (col, row)
                        possible_moves = chessboard.get_possible_moves(pieces.Piece.WHITE)
                        possible_moves = [m for m in possible_moves if m.xfrom == col and m.yfrom == row]
                        print(f"Selected piece at ({col}, {row})")
                        print(f"Possible moves: {[m.to_string() for m in possible_moves]}")
                else:
                    move = Move(selected[0], selected[1], col, row)
                    for possible_move in possible_moves:
                        if move.equals(possible_move):
                            moving_piece = chessboard.get_piece(selected[0], selected[1])
                            try:
                                animate_move(chessboard, move, moving_piece)
                                print("User move: " + move.to_string())
                                selected = None
                                possible_moves = None

                                if is_king_captured(chessboard, pieces.Piece.BLACK):
                                    print("Checkmate! White wins.")
                                    game_over = True
                                    break

                                ai_move = ai.AI.get_ai_move(chessboard, [])
                                if ai_move == 0:
                                    if chessboard.is_check(pieces.Piece.BLACK):
                                        print("Checkmate. White wins.")
                                    else:
                                        print("Stalemate.")
                                    game_over = True
                                else:
                                    moving_piece = chessboard.get_piece(ai_move.xfrom, ai_move.yfrom)
                                    animate_move(chessboard, ai_move, moving_piece)
                                    print("AI move: " + ai_move.to_string())

                                if is_king_captured(chessboard, pieces.Piece.WHITE):
                                    print("Checkmate! Black wins.")
                                    game_over = True
                            except Exception as e:
                                print(f"Error during move: {e}")
                                running = False
                            break
                    else:
                        print("Invalid move, resetting selection.")
                        selected = None
                        possible_moves = None

        screen.fill(BLACK)
        draw_board(chessboard, selected, possible_moves)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    print("Game ended.")

if __name__ == "__main__":
    main()