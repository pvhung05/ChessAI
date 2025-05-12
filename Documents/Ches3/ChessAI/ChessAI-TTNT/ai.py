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
        [-10,   0,   5,  5,  5,   5,   0, -10],
        [-10,   0,   0,  0,  0,   0,   0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20]
    ])
    
    # Bảng giá trị vị trí cho vua ở giữa ván
    KING_MIDDLE_TABLE = numpy.array([
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [ 20,  20,   0,   0,   0,   0,  20,  20],
        [ 20,  30,  10,   0,   0,  10,  30,  20]
    ])
    
    # Bảng giá trị vị trí cho vua ở tàn cuộc
    KING_END_TABLE = numpy.array([
        [-50, -40, -30, -20, -20, -30, -40, -50],
        [-30, -20, -10,   0,   0, -10, -20, -30],
        [-30, -10,  20,  30,  30,  20, -10, -30],
        [-30, -10,  30,  40,  40,  30, -10, -30],
        [-30, -10,  30,  40,  40,  30, -10, -30],
        [-30, -10,  20,  30,  30,  20, -10, -30],
        [-30, -30,   0,   0,   0,   0, -30, -30],
        [-50, -30, -30, -30, -30, -30, -30, -50]
    ])
    
    # Hằng số cho các yếu tố chiến thuật
    BISHOP_PAIR_BONUS = 30
    KNIGHT_OUTPOST_BONUS = 15
    ROOK_ON_OPEN_FILE_BONUS = 25
    ROOK_ON_SEMI_OPEN_FILE_BONUS = 10
    PASSED_PAWN_BONUS = [0, 10, 15, 20, 35, 60, 100, 0]  # Theo hàng
    DOUBLED_PAWN_PENALTY = -15
    ISOLATED_PAWN_PENALTY = -10
    KING_SHIELD_BONUS = 5  # Điểm cho mỗi tốt bảo vệ vua
    MOBILITY_WEIGHT = 2    # Trọng số cho tính cơ động

    @staticmethod
    def evaluate(board):
        # Điểm vật chất
        material = Heuristics.get_material_score(board)
        
        # Điểm vị trí
        pawns = Heuristics.get_piece_position_score(board, pieces.Pawn.PIECE_TYPE, Heuristics.PAWN_TABLE)
        knights = Heuristics.get_piece_position_score(board, pieces.Knight.PIECE_TYPE, Heuristics.KNIGHT_TABLE)
        bishops = Heuristics.get_piece_position_score(board, pieces.Bishop.PIECE_TYPE, Heuristics.BISHOP_TABLE)
        rooks = Heuristics.get_piece_position_score(board, pieces.Rook.PIECE_TYPE, Heuristics.ROOK_TABLE)
        queens = Heuristics.get_piece_position_score(board, pieces.Queen.PIECE_TYPE, Heuristics.QUEEN_TABLE)
        
        # Xác định giai đoạn ván đấu
        is_endgame = Heuristics.is_endgame(board)
        
        # Điểm cho vua tùy thuộc vào giai đoạn ván đấu
        if is_endgame:
            kings = Heuristics.get_piece_position_score(board, pieces.King.PIECE_TYPE, Heuristics.KING_END_TABLE)
        else:
            kings = Heuristics.get_piece_position_score(board, pieces.King.PIECE_TYPE, Heuristics.KING_MIDDLE_TABLE)
        
        # Cộng điểm chiến thuật
        tactics_score = Heuristics.evaluate_tactics(board, is_endgame)
        
        # Tính điểm cơ động (bao nhiêu nước đi có thể thực hiện)
        mobility = Heuristics.evaluate_mobility(board)
        
        # Tính tổng điểm
        total_score = material + pawns + knights + bishops + rooks + queens + kings + tactics_score + mobility
        
        return total_score

    @staticmethod
    def get_piece_position_score(board, piece_type, table):
        white = 0
        black = 0
        for x in range(8):
            for y in range(8):
                piece = board.chesspieces[x][y]
                if (piece != 0):
                    if (piece.piece_type == piece_type):
                        if (piece.color == pieces.Piece.WHITE):
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
                if (piece != 0):
                    if (piece.color == pieces.Piece.WHITE):
                        white += piece.value
                    else:
                        black += piece.value

        return white - black
    
    @staticmethod
    def is_endgame(board):
        """Xác định xem ván đấu có ở giai đoạn tàn cuộc không"""
        # Không có hậu hoặc tổng quân ít hơn 10
        white_queen_count = 0
        black_queen_count = 0
        total_piece_value = 0
        
        for x in range(8):
            for y in range(8):
                piece = board.chesspieces[x][y]
                if piece != 0:
                    if piece.piece_type == pieces.Queen.PIECE_TYPE:
                        if piece.color == pieces.Piece.WHITE:
                            white_queen_count += 1
                        else:
                            black_queen_count += 1
                    
                    # Chỉ tính điểm các quân tốt, mã, tượng, xe, hậu
                    if piece.piece_type != pieces.King.PIECE_TYPE:
                        total_piece_value += piece.value
        
        return (white_queen_count == 0 and black_queen_count == 0) or total_piece_value < 3000
    
    @staticmethod
    def evaluate_tactics(board, is_endgame):
        """Đánh giá các yếu tố chiến thuật"""
        score = 0
        
        # Đếm cặp tượng
        white_bishop_count = 0
        black_bishop_count = 0
        
        # Mảng lưu thông tin tốt cho từng cột
        white_pawns_by_file = [0] * 8
        black_pawns_by_file = [0] * 8
        
        # Thống kê quân trên bàn cờ
        for x in range(8):
            for y in range(8):
                piece = board.chesspieces[x][y]
                if piece != 0:
                    # Đếm tượng
                    if piece.piece_type == pieces.Bishop.PIECE_TYPE:
                        if piece.color == pieces.Piece.WHITE:
                            white_bishop_count += 1
                        else:
                            black_bishop_count += 1
                    
                    # Đếm tốt theo cột
                    elif piece.piece_type == pieces.Pawn.PIECE_TYPE:
                        if piece.color == pieces.Piece.WHITE:
                            white_pawns_by_file[y] += 1
                        else:
                            black_pawns_by_file[y] += 1
                    
                    # Đánh giá xe ở cột mở hoặc nửa mở
                    elif piece.piece_type == pieces.Rook.PIECE_TYPE:
                        if piece.color == pieces.Piece.WHITE:
                            if white_pawns_by_file[y] == 0 and black_pawns_by_file[y] == 0:
                                # Cột mở
                                score += Heuristics.ROOK_ON_OPEN_FILE_BONUS
                            elif white_pawns_by_file[y] == 0:
                                # Cột nửa mở
                                score += Heuristics.ROOK_ON_SEMI_OPEN_FILE_BONUS
                        else:
                            if white_pawns_by_file[y] == 0 and black_pawns_by_file[y] == 0:
                                # Cột mở
                                score -= Heuristics.ROOK_ON_OPEN_FILE_BONUS
                            elif black_pawns_by_file[y] == 0:
                                # Cột nửa mở
                                score -= Heuristics.ROOK_ON_SEMI_OPEN_FILE_BONUS
        
        # Thưởng cho cặp tượng (bishop pair)
        if white_bishop_count >= 2:
            score += Heuristics.BISHOP_PAIR_BONUS
        if black_bishop_count >= 2:
            score -= Heuristics.BISHOP_PAIR_BONUS
        
        # Đánh giá cấu trúc tốt
        for y in range(8):  # Duyệt qua các cột
            # Tốt bị kép (doubled pawns)
            if white_pawns_by_file[y] > 1:
                score += Heuristics.DOUBLED_PAWN_PENALTY * (white_pawns_by_file[y] - 1)
            if black_pawns_by_file[y] > 1:
                score -= Heuristics.DOUBLED_PAWN_PENALTY * (black_pawns_by_file[y] - 1)
            
            # Tốt bị cô lập (isolated pawns)
            if white_pawns_by_file[y] > 0:
                is_isolated = (y == 0 or white_pawns_by_file[y-1] == 0) and (y == 7 or white_pawns_by_file[y+1] == 0)
                if is_isolated:
                    score += Heuristics.ISOLATED_PAWN_PENALTY
            
            if black_pawns_by_file[y] > 0:
                is_isolated = (y == 0 or black_pawns_by_file[y-1] == 0) and (y == 7 or black_pawns_by_file[y+1] == 0)
                if is_isolated:
                    score -= Heuristics.ISOLATED_PAWN_PENALTY
            
            # Tốt thông hành (passed pawns)
            white_passed = False
            black_passed = False
            
            # Tìm tốt trắng xa nhất
            white_furthest_pawn_rank = -1
            for x in range(8):
                if board.chesspieces[x][y] != 0 and board.chesspieces[x][y].piece_type == pieces.Pawn.PIECE_TYPE and board.chesspieces[x][y].color == pieces.Piece.WHITE:
                    white_furthest_pawn_rank = x if x < white_furthest_pawn_rank or white_furthest_pawn_rank == -1 else white_furthest_pawn_rank
            
            # Tìm tốt đen xa nhất
            black_furthest_pawn_rank = -1
            for x in range(8):
                if board.chesspieces[x][y] != 0 and board.chesspieces[x][y].piece_type == pieces.Pawn.PIECE_TYPE and board.chesspieces[x][y].color == pieces.Piece.BLACK:
                    black_furthest_pawn_rank = x if x > black_furthest_pawn_rank else black_furthest_pawn_rank
            
            # Kiểm tra tốt thông hành
            if white_furthest_pawn_rank != -1:
                white_passed = True
                # Kiểm tra có tốt đen nào ở phía trước hoặc ở cột kế không
                for check_x in range(white_furthest_pawn_rank):
                    for check_y in range(max(0, y-1), min(8, y+2)):
                        if board.chesspieces[check_x][check_y] != 0 and board.chesspieces[check_x][check_y].piece_type == pieces.Pawn.PIECE_TYPE and board.chesspieces[check_x][check_y].color == pieces.Piece.BLACK:
                            white_passed = False
                            break
                
                if white_passed:
                    score += Heuristics.PASSED_PAWN_BONUS[white_furthest_pawn_rank]
            
            if black_furthest_pawn_rank != -1:
                black_passed = True
                # Kiểm tra có tốt trắng nào ở phía trước hoặc ở cột kế không
                for check_x in range(black_furthest_pawn_rank + 1, 8):
                    for check_y in range(max(0, y-1), min(8, y+2)):
                        if board.chesspieces[check_x][check_y] != 0 and board.chesspieces[check_x][check_y].piece_type == pieces.Pawn.PIECE_TYPE and board.chesspieces[check_x][check_y].color == pieces.Piece.WHITE:
                            black_passed = False
                            break
                
                if black_passed:
                    score -= Heuristics.PASSED_PAWN_BONUS[7 - black_furthest_pawn_rank]
        
        # Đánh giá quân tốt bảo vệ vua
        score += Heuristics.evaluate_king_safety(board)
        
        return score
    
    @staticmethod
    def evaluate_king_safety(board):
        """Đánh giá an toàn của vua dựa trên các tốt bảo vệ xung quanh"""
        score = 0
        
        # Tìm vị trí vua
        white_king_x, white_king_y = -1, -1
        black_king_x, black_king_y = -1, -1
        
        for x in range(8):
            for y in range(8):
                piece = board.chesspieces[x][y]
                if piece != 0 and piece.piece_type == pieces.King.PIECE_TYPE:
                    if piece.color == pieces.Piece.WHITE:
                        white_king_x, white_king_y = x, y
                    else:
                        black_king_x, black_king_y = x, y
        
        # Kiểm tra tốt bảo vệ vua trắng
        if white_king_x != -1:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    check_x, check_y = white_king_x + dx, white_king_y + dy
                    if 0 <= check_x < 8 and 0 <= check_y < 8:
                        piece = board.chesspieces[check_x][check_y]
                        if piece != 0 and piece.piece_type == pieces.Pawn.PIECE_TYPE and piece.color == pieces.Piece.WHITE:
                            # Tốt đang bảo vệ vua
                            score += Heuristics.KING_SHIELD_BONUS
        
        # Kiểm tra tốt bảo vệ vua đen
        if black_king_x != -1:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    check_x, check_y = black_king_x + dx, black_king_y + dy
                    if 0 <= check_x < 8 and 0 <= check_y < 8:
                        piece = board.chesspieces[check_x][check_y]
                        if piece != 0 and piece.piece_type == pieces.Pawn.PIECE_TYPE and piece.color == pieces.Piece.BLACK:
                            # Tốt đang bảo vệ vua
                            score -= Heuristics.KING_SHIELD_BONUS
        
        return score
    
    @staticmethod
    def evaluate_mobility(board):
        """Đánh giá tính cơ động của các quân cờ"""
        # Tính số nước đi có thể của bên trắng
        white_moves = len(board.get_possible_moves(pieces.Piece.WHITE))
        
        # Tính số nước đi có thể của bên đen
        black_moves = len(board.get_possible_moves(pieces.Piece.BLACK))
        
        # Trả về điểm cơ động
        return (white_moves - black_moves) * Heuristics.MOBILITY_WEIGHT

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
            
            score = AI.alphabeta(copy, 3, -AI.INFINITE, AI.INFINITE, True)
            
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