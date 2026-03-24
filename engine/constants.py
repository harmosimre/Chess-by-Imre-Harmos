import chess

# ================= ENGINE LIMITS =================

INF = 999999

MAX_TIME = 1.0
STOP_SEARCH = False
NODES = 0


# ================= PIECE VALUES =================

VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}


# ================= TRANSPOSITION =================

TT = {}

EXACT = 0
LOWER = 1
UPPER = 2


# ================= MOVE ORDER =================

MAX_PLY = 256

KILLERS = [[None, None] for _ in range(MAX_PLY)]
HISTORY = {}