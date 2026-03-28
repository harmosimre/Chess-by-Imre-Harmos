import numpy as np
import chess


# ================= NETWORK SIZE =================

FEATURES = 64 * 12 * 64
HIDDEN = 64


# ================= FEATURE INDEX =================

def nnue_index(king_sq, piece_sq, piece_type, color):
    return (
        king_sq * 12 * 64 +
        (piece_type - 1 + (0 if color else 6)) * 64 +
        piece_sq
    )


# ================= NNUE =================

class IncrementalNNUE:

    def __init__(self):

        # üres init (nem random!)
        self.W1 = np.zeros((FEATURES, HIDDEN), dtype=np.float32)
        self.B1 = np.zeros(HIDDEN, dtype=np.float32)

        self.W2 = np.zeros(HIDDEN, dtype=np.float32)
        self.B2 = 0.0

        self.acc = None
        self.stack = []

    # ================= LOAD =================

    def load(self, path="nnue_weights.npz"):

        data = np.load(path)

        self.W1 = data["W1"]
        self.B1 = data["B1"]
        self.W2 = data["W2"]
        self.B2 = float(data["B2"])

        print("NNUE weights loaded!")
    

    # ================= FULL REBUILD =================

    def rebuild(self, board):

        acc = self.B1.copy()

        wk = board.king(chess.WHITE)
        bk = board.king(chess.BLACK)

        for sq, piece in board.piece_map().items():

            acc += self.W1[
                nnue_index(wk, sq, piece.piece_type, piece.color)
            ]

            acc -= self.W1[
                nnue_index(bk, sq, piece.piece_type, piece.color)
            ]

        self.acc = acc

    # ================= PUSH =================

    def push(self, board, move):

        self.stack.append(self.acc.copy())

        piece = board.piece_at(move.from_square)

        # KING MOVE → FULL REBUILD
        if piece.piece_type == chess.KING:
            board.push(move)
            self.rebuild(board)
            board.pop()
            return

        wk = board.king(chess.WHITE)
        bk = board.king(chess.BLACK)

        # REMOVE FROM OLD SQUARE
        self.acc -= self.W1[
            nnue_index(wk, move.from_square,
                       piece.piece_type, piece.color)
        ]
        self.acc += self.W1[
            nnue_index(bk, move.from_square,
                       piece.piece_type, piece.color)
        ]

        # CAPTURE
        if board.is_capture(move):

            if board.is_en_passant(move):

                if piece.color == chess.WHITE:
                    cap_sq = move.to_square - 8
                else:
                    cap_sq = move.to_square + 8

                captured_type = chess.PAWN
                captured_color = not piece.color

            else:
                cap_sq = move.to_square
                captured_piece = board.piece_at(cap_sq)

                if captured_piece is not None:
                    captured_type = captured_piece.piece_type
                    captured_color = captured_piece.color
                else:
                    cap_sq = None

            if cap_sq is not None:

                self.acc -= self.W1[
                    nnue_index(wk, cap_sq,
                               captured_type,
                               captured_color)
                ]
                self.acc += self.W1[
                    nnue_index(bk, cap_sq,
                               captured_type,
                               captured_color)
                ]

        # ADD TO NEW SQUARE
        self.acc += self.W1[
            nnue_index(wk, move.to_square,
                       piece.piece_type, piece.color)
        ]
        self.acc -= self.W1[
            nnue_index(bk, move.to_square,
                       piece.piece_type, piece.color)
        ]

        # PROMOTION
        if move.promotion:

            self.acc -= self.W1[
                nnue_index(wk, move.to_square,
                           chess.PAWN,
                           piece.color)
            ]
            self.acc += self.W1[
                nnue_index(bk, move.to_square,
                           chess.PAWN,
                           piece.color)
            ]

            self.acc += self.W1[
                nnue_index(wk, move.to_square,
                           move.promotion,
                           piece.color)
            ]
            self.acc -= self.W1[
                nnue_index(bk, move.to_square,
                           move.promotion,
                           piece.color)
            ]

    # ================= POP =================

    def pop(self):
        self.acc = self.stack.pop()

    # ================= EVAL =================

    def evaluate(self):

        if self.acc is None:
            return 0

        h = np.maximum(self.acc, 0)
        score = float(h @ self.W2 + self.B2)

        # scaling (nagyon fontos!)
        return int(score * 100)


# ================= GLOBAL =================

nnue = IncrementalNNUE()
nnue.load("nnue_weights.npz")
