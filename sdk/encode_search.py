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
    # the example decoded in README §9 — the encoder reproduces its bytes exactly
    windows = [(0, A_TO_B, 6, 13, 5), (7, 0, 20, 14, 1)]
    routes = [(0, [0, 1])]
    data = encode_search([(Q32, 10_000_000, NO_CAP)], windows, routes, min_profit=1_000_000, budget=300_000)
    example = bytes.fromhex("01070040420f000000000001020100000000010000008096980000000000ffffffffffffff3f0001060d0507001" "40e01000200 01e0930400".replace(" ", ""))
    assert data == example, data.hex()
    import base64
    print("ok:", len(data), "bytes, identical to the README example;", decode_return(base64.b64decode("AABlzR0AAAAAAAk9AAAAAAAFAA==")))
