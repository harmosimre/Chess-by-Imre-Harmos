import chess
import time
from concurrent.futures import ThreadPoolExecutor

from .constants import *
from .evaluation import evaluate
from .move_order import ordered_moves
from .neural_eval import neural_eval
from .nnue import nnue
import chess.syzygy
import chess.polyglot


BOOK1 = chess.polyglot.open_reader(
    r"D:\Chess by Imre Harmos\openings.bin"
)

BOOK2 = chess.polyglot.open_reader(
    r"D:\Chess by Imre Harmos\komodo.bin"
)

TB = chess.syzygy.open_tablebase(
    r"D:\Chess by Imre Harmos additional files\Endgame_database"
)

POOL = ThreadPoolExecutor(max_workers=8)

def book_move(board):

    try:
        return BOOK1.weighted_choice(board).move
    except:
        pass

    try:
        return BOOK2.weighted_choice(board).move
    except:
        pass

    return None
    

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

    # ===== TABLEBASE DRAW CUTOFF =====
    if len(board.piece_map()) <= 5:
        try:
            wdl = TB.probe_wdl(board)
            if wdl == 0:
                return 0
        except:
            pass

    stand = evaluate(board)
    if stand + 200 < alpha:
        return alpha
    
    if stand >= beta:
        return beta

    if stand > alpha:
        alpha = stand

    moves = [m for m in board.legal_moves if board.is_capture(m)]

    def capture_score(board, move):

        # EN PASSANT
        if board.is_en_passant(move):
            return VALUES[chess.PAWN]

        piece = board.piece_at(move.to_square)

        if piece is None:
            return 0

        return VALUES[piece.piece_type]

    moves.sort(
        key=lambda m: see(board, m),
        reverse=True
    )

    for move in moves:

        extension = 1 if board.gives_check(move) else 0

        nnue.push(board, move)
        board.push(move)

        score = -quiescence(board, -beta, -alpha)

        if extension:
            score = max(score,
                -search(board, 0, -beta, -alpha, 0)
            )

        board.pop()
        nnue.pop()

        if score >= beta:
            return beta

        if score > alpha:
            alpha = score

    return alpha


# ================= SEARCH =================

def search(board, depth, alpha, beta, ply):

    global STOP_SEARCH, NODES

    # ===== safe stop
    if STOP_SEARCH:
        return evaluate(board)
    
    if depth <= 2 and not board.is_check():
        return (evaluate(board) + nnue.evaluate()) // 2

    NODES += 1

        # ===== TABLEBASE CUTOFF =====
    if len(board.piece_map()) <= 5:
        try:
            wdl = TB.probe_wdl(board)

            if wdl is not None:
                if wdl > 0:
                    return 10000 - ply
                elif wdl < 0:
                    return -10000 + ply
                else:
                    return 0
        except:
            pass

    # ===== mate distance pruning
    alpha = max(alpha, -INF + ply)
    beta = min(beta, INF - ply)
    if alpha >= beta:
        return alpha

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

    static_eval = (evaluate(board) * 2 + nnue.evaluate()) // 3

    # ===== reverse futility
    if depth <= 3 and not board.is_check():
        margin = 100 + 70 * depth
        if static_eval - margin >= beta:
            return static_eval

    # ===== null move (zugzwang safe)
    # ===== null move =====
    if (
        depth >= 3
        and not board.is_check()
        and any(board.pieces(pt, board.turn)
                for pt in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT])
    ):
        R = 3 + depth // 4

        board.push(chess.Move.null())
        score = -search(board, depth - R, -beta, -beta + 1, ply + 1)
        board.pop()

        if score >= beta:
            return beta

    best_move = None
    legal_moves = 0
    first = True

    moves = ordered_moves(board, tt_move, ply)

    for move_index, move in enumerate(moves):

        # ===== modern LMP
        if depth <= 4 and move_index > 4 + depth * depth \
           and not board.is_capture(move):
            break

        extension = 1 if board.gives_check(move) else 0

        piece = board.piece_at(move.from_square)
        king_move = piece and piece.piece_type == chess.KING

        nnue.push(board, move)
        board.push(move)

        if king_move:
            nnue.rebuild(board)

        legal_moves += 1

        if first:
            score = -search(board, depth - 1 + extension,
                            -beta, -alpha, ply + 1)
            first = False
        else:

            reduction = 0
            if (
                depth >= 3
                and move_index > 3
                and not board.is_capture(move)
                and not board.gives_check(move)
            ):
                reduction = depth // 3

            score = -search(
                board,
                depth - 1 - reduction + extension,
                -alpha - 1,
                -alpha,
                ply + 1
            )

            if alpha < score < beta:
                score = -search(
                    board,
                    depth - 1 + extension,
                    -beta,
                    -alpha,
                    ply + 1
                )

        board.pop()
        nnue.pop()
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

    if legal_moves == 0:
        if board.is_check():
            return -INF + ply
        return 0

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

def find_best_move(board, max_time):

    # ===== OPENING BOOK =====
    if board.fullmove_number <= 12:
        move = book_move(board)
        if move:
            return move
    
    # ===== TABLEBASE ROOT =====
    if len(board.piece_map()) <= 5:
        try:
            move = TB.probe_root(board)
            if move:
                return move
        except:
            pass

    global STOP_SEARCH, NODES
    nnue.rebuild(board)
    STOP_SEARCH = False
    start = time.time()

    best_move = None
    last_score = 0
    depth = 1

    moves = ordered_moves(board, None, 0)

    while True:

        if time.time() - start > max_time:
            break

        best_score = -INF

        for move in moves:

            nnue.push(board, move)
            board.push(move)

            score = -search(board, depth - 1, -INF, INF, 1)

            board.pop()
            nnue.pop()

            if score > best_score:
                best_score = score
                best_move = move

        last_score = best_score
        depth += 1

    STOP_SEARCH = True

    return best_move