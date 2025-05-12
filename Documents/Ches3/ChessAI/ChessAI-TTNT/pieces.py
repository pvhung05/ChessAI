import ai
from move import Move

class Piece():

    WHITE = "W"
    BLACK = "B"

    def __init__(self, x, y, color, piece_type, value):
        self.x = x
        self.y = y
        self.color = color
        self.piece_type = piece_type
        self.value = value



    # Trả về tất cả các nước đi chéo cho quân cờ này. Do đó, điều này chỉ nên được
    # Sử dụng bởi Tượng và Hậu vì chúng là những quân cờ duy nhất có thể
    # Di chuyển theo đường chéo.
    def get_possible_diagonal_moves(self, board):
        moves = []

        for i in range(1, 8):
            if (not board.in_bounds(self.x+i, self.y+i)):
                break

            piece = board.get_piece(self.x+i, self.y+i)
            moves.append(self.get_move(board, self.x+i, self.y+i))
            if (piece != 0):
                break

        for i in range(1, 8):
            if (not board.in_bounds(self.x+i, self.y-i)):
                break

            piece = board.get_piece(self.x+i, self.y-i)
            moves.append(self.get_move(board, self.x+i, self.y-i))
            if (piece != 0):
                break

        for i in range(1, 8):
            if (not board.in_bounds(self.x-i, self.y-i)):
                break

            piece = board.get_piece(self.x-i, self.y-i)
            moves.append(self.get_move(board, self.x-i, self.y-i))
            if (piece != 0):
                break

        for i in range(1, 8):
            if (not board.in_bounds(self.x-i, self.y+i)):
                break

            piece = board.get_piece(self.x-i, self.y+i)
            moves.append(self.get_move(board, self.x-i, self.y+i))
            if (piece != 0):
                break

        return self.remove_null_from_list(moves)

    # Trả về tất cả các nước đi theo chiều ngang cho quân cờ này. Do đó, điều này chỉ nên được
    # Sử dụng bởi Xe và Hậu vì chúng là những quân cờ duy nhất có thể
    # Di chuyển theo chiều ngang.
    def get_possible_horizontal_moves(self, board):
        moves = []

        # Di chuyển sang bên phải của quân cờ.
        for i in range(1, 8 - self.x):
            piece = board.get_piece(self.x + i, self.y)
            moves.append(self.get_move(board, self.x+i, self.y))

            if (piece != 0):
                break

        # Di chuyển sang bên trái của quân cờ.
        for i in range(1, self.x + 1):
            piece = board.get_piece(self.x - i, self.y)
            moves.append(self.get_move(board, self.x-i, self.y))
            if (piece != 0):
                break

        # Di chuyển xuống dưới.
        for i in range(1, 8 - self.y):
            piece = board.get_piece(self.x, self.y + i)
            moves.append(self.get_move(board, self.x, self.y+i))
            if (piece != 0):
                break

        # Di chuyển lên trên.
        for i in range(1, self.y + 1):
            piece = board.get_piece(self.x, self.y - i)
            moves.append(self.get_move(board, self.x, self.y-i))
            if (piece != 0):
                break

        return self.remove_null_from_list(moves)

    # Trả về một đối tượng Move với (xfrom, yfrom) được đặt thành vị trí hiện tại của quân cờ.
    # (xto, yto) được đặt thành vị trí đã cho. Nếu nước đi không hợp lệ, 0 sẽ được trả về.
    # Một nước đi không hợp lệ nếu nó nằm ngoài giới hạn hoặc một quân cờ cùng màu đang
    # Bị ăn.
    def get_move(self, board, xto, yto):
        move = 0
        if (board.in_bounds(xto, yto)):
            piece = board.get_piece(xto, yto)
            if (piece != 0):
                if (piece.color != self.color):
                    move = Move(self.x, self.y, xto, yto)
            else:
                move = Move(self.x, self.y, xto, yto)
        return move

    # Returns the list of moves cleared of all the 0's.
    def remove_null_from_list(self, l):
        return [move for move in l if move != 0]

    def to_string(self):
        return self.color + self.piece_type + " "

class Rook(Piece):

    PIECE_TYPE = "R"
    VALUE = 500

    def __init__(self, x, y, color):
        super(Rook, self).__init__(x, y, color, Rook.PIECE_TYPE, Rook.VALUE)

    def get_possible_moves(self, board):
        return self.get_possible_horizontal_moves(board)

    def clone(self):
        return Rook(self.x, self.y, self.color)


class Knight(Piece):

    PIECE_TYPE = "N"
    VALUE = 320

    def __init__(self, x, y, color):
        super(Knight, self).__init__(x, y, color, Knight.PIECE_TYPE, Knight.VALUE)

    def get_possible_moves(self, board):
        moves = []

        moves.append(self.get_move(board, self.x+2, self.y+1))
        moves.append(self.get_move(board, self.x-1, self.y+2))
        moves.append(self.get_move(board, self.x-2, self.y+1))
        moves.append(self.get_move(board, self.x+1, self.y-2))
        moves.append(self.get_move(board, self.x+2, self.y-1))
        moves.append(self.get_move(board, self.x+1, self.y+2))
        moves.append(self.get_move(board, self.x-2, self.y-1))
        moves.append(self.get_move(board, self.x-1, self.y-2))

        return self.remove_null_from_list(moves)

    def clone(self):
        return Knight(self.x, self.y, self.color)


class Bishop(Piece):

    PIECE_TYPE = "B"
    VALUE = 330

    def __init__(self, x, y, color):
        super(Bishop, self).__init__(x, y, color, Bishop.PIECE_TYPE, Bishop.VALUE)

    def get_possible_moves(self, board):
        return self.get_possible_diagonal_moves(board)

    def clone(self):
        return Bishop(self.x, self.y, self.color)


