"""
Compare solution_v14.cpp (C++ algorithm translated to Python)
against the Python reference (verify_bergeron.py).

The C++ code uses:
- NTT convolution with q-factorials
- q-binomial via: fact[r+k-1] / (fact[r] * fact[k-1])
"""

MOD = 998244353
PRIMITIVE_ROOT = 3


def modpow(a, e):
    r = 1
    while e:
        if e & 1:
            r = r * a % MOD
        a = a * a % MOD
        e >>= 1
    return r


def ntt(a, invert):
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]

    len_ = 2
    while len_ <= n:
        wlen = modpow(PRIMITIVE_ROOT, (MOD - 1) // len_)
        if invert:
            wlen = modpow(wlen, MOD - 2)
        for i in range(0, n, len_):
            w = 1
            for j in range(len_ // 2):
                u = a[i + j]
                v = a[i + j + len_ // 2] * w % MOD
                a[i + j] = (u + v) % MOD
                a[i + j + len_ // 2] = (u - v + MOD) % MOD
                w = w * wlen % MOD
        len_ <<= 1

    if invert:
        inv_n = modpow(n, MOD - 2)
        for i in range(n):
            a[i] = a[i] * inv_n % MOD


def cpp_v14_solve(N, a_val, b_val):
    """Exact translation of solution_v14.cpp algorithm."""
    a_val %= MOD
    b_val %= MOD

    N1 = N + 1
    N2 = N + 2

    pow_a = [0] * (N2 + 1)
    pow_b = [0] * (N2 + 1)
    inv_pow_b = [0] * (N2 + 1)
    pow_a[0] = pow_b[0] = inv_pow_b[0] = 1
    for i in range(1, N2 + 1):
        pow_a[i] = pow_a[i - 1] * a_val % MOD
        pow_b[i] = pow_b[i - 1] * b_val % MOD

    inv_b = modpow(b_val, MOD - 2)
    for i in range(1, N2 + 1):
        inv_pow_b[i] = inv_pow_b[i - 1] * inv_b % MOD

    powbinom = [0] * (N2 + 1)
    powbinom[0] = 1
    for k in range(1, N2 + 1):
        powbinom[k] = powbinom[k - 1] * pow_a[k - 1] % MOD

    fact = [0] * (N2 + 1)
    inv_fact = [0] * (N2 + 1)
    fact[0] = 1
    if a_val == 1:
        for i in range(1, N2 + 1):
            fact[i] = fact[i - 1] * i % MOD
    else:
        for i in range(1, N2 + 1):
            fact[i] = fact[i - 1] * (pow_a[i] - 1 + MOD) % MOD
    inv_fact[N2] = modpow(fact[N2], MOD - 2)
    if a_val == 1:
        for i in range(N2, 0, -1):
            inv_fact[i - 1] = inv_fact[i] * i % MOD
    else:
        for i in range(N2, 0, -1):
            inv_fact[i - 1] = inv_fact[i] * (pow_a[i] - 1 + MOD) % MOD

    def idx(n, k):
        return n * (n + 1) // 2 + k

    flat_size = idx(N2, N2) + 1
    H = [0] * flat_size

    for n in range(1, N2 + 1):
        H[idx(n, n)] = powbinom[n]

    ntt_size = 1
    while ntt_size <= 2 * N + 1:
        ntt_size <<= 1

    B = [0] * ntt_size
    for t in range(N2 + 1):
        B[t] = fact[t]
    B_ntt = B[:]
    ntt(B_ntt, False)

    A = [0] * ntt_size
    A_ntt = [0] * ntt_size
    C = [0] * ntt_size

    for m in range(1, N + 1):
        for i in range(ntt_size):
            A[i] = 0
        base_m = idx(m, 1)
        for r in range(1, m + 1):
            A[m - r] = H[base_m + r - 1] * inv_fact[r] % MOD

        for i in range(ntt_size):
            A_ntt[i] = A[i]
        ntt(A_ntt, False)
        for i in range(ntt_size):
            C[i] = A_ntt[i] * B_ntt[i] % MOD
        ntt(C, True)

        coef_m = pow_b[m]
        k_max = N1 - m
        for k in range(1, k_max + 1):
            conv_idx = m + k - 1
            val = coef_m * powbinom[k] % MOD * inv_fact[k - 1] % MOD * C[conv_idx] % MOD
            H[idx(m + k, k)] = val

    a_baseline = [0] * (N + 1)
    a_baseline[0] = 1
    for n in range(1, N + 1):
        a_baseline[n] = a_baseline[n - 1] * pow_a[n] % MOD

    result = []
    for n in range(1, N + 1):
        fn = a_baseline[n] * inv_pow_b[n] % MOD * H[idx(n + 1, 1)] % MOD
        result.append(fn)

    return result


# ======================== Python Reference ========================

def precompute_qbinom(N, q):
    qb = [[0] * (N + 1) for _ in range(N + 1)]
    for i in range(N + 1):
        qb[i][0] = qb[i][i] = 1
    for n in range(2, N + 1):
        for k in range(1, n):
            qb[n][k] = (qb[n - 1][k - 1] + pow(q, k, MOD) * qb[n - 1][k]) % MOD
    return qb


def compute_Fn_from_bergeron(N, a_val, b_val):
    """Python reference from verify_bergeron.py"""
    a_val %= MOD
    b_val %= MOD
    qb = precompute_qbinom(N + 1, a_val)

    powbinom = [1] * (N + 3)
    for k in range(1, N + 3):
        powbinom[k] = pow(a_val, k * (k - 1) // 2, MOD)

    powb = [1] * (N + 3)
    for d in range(1, N + 3):
        powb[d] = powb[d - 1] * b_val % MOD

    H = [[0] * (N + 3) for _ in range(N + 4)]

    for n in range(1, N + 2):
        H[n][n] = powbinom[n]
        for k in range(1, n):
            d = n - k
            total = 0
            for r in range(1, d + 1):
                term = qb[r + k - 1][r] * H[d][r] % MOD
                total = (total + term) % MOD
            H[n][k] = powb[d] * powbinom[k] % MOD * total % MOD

    inv_b = pow(b_val, MOD - 2, MOD)
    Cn = [0] * (N + 1)
    for n in range(1, N + 1):
        inv_bn = pow(inv_b, n, MOD)
        Cn[n] = inv_bn * H[n + 1][1] % MOD

    Fn = []
    for n, c in enumerate(Cn[1:], 1):
        baseline = pow(a_val, n * (n + 1) // 2, MOD)
        Fn.append(baseline * c % MOD)
    return Fn


# ======================== Brute Force (n <= 8) ========================

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
    cnt = 0
    for i in range(len(s)):
        if s[i] == '(':
            for j in range(i + 1, len(s)):
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


def brute_force_Fn(N, a_val, b_val):
    results = []
    for n in range(1, N + 1):
        words = generate_dyck(n)
        total = 0
        for s in words:
            alice = alice_of(s)
            X, bob = x_seq_and_bob(s)
            total = (total + pow(a_val, alice, MOD) * pow(b_val, bob, MOD)) % MOD
        results.append(total)
    return results


# ======================== Comparison ========================

def compare_fns(name_a, F_a, name_b, F_b, N):
    """Compare two F arrays element by element."""
    mismatches = []
    for i in range(min(len(F_a), len(F_b))):
        if F_a[i] != F_b[i]:
            mismatches.append((i + 1, F_a[i], F_b[i]))
    return mismatches


def run_test(N, a_val, b_val, compare_brute_force=True):
    """Run one test case and report results."""
    a_val_mod = a_val % MOD
    b_val_mod = b_val % MOD

    print(f"\n{'='*60}")
    print(f"Test: N={N}, a={a_val}, b={b_val} (mod: a={a_val_mod}, b={b_val_mod})")

    # C++ translated
    try:
        F_cpp = cpp_v14_solve(N, a_val, b_val)
        cpp_ok = True
    except Exception as e:
        print(f"  C++v14 ERROR: {e}")
        F_cpp = None
        cpp_ok = False

    # Python reference
    try:
        F_ref = compute_Fn_from_bergeron(N, a_val, b_val)
        ref_ok = True
    except Exception as e:
        print(f"  Reference ERROR: {e}")
        F_ref = None
        ref_ok = False

    if cpp_ok and ref_ok:
        mm = compare_fns("C++v14", F_cpp, "Reference", F_ref, N)
        if mm:
            print(f"  C++v14 vs Reference: {len(mm)} MISMATCHES (out of {N})")
            for n, cpp_val, ref_val in mm[:10]:
                print(f"    n={n}: cpp={cpp_val}, ref={ref_val}")
            if len(mm) > 10:
                print(f"    ... and {len(mm) - 10} more")
        else:
            print(f"  C++v14 vs Reference: ALL OK (n=1..{N})")
    else:
        if cpp_ok:
            print(f"  C++v14 first 5: {F_cpp[:min(5, len(F_cpp))]}")
        if ref_ok:
            print(f"  Reference first 5: {F_ref[:min(5, len(F_ref))]}")
        if cpp_ok and ref_ok:
            mm = compare_fns("C++v14", F_cpp, "Reference", F_ref, N)
            if mm:
                print(f"  Mismatches: {len(mm)}")
                for n, cpp_val, ref_val in mm[:5]:
                    print(f"    n={n}: cpp={cpp_val}, ref={ref_val}")

    # Brute force for small N
    if compare_brute_force and N <= 8:
        try:
            F_bf = brute_force_Fn(N, a_val, b_val)
            if cpp_ok:
                mm = compare_fns("C++v14", F_cpp, "BruteForce", F_bf, N)
                if mm:
                    print(f"  C++v14 vs BruteForce: {len(mm)} MISMATCHES")
                    for n, cpp_val, bf_val in mm[:5]:
                        print(f"    n={n}: cpp={cpp_val}, bf={bf_val}")
                else:
                    print(f"  C++v14 vs BruteForce: ALL OK")
            if ref_ok:
                mm = compare_fns("Reference", F_ref, "BruteForce", F_bf, N)
                if mm:
                    print(f"  Reference vs BruteForce: {len(mm)} MISMATCHES (this is unexpected!)")
                else:
                    print(f"  Reference vs BruteForce: ALL OK")
        except Exception as e:
            print(f"  BruteForce ERROR: {e}")

    return F_cpp, F_ref


def main():
    print("=" * 70)
    print("  SOLUTION_V14.CPP BUG HUNT - Comparing C++v14 vs Python Reference")
    print("=" * 70)

    # Phase 1: Small tests with brute force verification
    print("\n" + "=" * 70)
    print("  PHASE 1: Small N tests with brute force verification (N <= 8)")
    print("=" * 70)

    small_tests = [
        (8, 2, 3), (8, 3, 2), (8, 5, 7), (8, 7, 11),
        (8, 1, 1), (8, 1, 7), (8, 7, 1),
        (8, 123, 456),
        (8, MOD - 1, 2),
        (8, 2, MOD - 1),
        (8, 1234567 % MOD, 7654321 % MOD),
        (8, 1, 2), (8, 1, MOD - 1),
        (8, 2, 1), (8, MOD - 1, 1),
        (8, MOD - 1, MOD - 2),
        (8, MOD - 2, MOD - 1),
    ]

    all_failures = []

    for N, a, b in small_tests:
        F_cpp, F_ref = run_test(N, a, b)
        if F_cpp and F_ref:
            mm = compare_fns("C++v14", F_cpp, "Reference", F_ref, N)
            if mm:
                all_failures.append((N, a, b, mm))

    # Phase 2: Medium tests (N <= 10 comparison with reference only)
    print("\n" + "=" * 70)
    print("  PHASE 2: Medium N tests (N=10, 20, 30, 50)")
    print("=" * 70)

    for N in [10, 20, 30, 50]:
        for a, b in [(2, 3), (5, 7), (3, 2), (1, 1), (MOD - 1, 2), (2, MOD - 1)]:
            F_cpp, F_ref = run_test(N, a, b, compare_brute_force=False)
            if F_cpp and F_ref:
                mm = compare_fns("C++v14", F_cpp, "Reference", F_ref, N)
                if mm:
                    all_failures.append((N, a, b, mm))

    # Phase 3: Large tests with specific combos
    print("\n" + "=" * 70)
    print("  PHASE 3: Large N tests (N=100) with reference")
    print("=" * 70)

    for a, b in [(2, 3), (5, 7), (3, 2), (1, 1), (MOD - 1, 2), (2, MOD - 1)]:
        N = 100
        F_cpp, F_ref = run_test(N, a, b, compare_brute_force=False)
        if F_cpp and F_ref:
            mm = compare_fns("C++v14", F_cpp, "Reference", F_ref, N)
            if mm:
                all_failures.append((N, a, b, mm))

    # Phase 4: Test a=b with large values
    print("\n" + "=" * 70)
    print("  PHASE 4: a=b tests with medium N")
    print("=" * 70)
    for ab in [2, 10, 100, 1000000, MOD // 2]:
        for N in [10, 50]:
            F_cpp, F_ref = run_test(N, ab, ab, compare_brute_force=False)
            if F_cpp and F_ref:
                mm = compare_fns("C++v14", F_cpp, "Reference", F_ref, N)
                if mm:
                    all_failures.append((N, ab, ab, mm))

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY OF FAILURES")
    print("=" * 70)
    if all_failures:
        print(f"Total failing test cases: {len(all_failures)}")
        for N, a, b, mm in all_failures:
            a_mod = a % MOD
            b_mod = b % MOD
            print(f"  N={N}, a={a_mod}, b={b_mod}: {len(mm)} mismatches")
            for n, cpp_val, ref_val in mm[:3]:
                print(f"    n={n}: cpp={cpp_val}, ref={ref_val}")
            if len(mm) > 3:
                print(f"    ... {len(mm) - 3} more")
    else:
        print("ALL TESTS PASSED! No mismatches found.")

    # Also report passing cases
    print(f"\nTotal passing cases: all others")


if __name__ == '__main__':
    main()
