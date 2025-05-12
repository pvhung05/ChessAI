import sys

import pygame
import board
import pieces
import ai
from move import Move
import math
from button import Button
import tkinter as tk
from tkinter import filedialog
import threading

import ai_opponent

# Biến toàn cục lưu đường dẫn engine
engine_path = None
ai_compete = True  # Biến toàn cục để xác định chế độ chơi (AI vs AI hay người vs AI)

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

#mot so ham ho tro lay ai dau voi nhau
def get_fen(self, active_color="w"):
    fen = ""
    for y in range(Board.HEIGHT - 1, -1, -1):  # Lặp từ hàng 8 đến hàng 1
        empty_count = 0
        for x in range(Board.WIDTH):  # Lặp qua các cột
            piece = self.chesspieces[x][y]
            if piece == 0:  # Nếu là ô trống
                empty_count += 1
            else:
                if empty_count > 0:  # Nếu có ô trống trước đó
                    fen += str(empty_count)
                    empty_count = 0
                symbol = piece.to_string()[1]  # Lấy ký hiệu của quân cờ
                if piece.to_string()[0] == "B":  # Nếu là quân đen
                    symbol = symbol.lower()  # Đổi ký hiệu thành chữ thường
                fen += symbol
        if empty_count > 0:  # Nếu có ô trống còn lại
            fen += str(empty_count)
        if y > 0:
            fen += "/"  # Phân cách các hàng

    # Lượt đi (w hoặc b)
    fen += " " + ("w" if active_color == "w" else "b")

    return self.reverse_fen(fen)

def reverse_fen(self,fen):
    # Tách chuỗi FEN thành các phần
    parts = fen.split(' ')
    
    # Lấy phần bàn cờ (trạng thái của bàn cờ)
    board_state = parts[0]
    
    # Đảo ngược thứ tự các hàng quân cờ
    reversed_board_state = "/".join(reversed(board_state.split('/')))
    
    # Lưu lại phần còn lại của FEN (lượt đi, castling, en passant, số nước đi, số lượt chơi)
    rest_of_fen = ' '.join(parts[1:])
    
    # Kết hợp lại thành chuỗi FEN mới
    reversed_fen = reversed_board_state + ' ' + rest_of_fen
    return reversed_fen

def coordinateMoveConvert(ai_enemy_move):
    from_square = ai_enemy_move[:2]
    to_square = ai_enemy_move[2:4]

    print(from_square)
    print(to_square)

    row = {
    "a": 0,
    "b": 1,
    "c": 2,
    "d": 3,
    "e": 4,
    "f": 5,
    "g": 6,
    "h": 7
    }
  

    s_x_from = row[from_square[0]]
    s_y_from = 8 - int(from_square[1])
    s_x_to = row[to_square[0]]  # Cột (file)
    s_y_to = 8 - int(to_square[1])  # Hàng (rank)

    return s_x_from, s_y_from, s_x_to, s_y_to

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
    global engine_path
    global ai_compete  # Sử dụng biến toàn cục để lưu đường dẫn engine
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
                    if not engine_path:
                        ai_compete = False
                    main()

                if(OPTION_BUTTON.checkForInput(MENU_MOUSE_POS)):
                    click_sound.play()
                    option_menu()

                if(QUIT_BUTTON.checkForInput(MENU_MOUSE_POS)):
                    click_sound.play()
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)
        pygame.display.update()