class Queen(Piece):

    PIECE_TYPE = "Q"
    VALUE = 900

    def __init__(self, x, y, color):
        super(Queen, self).__init__(x, y, color, Queen.PIECE_TYPE, Queen.VALUE)

    def get_possible_moves(self, board):
        diagonal = self.get_possible_diagonal_moves(board)
        horizontal = self.get_possible_horizontal_moves(board)
        return horizontal + diagonal

    def clone(self):
        return Queen(self.x, self.y, self.color)


class King(Piece):

    PIECE_TYPE = "K"
    VALUE = 20000

    def __init__(self, x, y, color):
        super(King, self).__init__(x, y, color, King.PIECE_TYPE, King.VALUE)

    def get_possible_moves(self, board):
        moves = []

        moves.append(self.get_move(board, self.x+1, self.y))
        moves.append(self.get_move(board, self.x+1, self.y+1))
        moves.append(self.get_move(board, self.x, self.y+1))
        moves.append(self.get_move(board, self.x-1, self.y+1))
        moves.append(self.get_move(board, self.x-1, self.y))
        moves.append(self.get_move(board, self.x-1, self.y-1))
        moves.append(self.get_move(board, self.x, self.y-1))
        moves.append(self.get_move(board, self.x+1, self.y-1))

        moves.append(self.get_castle_kingside_move(board))
        moves.append(self.get_castle_queenside_move(board))

        return self.remove_null_from_list(moves)

    # Chỉ kiểm tra lâu đài bên vua
    def get_castle_kingside_move(self, board):
        # Chúng ta đang nhìn vào một quân xe hợp lệ
        piece_in_corner = board.get_piece(self.x+3, self.y)
        if (piece_in_corner == 0 or piece_in_corner.piece_type != Rook.PIECE_TYPE):
            return 0

        # Nếu quân xe ở góc không cùng màu với quân của mình thì chúng ta không thể nhập thành (điều hiển nhiên).
        if (piece_in_corner.color != self.color):
            return 0
        
        # Nếu vua đã di chuyển, chúng ta không thể nhập thành
        if (self.color == Piece.WHITE and board.white_king_moved):
            return 0
        
        if (self.color == Piece.BLACK and board.black_king_moved):
            return 0

        # Nếu có quân cờ ở giữa vua và xe thì chúng ta không thể nhập thành
        if (board.get_piece(self.x+1, self.y) != 0 or board.get_piece(self.x+2, self.y) != 0):
            return 0
        
        return Move(self.x, self.y, self.x+2, self.y)

    def get_castle_queenside_move(self, board):
        # Chúng ta đang nhìn vào một quân xe hợp lệ
        piece_in_corner = board.get_piece(self.x-4, self.y)
        if (piece_in_corner == 0 or piece_in_corner.piece_type != Rook.PIECE_TYPE):
            return 0

        # Nếu quân xe ở góc không cùng màu với quân của mình thì chúng ta không thể nhập thành (điều hiển nhiên).
        if (piece_in_corner.color != self.color):
            return 0
        
        # Nếu vua đã di chuyển, chúng ta không thể nhập thành
        if (self.color == Piece.WHITE and board.white_king_moved):
            return 0
        
        if (self.color == Piece.BLACK and board.black_king_moved):
            return 0

        # Nếu có quân cờ ở giữa vua và xe thì chúng ta không thể nhập thành
        if (board.get_piece(self.x-1, self.y) != 0 or board.get_piece(self.x-2, self.y) != 0 or board.get_piece(self.x-3, self.y) != 0):
            return 0
        
        return Move(self.x, self.y, self.x-2, self.y)


    def clone(self):
        return King(self.x, self.y, self.color)


class Pawn(Piece):
    PIECE_TYPE = "P"
    VALUE = 100

    def __init__(self, x, y, color):
        super(Pawn, self).__init__(x, y, color, Pawn.PIECE_TYPE, Pawn.VALUE)

    def is_starting_position(self):
        return self.y == 1 if self.color == Piece.BLACK else self.y == 6

    def get_possible_moves(self, board):
        moves = []
        direction = -1 if self.color == Piece.WHITE else 1

    # Di chuyển tiến 1 ô
        if board.get_piece(self.x, self.y + direction) == 0:
            moves.append(self.get_move(board, self.x, self.y + direction))

    # Di chuyển tiến 2 ô từ vị trí ban đầu
        if self.is_starting_position() and board.get_piece(self.x, self.y + direction) == 0 and board.get_piece(self.x, self.y + 2*direction) == 0:
            moves.append(self.get_move(board, self.x, self.y + 2*direction))

        # Ăn quân chéo (bao gồm cả en passant)
        for dx in [-1, 1]:
            x, y = self.x + dx, self.y + direction
            if board.in_bounds(x, y):
                piece = board.get_piece(x, y)
                # Ăn quân bình thường
                if piece != 0 and piece.color != self.color:
                    moves.append(self.get_move(board, x, y))
                # Ăn en passant
                elif piece == 0 and board.en_passant_target == (x, y):
                    # Kiểm tra có tốt đối phương ở vị trí en passant không
                    enemy_pawn_pos = (x, self.y)
                    enemy_pawn = board.get_piece(*enemy_pawn_pos)
                    if (enemy_pawn != 0 and enemy_pawn.piece_type == Pawn.PIECE_TYPE and 
                        enemy_pawn.color != self.color):
                        moves.append(self.get_move(board, x, y))

        return self.remove_null_from_list(moves)

    def clone(self):
        return Pawn(self.x, self.y, self.color)