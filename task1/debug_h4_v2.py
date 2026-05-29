# -*- coding: utf-8 -*-
"""Debug H[4] (2,2) — trace each DP branch contribution"""
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

# Compute Q[k] brute force for reference (pair_seq of x-seq, for k=0..4)
words = {k: generate_dyck(k) for k in range(5)}
print("=== Q[k] brute force (pair_seq(X), NOT wrapping) ===")
for k in range(5):
    q_map = {}
    for s in words[k]:
        X, _ = x_seq_and_bob(s)
        Xp = pair_seq(X)
        bp = sum(j * Xp[j] for j in range(len(Xp)))
        kp = len(Xp)
        al = alice_of(s)
        c = sum(1 for xx in X if xx == 1)
        # c of the x_seq: leading 1 count
        c_lead = 0
        for xx in X:
            if xx == 1: c_lead += 1
            else: break
        c_flag = 1 if c_lead >= 1 else 0
        all1 = 1 if c_lead == len(X) and len(X) > 0 else 0
        key = (bp, kp, c_flag, all1)
        if key not in q_map: q_map[key] = []
        q_map[key].append((s, X, al, pa[al]))
    print("Q[%d]:" % k)
    for key, lst in sorted(q_map.items()):
        total = sum(x[3] for x in lst) % MOD
        print("  %s: total=%d words=%s" % (key, total, [x[0] for x in lst]))

print("\n=== H[k] brute force (wrapping) ===")
for k in range(5):
    h_map = {}
    for s in words[k]:
        X, _ = x_seq_and_bob(s)
        Xw = pair_seq([1]+X)
        bw = sum(j*Xw[j] for j in range(len(Xw)))
        kw = len(Xw)
        al = alice_of(s)
        c_lead = 0
        for xx in X:
            if xx == 1: c_lead += 1
            else: break
        c_flag = 1 if c_lead >= 1 else 0
        all1 = 1 if c_lead == k and k > 0 else 0
        # c_tail for c_flag=0: c of X[1:]
        c_tail = None
        if c_flag == 0 and len(X) > 1:
            ct = 0
            for xx in X[1:]:
                if xx == 1: ct += 1
                else: break
            c_tail = 1 if ct >= 1 else 0
        elif c_flag == 0:
            c_tail = 0
        key = (bw, kw, c_flag, all1, c_tail)
        if key not in h_map: h_map[key] = []
        h_map[key].append((s, X, al, pa[al], c_lead))
    print("H[%d]:" % k)
    for key, lst in sorted(h_map.items()):
        total = sum(x[3] for x in lst) % MOD
        print("  %s: total=%d words=%s" % (key, total, [(x[0], x[2], x[4]) for x in lst]))
