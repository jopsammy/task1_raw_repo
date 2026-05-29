# -*- coding: utf-8 -*-
"""Corrected c-based wrapping formulas."""
import sys

MOD = 998244353

def generate_dyck(n):
    res = []
    def backtrack(s, left, right):
        if len(s) == 2 * n:
            res.append(s)
            return
        if left < n:
            backtrack(s + '(', left + 1, right)
        if right < left:
            backtrack(s + ')', left + 1, right)
    backtrack('', 0, 0)
    return res

def x_seq_and_bob(s):
    n = len(s) // 2
    pair_pos = 0
    X = []
    while pair_pos < n:
        found = False
        for pp in range(1, n - pair_pos + 1):
            pos1 = 2 * pair_pos
            pos2 = 2 * pair_pos + 2 * pp
            segment = s[pos1:pos2]
            h = 0
            for ch in segment:
                h += 1 if ch == '(' else -1
                if h == 0:
                    X.append(pp)
                    pair_pos += pp
                    found = True
                    break
            if found:
                break
        if not found:
            X.append(n - pair_pos)
            pair_pos = n
    k = len(X)
    bob = sum((j - 1) * X[j - 1] for j in range(1, k + 1))
    return X, bob, k

def pair_seq(seq):
    res = []
    i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq):
            res.append(1 + seq[i + 1])
            i += 2
        else:
            res.append(seq[i])
            i += 1
    return res

def main():
    total, ok, fail = 0, 0, 0

    print("c=2p:   bw = p(k-p) + bw_rest,           kw = p + kw_rest")
    print("c=2p+1: bw = (p+1)(k-p-1) + bw_rest,     kw = p+1 + kw_rest")
    print("c=k:    degenerate all-1's chain")
    print()

    for k in range(1, 9):
        words = generate_dyck(k)
        for A in words:
            total += 1
            X, _, _ = x_seq_and_bob(A)
            Xw_act = pair_seq([1] + X)
            bw_act = sum((j-1)*Xw_act[j-1] for j in range(1, len(Xw_act)+1))
            kw_act = len(Xw_act)

            c = 0
            for val in X:
                if val == 1: c += 1
                else: break

            if c == k:
                t = k + 1
                if t % 2 == 0:
                    u = t // 2
                    exp_bw = u * (u - 1)
                    exp_kw = u
                else:
                    u = t // 2
                    exp_bw = u * u
                    exp_kw = u + 1
            else:
                rest_X = X[c:]
                rest_Xw = pair_seq([1] + rest_X)
                rest_bw = sum((j-1)*rest_Xw[j-1] for j in range(1, len(rest_Xw)+1))
                rest_kw = len(rest_Xw)

                if c % 2 == 0:
                    p = c // 2
                    exp_bw = p * (k - p) + rest_bw
                    exp_kw = p + rest_kw
                else:
                    p = (c - 1) // 2
                    exp_bw = (p + 1) * (k - p - 1) + rest_bw
                    exp_kw = p + 1 + rest_kw

            if (bw_act, kw_act) != (exp_bw, exp_kw):
                fail += 1
                if fail <= 5:
                    print("FAIL: k=%d c=%d X=%s Xw=%s act=(%d,%d) exp=(%d,%d)" %
                          (k, c, str(X), str(Xw_act), bw_act, kw_act, exp_bw, exp_kw))
            else:
                ok += 1

    print("\nTotal: %d, OK: %d, FAIL: %d" % (total, ok, fail))
    if fail == 0:
        print("*** ALL VERIFIED across n=1..8 ***")

if __name__ == '__main__':
    main()
