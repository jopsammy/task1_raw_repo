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
    n = len(s) // 2
    L = []
    for i, ch in enumerate(s):
        if ch == ')':
            left_before = s[:i+1].count('(')
            L.append(left_before)
    return sum(L)

def x_seq_and_bob(s):
    n = len(s) // 2
    l = 0
    X = []
    while l < n:
        h = 0
        max_t = 0
        for t in range(1, 2 * n - 2 * l + 1):
            pos = 2 * l + t
            if pos > len(s):
                break
            h += 1 if s[pos - 1] == '(' else -1
            if h == 0 and s[pos - 1] == ')':
                max_t = t
                break
            if h > 0:
                continue
        if max_t == 0:
            max_t = n - l
        X.append(max_t)
        l += max_t
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

def P_based_x_seq(s):
    P = []
    count_open = 0
    for pos, ch in enumerate(s):
        if ch == '(':
            count_open += 1
        else:
            P.append(pos + 1)
    n = len(s) // 2
    L_vals = [P[i] - i - 1 for i in range(n)]

    l = 0
    k = 0
    X = []
    while l < n:
        k += 1
        idx = l
        if idx >= n:
            break
        p_val = P[idx]
        x_val = p_val - 1 - 2 * l
        X.append(x_val)
        l = p_val - l - 1
    bob = sum(j * (X[j] - 1) for j in range(len(X)))
    return X, bob, len(X)

