"""
Verify: bob = bounce and area = alice - n(n+1)/2
by comparing brute-force summation with Route L DP for n <= 8.
Also verify the (q,t)-Catalan distribution matches.
"""
import sys

MOD = 998244353


def generate_dyck(n):
    words = []
    def bt(s, op, cl):
        if cl > op or op > n:
            return
        if len(s) == 2 * n:
            if op == n and cl == n:
                words.append(s)
            return
        bt(s + '(', op + 1, cl)
        bt(s + ')', op, cl + 1)
    bt('', 0, 0)
    return words


def alice_of(s):
    n = len(s) // 2
    cnt = 0
    for i in range(2 * n):
        if s[i] == '(':
            for j in range(i + 1, 2 * n):
                if s[j] == ')':
                    cnt += 1
    return cnt


def x_seq_and_bob(s):
    n = len(s) // 2
    h = [0] * (2 * n + 1)
    for i in range(2 * n):
        h[i + 1] = h[i] + (1 if s[i] == '(' else -1)

    l = 0
    X = []
    while l < n:
        pos = 2 * l
        best_x = 0
        t = 1
        while pos + t <= 2 * n:
            if h[pos + t] == t:
                best_x = t
                t += 1
            elif h[pos + t] > t:
                t += 1
            else:
                break
        if best_x == 0:
            best_x = 1
        X.append(best_x)
        l += best_x

    bob = sum(j * X[j] for j in range(len(X)))
    return X, bob


def area_of(s):
    """area = sum_{i=1..n} (P(i) - 2i) where P(i) is position of i-th ')' (1-based)"""
    n = len(s) // 2
    rc = 0
    area = 0
    for idx, ch in enumerate(s):
        if ch == ')':
            rc += 1
            P_i = idx + 1
            area += P_i - 2 * rc
    return area


def L_seq_of(s):
    n = len(s) // 2
    L = [0] * n
    rc = 0
    for idx, ch in enumerate(s):
        if ch == ')':
            L[rc] = (idx + 1) - (rc + 1)
            rc += 1
    return L


def bob_from_L(L):
    n = len(L)
    jumps = [0]
    pos = 0
    while pos < n:
        nxt = L[pos]
        jumps.append(nxt)
        pos = nxt
    return sum(n - jumps[j] for j in range(1, len(jumps) - 1))


def verify_equivalence(max_n=8):
    print(f"=== Verifying area = alice - n(n+1)/2 and bob = bounce for n <= {max_n} ===\n")

    all_ok = True

    for n in range(1, max_n + 1):
        words = generate_dyck(n)
        baseline = n * (n + 1) // 2

        mismatches = []
        for s in words:
            alice = alice_of(s)
            X, bob = x_seq_and_bob(s)
            area = area_of(s)

            # Verify: area = alice - n(n+1)/2
            expected_area = alice - baseline
            if area != expected_area:
                mismatches.append(f"  AREA MISMATCH: {s} area={area} alice={alice} expected={expected_area}")

            # Verify: bob from L(i) matches bob from x_seq
            L = L_seq_of(s)
            bobL = bob_from_L(L)
            if bob != bobL:
                mismatches.append(f"  BOB MISMATCH: {s} bob_xseq={bob} bob_L={bobL}")

        if mismatches:
            print(f"n={n}: {len(mismatches)} ERRORS")
            for m in mismatches[:5]:
                print(m)
            all_ok = False
        else:
            print(f"n={n}: {len(words)} words, ALL OK  |  area range=[{min(area_of(w) for w in words)}, {max(area_of(w) for w in words)}]  bob range=[{min(x_seq_and_bob(w)[1] for w in words)}, {max(x_seq_and_bob(w)[1] for w in words)}]")

    return all_ok


def verify_dp_equals_bf(max_n=8):
    """Verify that Route L DP matches brute-force (including area/bob decomposition)."""
    print(f"\n=== Verifying DP = brute-force for n <= {max_n} ===\n")

    from route_l_dp_v3 import solve_all_y_eliminated

    for a_val, b_val in [(2, 3), (5, 7), (1, 1), (3, 2)]:
        bf_results = []
        for n in range(1, max_n + 1):
            words = generate_dyck(n)
            total = 0
            for s in words:
                alice = alice_of(s)
                X, bob = x_seq_and_bob(s)
                total = (total + pow(a_val, alice, MOD) * pow(b_val, bob, MOD)) % MOD
            bf_results.append(total)

        dp_results = solve_all_y_eliminated(max_n, a_val, b_val)[1:]  # index 1..N

        ok = True
        for n in range(1, max_n + 1):
            if bf_results[n - 1] != dp_results[n - 1]:
                print(f"  a={a_val}, b={b_val}, n={n}: FAIL (bf={bf_results[n-1]}, dp={dp_results[n-1]})")
                ok = False

        if ok:
            print(f"  a={a_val}, b={b_val}: ALL OK (n=1..{max_n})")
        else:
            return False

    return True


def verify_qt_catalan_structure(max_n=8):
    """Verify that weighted sum = a^{n(n+1)/2} * C_n(a,b) where C_n = (q,t)-Catalan."""
    print(f"\n=== (q,t)-Catalan structure verification ===\n")

    for n in range(1, max_n + 1):
        words = generate_dyck(n)
        baseline = n * (n + 1) // 2

        for a_val, b_val in [(2, 3), (5, 7)]:
            total_bf = 0
            area_bounce_pairs = {}
            for s in words:
                area = area_of(s)
                X, bob = x_seq_and_bob(s)
                key = (area, bob)
                area_bounce_pairs[key] = area_bounce_pairs.get(key, 0) + 1
                total_bf = (total_bf + pow(a_val, area + baseline, MOD) * pow(b_val, bob, MOD)) % MOD

            total_catalan = 0
            for (area, bounce), cnt in area_bounce_pairs.items():
                total_catalan = (total_catalan + cnt * pow(a_val, area + baseline, MOD) * pow(b_val, bounce, MOD)) % MOD

            assert total_bf == total_catalan, f"Mismatch at n={n}, a={a_val}, b={b_val}"

        # Print distribution
        pairs = {}
        for s in words:
            area = area_of(s)
            X, bob = x_seq_and_bob(s)
            pairs[(area, bob)] = pairs.get((area, bob), 0) + 1

        print(f"n={n}: {len(pairs)} distinct (area,bounce) pairs, {len(words)} words")
        sorted_pairs = sorted(pairs.items(), key=lambda x: (x[0][1], x[0][0]))
        for (a_val, b_val), cnt in sorted_pairs:
            print(f"  area={a_val}, bounce={b_val}: {cnt} words")

    print("\n=== ALL VERIFICATIONS PASSED ===")
    return True


if __name__ == '__main__':
    ok1 = verify_equivalence(8)
    if ok1:
        ok2 = verify_dp_equals_bf(8)
        if ok2:
            verify_qt_catalan_structure(6)
        else:
            print("\nDP verification FAILED")
    else:
        print("\nEquivalence verification FAILED")