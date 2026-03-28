import chess
import numpy as np



PIECE_VALUES = np.array([0, 100, 320, 330, 500, 900, 0])

def neural_eval(board):

    score = 0

    # material
    for p in range(1, 6):
        score += PIECE_VALUES[p] * (
            len(board.pieces(p, chess.WHITE))
            - len(board.pieces(p, chess.BLACK))
        )

    # activity (nagyon gyors feature)
    for sq in board.pieces(chess.KNIGHT, chess.WHITE):
        score += 4 * len(board.attacks(sq))

    for sq in board.pieces(chess.KNIGHT, chess.BLACK):
        score -= 4 * len(board.attacks(sq))

    for sq in board.pieces(chess.BISHOP, chess.WHITE):
        score += 3 * len(board.attacks(sq))

    for sq in board.pieces(chess.BISHOP, chess.BLACK):
        score -= 3 * len(board.attacks(sq))

    return score if board.turn else -score