import multiprocessing as mp
import chess
import chess.engine
import random
import time

PATH = r"D:\Chess by Imre Harmos additional files\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"

TARGET = 500000
WORKERS = 4


def worker(q):

    print("worker started")

    engine = chess.engine.SimpleEngine.popen_uci(PATH)

    while True:

        board = chess.Board()

        for _ in range(10):

            if board.is_game_over():
                break

            moves = list(board.legal_moves)

            if not moves:
                break

            board.push(random.choice(moves))

        info = engine.analyse(board, chess.engine.Limit(depth=10))
        score = info["score"].white().score(mate_score=10000)

        if score is not None:
            q.put(board.fen() + " | " + str(score))


def writer(q):

    f = open("train.txt", "w")

    count = 0
    start = time.time()

    while count < TARGET:

        try:
            line = q.get(timeout=10)
        except:
            print("waiting...")
            continue

        f.write(line + "\n")
        count += 1

        if count % 1000 == 0:

            elapsed = time.time() - start
            speed = count / elapsed
            eta = (TARGET-count)/speed

            print(count, "speed", speed, "ETA", eta/60)

    f.close()


if __name__ == "__main__":

    mp.set_start_method("spawn")

    q = mp.Queue()

    procs = []

    for _ in range(WORKERS):
        p = mp.Process(target=worker, args=(q,))
        p.start()
        procs.append(p)

    writer(q)

    for p in procs:
        p.terminate()