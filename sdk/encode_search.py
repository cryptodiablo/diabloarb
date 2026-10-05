"""Encoder of the DiabloArb executor's search instruction (tag 1) — reference implementation for README.md.

    data = encode_search(bases, windows, routes, flags=FAIL_WHEN_DRY | VAULT | BUDGET, rounds=0, min_profit=0, budget=None)
"""
import struct

FAIL_WHEN_DRY, VAULT, BUDGET = 1, 2, 4      # search flags
A_TO_B, PUMP_CANONICAL, LEGACY = 1, 2, 4    # hop flags
HINT = 0x80                                 # rounds bit: bases' start is an estimate of the optimum
NO_CAP = (1 << 64) // 4 - 1                 # u64::MAX / 4
Q32 = 1 << 32                               # weight of WSOL (1 lamport = 1 lamport)

def encode_search(bases, windows, routes, flags=FAIL_WHEN_DRY | VAULT | BUDGET, rounds=0, min_profit=0, budget=None):
    """bases: [(weight, start, max_in)], windows: [(dex, hop_flags, first, len, out)], routes: [(base, [window, ...])]."""
    assert 1 <= len(bases) <= 4 and len(windows) >= 1 and 1 <= len(routes) <= 16
    out = bytes([1, flags, rounds]) + struct.pack("<q", min_profit) + bytes([len(bases), len(windows), len(routes)])
    for weight, start, max_in in bases:
        out += struct.pack("<QQQ", weight, start, max_in)
    for w in windows:
        assert all(0 <= x <= 255 for x in w)
        out += bytes(w)
    for base, hops in routes:
        assert 1 <= len(hops) <= 5 and base < len(bases) and all(h < len(windows) for h in hops)
        out += bytes([base, len(hops)] + list(hops))
    if flags & BUDGET:
        out += struct.pack("<I", budget)
    return out

def decode_return(data: bytes):
    """Return data of a search: (route or None, amount_in, profit, quotes)."""
    route, amount_in, profit, quotes = struct.unpack("<BQQH", data)
    return (None if route == 255 else route, amount_in, profit, quotes)

if __name__ == "__main__":
    # the real transaction decoded in README §9 — the encoder reproduces its data byte for byte
    windows = [(6,0,5,17,11),(1,3,23,24,1),(6,0,48,17,54),(1,3,66,24,1),(2,2,91,26,11),(6,1,118,18,1),(2,2,137,26,54),
               (6,1,164,18,1),(7,1,183,14,1),(7,0,198,14,11),(7,0,213,14,54),(7,1,228,14,1)]
    routes = [(0,[0,1]),(0,[2,3]),(0,[4,5]),(0,[6,7]),(0,[4,8]),(0,[9,1]),(0,[0,8]),(0,[9,5]),(0,[10,3]),(0,[2,11]),(0,[6,11]),(0,[10,7])]
    data = encode_search([(Q32, 97212086, NO_CAP)], windows, routes, rounds=HINT, min_profit=5260694, budget=426612)
    real = bytes.fromhex("0107809645500000000000010c0c0000000001000000b656cb0500000000ffffffffffffff3f060005110b01031718010600301136010342180102025b1a0b06017612010202891a360601a412010701b70e010700c60e0b0700d50e360701e40e01000200010002020300020405000206070002040800020901000200080002090500020a030002020b0002060b00020a0774820600")
    assert data == real, "mismatch"
    import base64
    print("ok:", len(data), "bytes, identical to the real transaction;", decode_return(base64.b64decode("AcCB1S0AAAAAKzuYAAAAAAATAA==")))
