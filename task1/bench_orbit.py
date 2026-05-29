"""
Quick benchmark: enumerate orbits up to k=14 and measure time.
"""
import time
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

MOD = 998244353

for k in range(1, 15):
    t0 = time.time()
    words = generate_dyck(k)
    orbits = {}
    for s in words:
        al = alice_of(s)
        ws = '(' + s + ')'
        Xw, bobw = x_seq_and_bob(ws)
        kw = len(Xw)
        orbits[(bobw, kw)] = orbits.get((bobw, kw), 0) + 1
    t1 = time.time()
    print(f"k={k:2d}: Catalan={len(words):7d} orbits={len(orbits):4d} time={t1-t0:.3f}s")
