import chess
import chess.engine

class StockfishAI:
    def __init__(self, engine_path, time_limit=0.1):
        self.engine_path = engine_path
        self.time_limit = time_limit
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)

    def get_best_move(self, fen):
        try:
            board = chess.Board(fen)
            result = self.engine.play(board, chess.engine.Limit(time=self.time_limit))
            return result.move
        except Exception as e:
            print(f"[ERROR] Lỗi khi lấy nước đi từ Stockfish: {e}")
            return None

    def quit(self):
        self.engine.quit()
