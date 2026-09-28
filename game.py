#!/usr/bin/env python3
"""Tekstgebaseerd schaakspel voor twee spelers.

Starten:  python schaken.py          (unicode-stukken)
          python schaken.py --ascii  (letters, als je terminal geen unicode toont)

Zetten invoeren als: e2e4  of  e2 e4  (promotie: e7e8q, e7e8r, e7e8b, e7e8n)
Commando's: moves, help, quit
"""
import sys

UNICODE = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',
}

KNIGHT = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
KING = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
DIAG = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
ORTHO = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def color(p):
    return 'w' if p.isupper() else 'b'


def on_board(r, c):
    return 0 <= r < 8 and 0 <= c < 8


def sq_name(r, c):
    return "abcdefgh"[c] + str(8 - r)


class Game:
    def __init__(self):
        self.board = [list("rnbqkbnr"), list("pppppppp")] \
            + [list("........") for _ in range(4)] \
            + [list("PPPPPPPP"), list("RNBQKBNR")]
        self.turn = 'w'
        self.castle = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.ep = None          # en-passant doelvakje (r, c)
        self.halfmove = 0       # voor de 50-zettenregel

    def copy(self):
        g = Game.__new__(Game)
        g.board = [row[:] for row in self.board]
        g.turn = self.turn
        g.castle = dict(self.castle)
        g.ep = self.ep
        g.halfmove = self.halfmove
        return g

    # ---------- aanvallen / schaak ----------
    def attacked(self, r, c, by):
        b = self.board
        # pionnen
        pr = r + 1 if by == 'w' else r - 1
        pawn = 'P' if by == 'w' else 'p'
        for dc in (-1, 1):
            if on_board(pr, c + dc) and b[pr][c + dc] == pawn:
                return True
        knight = 'N' if by == 'w' else 'n'
        for dr, dc in KNIGHT:
            if on_board(r + dr, c + dc) and b[r + dr][c + dc] == knight:
                return True
        king = 'K' if by == 'w' else 'k'
        for dr, dc in KING:
            if on_board(r + dr, c + dc) and b[r + dr][c + dc] == king:
                return True
        for dirs, pieces in ((DIAG, "bq"), (ORTHO, "rq")):
            for dr, dc in dirs:
                rr, cc = r + dr, c + dc
                while on_board(rr, cc):
                    p = b[rr][cc]
                    if p != '.':
                        if color(p) == by and p.lower() in pieces:
                            return True
                        break
                    rr += dr
                    cc += dc
        return False

    def find_king(self, side):
        k = 'K' if side == 'w' else 'k'
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == k:
                    return r, c

    def in_check(self, side=None):
        side = side or self.turn
        r, c = self.find_king(side)
        return self.attacked(r, c, 'b' if side == 'w' else 'w')

    # ---------- zetten genereren ----------
    def pseudo_moves(self):
        b, side = self.board, self.turn
        enemy = 'b' if side == 'w' else 'w'
        moves = []
        for r in range(8):
            for c in range(8):
                p = b[r][c]
                if p == '.' or color(p) != side:
                    continue
                t = p.lower()
                if t == 'p':
                    d = -1 if side == 'w' else 1
                    start = 6 if side == 'w' else 1
                    last = 0 if side == 'w' else 7
                    if on_board(r + d, c) and b[r + d][c] == '.':
                        self._add_pawn(moves, r, c, r + d, c, last, side)
                        if r == start and b[r + 2 * d][c] == '.':
                            moves.append((r, c, r + 2 * d, c, None))
                    for dc in (-1, 1):
                        rr, cc = r + d, c + dc
                        if not on_board(rr, cc):
                            continue
                        if b[rr][cc] != '.' and color(b[rr][cc]) == enemy:
                            self._add_pawn(moves, r, c, rr, cc, last, side)
                        elif self.ep == (rr, cc):
                            moves.append((r, c, rr, cc, None))
                elif t == 'n':
                    for dr, dc in KNIGHT:
                        self._step(moves, r, c, r + dr, c + dc, side)
                elif t == 'k':
                    for dr, dc in KING:
                        self._step(moves, r, c, r + dr, c + dc, side)
                    self._castling(moves, r, c, side, enemy)
                else:
                    dirs = DIAG if t == 'b' else ORTHO if t == 'r' else DIAG + ORTHO
                    for dr, dc in dirs:
                        rr, cc = r + dr, c + dc
                        while on_board(rr, cc):
                            if b[rr][cc] == '.':
                                moves.append((r, c, rr, cc, None))
                            else:
                                if color(b[rr][cc]) != side:
                                    moves.append((r, c, rr, cc, None))
                                break
                            rr += dr
                            cc += dc
        return moves

    def _step(self, moves, r, c, rr, cc, side):
        if on_board(rr, cc) and (self.board[rr][cc] == '.' or color(self.board[rr][cc]) != side):
            moves.append((r, c, rr, cc, None))

    def _add_pawn(self, moves, r, c, rr, cc, last, side):
        if rr == last:
            for promo in "qrbn":
                moves.append((r, c, rr, cc, promo.upper() if side == 'w' else promo))
        else:
            moves.append((r, c, rr, cc, None))

    def _castling(self, moves, r, c, side, enemy):
        home = 7 if side == 'w' else 0
        if (r, c) != (home, 4) or self.attacked(r, c, enemy):
            return
        b = self.board
        ks, qs = ('K', 'Q') if side == 'w' else ('k', 'q')
        rook = 'R' if side == 'w' else 'r'
        if self.castle[ks] and b[home][7] == rook and b[home][5] == '.' and b[home][6] == '.' \
                and not self.attacked(home, 5, enemy) and not self.attacked(home, 6, enemy):
            moves.append((r, c, home, 6, None))
        if self.castle[qs] and b[home][0] == rook and all(b[home][x] == '.' for x in (1, 2, 3)) \
                and not self.attacked(home, 3, enemy) and not self.attacked(home, 2, enemy):
            moves.append((r, c, home, 2, None))

    def legal_moves(self):
        side = self.turn
        result = []
        for m in self.pseudo_moves():
            g = self.apply(m)
            if not g.in_check(side):
                result.append(m)
        return result

    # ---------- zet uitvoeren ----------
    def apply(self, m):
        r1, c1, r2, c2, promo = m
        g = self.copy()
        b = g.board
        p = b[r1][c1]
        target = b[r2][c2]
        b[r1][c1] = '.'
        if p.lower() == 'p' and c1 != c2 and target == '.':   # en passant
            b[r1][c2] = '.'
        b[r2][c2] = promo if promo else p
        if p.lower() == 'k' and abs(c2 - c1) == 2:            # rokade
            if c2 > c1:
                b[r1][5], b[r1][7] = b[r1][7], '.'
            else:
                b[r1][3], b[r1][0] = b[r1][0], '.'
        g.ep = ((r1 + r2) // 2, c1) if p.lower() == 'p' and abs(r2 - r1) == 2 else None
        if p == 'K':
            g.castle['K'] = g.castle['Q'] = False
        if p == 'k':
            g.castle['k'] = g.castle['q'] = False
        for (rr, cc), key in (((7, 0), 'Q'), ((7, 7), 'K'), ((0, 0), 'q'), ((0, 7), 'k')):
            if (r1, c1) == (rr, cc) or (r2, c2) == (rr, cc):
                g.castle[key] = False
        g.halfmove = 0 if (p.lower() == 'p' or target != '.') else self.halfmove + 1
        g.turn = 'b' if self.turn == 'w' else 'w'
        return g

    # ---------- einde van het spel ----------
    def insufficient_material(self):
        pieces = [p for row in self.board for p in row if p != '.' and p.lower() != 'k']
        if not pieces:
            return True
        if len(pieces) == 1 and pieces[0].lower() in "bn":
            return True
        return False

    # ---------- weergave ----------
    def show(self, ascii_mode=False):
        print()
        for r in range(8):
            row = []
            for c in range(8):
                p = self.board[r][c]
                if p == '.':
                    row.append('·' if not ascii_mode else '.')
                else:
                    row.append(p if ascii_mode else UNICODE[p])
            print(f" {8 - r}  " + " ".join(row))
        print("\n    a b c d e f g h\n")


def parse_move(text, legal):
    s = text.replace(" ", "").replace("-", "").lower()
    if len(s) not in (4, 5) or s[0] not in "abcdefgh" or s[2] not in "abcdefgh" \
            or s[1] not in "12345678" or s[3] not in "12345678":
        return None
    c1, r1 = ord(s[0]) - 97, 8 - int(s[1])
    c2, r2 = ord(s[2]) - 97, 8 - int(s[3])
    promo = s[4] if len(s) == 5 else 'q'
    if promo not in "qrbn":
        return None
    for m in legal:
        if m[:4] == (r1, c1, r2, c2):
            if m[4] is None or m[4].lower() == promo:
                return m
    return None


HELP = """
Zet invoeren:   e2e4   of   e2 e4
Promotie:       e7e8q  (q=dame, r=toren, b=loper, n=paard; standaard dame)
Rokade:         zet de koning twee vakjes, bv. e1g1 of e1c1
Commando's:     moves = toon alle legale zetten, help, quit
"""


def main():
    ascii_mode = "--ascii" in sys.argv
    game = Game()
    print("=== SCHAKEN ===")
    print(HELP)
    while True:
        game.show(ascii_mode)
        legal = game.legal_moves()
        check = game.in_check()
        if not legal:
            if check:
                winner = "Zwart" if game.turn == 'w' else "Wit"
                print(f"Schaakmat! {winner} wint.")
            else:
                print("Pat! Remise.")
            break
        if game.halfmove >= 100:
            print("Remise door de 50-zettenregel.")
            break
        if game.insufficient_material():
            print("Remise: onvoldoende materiaal.")
            break
        name = "Wit" if game.turn == 'w' else "Zwart"
        if check:
            print("Schaak!")
        try:
            text = input(f"{name} aan zet > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nTot ziens!")
            break
        cmd = text.lower()
        if cmd in ("quit", "exit", "q"):
            print("Spel gestopt.")
            break
        if cmd == "help":
            print(HELP)
            continue
        if cmd == "moves":
            print(", ".join(sorted(sq_name(m[0], m[1]) + sq_name(m[2], m[3]) + (m[4].lower() if m[4] else "")
                                   for m in legal)))
            continue
        m = parse_move(text, legal)
        if m is None:
            print("Ongeldige zet. Typ 'moves' voor de legale zetten.")
            continue
        game = game.apply(m)


if __name__ == "__main__":
    main()