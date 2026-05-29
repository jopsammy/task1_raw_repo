# -*- coding: utf-8 -*-
"""Debug H[4] (2,2) discrepancy"""
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

def pair_seq(seq):
    res = []; i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq): res.append(1 + seq[i + 1]); i += 2
        else: res.append(seq[i]); i += 1
    return res

def alice_of(s):
    n = len(s)//2; cnt = 0
    for i in range(2*n):
        if s[i] == '(':
            for j in range(i+1, 2*n):
                if s[j] == ')': cnt += 1
    return cnt

a_val = 2; b_val = 3
pa = [1]*100
for i in range(1, 100): pa[i] = pa[i-1]*a_val % MOD

print("=== BF details for k=4 (bw=2, kw=2) ===")
words = generate_dyck(4)
for s in sorted(words):
    X, _ = x_seq_and_bob(s)
    c = 0
    for xx in X:
        if xx == 1: c += 1
        else: break
    Xw = pair_seq([1]+X)
    bw = sum(j * Xw[j] for j in range(len(Xw)))
    kw = len(Xw)
    al = alice_of(s)
    if (bw, kw) == (2, 2):
        print("  %s  X=%s c=%d Xw=%s bw=%d kw=%d alice=%d pa[al]=%d" % 
              (s, X, c, Xw, bw, kw, al, pa[al]))

total_bf = 0
for s in words:
    Xw = pair_seq([1]+x_seq_and_bob(s)[0])
    bw = sum(j*Xw[j] for j in range(len(Xw)))
    if bw == 2 and len(Xw) == 2:
        total_bf = (total_bf + pa[alice_of(s)]) % MOD
print("BF total for (2,2): %d" % (total_bf % MOD))

# Now trace DP contributions
print("\n=== DP contribution trace ===")
print("Current DP says 45056, BF says 34816, diff=10240")
print("10240 = %d * 1024 (a^10)" % (10240//1024))
print()

# Let's look at what the non-primitive c=0 branch generates
# k=4, s=1..k-2 (s=1,2), rest_size = k-s-1
print("Non-primitive c=0 for k=4:")
for s in range(1, 3):
    rest_size = 4 - s - 1
    print("  s=%d rest_size=%d" % (s, rest_size))
    if rest_size <= 0: continue
    # H[s] (size s=A1)
    # For s=1: H[1] has one orbit: (bw=0,kw=1,c=1,all1=1,...). x1=1, a1c=pa[1]=2
    #   x1_word=1+1=2, tail_size=4-2=2
    #   Q[2]: needs to be computed
    # For s=2: H[2] has two orbits...
    pass

# Compute H manually for A1 in non-primitive c=0
print("\nComputing H for sizes 1-3 manually...")
for sz in range(1, 4):
    words_sz = generate_dyck(sz)
    h_map = {}
    for s in words_sz:
        X, _ = x_seq_and_bob(s)
        Xw = pair_seq([1]+X)
        bw = sum(j*Xw[j] for j in range(len(Xw)))
        kw = len(Xw)
        al = alice_of(s)
        c = 0
        for xx in X:
            if xx == 1: c += 1
            else: break
        all1 = 1 if c == sz else 0
        key = (bw, kw, min(c,1), all1)
        if key not in h_map:
            h_map[key] = []
        h_map[key].append((s, X, c, al, pa[al]))
    print("H[%d]:" % sz)
    for k, v in sorted(h_map.items()):
        total = sum(x[4] for x in v) % MOD
        print("  %s: total=%d words=%s" % (k, total, [x[0] for x in v]))
