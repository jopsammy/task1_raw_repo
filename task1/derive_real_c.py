# -*- coding: utf-8 -*-
"""Re-derive c-based wrapping formula for REAL x_seq_and_bob (not pair_seq).

For any Dyck word T of size k with c leading 1s in X(T):
X(T) = [1, 1, ..., 1 (c times), v, r_2, r_3, ...] where v >= 2 (or rest is empty).
We want Xw = x_seq_and_bob('(' + T + ')') — the REAL wrapped x_seq.

Key difference from pair_seq: in real x_seq, the outer '(' +1 height shift
can cause additional merges that pair_seq doesn't capture.

Let's enumerate all words up to k=8 and find the real (bw,kw) patterns.
"""
import sys
MOD = 998244353

def generate_dyck(n):
    res = []
    def bt(s, op, cl):
        if cl > op or op > n: return
        if len(s) == 2*n:
            if op == n and cl == n: res.append(s)
            return
        bt(s + '(', op+1, cl)
        bt(s + ')', op, cl+1)
    bt('', 0, 0)
    return res

def x_seq_and_bob(s):
    n = len(s)//2
    h = [0]*(2*n+1)
    for i in range(2*n): h[i+1] = h[i] + (1 if s[i]=='(' else -1)
    l = 0; X = []
    while l < n:
        pos = 2*l; t = 1; best_x = 0
        while pos + t <= 2*n:
            if h[pos + t] == t: best_x = t; t += 1
            elif h[pos + t] > t: t += 1
            else: break
        if best_x == 0: best_x = 1
        X.append(best_x); l += best_x
    bob = sum(j * X[j] for j in range(len(X)))
    return X, bob

def alice_of(s):
    n = len(s)//2; cnt = 0
    for i in range(2*n):
        if s[i] == '(':
            for j in range(i+1, 2*n):
                if s[j] == ')': cnt += 1
    return cnt

# For each word up to k=8, compute real X((T)) and compare with c-based prediction
max_k = 8
print("Re-deriving c-based formula for REAL wrapping...")
print("Format: T, X(T), c, X((T))_real vs X((T))_pair, (bw,kw)_real vs (bw,kw)_pair, diff")
print()

for k in range(1, max_k + 1):
    words = generate_dyck(k)
    mismatches = []
    for T in sorted(words):
        X_T, _ = x_seq_and_bob(T)
        c = 0
        for xx in X_T:
            if xx == 1: c += 1
            else: break
        
        Xw_real, _ = x_seq_and_bob('(' + T + ')')
        bw_real = sum(j*Xw_real[j] for j in range(len(Xw_real)))
        kw_real = len(Xw_real)
        
        from orbit_dp_v11 import pair_seq
        Xw_pair = pair_seq([1] + X_T)
        bw_pair = sum(j*Xw_pair[j] for j in range(len(Xw_pair)))
        kw_pair = len(Xw_pair)
        
        if Xw_real != Xw_pair:
            mismatches.append((T, X_T, c, Xw_real, Xw_pair, bw_real, kw_real, bw_pair, kw_pair))
    
    if mismatches:
        print("k=%d: %d mismatches (out of %d Catalan)" % (k, len(mismatches), len(words)))
        for T, X_T, c, Xw_r, Xw_p, bw_r, kw_r, bw_p, kw_p in mismatches[:10]:
            print("  %-24s X=%s c=%d real=%s (bw=%d,kw=%d) pair=%s (bw=%d,kw=%d)" % (
                T, X_T, c, Xw_r, bw_r, kw_r, Xw_p, bw_p, kw_p))

# Now derive the correct formula for each c value
print("\n\nDeriving real c-based formula...")
print("For each (c, X(rest)_real_bw, X(rest)_real_kw), what is X((T))_real?")
print()

for k in range(1, max_k + 1):
    words = generate_dyck(k)
    for T in sorted(words):
        X_T, _ = x_seq_and_bob(T)
        c = 0
        for xx in X_T:
            if xx == 1: c += 1
            else: break
        
        rest = T[2*c:]  # remove c leading "()"
        rest_k = len(rest)//2
        
        Xw_real, _ = x_seq_and_bob('(' + T + ')')
        bw_real = sum(j*Xw_real[j] for j in range(len(Xw_real)))
        kw_real = len(Xw_real)
        
        if rest_k > 0:
            X_rest, _ = x_seq_and_bob(rest)
            Xw_rest_real, _ = x_seq_and_bob('(' + rest + ')')
            bw_rest_real = sum(j*Xw_rest_real[j] for j in range(len(Xw_rest_real)))
            kw_rest_real = len(Xw_rest_real)
            
            print("  k=%d c=%d rest_k=%d Xw_rest=%s (bw=%d,kw=%d) → Xw_real=%s (bw=%d,kw=%d)" % (
                k, c, rest_k, Xw_rest_real, bw_rest_real, kw_rest_real,
                Xw_real, bw_real, kw_real))
