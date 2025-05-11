import board, pieces, numpy

class Heuristics:
    PAWN_TABLE = numpy.array([
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [ 5, 10, 10,-20,-20, 10, 10,  5],
        [ 5, -5,-10,  0,  0,-10, -5,  5],
        [ 0,  0,  0, 20, 20,  0,  0,  0],
        [ 5,  5, 10, 25, 25, 10,  5,  5],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [ 0,  0,  0,  0,  0,  0,  0,  0]
    ])

    KNIGHT_TABLE = numpy.array([
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20,   0,   5,   5,   0, -20, -40],
        [-30,   5,  10,  15,  15,  10,   5, -30],
        [-30,   0,  15,  20,  20,  15,   0, -30],
        [-30,   5,  15,  20,  20,  15,   0, -30],
        [-30,   0,  10,  15,  15,  10,   0, -30],
        [-40, -20,   0,   0,   0,   0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50]
    ])

    BISHOP_TABLE = numpy.array([
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10,   5,   0,   0,   0,   0,   5, -10],
        [-10,  10,  10,  10,  10,  10,  10, -10],
        [-10,   0,  10,  10,  10,  10,   0, -10],
        [-10,   5,   5,  10,  10,   5,   5, -10],
        [-10,   0,   5,  10,  10,   5,   0, -10],
        [-10,   0,   0,   0,   0,   0,   0, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20]
    ])

    ROOK_TABLE = numpy.array([
        [ 0,  0,  0,  5,  5,  0,  0,  0],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [ 5, 10, 10, 10, 10, 10, 10,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0]
    ])

    QUEEN_TABLE = numpy.array([
        [-20, -10, -10, -5, -5, -10, -10, -20],
        [-10,   0,   5,  0,  0,   0,   0, -10],
        [-10,   5,   5,  5,  5,   5,   0, -10],
        [  0,   0,   5,  5,  5,   5,   0,  -5],
        [ -5,   0,   5,  5,  5,   5,   0,  -5],
        [-10,   0,   5,  5,   5,   5,   0, -10],
        [-10,   0,   0,  0,  0,   0,   0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20]
    ])

    @staticmethod
    def evaluate(board):
        material = Heuristics.get_material_score(board)
        pawns = Heuristics.get_piece_position_score(board, pieces.Pawn.PIECE_TYPE, Heuristics.PAWN_TABLE)
        knights = Heuristics.get_piece_position_score(board, pieces.Knight.PIECE_TYPE, Heuristics.KNIGHT_TABLE)
        bishops = Heuristics.get_piece_position_score(board, pieces.Bishop.PIECE_TYPE, Heuristics.BISHOP_TABLE)
        rooks = Heuristics.get_piece_position_score(board, pieces.Rook.PIECE_TYPE, Heuristics.ROOK_TABLE)
        queens = Heuristics.get_piece_position_score(board, pieces.Queen.PIECE_TYPE, Heuristics.QUEEN_TABLE)
        return material + pawns + knights + bishops + rooks + queens

    @staticmethod
    def get_piece_position_score(board, piece_type, table):
        white = 0
        black = 0
        for x in range(8):
            for y in range(8):
                piece = board.chesspieces[x][y]
                if piece != 0:
                    if piece.piece_type == piece_type:
                        if piece.color == pieces.Piece.WHITE:
                            white += table[x][y]
                        else:
                            black += table[7 - x][y]
        return white - black

    @staticmethod
    def get_material_score(board):
        white = 0
        black = 0
        for x in range(8):
            for y in range(8):
                piece = board.chesspieces[x][y]
                if piece != 0:
                    if piece.color == pieces.Piece.WHITE:
                        white += piece.value
                    else:
                        black += piece.value
        return white - black

