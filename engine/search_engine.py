import chess
import time
from concurrent.futures import ThreadPoolExecutor

from .constants import *
from .evaluation import evaluate
from .move_order import ordered_moves
from .neural_eval import neural_eval


POOL = ThreadPoolExecutor(max_workers=8)


# ================= SEE =================

def see(board, move):

    if not board.is_capture(move):
        return 0

    if board.is_en_passant(move):
        return VALUES[chess.PAWN] - VALUES[chess.PAWN]

    victim = board.piece_at(move.to_square)
    attacker = board.piece_at(move.from_square)

    if victim and attacker:
        return VALUES[victim.piece_type] - VALUES[attacker.piece_type]

    return 0


# ================= QUIESCENCE =================

def quiescence(board, alpha, beta):

    global NODES
    NODES += 1

    stand = evaluate(board)

    if stand >= beta:
        return beta

    if stand > alpha:
        alpha = stand

    moves = [
        m for m in board.legal_moves
        if board.is_capture(m) and see(board, m) >= -50
    ]

    def capture_score(board, move):

        # EN PASSANT
        if board.is_en_passant(move):
            return VALUES[chess.PAWN]

        piece = board.piece_at(move.to_square)

        if piece is None:
            return 0

        return VALUES[piece.piece_type]

    moves.sort(
        key=lambda m: capture_score(board, m),
        reverse=True
    )

    for move in moves:
        board.push(move)
        score = -quiescence(board, -beta, -alpha)
        board.pop()

        if score >= beta:
            return beta

        if score > alpha:
            alpha = score

    return alpha


# ================= SEARCH =================

def search(board, depth, alpha, beta, ply):

    global STOP_SEARCH, NODES

    if STOP_SEARCH:
        return neural_eval(board)

    NODES += 1

    original_alpha = alpha
    key = board._transposition_key()

    entry = TT.get(key)
    tt_move = None

    if entry:
        tt_depth, tt_score, tt_flag, tt_move = entry

        if tt_depth >= depth:

            if tt_flag == EXACT:
                return tt_score

            if tt_flag == LOWER and tt_score >= beta:
                return tt_score

            if tt_flag == UPPER and tt_score <= alpha:
                return tt_score

    if depth <= 0:
        return quiescence(board, alpha, beta)

    # ===== FUTILITY =====
    static_eval = evaluate(board)
    if depth == 1 and static_eval + 120 <= alpha:
        return static_eval

    # ===== NULL MOVE =====
    if depth >= 3 and not board.is_check():
        board.push(chess.Move.null())
        score = -search(board, depth - 3, -beta, -beta + 1, ply + 1)
        board.pop()

        if score >= beta:
            return beta

    best_move = None
    legal_count = 0
    first = True

    moves = ordered_moves(board, tt_move, ply)

    for move_index, move in enumerate(moves):

        # ===== LMP =====
        if depth <= 3 and move_index > 6 and not board.is_capture(move):
            break

        board.push(move)

        if first:
            score = -search(board, depth - 1, -beta, -alpha, ply + 1)
            first = False
        else:

            reduction = 1 if (
                move_index > 3 and
                depth > 3 and
                not board.is_capture(move)
            ) else 0

            score = -search(
                board,
                depth - 1 - reduction,
                -alpha - 1,
                -alpha,
                ply + 1
            )

            if alpha < score < beta:
                score = -search(
                    board,
                    depth - 1,
                    -beta,
                    -alpha,
                    ply + 1
                )

        board.pop()

        legal_count += 1

        if score > alpha:
            alpha = score
            best_move = move

            if not board.is_capture(move):
                HISTORY[(board.turn, move.from_square, move.to_square)] = \
                    HISTORY.get(
                        (board.turn, move.from_square, move.to_square),
                        0
                    ) + depth * depth

        if alpha >= beta:

            if not board.is_capture(move):
                KILLERS[ply][1] = KILLERS[ply][0]
                KILLERS[ply][0] = move

            break

    flag = EXACT
    if alpha <= original_alpha:
        flag = UPPER
    elif alpha >= beta:
        flag = LOWER

    TT[key] = (depth, alpha, flag, best_move)

    return alpha


# ================= ROOT WORKER =================

def root_task(board, move, depth):

    b = board.copy()
    b.push(move)

    score = -search(b, depth - 1, -INF, INF, 1)

    return move, score


# ================= BEST MOVE =================

def find_best_move(board, max_time=1.0):

    global STOP_SEARCH, NODES

    STOP_SEARCH = False
    start = time.time()

    best_move = None
    last_score = 0
    depth = 1

    moves = ordered_moves(board, None, 0)

    while True:

        if time.time() - start > max_time:
            break

        window = 50

        while True:

            alpha = last_score - window
            beta = last_score + window

            futures = [
                POOL.submit(root_task, board, m, depth)
                for m in moves
            ]

            best_score = -INF

            for f in futures:
                move, score = f.result()

                if score > best_score:
                    best_score = score
                    best_move = move

            if best_score <= alpha:
                window *= 2
                continue

            if best_score >= beta:
                window *= 2
                continue

            break

        last_score = best_score
        depth += 1

    STOP_SEARCH = True

    return best_move