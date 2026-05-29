# -*- coding: utf-8 -*-
"""Comprehensive H[4] debug: trace every word to identify branch errors."""
MOD = 998244353
a_val = 2; b_val = 3
pa = [1]*50
for i in range(1,50): pa[i]=pa[i-1]*a_val%MOD

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
    return X, sum(j*X[j] for j in range(len(X)))

def alice_of(s):
    n = len(s)//2; cnt = 0
    for i in range(2*n):
        if s[i] == '(':
            for j in range(i+1, 2*n):
                if s[j] == ')': cnt += 1
    return cnt

def pair_seq(seq):
    res = []; i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq): res.append(1 + seq[i + 1]); i += 2
        else: res.append(seq[i]); i += 1
    return res

# All D_4 words
k = 4
words = generate_dyck(k)
print("=== H[4]: REAL X((A)) for each word ===")
for A in sorted(words):
    X_A, _ = x_seq_and_bob(A)
    Xw_real, bw_real = x_seq_and_bob('(' + A + ')')
    kw_real = len(Xw_real)
    al = alice_of(A)
    
    c = 0
    for xx in X_A:
        if xx == 1: c += 1
        else: break
    
    # Check if primitive
    h_test = 0
    is_prim = True
    for i, ch in enumerate(A):
        h_test += 1 if ch == '(' else -1
        if 0 < i < len(A)-1 and h_test == 0:
            is_prim = False
            break
    
    Xw_pair = pair_seq([1]+X_A)
    bw_pair = sum(j*Xw_pair[j] for j in range(len(Xw_pair)))
    
    print("  %-20s X=%s c=%d prim=%s | REAL Xw=%s bw=%d kw=%d al=%d pa[al]=%d" % (
        A, str(X_A), c, is_prim, str(Xw_real), bw_real, kw_real, al, pa[al]))

# Now show BF (bw,kw) aggregation
print("\n=== BF aggregation ===")
Hbf = {}
for A in words:
    Xw_real, _ = x_seq_and_bob('(' + A + ')')
    bw = sum(j*Xw_real[j] for j in range(len(Xw_real)))
    kw = len(Xw_real)
    al = alice_of(A)
    key = (bw, kw)
    if key not in Hbf: Hbf[key] = (0, [])
    Hbf[key] = (Hbf[key][0] + pa[al], Hbf[key][1] + [A])

for (bw,kw), (val, wlist) in sorted(Hbf.items()):
    print("  bw=%d kw=%d: BF=%d words: %s" % (bw, kw, val % MOD, wlist))

# Categorize each word by which DP branch should handle it
print("\n=== Branch categorization ===")
for A in sorted(words):
    X_A, _ = x_seq_and_bob(A)
    c = 0
    for xx in X_A:
        if xx == 1: c += 1
        else: break
    
    # Find (A1)B decomposition for c=0
    branch = ""
    if c == k:
        branch = "c=k (all1)"
    elif c >= 2:
        if c % 2 == 0: branch = "c=2p (c=%d)" % c
        else: branch = "c=2p+1 (c=%d)" % c
    elif c == 1:
        branch = "c=2p+1 (c=1)"
    else:
        # c=0: check if primitive
        h_test = 0
        is_prim = True
        for i, ch in enumerate(A):
            h_test += 1 if ch == '(' else -1
            if 0 < i < len(A)-1 and h_test == 0:
                is_prim = False
                break
        if is_prim:
            branch = "c=0 primitive"
        else:
            branch = "c=0 non-primitive"
    
    Xw_real, _ = x_seq_and_bob('(' + A + ')')
    bw_real = sum(j*Xw_real[j] for j in range(len(Xw_real)))
    kw_real = len(Xw_real)
    al = alice_of(A)
    print("  %-20s al=%2d pa=%5d X(A)=%s c=%d → %s → REAL Xw=%s (bw=%d,kw=%d)" % (
        A, al, pa[al], X_A, c, branch, Xw_real, bw_real, kw_real))
