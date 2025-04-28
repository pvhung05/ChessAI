import sys

import pygame
import board
import pieces
import ai
from move import Move
import math
from button import Button

# Khởi tạo Pygame
pygame.init()
pygame.mixer.init()

#Tải âm thanh
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

#Thêm ảnh nền menu
BG = pygame.image.load("images/chess_menu.png")

def get_font(size):
    return pygame.font.Font("images/font.ttf", size)


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
def draw_board(chessboard, selected=None, possible_moves=None, moving_piece_pos=None, additional_moving_pos=None):
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else GRAY
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = chessboard.chesspieces[col][row]
            # Bỏ qua vẽ quân cờ nếu nó đang di chuyển (vua hoặc xe)
            if piece != 0:
                # Kiểm tra xem ô này có phải là vị trí đang di chuyển không
                if (moving_piece_pos and col == moving_piece_pos[0] and row == moving_piece_pos[1]) or \
                   (additional_moving_pos and col == additional_moving_pos[0] and row == additional_moving_pos[1]):
                    continue  # Bỏ qua ô này nếu là vị trí của vua hoặc xe đang di chuyển
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

    # Kiểm tra bắt qua đường
    is_en_passant = (piece.piece_type == 'P' and move.xto != move.xfrom and 
                     chessboard.get_piece(move.xto, move.yto) == 0)
    captured_piece_pos = None
    if is_en_passant:
        captured_piece_pos = (move.xto, move.yfrom)  # Vị trí quân tốt bị bắt

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
        rook_image = piece_images[rook.color + rook.piece_type]

    for i in range(frames + 1):
        t = i / frames
        eased_t = t * t * (3 - 2 * t)
        x = x_start + (x_end - x_start) * eased_t
        y = y_start + (y_end - y_start) * eased_t

        screen.fill(BLACK)
        if is_castling and rook_pos:
            draw_board(chessboard, moving_piece_pos=(move.xfrom, move.yfrom), additional_moving_pos=rook_pos)
        elif is_en_passant and captured_piece_pos:
            draw_board(chessboard, moving_piece_pos=(move.xfrom, move.yfrom), additional_moving_pos=captured_piece_pos)
        else:
            draw_board(chessboard, moving_piece_pos=(move.xfrom, move.yfrom))

        screen.blit(piece_image, (x, y))
        if is_castling and rook_image:
            rook_x = rook_x_start + (rook_x_end - rook_x_start) * eased_t
            screen.blit(rook_image, (rook_x, rook_y_start))

        pygame.display.flip()
        clock.tick(FPS)

    chessboard.perform_move(move)

#Hàm game_over
def game_over_screen(text):
    font_big = get_font(45)
    text_surf = font_big.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))

    #Tạo nút
    PLAY_AGAIN = Button(image=None, pos = (WIDTH//2, HEIGHT//2 + 20), text_input="PLAY AGAIN",
                        font = get_font(20), base_color="#d7dcd4", hovering_color="white")
    QUIT = Button(image=None, pos = (WIDTH//2, HEIGHT//2 + 100), text_input="QUIT",
                  font = get_font(20), base_color="#d7dcd4",hovering_color="white")

    #Vong lap
    while True:
        screen.fill(BLACK)
        screen.blit(text_surf, text_rect)

        mouse_pos = pygame.mouse.get_pos()

        for btn in (PLAY_AGAIN, QUIT):
            btn.changeColor(mouse_pos)
            btn.update(screen)

        for event in pygame.event.get():
            if(event.type == QUIT):
                pygame.quit()
                sys.exit()
            if(event.type==pygame.MOUSEBUTTONDOWN):
                if(PLAY_AGAIN.checkForInput(mouse_pos)):
                    click_sound.play()
                    return True
                if(QUIT.checkForInput(mouse_pos)):
                    click_sound.play()
                    return False
        pygame.display.update()
        clock.tick(FPS)
def menu():
    while True:
        screen.blit(BG, (0, 0))
        # Lấy vị trí con chuột
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        # Xét nút
        PLAY_BUTTON = Button(image=pygame.image.load("images/game_button.png"), pos=(395,350),
                             text_input="PLAY", font=get_font(25),base_color="black", hovering_color="White")
        OPTION_BUTTON = Button(image=pygame.image.load("images/game_button.png"), pos=(395,500),
                                text_input="OPTION", font=get_font(25),base_color="black", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("images/game_button.png"), pos=(395,650),
                             text_input="QUIT", font=get_font(25),base_color="black", hovering_color="White")

        for button in [PLAY_BUTTON, OPTION_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if(PLAY_BUTTON.checkForInput(MENU_MOUSE_POS)):
                    click_sound.play()
                    main()
                if(QUIT_BUTTON.checkForInput(MENU_MOUSE_POS)):
                    click_sound.play()
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)
        pygame.display.update()

# Hàm main
def main():
    chessboard = board.Board.new()
    running = True
    selected = None
    possible_moves = None
    game_over = False
    result_text = ""

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
                                move_sound.play()
                                print("User move: " + move.to_string())
                                selected = None
                                possible_moves = None

                                if is_king_captured(chessboard, pieces.Piece.BLACK):
                                    result_text = "YOU WIN"
                                    print("Checkmate! White wins.")
                                    game_over = True
                                    win_sound.play()
                                    break   

                                ai_move = ai.AI.get_ai_move(chessboard, [])
                                if ai_move == 0:
                                    if chessboard.is_check(pieces.Piece.BLACK):
                                        print("Checkmate. White wins.")
                                    else:
                                        print("Stalemate.")
                                    game_over = True
                                    win_sound.play()
                                else:
                                    moving_piece = chessboard.get_piece(ai_move.xfrom, ai_move.yfrom)
                                    animate_move(chessboard, ai_move, moving_piece)
                                    move_sound.play()
                                    print("AI move: " + ai_move.to_string())

                                if is_king_captured(chessboard, pieces.Piece.WHITE):
                                    result_text = "YOU LOSE"
                                    loss_sound.play()
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
            if(game_over):
                should_restart = game_over_screen(result_text)
                if (should_restart == True):
                    main()
                elif (should_restart == False):
                    menu()
        screen.fill(BLACK)
        draw_board(chessboard, selected, possible_moves)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    print("Game ended.")

if __name__ == "__main__":
    menu()