def analyze_orbit_alice(max_n, a_val, b_val):
    a = a_val % MOD
    b = b_val % MOD

    orbit_info = {}
    orbit_alice_sum = {}
    orbit_words = {}

    for n in range(1, max_n + 1):
        words = generate_dyck(n)
        for s in words:
            X, bob, k = x_seq_and_bob(s)
            Xw_raw = pair_seq([1] + X)
            bob_w = sum((j - 1) * Xw_raw[j - 1] for j in range(1, len(Xw_raw) + 1))
            k_w = len(Xw_raw)

            orbit_key = (n, bob_w, k_w)
            if orbit_key not in orbit_info:
                orbit_info[orbit_key] = []
                orbit_alice_sum[orbit_key] = 0
                orbit_words[orbit_key] = []
            alice_val = alice_of(s)
            orbit_info[orbit_key].append({
                'word': s,
                'X': X,
                'x1': X[0],
                'alice': alice_val,
                'bobw': bob_w,
                'kw': k_w,
            })
            orbit_alice_sum[orbit_key] = (orbit_alice_sum[orbit_key] + pow(a, alice_val, MOD)) % MOD
            orbit_words[orbit_key].append(s)

    print(f"=== Orbit Analysis for n=1..{max_n}, a={a_val}, b={b_val} ===")
    print()

    Xw_set = set()
    for (n, bw, kw) in orbit_info:
        Xw_set.add((n, bw, kw))

    by_n = {}
    for (n, bw, kw) in Xw_set:
        by_n.setdefault(n, []).append((bw, kw))

    for n in sorted(by_n):
        print(f"n={n}: {len(by_n[n])} wrapping orbits")
    print()

    for n in range(1, max_n + 1):
        orbits_n = [(bw, kw) for (nn, bw, kw) in Xw_set if nn == n]
        print(f"--- n={n} ({len(orbits_n)} orbits) ---")
        for bw, kw in sorted(orbits_n):
            entries = orbit_info[(n, bw, kw)]
            alpha = orbit_alice_sum[(n, bw, kw)]
            x1_counts = {}
            for e in entries:
                x1_counts[e['x1']] = x1_counts.get(e['x1'], 0) + 1
            print(f"  orbit (bw={bw}, kw={kw}): α={alpha}, words={len(entries)}, x1_dist={x1_counts}")
            for e in entries[:5]:
                print(f"    {e['word']}: X={e['X']}, x1={e['x1']}, alice={e['alice']}")
            if len(entries) > 5:
                print(f"    ... and {len(entries)-5} more")

    print()
    print("=== x1=2 vs x1>=3 alice analysis ===")
    print()

    for n in range(3, max_n + 1):
        words = generate_dyck(n)
        x1_2_words = []
        x1_ge3_words = []
        for s in words:
            X, _, _ = x_seq_and_bob(s)
            if X[0] == 2:
                x1_2_words.append(s)
            elif X[0] >= 3:
                x1_ge3_words.append(s)

        print(f"n={n}: x1=2: {len(x1_2_words)} words, x1>=3: {len(x1_ge3_words)} words")

    print()
    print("=== Orbit-to-orbit mapping analysis ===")
    print()

    for n in range(3, max_n + 1):
        print(f"--- n={n} orbit mapping ---")
        words = generate_dyck(n)
        for s in words:
            X, bob_orig, k_orig = x_seq_and_bob(s)
            x1 = X[0]

            Xw = pair_seq([1] + X)
            bw = sum((j-1)*Xw[j-1] for j in range(1, len(Xw)+1))
            kw = len(Xw)
            alice_val = alice_of(s)

            if x1 == 2:
                P_vals = [0]
                count_open = 0
                for pos, ch in enumerate(s):
                    if ch == '(':
                        count_open += 1
                    else:
                        P_vals.append(pos + 1)

                first_x_consume = X[0]
                rest_s = s[2*first_x_consume:]
                if rest_s:
                    rest_X, rest_bob, rest_k = x_seq_and_bob(rest_s)
                    rest_Xw = pair_seq([1] + rest_X)
                    rest_bw = sum((j-1)*rest_Xw[j-1] for j in range(1, len(rest_Xw)+1))
                    rest_kw = len(rest_Xw)
                    rest_n = len(rest_s) // 2
                else:
                    rest_X = []
                    rest_Xw = pair_seq([1])

    print()
    print("=== Detailed orbit mapping with x1 and sub-word analysis ===")
    print()

    for n in range(2, max_n + 1):
        words = generate_dyck(n)
        for s in words:
            X, bob_orig, k_orig = x_seq_and_bob(s)
            x1 = X[0]
            alice_val = alice_of(s)

            Xw = pair_seq([1] + X)
            bw = sum((j-1)*Xw[j-1] for j in range(1, len(Xw)+1))
            kw = len(Xw)

            rest = s[2*x1:] if 2*x1 < len(s) else ""
            if x1 >= 2 and rest:
                rest_X, rest_bob, rest_k = x_seq_and_bob(rest)
                rest_Xw = pair_seq([1] + rest_X)
                rest_bw = sum((j-1)*rest_Xw[j-1] for j in range(1, len(rest_Xw)+1))
                rest_kw = len(rest_Xw)
                rest_n = (len(rest)) // 2
                rest_alice = alice_of(rest)

                Xw_rest = pair_seq([1] + rest_X)

                if x1 == 2 and n <= 6:
                    print(f"  x1=2: s={s}, n={n}, alice={alice_val}, orbit=({bw},{kw})")
                    print(f"         rest={rest}, rest_n={rest_n}, rest_alice={rest_alice}")
                    print(f"         Xw={Xw}, rest_Xw={Xw_rest}")
                    print(f"         rest_orbit=({rest_bw},{rest_kw})")
                    print()
                if x1 == 3 and n <= 6:
                    print(f"  x1=3: s={s}, n={n}, alice={alice_val}, orbit=({bw},{kw})")
                    print(f"         rest={rest}, rest_n={rest_n}, rest_alice={rest_alice}")
                    print(f"         Xw={Xw}, rest_Xw={Xw_rest}")
                    print(f"         rest_orbit=({rest_bw},{rest_kw})")
                    print()

    print()
    print("=== KEY ANALYSIS: x1=2 → k-2, x1>=3 → k-1 mapping ===")
    print()

    for n in range(2, 9):
        words = generate_dyck(n)
        orbits_by_x1 = {}
        for s in words:
            X, _, _ = x_seq_and_bob(s)
            x1 = X[0]
            Xw = pair_seq([1] + X)
            bw = sum((j-1)*Xw[j-1] for j in range(1, len(Xw)+1))
            kw = len(Xw)
            if x1 not in orbits_by_x1:
                orbits_by_x1[x1] = set()
            orbits_by_x1[x1].add((bw, kw))
        print(f"n={n}: total orbits={len(set().union(*orbits_by_x1.values()))}")
        for x1 in sorted(orbits_by_x1):
            print(f"  x1={x1}: {len(orbits_by_x1[x1])} orbits")

    print()
    print("=== Verify x1=2 → removing () maps to k-2 orbit ===")
    for n in range(2, 8):
        words = generate_dyck(n)
        for s in words:
            X, _, _ = x_seq_and_bob(s)
            x1 = X[0]
            if x1 != 2:
                continue
            Xw = pair_seq([1] + X)
            bw = sum((j-1)*Xw[j-1] for j in range(1, len(Xw)+1))
            kw = len(Xw)

            rest = s[2*x1:]
            if not rest:
                continue
            rest_X, _, _ = x_seq_and_bob(rest)
            rest_Xw = pair_seq([1] + rest_X)
            rest_bw = sum((j-1)*rest_Xw[j-1] for j in range(1, len(rest_Xw)+1))
            rest_kw = len(rest_Xw)

            if n <= 6:
                print(f"  n={n}, s={s}, x1=2")
                print(f"    orbit=({bw},{kw}), rest={rest}, rest_orbit=({rest_bw},{rest_kw})")

    print()
    print("=== ALPHA analysis: Σ a^{alice} per orbit, across x1 branches ===")
    print()

    for n in range(1, 8):
        print(f"\nn={n}:")
        words = generate_dyck(n)
        orbit_alpha = {}
        for s in words:
            X, _, _ = x_seq_and_bob(s)
            Xw = pair_seq([1] + X)
            bw = sum((j-1)*Xw[j-1] for j in range(1, len(Xw)+1))
            kw = len(Xw)
            key = (bw, kw)
            if key not in orbit_alpha:
                orbit_alpha[key] = 0
            alice_val = alice_of(s)
            orbit_alpha[key] = (orbit_alpha[key] + pow(a_val, alice_val, MOD)) % MOD

        for (bw, kw), alpha in sorted(orbit_alpha.items()):
            print(f"  orbit (bw={bw}, kw={kw}): α = {alpha}")

    print()
    print("=== Formula attempt: alice for x1=2 and x1>=3 ===")
    print()

    for n in range(2, 9):
        words = generate_dyck(n)
        print(f"\nn={n}:")
        for s in words:
            X, _, _ = x_seq_and_bob(s)
            x1 = X[0]
            alice_val = alice_of(s)
            if 2*x1 <= len(s):
                rest = s[2*x1:]
                rest_alice = alice_of(rest) if rest else 0
                rest_n = len(rest) // 2 if rest else 0
                if x1 == 2:
                    print(f"  x1=2: s={s}, alice={alice_val}, rest_alice={rest_alice}, n={n}, rest_n={rest_n}")
                    print(f"         alice - rest_alice = {alice_val - rest_alice}")
                    print(f"         X={X}")
                elif x1 == 3 and n <= 6:
                    print(f"  x1=3: s={s}, alice={alice_val}, rest_alice={rest_alice}, n={n}, rest_n={rest_n}")
                    print(f"         alice - rest_alice = {alice_val - rest_alice}")
                    print(f"         X={X}")

if __name__ == '__main__':
    analyze_orbit_alice(8, 2, 3)
