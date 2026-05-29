# -*- coding: utf-8 -*-
"""Route K: H[k][L] recurrence - tracking (bw,kw,xw1) for correct wrapping mapping"""
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

def alice_of(s):
    cnt = 0
    for i in range(len(s)):
        if s[i] == '(':
            for j in range(i+1, len(s)):
                if s[j] == ')':
                    cnt += 1
    return cnt

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

def wrapping_of(X):
    Xw = pair_seq([1] + X)
    bw = sum((j-1)*Xw[j-1] for j in range(1, len(Xw)+1))
    kw = len(Xw)
    xw1 = Xw[0] if Xw else 0
    return bw, kw, Xw, xw1

def main():
    sep = "=" * 60
    print(sep)
    print("MAPPING TABLE: (bw_rest, kw_rest, xw1_rest) -> (bw_full, kw_full, xw1_full)")
    print("for x1=1 (A = () + rest)")
    print(sep)

    for k in range(3, 9):
        rest_words = generate_dyck(k - 1)
        print("\nk=%d (rest size %d):" % (k, k - 1))
        mapping = {}
        for rest in rest_words:
            Xr, _, _ = x_seq_and_bob(rest)
            bw_r, kw_r, Xwr, xw1_r = wrapping_of(Xr)

            A = "()" + rest
            Xa, _, _ = x_seq_and_bob(A)
            bw_a, kw_a, Xwa, xw1_a = wrapping_of(Xa)

            key = (bw_r, kw_r, xw1_r)
            if key not in mapping:
                mapping[key] = set()
            mapping[key].add((bw_a, kw_a, xw1_a))

        for (bw_r, kw_r, xw1_r), results in sorted(mapping.items()):
            print("  rest (%d,%d,xw1=%d) -> full %s" % (bw_r, kw_r, xw1_r, str(sorted(results))))

    print()
    print(sep)
    print("MAPPING TABLE: (x, bw_rest, kw_rest, xw1_rest) -> (bw_full, kw_full, xw1_full)")
    print("for x1>=2 (A = P_x + rest)")
    print(sep)

    for k in range(3, 8):
        print("\nk=%d:" % k)
        mapping = {}
        for A in generate_dyck(k):
            Xa, _, _ = x_seq_and_bob(A)
            x1 = Xa[0]
            if x1 == 1:
                continue
            bw_a, kw_a, Xwa, xw1_a = wrapping_of(Xa)

            rest = A[2*x1:] if 2*x1 <= len(A) else ""
            if not rest:
                key = (x1, None)
                if key not in mapping:
                    mapping[key] = set()
                mapping[key].add((bw_a, kw_a, xw1_a))
            else:
                Xr, _, _ = x_seq_and_bob(rest)
                bw_r, kw_r, Xwr, xw1_r = wrapping_of(Xr)
                key = (x1, bw_r, kw_r, xw1_r, len(rest)//2)
                if key not in mapping:
                    mapping[key] = set()
                mapping[key].add((bw_a, kw_a, xw1_a))

        for key, results in sorted(mapping.items()):
            print("  %s -> full %s" % (str(key), str(sorted(results))))

    print()
    print(sep)
    print("VERIFY: derived wrapping formulas with xw1 tracking")
    print(sep)

    for k in range(2, 8):
        words = generate_dyck(k)
        ok = True
        for A in words:
            Xa, _, _ = x_seq_and_bob(A)
            x1 = Xa[0]
            bw_a, kw_a, Xwa, xw1_a = wrapping_of(Xa)

            if x1 == 1:
                rest = A[2:]
                Xr, _, _ = x_seq_and_bob(rest)
                bw_r, kw_r, Xwr, xw1_r = wrapping_of(Xr)

                if xw1_r >= 2:
                    expected_bw = bw_r + k - 1
                    expected_kw = kw_r + 1
                    expected_xw1 = 2
                else:
                    expected_bw = k - 1
                    expected_kw = 2
                    expected_xw1 = 2

                if (bw_a, kw_a, xw1_a) != (expected_bw, expected_kw, expected_xw1):
                    if k <= 6:
                        print("  FAIL x1=1: %s Xw=%s, rest_Xw=%s (bw=%d,kw=%d,xw1=%d) != expected (%d,%d,%d)" %
                              (A, str(Xwa), str(Xwr), bw_a, kw_a, xw1_a, expected_bw, expected_kw, expected_xw1))
                    ok = False

            elif x1 >= 2:
                rest = A[2*x1:] if 2*x1 <= len(A) else ""
                if not rest:
                    expected_bw = 0
                    expected_kw = 1
                    expected_xw1 = 1 + x1
                else:
                    Xr, _, _ = x_seq_and_bob(rest)
                    bw_r, kw_r, Xwr, xw1_r = wrapping_of(Xr)

                    if xw1_r >= 2:
                        expected_bw = bw_r + k - 1
                        expected_kw = kw_r + 1
                        expected_xw1 = 1 + x1
                    else:
                        expected_bw = (k - x1) + k - 1
                        expected_kw = kw_r + 1
                        expected_xw1 = 1 + x1

                if (bw_a, kw_a, xw1_a) != (expected_bw, expected_kw, expected_xw1):
                    if k <= 6:
                        print("  FAIL x1=%d: %s Xw=%s expected (%d,%d,%d) got (%d,%d,%d)" %
                              (x1, A, str(Xwa), expected_bw, expected_kw, expected_xw1, bw_a, kw_a, xw1_a))
                    ok = False

        print("  k=%d: %s" % (k, "ALL OK" if ok else "HAS FAILURES"))

if __name__ == '__main__':
    main()
