# -*- coding: utf-8 -*-
"""Debug H[5] orbits"""
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

print("=== H[5] brute force grouped by (bw,kw) with details ===")
words = generate_dyck(5)
h_map = {}
for s in words:
    X, _ = x_seq_and_bob(s)
    c = sum(1 for xx in X if xx==1)
    c_lead = 0
    for xx in X: 
        if xx == 1: c_lead += 1
        else: break
    c_flag = 1 if c_lead >= 1 else 0
    all1 = 1 if c_lead == len(X) and len(X) > 0 else 0
    Xw = pair_seq([1]+X)
    bw = sum(j*Xw[j] for j in range(len(Xw)))
    kw = len(Xw)
    al = alice_of(s)
    
    # c_tail
    if c_flag == 0 and len(X) > 1:
        ct = 0
        for xx in X[1:]:
            if xx == 1: ct += 1
            else: break
        c_tail = 1 if ct >= 1 else 0
    elif c_flag == 0:
        c_tail = 0
    else:
        c_tail = None
    
    bk = (bw, kw)
    if bk not in h_map: h_map[bk] = []
    h_map[bk].append((s, X, c_lead, c_flag, all1, c_tail, al, pa[al]))

for bk in sorted(h_map.keys()):
    total = sum(x[7] for x in h_map[bk]) % MOD
    print("(bw=%d,kw=%d) BF=%d" % (bk[0], bk[1], total))
    for item in h_map[bk]:
        print("  %s X=%s c=%d c_flag=%d all1=%d c_tail=%s al=%d pa=%d" % 
              (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7]))

print("\n=== Which branch should each word come from? ===")
for bk in [(3,2), (4,3)]:
    print("\n(bw=%d,kw=%d):" % bk)
    for item in h_map[bk]:
        s, X, c_lead, c_flag, all1, c_tail, al, pal = item
        if c_flag == 1 and all1 == 1:
            branch = "c=k (all1)"
        elif c_flag == 1:
            branch = "c=2p or c=2p+1"
        elif c_flag == 0:
            if len(X) > 0:
                x1 = X[0]
                if s == '('*x1 + ')'*x1 + '...':
                    branch = "primitive c=0"
                else:
                    branch = "non-prim c=0"
            import re
            # Check if primitive
            h = [0]*11
            for i in range(10): h[i+1] = h[i] + (1 if s[i]=='(' else -1)
            is_prim = True
            for i in range(1, 10):
                if h[i] == 0 and i < 10:
                    is_prim = False
                    break
            if is_prim:
                branch = "primitive c=0"
            else:
                branch = "non-prim c=0 (A1 size ?, rest size ?)"
        print("  %s X=%s al=%d -> %s" % (s, X, al, branch))
