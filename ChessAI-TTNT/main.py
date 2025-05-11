import sys
import pygame
import board
import pieces
import ai
from move import Move
from button import Button

# Khởi tạo Pygame
pygame.init()
pygame.mixer.init()

# Tải âm thanh
move_sound = pygame.mixer.Sound("sound/standard/move-self.mp3")
check_sound = pygame.mixer.Sound("sound/standard/move-check.mp3")
loss_sound = pygame.mixer.Sound("sound/standard/game-lose-long.mp3")
win_sound = pygame.mixer.Sound("sound/standard/game-win-long.mp3")
click_sound = pygame.mixer.Sound("sound/standard/click.mp3")

# Thiết lập cửa sổ
WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 8
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()

# Ảnh nền menu
BG = pygame.image.load("images/chess_menu.png")

# Hàm lấy font
def get_font(size):
    return pygame.font.Font("images/font.ttf", size)

# Màu sắc
YELLOW = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (125, 125, 125)
GREEN = (0, 255, 0)

# Tải và scale ảnh quân cờ
piece_images = {
    'WP': pygame.transform.scale(pygame.image.load('images/WP.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'WR': pygame.transform.scale(pygame.image.load('images/WR.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'WN': pygame.transform.scale(pygame.image.load('images/WN.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'WB': pygame.transform.scale(pygame.image.load('images/WB.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'WQ': pygame.transform.scale(pygame.image.load('images/WQ.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'WK': pygame.transform.scale(pygame.image.load('images/WK.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'BP': pygame.transform.scale(pygame.image.load('images/BP.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'BR': pygame.transform.scale(pygame.image.load('images/BR.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'BN': pygame.transform.scale(pygame.image.load('images/BN.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'BB': pygame.transform.scale(pygame.image.load('images/BB.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'BQ': pygame.transform.scale(pygame.image.load('images/BQ.png'), (SQUARE_SIZE, SQUARE_SIZE)),
    'BK': pygame.transform.scale(pygame.image.load('images/BK.png'), (SQUARE_SIZE, SQUARE_SIZE))
}

# Hàm kiểm tra vua còn trên bàn cờ
def is_king_captured(chessboard, color):
    for row in chessboard.chesspieces:
        for piece in row:
            if piece != 0 and piece.color == color and piece.piece_type == 'K':
                return False
    return True

# Hàm vẽ bàn cờ với surface riêng
def draw_board(chessboard, selected=None, possible_moves=None, moving_piece_pos=None, additional_moving_pos=None, board_surface=None):
    if board_surface is None:
        board_surface = pygame.Surface((WIDTH, HEIGHT))
    
    board_surface.fill(BLACK)
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else GRAY
            pygame.draw.rect(board_surface, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = chessboard.chesspieces[col][row]
            if piece != 0:
                if (moving_piece_pos and col == moving_piece_pos[0] and row == moving_piece_pos[1]) or \
                   (additional_moving_pos and col == additional_moving_pos[0] and row == additional_moving_pos[1]):
                    continue
                key = piece.color + piece.piece_type
                board_surface.blit(piece_images[key], (col * SQUARE_SIZE, row * SQUARE_SIZE))
    
    if selected:
        pygame.draw.rect(board_surface, GREEN, (selected[0] * SQUARE_SIZE, selected[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
    
    if possible_moves:
        for move in possible_moves:
            pygame.draw.rect(board_surface, YELLOW, (move.xto * SQUARE_SIZE, move.yto * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
    
    screen.blit(board_surface, (0, 0))
    return board_surface

# Hàm xử lý hoạt hình di chuyển
def animate_move(chessboard, move, piece, board_surface):
    frames = 30
    piece_image = piece_images[piece.color + piece.piece_type]
    x_start, y_start = move.xfrom * SQUARE_SIZE, move.yfrom * SQUARE_SIZE
    x_end, y_end = move.xto * SQUARE_SIZE, move.yto * SQUARE_SIZE

    # Kiểm tra bắt qua đường
    is_en_passant = (piece.piece_type == 'P' and move.xto != move.xfrom and 
                     chessboard.get_piece(move.xto, move.yto) == 0)
    captured_piece_pos = (move.xto, move.yfrom) if is_en_passant else None

    # Kiểm tra nhập thành
    is_castling = piece.piece_type == 'K' and abs(move.xto - move.xfrom) == 2
    rook_image = rook_x_start = rook_y_start = rook_x_end = rook_y_end = rook_pos = None

    if is_castling:
        if move.xto > move.xfrom:
            rook = chessboard.get_piece(move.xto + 1, move.yfrom)
            rook_x_start = (move.xto + 1) * SQUARE_SIZE
            rook_x_end = (move.xto - 1) * SQUARE_SIZE
            rook_pos = (move.xto + 1, move.yfrom)
        else:
            rook = chessboard.get_piece(move.xto - 2, move.yfrom)
            rook_x_start = (move.xto - 2) * SQUARE_SIZE
            rook_x_end = (move.xto + 1) * SQUARE_SIZE
            rook_pos = (move.xto - 2, move.yfrom)
        rook_y_start = rook_y_end = move.yfrom * SQUARE_SIZE
        rook_image = piece_images[rook.color + rook.piece_type] if rook else None

    for i in range(frames + 1):
        t = i / frames
        eased_t = t * t * (3 - 2 * t)
        x = x_start + (x_end - x_start) * eased_t
        y = y_start + (y_end - y_start) * eased_t

        screen.fill(BLACK)
        draw_board(chessboard, moving_piece_pos=(move.xfrom, move.yfrom), 
                  additional_moving_pos=rook_pos or captured_piece_pos, board_surface=board_surface)
        screen.blit(piece_image, (x, y))
        if is_castling and rook_image:
            rook_x = rook_x_start + (rook_x_end - rook_x_start) * eased_t
            screen.blit(rook_image, (rook_x, rook_y_start))

        pygame.display.flip()
        clock.tick(FPS)

    try:
        chessboard.perform_move(move)
    except AttributeError as e:
        print(f"Error in perform_move: {e}")
        raise

# Hàm giao diện game over
def game_over_screen(text):
    font_big = get_font(45)
    text_surf = font_big.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))

    buttons = [
        Button(None, (WIDTH // 2, HEIGHT // 2 + 20), "PLAY AGAIN", get_font(20), "#d7dcd4", "white"),
        Button(None, (WIDTH // 2, HEIGHT // 2 + 100), "QUIT", get_font(20), "#d7dcd4", "white")
    ]

    while True:
        screen.fill(BLACK)
        screen.blit(text_surf, text_rect)
        mouse_pos = pygame.mouse.get_pos()

        for btn in buttons:
            btn.changeColor(mouse_pos)
            btn.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].checkForInput(mouse_pos):
                    click_sound.play()
                    return True
                if buttons[1].checkForInput(mouse_pos):
                    click_sound.play()
                    return False

        pygame.display.flip()
        clock.tick(FPS)

# Hàm giao diện menu
def menu():
    board_surface = pygame.Surface((WIDTH, HEIGHT))
    buttons = [
        Button(pygame.image.load("images/game_button.png"), (395, 350), "PLAY", get_font(25), "black", "White"),
        Button(pygame.image.load("images/game_button.png"), (395, 500), "OPTION", get_font(25), "black", "White"),
        Button(pygame.image.load("images/game_button.png"), (395, 650), "QUIT", get_font(25), "black", "White")
    ]

    while True:
        screen.blit(BG, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        for button in buttons:
            button.changeColor(mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].checkForInput(mouse_pos):
                    click_sound.play()
                    main_game(board_surface)
                elif buttons[2].checkForInput(mouse_pos):
                    click_sound.play()
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

# Hàm chính của trò chơi
def main_game(board_surface):
    chessboard = board.Board.new()
    selected = None
    possible_moves = None
    game_over = False
    result_text = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                col, row = x // SQUARE_SIZE, y // SQUARE_SIZE
                
                if selected is None:
                    piece = chessboard.get_piece(col, row)
                    if piece != 0 and piece.color == pieces.Piece.WHITE:
                        selected = (col, row)
                        possible_moves = chessboard.get_possible_moves(pieces.Piece.WHITE)
                        possible_moves = [m for m in possible_moves if m.xfrom == col and m.yfrom == row]
                else:
                    # Kiểm tra bắt qua đường để truyền captured_piece
                    moving_piece = chessboard.get_piece(selected[0], selected[1])
                    captured_piece = None
                    if (moving_piece.piece_type == 'P' and col != selected[0] and 
                        chessboard.get_piece(col, row) == 0):
                        captured_piece = chessboard.get_piece(col, selected[1])
                    
                    # Giả định Move hỗ trợ captured_piece, nếu không thì bỏ tham số này
                    try:
                        move = Move(selected[0], selected[1], col, row, captured_piece=captured_piece)
                    except TypeError:
                        move = Move(selected[0], selected[1], col, row)

                    for possible_move in possible_moves:
                        if move.equals(possible_move):
                            try:
                                animate_move(chessboard, move, moving_piece, board_surface)
                                move_sound.play()
                                selected = None
                                possible_moves = None

                                if is_king_captured(chessboard, pieces.Piece.BLACK):
                                    result_text = "YOU WIN"
                                    game_over = True
                                    win_sound.play()
                                    break

                                ai_move = ai.AI.get_ai_move(chessboard, [])
                                if ai_move == 0:
                                    if chessboard.is_check(pieces.Piece.BLACK):
                                        result_text = "YOU WIN"
                                    else:
                                        result_text = "STALEMATE"
                                    game_over = True
                                    win_sound.play()
                                else:
                                    ai_moving_piece = chessboard.get_piece(ai_move.xfrom, ai_move.yfrom)
                                    # Kiểm tra bắt qua đường cho AI
                                    try:
                                        ai_move.captured_piece = None
                                        if (ai_moving_piece.piece_type == 'P' and ai_move.xto != ai_move.xfrom and 
                                            chessboard.get_piece(ai_move.xto, ai_move.yto) == 0):
                                            ai_move.captured_piece = chessboard.get_piece(ai_move.xto, ai_move.yfrom)
                                    except AttributeError:
                                        pass  # Nếu Move không hỗ trợ captured_piece, bỏ qua
                                    
                                    animate_move(chessboard, ai_move, ai_moving_piece, board_surface)
                                    move_sound.play()

                                if is_king_captured(chessboard, pieces.Piece.WHITE):
                                    result_text = "YOU LOSE"
                                    game_over = True
                                    loss_sound.play()
                            except Exception as e:
                                print(f"Error during move: {e}")
                                result_text = "ERROR OCCURRED"
                                game_over = True
                            break
                    else:
                        selected = None
                        possible_moves = None

            if game_over:
                should_restart = game_over_screen(result_text)
                if should_restart:
                    main_game(board_surface)
                else:
                    menu()

        screen.fill(BLACK)
        board_surface = draw_board(chessboard, selected, possible_moves, board_surface=board_surface)
        pygame.display.flip()
        clock.tick(FPS)

# Hàm main
def main():
    menu()

if __name__ == "__main__":
    main()