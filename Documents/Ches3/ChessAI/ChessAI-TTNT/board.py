import pieces
from move import Move

class Board:

    WIDTH = 8
    HEIGHT = 8

    def __init__(self, chesspieces, white_king_moved, black_king_moved):
        self.chesspieces = chesspieces
        self.white_king_moved = white_king_moved
        self.black_king_moved = black_king_moved
        self.en_passant_target = None

    @classmethod
    def clone(cls, chessboard):
        chesspieces = [[0 for x in range(Board.WIDTH)] for y in range(Board.HEIGHT)]
        for x in range(Board.WIDTH):
            for y in range(Board.HEIGHT):
                piece = chessboard.chesspieces[x][y]
                if piece != 0:
                    chesspieces[x][y] = piece.clone()
        return cls(chesspieces, chessboard.white_king_moved, chessboard.black_king_moved)

    @classmethod
    def new(cls):
        chess_pieces = [[0 for x in range(Board.WIDTH)] for y in range(Board.HEIGHT)]
        # Create pawns.
        for x in range(Board.WIDTH):
            chess_pieces[x][Board.HEIGHT-2] = pieces.Pawn(x, Board.HEIGHT-2, pieces.Piece.WHITE)
            chess_pieces[x][1] = pieces.Pawn(x, 1, pieces.Piece.BLACK)

        # Create rooks.
        chess_pieces[0][Board.HEIGHT-1] = pieces.Rook(0, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[Board.WIDTH-1][Board.HEIGHT-1] = pieces.Rook(Board.WIDTH-1, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[0][0] = pieces.Rook(0, 0, pieces.Piece.BLACK)
        chess_pieces[Board.WIDTH-1][0] = pieces.Rook(Board.WIDTH-1, 0, pieces.Piece.BLACK)

        # Create Knights.
        chess_pieces[1][Board.HEIGHT-1] = pieces.Knight(1, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[Board.WIDTH-2][Board.HEIGHT-1] = pieces.Knight(Board.WIDTH-2, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[1][0] = pieces.Knight(1, 0, pieces.Piece.BLACK)
        chess_pieces[Board.WIDTH-2][0] = pieces.Knight(Board.WIDTH-2, 0, pieces.Piece.BLACK)

        # Create Bishops.
        chess_pieces[2][Board.HEIGHT-1] = pieces.Bishop(2, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[Board.WIDTH-3][Board.HEIGHT-1] = pieces.Bishop(Board.WIDTH-3, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[2][0] = pieces.Bishop(2, 0, pieces.Piece.BLACK)
        chess_pieces[Board.WIDTH-3][0] = pieces.Bishop(Board.WIDTH-3, 0, pieces.Piece.BLACK)

        # Create King & Queen.
        chess_pieces[4][Board.HEIGHT-1] = pieces.King(4, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[3][Board.HEIGHT-1] = pieces.Queen(3, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[4][0] = pieces.King(4, 0, pieces.Piece.BLACK)
        chess_pieces[3][0] = pieces.Queen(3, 0, pieces.Piece.BLACK)

        return cls(chess_pieces, False, False)

    def get_possible_moves(self, color):
        moves = []
        for x in range(Board.WIDTH):
            for y in range(Board.HEIGHT):
                piece = self.chesspieces[x][y]
                if (piece != 0):
                    if (piece.color == color):
                        moves += piece.get_possible_moves(self)

        return moves

    def perform_move(self, move):
        piece = self.chesspieces[move.xfrom][move.yfrom]
        self.move_piece(piece, move.xto, move.yto)

        # Xử lý bắt tốt qua đường
        if piece.piece_type == pieces.Pawn.PIECE_TYPE:
            # Kiểm tra di chuyển 2 ô của tốt
            if abs(move.yto - move.yfrom) == 2:
                self.en_passant_target = (move.xfrom, (move.yfrom + move.yto) // 2)
            # Kiểm tra nước đi bắt qua đường
            elif (move.xto, move.yto) == self.en_passant_target:
                # Xóa quân tốt bị bắt (nằm ở cùng cột với đích đến, cùng hàng với vị trí ban đầu)
                captured_pawn_pos = (move.xto, move.yfrom)
                self.chesspieces[captured_pawn_pos[0]][captured_pawn_pos[1]] = 0
            else:
                self.en_passant_target = None
        else:
            self.en_passant_target = None

        # Phong cấp tốt
        if piece.piece_type == pieces.Pawn.PIECE_TYPE:
            if piece.y == 0 or piece.y == Board.HEIGHT - 1:
                self.chesspieces[piece.x][piece.y] = pieces.Queen(piece.x, piece.y, piece.color)

        # Cập nhật trạng thái vua
        if piece.piece_type == pieces.King.PIECE_TYPE:
            if piece.color == pieces.Piece.WHITE:
                self.white_king_moved = True
            else:
                self.black_king_moved = True
            # Nhập thành
            if move.xto - move.xfrom == 2:
                rook = self.chesspieces[piece.x + 1][piece.y]
                self.move_piece(rook, piece.x - 1, piece.y)
            elif move.xto - move.xfrom == -2:
                rook = self.chesspieces[piece.x - 2][piece.y]
                self.move_piece(rook, piece.x + 1, piece.y)
    
    def move_piece(self, piece, xto, yto):
        self.chesspieces[piece.x][piece.y] = 0
        piece.x = xto
        piece.y = yto

        self.chesspieces[xto][yto] = piece


    # Trả về nếu màu đã cho được kiểm tra.
    def is_check(self, color):
        other_color = pieces.Piece.WHITE
        if (color == pieces.Piece.WHITE):
            other_color = pieces.Piece.BLACK

        for move in self.get_possible_moves(other_color):
            copy = Board.clone(self)
            copy.perform_move(move)

            king_found = False
            for x in range(Board.WIDTH):
                for y in range(Board.HEIGHT):
                    piece = copy.chesspieces[x][y]
                    if (piece != 0):
                        if (piece.color == color and piece.piece_type == pieces.King.PIECE_TYPE):
                            king_found = True

            if (not king_found):
                return True

        return False

    def get_piece(self, x, y):
        if (not self.in_bounds(x, y)):
            return 0

        return self.chesspieces[x][y]

    def in_bounds(self, x, y):
        return (x >= 0 and y >= 0 and x < Board.WIDTH and y < Board.HEIGHT)

    # def to_string(self):
    #     string =  "    A  B  C  D  E  F  G  H\n"
    #     string += "    -----------------------\n"
    #     for y in range(Board.HEIGHT):
    #         string += str(8 - y) + " | "
    #         for x in range(Board.WIDTH):
    #             piece = self.chesspieces[x][y]
    #             if (piece != 0):
    #                 string += piece.to_string()
    #             else:
    #                 string += ".. "
    #         string += "\n"
    #     return string + "\n"
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