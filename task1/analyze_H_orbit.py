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

    print("=== Verify x_seq (pair-based) ===")
    for n in range(1, 5):
        words = generate_dyck(n)
        for s in words:
            X, bob, k = x_seq_and_bob(s)
            print("n=%d s=%s X=%s bob=%d k=%d" % (n, s, str(X), bob, k))

    print()
    print(sep)
    print("DETAILED ORBIT STRUCTURE (a=2, by bw,kw)")
    print(sep)

    for k in range(1, 10):
        words = generate_dyck(k)
        orbits = {}
        for s in words:
            X, _, _ = x_seq_and_bob(s)
            x1 = X[0]
            Xw = pair_seq([1] + X)
            bw = sum((j-1)*Xw[j-1] for j in range(1, len(Xw)+1))
            kw = len(Xw)
            alice_val = alice_of(s)
            key = (bw, kw)
            if key not in orbits:
                orbits[key] = {'alpha': 0, 'items': []}
            orbits[key]['alpha'] = (orbits[key]['alpha'] + pow(2, alice_val, MOD)) % MOD
            orbits[key]['items'].append((s, X, x1, alice_val))
            orbits[key]['items'].sort(key=lambda x: x[3])

        print("\nk=%d: %d orbits" % (k, len(orbits)))
        for (bw, kw), info in sorted(orbits.items()):
            print("  (bw=%d, kw=%d): alpha=%d, #%d words" % (bw, kw, info['alpha'], len(info['items'])))
            for s, X, x1, alice_val in info['items']:
                print("    %s X=%s x1=%d alice=%d" % (s, str(X), x1, alice_val))

    print()
    print(sep)
    print("ORBIT COUNT TABLE")
    print(sep)
    counts = []
    for k in range(1, 11):
        words = generate_dyck(k)
        orbits = set()
        for s in words:
            X, _, _ = x_seq_and_bob(s)
            Xw = pair_seq([1] + X)
            bw = sum((j-1)*Xw[j-1] for j in range(1, len(Xw)+1))
            kw = len(Xw)
            orbits.add((bw, kw))
        counts.append(len(orbits))
    print("k:       ", " ".join("%3d" % k for k in range(1, len(counts)+1)))
    print("orbits:  ", " ".join("%3d" % c for c in counts))
    print("Catalan: ", " ".join("%3d" % len(generate_dyck(k)) for k in range(1, len(counts)+1)))

    print()
    print(sep)
    print("x1=1 vs x1>=2 orbit mapping analysis")
    print(sep)

    for k in range(3, 9):
        words = generate_dyck(k)
        print("\nk=%d:" % k)
        x1_1_orbits = set()
        x1_ge2_orbits = set()
        for s in words:
            X, _, _ = x_seq_and_bob(s)
            x1 = X[0]
            Xw = pair_seq([1] + X)
            bw = sum((j-1)*Xw[j-1] for j in range(1, len(Xw)+1))
            kw = len(Xw)
            if x1 == 1:
                x1_1_orbits.add((bw, kw))
            else:
                x1_ge2_orbits.add((bw, kw))
        print("  x1=1 orbits: %s" % str(sorted(x1_1_orbits)))
        print("  x1>=2 orbits: %s" % str(sorted(x1_ge2_orbits)))
        print("  union size: %d" % len(x1_1_orbits | x1_ge2_orbits))

if __name__ == '__main__':
    main()
