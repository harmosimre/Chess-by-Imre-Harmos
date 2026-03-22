import chess
from engine.constants import VALUES, INF


def evaluate(board):

    if board.is_checkmate():
        return -INF

    score = 0

    # ================= MATERIAL =================
    for p in VALUES:
        score += len(board.pieces(p, chess.WHITE)) * VALUES[p]
        score -= len(board.pieces(p, chess.BLACK)) * VALUES[p]

    # ================= PIECE SQUARE TABLES =================

    KNIGHT_TABLE = [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ]

    PAWN_TABLE = [
          0, 0, 0, 0, 0, 0, 0, 0,
         50,50,50,50,50,50,50,50,
         10,10,20,30,30,20,10,10,
          5, 5,10,25,25,10, 5, 5,
          0, 0, 0,20,20, 0, 0, 0,
          5,-5,-10, 0, 0,-10,-5, 5,
          5,10,10,-20,-20,10,10, 5,
          0, 0, 0, 0, 0, 0, 0, 0
    ]

    BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
    ]

    ROOK_TABLE = [
    0,0,5,10,10,5,0,0,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    5,10,10,10,10,10,10,5,
    0,0,0,0,0,0,0,0
    ]

    QUEEN_TABLE = [
    -20,-10,-10,-5,-5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,   0,  5,  5,  5,  5,  0,-5,
    0,    0,  5,  5,  5,  5,  0,-5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10,-5,-5,-10,-10,-20
    ]

    for sq in board.pieces(chess.KNIGHT, chess.WHITE):
        score += KNIGHT_TABLE[sq]

    for sq in board.pieces(chess.KNIGHT, chess.BLACK):
        score -= KNIGHT_TABLE[chess.square_mirror(sq)]

    for sq in board.pieces(chess.PAWN, chess.WHITE):
        score += PAWN_TABLE[sq]

    for sq in board.pieces(chess.PAWN, chess.BLACK):
        score -= PAWN_TABLE[chess.square_mirror(sq)]


    for sq in board.pieces(chess.BISHOP, chess.WHITE):
        score += BISHOP_TABLE[sq]

    for sq in board.pieces(chess.BISHOP, chess.BLACK):
        score -= BISHOP_TABLE[chess.square_mirror(sq)]

    for sq in board.pieces(chess.ROOK, chess.WHITE):
        score += ROOK_TABLE[sq]

    for sq in board.pieces(chess.ROOK, chess.BLACK):
        score -= ROOK_TABLE[chess.square_mirror(sq)]

    for sq in board.pieces(chess.QUEEN, chess.WHITE):
        score += QUEEN_TABLE[sq]

    for sq in board.pieces(chess.QUEEN, chess.BLACK):
        score -= QUEEN_TABLE[chess.square_mirror(sq)]

    # ================= BISHOP PAIR =================
    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
        score += 40
    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
        score -= 40

    # ================= PAWN STRUCTURE =================

    for color in [chess.WHITE, chess.BLACK]:

        pawns = list(board.pieces(chess.PAWN, color))
        files = [chess.square_file(p) for p in pawns]

        for p in pawns:

            file = chess.square_file(p)
            rank = chess.square_rank(p)

            # doubled pawn
            if files.count(file) > 1:
                score += -30 if color == chess.WHITE else 30

            # isolated pawn
            if file-1 not in files and file+1 not in files:
                score += -20 if color == chess.WHITE else 20

            # passed pawn
            passed = True
            for opp in board.pieces(chess.PAWN, not color):
                if abs(chess.square_file(opp) - file) <= 1:
                    if (color == chess.WHITE and chess.square_rank(opp) > rank) or \
                       (color == chess.BLACK and chess.square_rank(opp) < rank):
                        passed = False
                        break

            if passed:
                bonus = 40 + (rank * 5 if color == chess.WHITE else (7-rank)*5)
                score += bonus if color == chess.WHITE else -bonus

            

    # ================= ROOK OPEN FILE =================

    for color in [chess.WHITE, chess.BLACK]:
        for r in board.pieces(chess.ROOK, color):

            file = chess.square_file(r)

            own_pawn = any(chess.square_file(p)==file for p in board.pieces(chess.PAWN,color))
            opp_pawn = any(chess.square_file(p)==file for p in board.pieces(chess.PAWN,not color))

            if not own_pawn and not opp_pawn:
                score += 25 if color == chess.WHITE else -25
            elif not own_pawn:
                score += 10 if color == chess.WHITE else -10

    # ================= KING SAFETY =================

    for color in [chess.WHITE, chess.BLACK]:

        ksq = board.king(color)
        if ksq is None:
            continue

        shield = 0
        for sq in chess.SquareSet(chess.BB_KING_ATTACKS[ksq]):
            piece = board.piece_at(sq)
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                shield += 1

        penalty = (3 - shield) * 15
        score += -penalty if color == chess.WHITE else penalty

    # ================= MOBILITY =================

    turn = board.turn
    my_moves = board.legal_moves.count()
    board.push(chess.Move.null())
    opp_moves = board.legal_moves.count()
    board.pop()

    mobility_score = 3 * (my_moves - opp_moves)

    score += mobility_score if turn == chess.WHITE else -mobility_score


    # ===== piece activity =====

    for sq in board.pieces(chess.BISHOP, chess.WHITE):
        score += 3 * len(board.attacks(sq))

    for sq in board.pieces(chess.BISHOP, chess.BLACK):
        score -= 3 * len(board.attacks(sq))

    for sq in board.pieces(chess.ROOK, chess.WHITE):
        score += 2 * len(board.attacks(sq))

    for sq in board.pieces(chess.ROOK, chess.BLACK):
        score -= 2 * len(board.attacks(sq))


    wk = board.king(chess.BLACK)
    bk = board.king(chess.WHITE)

    if wk is not None:
        for sq in board.pieces(chess.QUEEN, chess.WHITE):
            score += 14 - chess.square_distance(sq, wk)

    if bk is not None:
        for sq in board.pieces(chess.QUEEN, chess.BLACK):
            score -= 14 - chess.square_distance(sq, bk)


    for sq in board.pieces(chess.KNIGHT, chess.WHITE):
        file = chess.square_file(sq)

        if not any(
            abs(chess.square_file(p)-file)<=1 and
            chess.square_rank(p)>chess.square_rank(sq)
            for p in board.pieces(chess.PAWN, chess.BLACK)
        ):
            score += 30

    for sq in board.pieces(chess.KNIGHT, chess.BLACK):
        file = chess.square_file(sq)

        if not any(
            abs(chess.square_file(p)-file)<=1 and
            chess.square_rank(p)<chess.square_rank(sq)
            for p in board.pieces(chess.PAWN, chess.WHITE)
        ):
            score -= 30


    CENTER = [
        chess.C4,chess.D4,chess.E4,chess.F4,
        chess.C5,chess.D5,chess.E5,chess.F5
    ]

    for sq in CENTER:
        p = board.piece_at(sq)
        if p:
            score += 12 if p.color else -12

    

    # ===== ENDGAME KING ACTIVITY =====

    material = 0
    for p in VALUES:
        material += len(board.pieces(p, chess.WHITE)) * VALUES[p]
        material += len(board.pieces(p, chess.BLACK)) * VALUES[p]

    ENDGAME = material < 2600

    KING_TABLE = [
    -50,-30,-30,-30,-30,-30,-30,-50,
    -30,-10,  0,  0,  0,  0,-10,-30,
    -30,  0, 20, 30, 30, 20,  0,-30,
    -30,  0, 30, 40, 40, 30,  0,-30,
    -30,  0, 30, 40, 40, 30,  0,-30,
    -30,  0, 20, 30, 30, 20,  0,-30,
    -30,-10,  0,  0,  0,  0,-10,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
    ]

    if ENDGAME:
        for sq in board.pieces(chess.KING, chess.WHITE):
            score += KING_TABLE[sq]

        for sq in board.pieces(chess.KING, chess.BLACK):
            score -= KING_TABLE[chess.square_mirror(sq)]


    # ===== PASSED PAWN RUN =====

    for sq in board.pieces(chess.PAWN, chess.WHITE):
        rank = chess.square_rank(sq)
        score += rank * rank * 2

    for sq in board.pieces(chess.PAWN, chess.BLACK):
        rank = 7 - chess.square_rank(sq)
        score -= rank * rank * 2


    for r in board.pieces(chess.ROOK, chess.WHITE):
        for p in board.pieces(chess.PAWN, chess.WHITE):
            if chess.square_file(r) == chess.square_file(p):
                if chess.square_rank(r) < chess.square_rank(p):
                    score += 20

    for r in board.pieces(chess.ROOK, chess.BLACK):
        for p in board.pieces(chess.PAWN, chess.BLACK):
            if chess.square_file(r) == chess.square_file(p):
                if chess.square_rank(r) > chess.square_rank(p):
                    score -= 20


    

    return score if board.turn else -score