#ham lua chon menu option
def option_menu():
    global engine_path  # Sử dụng biến toàn cục để lưu đường dẫn engine
    global ai_compete  # Sử dụng biến toàn cục để xác định chế độ chơi

    selected_option = None
    while True:
        # Hiển thị background
        screen.blit(BG, (0, 0))
        
        font = get_font(30)
        title = font.render("Options", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Radio buttons
        OPTION_1 = Button(image=None, pos=(WIDTH // 2, 250), text_input="AI Vs AI",
                          font=get_font(25), base_color="white", hovering_color="yellow")
        OPTION_2 = Button(image=None, pos=(WIDTH // 2, 350), text_input="Player Vs AI",
                          font=get_font(25), base_color="white", hovering_color="yellow")
        BACK_BUTTON = Button(image=None, pos=(WIDTH // 2, 500), text_input="BACK",
                             font=get_font(25), base_color="white", hovering_color="yellow")

        mouse_pos = pygame.mouse.get_pos()

        for button in [OPTION_1, OPTION_2, BACK_BUTTON]:
            button.changeColor(mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTION_1.checkForInput(mouse_pos):
                    click_sound.play()
                    selected_option = "ai"
                    print("Selected Option: AI Vs AI")
                    
                    # Kiểm tra đường dẫn engine
                    if not engine_path:
                        print("Engine path not set. Please select the engine file.")
                        root = tk.Tk()
                        root.withdraw()  # Ẩn cửa sổ chính của tkinter
                        engine_path = filedialog.askopenfilename(title="Select AI Engine",
                                                                 filetypes=[("Executable Files", "*.exe")])
                        if engine_path:
                            print(f"Engine path set to: {engine_path}")

                            ai_compete = True  # Chế độ AI vs AI
                        else:
                            print("No engine selected. Returning to options menu.")
                            selected_option = None  # Reset lựa chọn nếu không chọn file

                if OPTION_2.checkForInput(mouse_pos):
                    click_sound.play()
                    selected_option = "human"
                    ai_compete = False  # Chế độ người vs AI
                    engine_path = None  # Đặt lại đường dẫn engine
                    print("Selected Option: Player Vs AI")
                if BACK_BUTTON.checkForInput(mouse_pos):
                    click_sound.play()
                    return  # Quay lại menu chính

        # Hiển thị lựa chọn đã chọn
        if selected_option:
            selected_text = font.render(f"Selected: {selected_option}", True, WHITE)
            screen.blit(selected_text, (WIDTH // 2 - selected_text.get_width() // 2, 400))

        pygame.display.flip()
        clock.tick(FPS)


# Hàm main
def main():
    global engine_path
    global ai_compete

    chessboard = board.Board.new()
    running = True
    selected = None
    possible_moves = None
    game_over = False
    result_text = ""
    ai_thread = None
    ai_move_result = [None]  # Use a list to store the result from the thread

    def compute_ai_move():
        # Function to compute the AI move in a separate thread
        ai_move_result[0] = ai.AI.get_ai_move(chessboard, [])

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif not game_over and ai_compete and ai_thread is None:
                #hmodel
                #rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w
                print(chessboard.get_fen('w'))
                #ai enemy
                ai_enemy = ai_opponent.OpponentAI(engine_path, time_limit=0.1)
                ai_enemy_move=ai_enemy.get_best_move(chessboard.get_fen('w'))
                print(ai_enemy_move)
                s_x_from, s_y_from, s_x_to, s_y_to = coordinateMoveConvert(ai_enemy_move.uci())
                moving_piece_stkfish = chessboard.get_piece(s_x_from, s_y_from)
                print(moving_piece_stkfish)
                s_move = Move( s_x_from, s_y_from, s_x_to, s_y_to)           
                animate_move(chessboard, s_move, moving_piece_stkfish)
                print(f"ai enemy move ({s_x_from},{s_y_from}) -> ({s_x_to},{s_y_to})")
                #chessboard.perform_move(s_move)
                ai_enemy.quit()                     
                # Start the AI computation in a separate thread
                ai_thread = threading.Thread(target=compute_ai_move)
                ai_thread.start()

            elif not game_over and ai_compete and ai_thread is not None:
                # Check if the AI thread has finished
                if not ai_thread.is_alive():
                    ai_thread.join()  # Ensure the thread is cleaned up
                    ai_thread = None  # Reset the thread
                    ai_move = ai_move_result[0]
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
                        print(chessboard.get_fen('b'))
                    if is_king_captured(chessboard, pieces.Piece.WHITE):
                        print("Checkmate! Black wins.")
                        game_over = True

            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and not ai_compete:
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
                                else:
                                    moving_piece = chessboard.get_piece(ai_move.xfrom, ai_move.yfrom)
                                    animate_move(chessboard, ai_move, moving_piece)
                                    print("AI move: " + ai_move.to_string())
                                    print(chessboard.get_fen('b'))

                            except Exception as e:
                                print(f"Error during move: {e}")
                            break
                    else:
                        print("Invalid move, resetting selection.")
                        selected = None
                        possible_moves = None
            if game_over:
                should_restart = game_over_screen(result_text)
                if should_restart:
                    main()
                else:
                    menu()

        screen.fill(BLACK)
        draw_board(chessboard, selected, possible_moves)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    print("Game ended.")

if __name__ == "__main__":
    menu()
    