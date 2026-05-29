# -*- coding: utf-8 -*-
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
    L = []
    for i, ch in enumerate(s):
        if ch == ')':
            left_before = s[:i+1].count('(')
            L.append(left_before)
    return sum(L)

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
    sep = "=" * 70
    print(sep)
    print("RECURRENCE VERIFICATION for x1=1 and x1>=2")
    print(sep)

    for k in range(3, 9):
        words = generate_dyck(k)
        print("\nk=%d:" % k)

        x1_1_recurrence_ok = True
        x1_ge2_recurrence_ok = True

        for s in words:
            X, _, _ = x_seq_and_bob(s)
            x1 = X[0]
            alice_val = alice_of(s)
            Xw = pair_seq([1] + X)
            bw = sum((j-1)*Xw[j-1] for j in range(1, len(Xw)+1))
            kw = len(Xw)

            if x1 == 1:
                prefix = "()"
                rest = s[2:]
                rest_n = len(rest) // 2

                if k <= 7:
                    print("  x1=1: %s (alice=%d) -> rest=%s (rest_alice=%d, rest_n=%d)" %
                          (s, alice_val, rest, alice_of(rest), rest_n))

            elif x1 >= 2 and k <= 7:
                if 2*x1 <= len(s):
                    rest = s[2*x1:]
                    rest_n = len(rest) // 2
                    print("  x1=%d: %s (alice=%d) -> rest=%s (rest_alice=%d, rest_n=%d)" %
                          (x1, s, alice_val, rest, alice_of(rest), rest_n))

    print()
    print(sep)
    print("ALICE FORMULA TEST: alice(A) = alice(rest) + f(k, x1)")
    print(sep)

    for k in range(3, 9):
        words = generate_dyck(k)
        print("\nk=%d:" % k)
        for s in words:
            X, _, _ = x_seq_and_bob(s)
            x1 = X[0]
            alice_val = alice_of(s)
            Xw = pair_seq([1] + X)
            bw = sum((j-1)*Xw[j-1] for j in range(1, len(Xw)+1))
            kw = len(Xw)

            if x1 == 1:
                rest = s[2:]
                rest_alice = alice_of(rest)
                diff = alice_val - rest_alice
            else:
                rest = s[2*x1:] if 2*x1 <= len(s) else ""
                rest_alice = alice_of(rest) if rest else 0
                diff = alice_val - rest_alice

            expected_diff = None
            if x1 == 1:
                expected_diff = k
            else:
                expected_diff = x1 * k

            match = "OK" if diff == expected_diff else "FAIL(expected=%d)" % expected_diff
            if k <= 6:
                print("  x1=%d: %s alice=%d rest_alice=%d diff=%d %s" %
                      (x1, s, alice_val, rest_alice, diff, match))

    print()
    print(sep)
    print("WRAPPING FORMULA TEST")
    print(sep)

    for k in range(3, 9):
        words = generate_dyck(k)
        print("\nk=%d:" % k)
        for s in words:
            X, _, _ = x_seq_and_bob(s)
            x1 = X[0]
            Xw = pair_seq([1] + X)
            bw = sum((j-1)*Xw[j-1] for j in range(1, len(Xw)+1))
            kw = len(Xw)
            alice_val = alice_of(s)

            if x1 == 1:
                rest = s[2:]
                if not rest:
                    continue
                rest_X, _, _ = x_seq_and_bob(rest)
                rest_Xw = pair_seq([1] + rest_X)
                rest_bw = sum((j-1)*rest_Xw[j-1] for j in range(1, len(rest_Xw)+1))
                rest_kw = len(rest_Xw)

                if k <= 7:
                    print("  x1=1: %s (bw=%d,kw=%d) rest=%s (bw=%d,kw=%d) Xw=%s rest_Xw=%s" %
                          (s, bw, kw, rest, rest_bw, rest_kw, str(Xw), str(rest_Xw)))

            elif x1 >= 2:
                rest = s[2*x1:] if 2*x1 <= len(s) else ""
                if not rest:
                    continue
                rest_X, _, _ = x_seq_and_bob(rest)
                rest_Xw = pair_seq([1] + rest_X)
                rest_bw = sum((j-1)*rest_Xw[j-1] for j in range(1, len(rest_Xw)+1))
                rest_kw = len(rest_Xw)

                if k <= 7:
                    print("  x1=%d: %s (bw=%d,kw=%d) rest=%s (bw=%d,kw=%d) X=%s Xw=%s rest_Xw=%s" %
                          (x1, s, bw, kw, rest, rest_bw, rest_kw, str(X), str(Xw), str(rest_Xw)))

    print()
    print(sep)
    print("COMPLETE MAPPING: x1=1 -> all rest words, x1>=2 -> all rest words")
    print(sep)

    for k in range(3, 9):
        words = generate_dyck(k)
        print("\nk=%d: |A|=k" % k)
        print("  x1=1 (starts with '()'): rest has size k-1=%d" % (k-1))
        print("  x1>=2 (starts with '(('): rest has size k-x1, x1 in [2..k]")

        x1_1_map = {}
        x1_ge2_map = {}

        for s in words:
            X, _, _ = x_seq_and_bob(s)
            x1 = X[0]
            Xw = pair_seq([1] + X)
            bw = sum((j-1)*Xw[j-1] for j in range(1, len(Xw)+1))
            kw = len(Xw)
            alice_val = alice_of(s)

            if x1 == 1:
                rest = s[2:]
                rest_X, _, _ = x_seq_and_bob(rest)
                rest_Xw = pair_seq([1] + rest_X)
                rest_bw = sum((j-1)*rest_Xw[j-1] for j in range(1, len(rest_Xw)+1))
                rest_kw = len(rest_Xw)
                key = (rest_bw, rest_kw)
                if key not in x1_1_map:
                    x1_1_map[key] = set()
                x1_1_map[key].add((bw, kw))
            elif x1 >= 2:
                rest = s[2*x1:] if 2*x1 <= len(s) else ""
                if rest:
                    rest_X, _, _ = x_seq_and_bob(rest)
                    rest_Xw = pair_seq([1] + rest_X)
                    rest_bw = sum((j-1)*rest_Xw[j-1] for j in range(1, len(rest_Xw)+1))
                    rest_kw = len(rest_Xw)
                    key = (x1, rest_bw, rest_kw)
                    if key not in x1_ge2_map:
                        x1_ge2_map[key] = set()
                    x1_ge2_map[key].add((bw, kw))

        print("  x1=1 mapping (rest_orbit -> full_orbits):")
        for rest_key, full_set in sorted(x1_1_map.items()):
            print("    rest %s -> full %s" % (str(rest_key), str(sorted(full_set))))

        print("  x1>=2 mapping ((x1, rest_orbit) -> full_orbits):")
        for rest_key, full_set in sorted(x1_ge2_map.items()):
            print("    (x1=%d, rest %s) -> full %s" % (rest_key[0], str(rest_key[1:]), str(sorted(full_set))))

if __name__ == '__main__':
    main()