class AI:
    INFINITE = 10000000

    @staticmethod
    def get_captured_value(chessboard, move):
        # Kiểm tra bắt qua đường
        piece_from = chessboard.get_piece(move.xfrom, move.yfrom)
        if (piece_from != 0 and piece_from.piece_type == pieces.Pawn.PIECE_TYPE and
            move.xto != move.xfrom and chessboard.get_piece(move.xto, move.yto) == 0 and
            chessboard.en_passant_target == (move.xto, move.yto)):
            captured_pawn = chessboard.get_piece(move.xto, move.yfrom)
            return captured_pawn.value if captured_pawn != 0 else 0
        
        # Trường hợp bình thường
        captured_piece = chessboard.get_piece(move.xto, move.yto)
        return captured_piece.value if captured_piece != 0 else 0

    @staticmethod
    def get_ai_move(chessboard, invalid_moves):
        possible_moves = chessboard.get_possible_moves(pieces.Piece.BLACK)
        
        if not possible_moves:
            return 0
        
        # Sắp xếp nước đi theo heuristic (ưu tiên ăn quân có giá trị cao)
        possible_moves.sort(key=lambda move: (
            -AI.get_captured_value(chessboard, move),
            0
        ))
        
        best_move = None
        best_score = AI.INFINITE
        
        for move in possible_moves:
            if AI.is_invalid_move(move, invalid_moves):
                continue
                
            # Tạo bản sao và kiểm tra
            copy = board.Board.clone(chessboard)
            copy.perform_move(move)
            
            # Kiểm tra chiếu tướng sau khi đi
            is_check = copy.is_check(pieces.Piece.WHITE)
            
            score = AI.alphabeta(copy, 2, -AI.INFINITE, AI.INFINITE, True)
            
            # Thêm điểm ưu tiên nếu chiếu tướng
            if is_check:
                score -= 50  # Giảm score (vì AI đang chơi quân đen và đang minimize)
            
            if score < best_score:
                best_score = score
                best_move = move
        
        if best_move is None:
            return 0
        
        # Kiểm tra nước đi có an toàn không
        copy = board.Board.clone(chessboard)
        copy.perform_move(best_move)
        if copy.is_check(pieces.Piece.BLACK):
            invalid_moves.append(best_move)
            return AI.get_ai_move(chessboard, invalid_moves)
        
        return best_move

    @staticmethod
    def is_invalid_move(move, invalid_moves):
        for invalid_move in invalid_moves:
            if invalid_move.equals(move):
                return True
        return False

    @staticmethod
    def minimax(board, depth, maximizing):
        if depth == 0:
            return Heuristics.evaluate(board)
        if maximizing:
            best_score = -AI.INFINITE
            for move in board.get_possible_moves(pieces.Piece.WHITE):
                copy = board.Board.clone(board)
                copy.perform_move(move)
                score = AI.minimax(copy, depth-1, False)
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = AI.INFINITE
            for move in board.get_possible_moves(pieces.Piece.BLACK):
                copy = board.Board.clone(board)
                copy.perform_move(move)
                score = AI.minimax(copy, depth-1, True)
                best_score = min(best_score, score)
            return best_score

    @staticmethod
    def alphabeta(chessboard, depth, a, b, maximizing):
        if depth == 0:
            return Heuristics.evaluate(chessboard)
        if maximizing:
            best_score = -AI.INFINITE
            for move in chessboard.get_possible_moves(pieces.Piece.WHITE):
                copy = board.Board.clone(chessboard)
                copy.perform_move(move)
                best_score = max(best_score, AI.alphabeta(copy, depth-1, a, b, False))
                a = max(a, best_score)
                if b <= a:
                    break
            return best_score
        else:
            best_score = AI.INFINITE
            for move in chessboard.get_possible_moves(pieces.Piece.BLACK):
                copy = board.Board.clone(chessboard)
                copy.perform_move(move)
                best_score = min(best_score, AI.alphabeta(copy, depth-1, a, b, True))
                b = min(b, best_score)
                if b <= a:
                    break
            return best_score