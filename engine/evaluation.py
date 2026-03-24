import chess
from engine.constants import VALUES, INF

PAWN_MG = [
0,0,0,0,0,0,0,0,
5,10,10,-20,-20,10,10,5,
5,-5,-10,0,0,-10,-5,5,
0,0,0,20,20,0,0,0,
5,5,10,25,25,10,5,5,
10,10,20,30,30,20,10,10,
50,50,50,50,50,50,50,50,
0,0,0,0,0,0,0,0
]

PAWN_EG = [
0,0,0,0,0,0,0,0,
10,10,10,10,10,10,10,10,
20,20,20,20,20,20,20,20,
30,30,30,30,30,30,30,30,
40,40,40,40,40,40,40,40,
60,60,60,60,60,60,60,60,
80,80,80,80,80,80,80,80,
0,0,0,0,0,0,0,0
]

KNIGHT_MG = [
-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,0,5,5,0,-20,-40,
-30,5,10,15,15,10,5,-30,
-30,0,15,20,20,15,0,-30,
-30,5,15,20,20,15,5,-30,
-30,0,10,15,15,10,0,-30,
-40,-20,0,0,0,0,-20,-40,
-50,-40,-30,-30,-30,-30,-40,-50
]

KNIGHT_EG = [
-40,-30,-20,-20,-20,-20,-30,-40,
-30,-10,0,0,0,0,-10,-30,
-20,0,10,15,15,10,0,-20,
-20,5,15,20,20,15,5,-20,
-20,5,15,20,20,15,5,-20,
-20,0,10,15,15,10,0,-20,
-30,-10,0,0,0,0,-10,-30,
-40,-30,-20,-20,-20,-20,-30,-40
]

BISHOP_MG = [
-20,-10,-10,-10,-10,-10,-10,-20,
-10,5,0,0,0,0,5,-10,
-10,10,10,10,10,10,10,-10,
-10,0,10,10,10,10,0,-10,
-10,5,5,10,10,5,5,-10,
-10,0,5,10,10,5,0,-10,
-10,0,0,0,0,0,0,-10,
-20,-10,-10,-10,-10,-10,-10,-20
]

BISHOP_EG = [
-10,-5,-5,-5,-5,-5,-5,-10,
-5,10,0,0,0,0,10,-5,
-5,0,10,10,10,10,0,-5,
-5,5,10,15,15,10,5,-5,
-5,5,10,15,15,10,5,-5,
-5,0,10,10,10,10,0,-5,
-5,10,0,0,0,0,10,-5,
-10,-5,-5,-5,-5,-5,-5,-10
]

ROOK_MG = [
0,0,5,10,10,5,0,0,
-5,0,0,0,0,0,0,-5,
-5,0,0,0,0,0,0,-5,
-5,0,0,0,0,0,0,-5,
-5,0,0,0,0,0,0,-5,
-5,0,0,0,0,0,0,-5,
5,10,10,10,10,10,10,5,
0,0,0,0,0,0,0,0
]

ROOK_EG = [
0,0,10,10,10,10,0,0,
5,10,10,10,10,10,10,5,
-5,0,0,0,0,0,0,-5,
-5,0,0,0,0,0,0,-5,
-5,0,0,0,0,0,0,-5,
-5,0,0,0,0,0,0,-5,
5,10,10,10,10,10,10,5,
0,0,10,10,10,10,0,0
]

QUEEN_MG = [
-20,-10,-10,-5,-5,-10,-10,-20,
-10,0,0,0,0,0,0,-10,
-10,0,5,5,5,5,0,-10,
-5,0,5,5,5,5,0,-5,
0,0,5,5,5,5,0,-5,
-10,5,5,5,5,5,0,-10,
-10,0,5,0,0,0,0,-10,
-20,-10,-10,-5,-5,-10,-10,-20
]

QUEEN_EG = [
-10,-5,-5,-5,-5,-5,-5,-10,
-5,0,0,0,0,0,0,-5,
-5,0,5,5,5,5,0,-5,
-5,0,5,5,5,5,0,-5,
-5,0,5,5,5,5,0,-5,
-5,0,5,5,5,5,0,-5,
-5,0,0,0,0,0,0,-5,
-10,-5,-5,-5,-5,-5,-5,-10
]


KING_MG = [
10,20,20,0,0,20,20,10,
10,10,0,0,0,0,10,10,
0,0,-10,-10,-10,-10,0,0,
-10,-10,-20,-20,-20,-20,-10,-10,
-20,-20,-30,-30,-30,-30,-20,-20,
-30,-30,-40,-40,-40,-40,-30,-30,
-40,-40,-50,-50,-50,-50,-40,-40,
-40,-40,-50,-50,-50,-50,-40,-40
]

