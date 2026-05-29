# -*- coding: utf-8 -*-
"""Verify X((T)) vs pair_seq([1]+X(T)) for T of sizes 1..6."""
from orbit_dp_v9 import x_seq_and_bob, pair_seq, generate_dyck

for k in range(1, 7):
    words = generate_dyck(k)
    mismatches = []
    for T in words:
        X_T, _ = x_seq_and_bob(T)
        Xw_T_pair = pair_seq([1] + X_T)
        T_wrapped = '(' + T + ')'
        X_real, _ = x_seq_and_bob(T_wrapped)
        if Xw_T_pair != X_real:
            c_lead = sum(1 for x in X_T if x == 1 and (not mismatches or True))
            c = 0
            for xx in X_T:
                if xx == 1: c += 1
                else: break
            mismatches.append((T, X_T, c, Xw_T_pair, X_real))
    if mismatches:
        print("k=%d: %d mismatches" % (k, len(mismatches)))
        for T, X_T, c, pair, real in mismatches:
            print("  T=%s X(T)=%s c=%d pair_seq=[%s] real=[%s]" % (T, X_T, c, ','.join(str(x) for x in pair), ','.join(str(x) for x in real)))
            # compute correction
            bw_pair = sum(j*pair[j] for j in range(len(pair)))
            kw_pair = len(pair)
            bw_real = sum(j*real[j] for j in range(len(real)))
            kw_real = len(real)
            print("    pair: bw=%d kw=%d  real: bw=%d kw=%d  dk=%d db=%d" % (bw_pair, kw_pair, bw_real, kw_real, kw_real-kw_pair, bw_real-bw_pair))
    else:
        print("k=%d: ALL MATCH" % k)
