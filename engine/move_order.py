import chess
from .constants import VALUES, KILLERS, HISTORY

def mvv_lva(board, move):

    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)

        if victim and attacker:
            return 10 * VALUES[victim.piece_type] - VALUES[attacker.piece_type]

    return 0


def score_move(board, move, tt_move, ply):

    if ply >= len(KILLERS):
        return 0
    
    if move == tt_move:
        return 1_000_000

    if board.is_capture(move):
        return 500_000 + mvv_lva(board, move)

    if KILLERS[ply][0] == move:
        return 400_000

    if KILLERS[ply][1] == move:
        return 390_000

    return HISTORY.get(
        (board.turn, move.from_square, move.to_square),
        0
    )


def ordered_moves(board, tt_move, ply):

    moves = list(board.legal_moves)

    moves.sort(
        key=lambda m: score_move(board, m, tt_move, ply),
        reverse=True
    )

    return moves