KING_EG = [
-50,-30,-30,-30,-30,-30,-30,-50,
-30,-10,0,0,0,0,-10,-30,
-30,0,20,30,30,20,0,-30,
-30,0,30,40,40,30,0,-30,
-30,0,30,40,40,30,0,-30,
-30,0,20,30,30,20,0,-30,
-30,-10,0,0,0,0,-10,-30,
-50,-30,-30,-30,-30,-30,-30,-50
]

PAWN_HASH = {}


PHASE = {
    chess.KNIGHT: 1,
    chess.BISHOP: 1,
    chess.ROOK: 2,
    chess.QUEEN: 4
}

MAX_PHASE = 24
CENTER = {chess.D4, chess.E4, chess.D5, chess.E5}


def see(board, square):

    gain = []
    side = board.turn

    attackers = board.attackers(side, square)
    if not attackers:
        return 0

    from_sq = min(attackers, key=lambda s: VALUES[board.piece_at(s).piece_type])
    captured = board.piece_at(square)

    gain.append(VALUES[captured.piece_type])

    board.push(chess.Move(from_sq, square))

    score = -see(board, square)

    board.pop()

    return max(0, gain[0] - score)

def see_square(board, sq):

    piece = board.piece_at(sq)
    if piece is None:
        return 0

    gain = VALUES[piece.piece_type]

    attackers = board.attackers(not piece.color, sq)
    defenders = board.attackers(piece.color, sq)

    if not attackers:
        return 0

    min_att = min(
        VALUES[board.piece_at(a).piece_type]
        for a in attackers
    )

    min_def = INF
    if defenders:
        min_def = min(
            VALUES[board.piece_at(d).piece_type]
            for d in defenders
        )

    return gain - min_att + min_def



def evaluate(board):

    if board.is_checkmate():
        return -INF

    mg = 0
    eg = 0

    # ================= MATERIAL =================
    for p in VALUES:
        mg += len(board.pieces(p, chess.WHITE)) * VALUES[p]
        mg -= len(board.pieces(p, chess.BLACK)) * VALUES[p]

    eg = mg

    # ================= PSQT =================

    for sq in board.pieces(chess.KNIGHT, chess.WHITE):
        mg += KNIGHT_MG[sq]
        eg += KNIGHT_EG[sq]

    for sq in board.pieces(chess.KNIGHT, chess.BLACK):
        ms = chess.square_mirror(sq)
        mg -= KNIGHT_MG[ms]
        eg -= KNIGHT_EG[ms]

    for sq in board.pieces(chess.BISHOP, chess.WHITE):
        mg += BISHOP_MG[sq]
        eg += BISHOP_EG[sq]

    for sq in board.pieces(chess.BISHOP, chess.BLACK):
        ms = chess.square_mirror(sq)
        mg -= BISHOP_MG[ms]
        eg -= BISHOP_EG[ms]

    for sq in board.pieces(chess.ROOK, chess.WHITE):
        mg += ROOK_MG[sq]
        eg += ROOK_EG[sq]

    for sq in board.pieces(chess.ROOK, chess.BLACK):
        ms = chess.square_mirror(sq)
        mg -= ROOK_MG[ms]
        eg -= ROOK_EG[ms]

    for sq in board.pieces(chess.QUEEN, chess.WHITE):
        mg += QUEEN_MG[sq]
        eg += QUEEN_EG[sq]

    for sq in board.pieces(chess.QUEEN, chess.BLACK):
        ms = chess.square_mirror(sq)
        mg -= QUEEN_MG[ms]
        eg -= QUEEN_EG[ms]

    for sq in board.pieces(chess.KING, chess.WHITE):
        mg += KING_MG[sq]
        eg += KING_EG[sq]

    for sq in board.pieces(chess.KING, chess.BLACK):
        ms = chess.square_mirror(sq)
        mg -= KING_MG[ms]
        eg -= KING_EG[ms]

    # ================= MOBILITY =================
    mob = 0

    for move in board.generate_legal_moves():

        piece = board.piece_at(move.from_square)
        if piece is None:
            continue

        if piece.piece_type in (
            chess.KNIGHT,
            chess.BISHOP,
            chess.ROOK,
            chess.QUEEN
        ):
            mob += 1 if piece.color == chess.WHITE else -1

    mg += mob * 2

    # ================= ROOK FILES =================
    for color in [chess.WHITE, chess.BLACK]:

        sign = 1 if color == chess.WHITE else -1

        for r in board.pieces(chess.ROOK, color):

            file = chess.square_file(r)
            file_mask = chess.BB_FILES[file]

            own_pawns = file_mask & board.pieces_mask(chess.PAWN, color)
            opp_pawns = file_mask & board.pieces_mask(chess.PAWN, not color)

            if not own_pawns and not opp_pawns:
                mg += sign * 25
            elif not own_pawns:
                mg += sign * 12

    # ================= ROOK 7th =================
    for r in board.pieces(chess.ROOK, chess.WHITE):
        if chess.square_rank(r) == 6:
            mg += 20

    for r in board.pieces(chess.ROOK, chess.BLACK):
        if chess.square_rank(r) == 1:
            mg -= 20

    # rook mobility bonus
    for sq in board.pieces(chess.ROOK, chess.WHITE):
        mg += len(board.attacks(sq)) // 2

    for sq in board.pieces(chess.ROOK, chess.BLACK):
        mg -= len(board.attacks(sq)) // 2

    # queen king tropism
    wk = board.king(chess.WHITE)
    bk = board.king(chess.BLACK)

    for q in board.pieces(chess.QUEEN, chess.WHITE):
        dist = chess.square_distance(q, bk)
        mg += max(0, 14 - dist)

    for q in board.pieces(chess.QUEEN, chess.BLACK):
        dist = chess.square_distance(q, wk)
        mg -= max(0, 14 - dist)

    # ================= BISHOP PAIR =================
    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
        mg += 35
    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
        mg -= 35

    # ================= PAWN STRUCTURE =================


    
    pawn_key = (
        tuple(sorted(board.pieces(chess.PAWN, chess.WHITE))),
        tuple(sorted(board.pieces(chess.PAWN, chess.BLACK))),
        board.turn
    )

    if pawn_key in PAWN_HASH:
        pmg, peg = PAWN_HASH[pawn_key]
        mg += pmg
        eg += peg
    else:

        pmg = 0
        peg = 0

        for color in [chess.WHITE, chess.BLACK]:

            pawns = board.pieces(chess.PAWN, color)
            sign = 1 if color else -1

            files = [0]*8
            for p in pawns:
                files[chess.square_file(p)] += 1

            # doubled
            for f in files:
                if f > 1:
                    pmg -= sign * 12*(f-1)
                    peg -= sign * 16*(f-1)

            # isolated
            for p in pawns:
                file = chess.square_file(p)

                iso = True
                for adj in [file-1, file+1]:
                    if 0 <= adj <= 7:
                        if any(chess.square_file(pp) == adj for pp in pawns):
                            iso = False

                if iso:
                    pmg -= sign * 18
                    peg -= sign * 10

        PAWN_HASH[pawn_key] = (pmg, peg)
        mg += pmg
        eg += peg

    # ================= PASSED PAWNS =================
    passed_list = []

    for color in [chess.WHITE, chess.BLACK]:
        for p in board.pieces(chess.PAWN, color):

            file = chess.square_file(p)
            rank = chess.square_rank(p)

            passed = True
            for opp in board.pieces(chess.PAWN, not color):
                if abs(chess.square_file(opp) - file) <= 1:
                    if (color and chess.square_rank(opp) > rank) or \
                       (not color and chess.square_rank(opp) < rank):
                        passed = False

            if passed:
                val = (rank if color else 7-rank)*20
                if color:
                    eg += val
                else:
                    eg -= val

                passed_list.append((p, color))

    # rook behind passed pawn
    for sq, color in passed_list:
        file = chess.square_file(sq)
        rank = chess.square_rank(sq)

        for r in board.pieces(chess.ROOK, color):
            if chess.square_file(r) == file:
                if (color and chess.square_rank(r) < rank) or \
                   (not color and chess.square_rank(r) > rank):
                    mg += 20 if color else -20


    # ===== CENTER PAWN BONUS =====

    if board.fullmove_number <= 15:

        if board.piece_at(chess.E4) == chess.Piece(chess.PAWN, chess.WHITE):
            mg += 60
        if board.piece_at(chess.D4) == chess.Piece(chess.PAWN, chess.WHITE):
            mg += 60

        if board.piece_at(chess.E5) == chess.Piece(chess.PAWN, chess.BLACK):
            mg -= 60
        if board.piece_at(chess.D5) == chess.Piece(chess.PAWN, chess.BLACK):
            mg -= 60

    # ===== DEVELOPMENT BONUS =====

    if board.fullmove_number <= 12:

        for sq in board.pieces(chess.KNIGHT, chess.WHITE):
            if sq not in (chess.B1, chess.G1):
                mg += 20

        for sq in board.pieces(chess.KNIGHT, chess.BLACK):
            if sq not in (chess.B8, chess.G8):
                mg -= 20

        for sq in board.pieces(chess.BISHOP, chess.WHITE):
            if sq not in (chess.C1, chess.F1):
                mg += 18

        for sq in board.pieces(chess.BISHOP, chess.BLACK):
            if sq not in (chess.C8, chess.F8):
                mg -= 18


    # ================= KNIGHT OUTPOST =================
    for color in [chess.WHITE, chess.BLACK]:

        sign = 1 if color == chess.WHITE else -1

        for n in board.pieces(chess.KNIGHT, color):

            file = chess.square_file(n)
            rank = chess.square_rank(n)

            supported = any(
                chess.square_file(p) in (file-1, file+1)
                and (
                    (color and chess.square_rank(p) == rank-1)
                    or
                    (not color and chess.square_rank(p) == rank+1)
                )
                for p in board.pieces(chess.PAWN, color)
            )

            attacked_by_pawn = any(
                abs(chess.square_file(p) - file) <= 1 and
                (
                    (color and chess.square_rank(p) > rank)
                    or
                    (not color and chess.square_rank(p) < rank)
                )
                for p in board.pieces(chess.PAWN, not color)
            )

            if supported and not attacked_by_pawn:
                mg += sign * 30

    # ================= KING SHIELD =================
    for color in [chess.WHITE, chess.BLACK]:

        ksq = board.king(color)
        if ksq is None:
            continue

        file = chess.square_file(ksq)
        rank = chess.square_rank(ksq)

        if (color and rank <= 1) or (not color and rank >= 6):

            for df in [-1,0,1]:
                f = file + df
                if 0 <= f <= 7:
                    sq = chess.square(f, 1 if color else 6)
                    piece = board.piece_at(sq)

                    if piece and piece.piece_type == chess.PAWN and piece.color == color:
                        mg += 12 if color else -12
                    else:
                        mg -= 14 if color else 14

    # ================= KING ATTACK MAP =================
    ATTACK_W = {
        chess.PAWN: 1,
        chess.KNIGHT: 2,
        chess.BISHOP: 2,
        chess.ROOK: 3,
        chess.QUEEN: 5
    }

    for defender in [chess.WHITE, chess.BLACK]:

        ksq = board.king(defender)
        if ksq is None:
            continue

        zone = chess.SquareSet(chess.BB_KING_ATTACKS[ksq]) | {ksq}
        units = 0

        for sq, piece in board.piece_map().items():
            if piece.color == defender:
                continue
            if piece.piece_type != chess.KING and board.attacks(sq) & zone:
                units += ATTACK_W[piece.piece_type]

        if defender == chess.WHITE:
            mg -= units * units
        else:
            mg += units * units

    

    # ================= HANGING (fast) =================
    for sq, piece in board.piece_map().items():

        attackers = board.attackers(not piece.color, sq)
        defenders = board.attackers(piece.color, sq)

        if attackers and not defenders:
            penalty = VALUES[piece.piece_type] // 8

            if piece.color == chess.WHITE:
                mg -= penalty
                eg -= penalty
            else:
                mg += penalty
                eg += penalty

    # ===== EARLY QUEEN MOVE PENALTY =====

    if board.fullmove_number <= 12:

        wq = list(board.pieces(chess.QUEEN, chess.WHITE))
        bq = list(board.pieces(chess.QUEEN, chess.BLACK))

        if wq and wq[0] != chess.D1:
            mg -= 25

        if bq and bq[0] != chess.D8:
            mg += 25            

    # ===== CASTLED KING BONUS =====

    wk = board.king(chess.WHITE)
    bk = board.king(chess.BLACK)

    if wk in (chess.G1, chess.C1):
        mg += 40

    if bk in (chess.G8, chess.C8):
        mg -= 40
    # ================= SPACE =================
    for sq in CENTER:
        p = board.piece_at(sq)
        if p:
            mg += 15 if p.color else -15

    # ================= TEMPO =================
    mg += 5 if board.turn else -5

    # ================= PHASE =================
    phase = 0
    for p in PHASE:
        phase += PHASE[p]*(len(board.pieces(p, chess.WHITE)) +
                           len(board.pieces(p, chess.BLACK)))

    phase = min(phase, MAX_PHASE)

    score = (mg*phase + eg*(MAX_PHASE-phase)) // MAX_PHASE

    # ================= DRAWISH =================
    if len(board.piece_map()) <= 5:
        score //= 2

    return score if board.turn else -score