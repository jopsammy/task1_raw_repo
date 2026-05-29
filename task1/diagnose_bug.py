"""
Diagnostic: Confirm the root cause of the bug and test extended cases.

Bug hypothesis: When a has SMALL multiplicative order d (i.e., a^d = 1 mod MOD),
then fact[d] = 0 (mod MOD), making modular inverse computation fail.
This causes the NTT convolution approach in solution_v14.cpp to output all zeros.

This script:
1. Confirms the root cause for a = MOD-1
2. Tests other a values with small order (order 4, 7, 8, etc.)
3. Tests random a values to ensure no other bugs
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


def find_order(a):
    """Find the multiplicative order of a mod MOD."""
    if a == 1:
        return 1
    if a == 0:
        return None  # undefined
    # MOD-1 = 998244352 = 2^23 * 7 * 17
    # We could compute full factorization, but let's just test small divisors
    order = MOD - 1
    # Test dividing by prime factors repeatedly
    primes = [2, 7, 17]
    for p in primes:
        while order % p == 0:
            if modpow(a, order // p) == 1:
                order //= p
            else:
                break
    return order


def smallest_i_with_a_pow_1(a, max_i):
    """Find smallest i <= max_i such that a^i = 1 mod MOD, or return None."""
    cur = 1
    for i in range(1, max_i + 1):
        cur = cur * a % MOD
        if cur == 1:
            return i
    return None


def precompute_qbinom(N, q):
    """Recurrence based, works for any q."""
    qb = [[0] * (N + 1) for _ in range(N + 1)]
    for i in range(N + 1):
        qb[i][0] = qb[i][i] = 1
    for n in range(2, N + 1):
        for k in range(1, n):
            qb[n][k] = (qb[n - 1][k - 1] + pow(q, k, MOD) * qb[n - 1][k]) % MOD
    return qb


def compute_Fn_reference(N, a_val, b_val):
    """Reference Bergeron recurrence with qb recurrence, works for any a."""
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


# ============ NTT-based (C++v14 algorithm) ============

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
    """Exact translation of solution_v14.cpp."""
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


# ============ FIXED C++v14 (using residue class approach) ============

def cpp_v14_fixed_solve(N, a_val, b_val):
    """
    Fixed version that handles a values with small multiplicative order.
    
    Strategy:
    - Compute order d = smallest i s.t. a^i = 1 mod MOD
    - If d > N+2: use standard NTT approach (no zero factors)
    - If d <= N+2: precompute qb via recurrence, then use NTT with
      zero-factor handling (one convolution per residue class mod d)
    """
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

    def idx(n, k):
        return n * (n + 1) // 2 + k

    flat_size = idx(N2, N2) + 1
    H = [0] * flat_size

    for n in range(1, N2 + 1):
        H[idx(n, n)] = powbinom[n]

    ntt_size = 1
    while ntt_size <= 2 * N + 1:
        ntt_size <<= 1

    # Determine if a has small order
    order_d = smallest_i_with_a_pow_1(a_val, N2 + 1)

    if order_d is None or order_d > N2:
        # Standard approach: no zero factors in fact array
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
    else:
        # a has small order d. Use per-residue-class convolution.
        d = order_d
        
        # Precompute stripped_fact (product of non-zero factors only)
        stripped_fact = [1] * (N2 + 1)
        inv_stripped = [0] * (N2 + 1)
        for i in range(1, N2 + 1):
            factor = (pow_a[i] - 1 + MOD) % MOD
            if factor != 0:
                stripped_fact[i] = stripped_fact[i - 1] * factor % MOD
            else:
                stripped_fact[i] = stripped_fact[i - 1]
        inv_stripped[N2] = modpow(stripped_fact[N2], MOD - 2)
        for i in range(N2, 0, -1):
            factor = (pow_a[i] - 1 + MOD) % MOD
            if factor != 0:
                inv_stripped[i - 1] = inv_stripped[i] * factor % MOD
            else:
                inv_stripped[i - 1] = inv_stripped[i]

        # Precompute B = stripped_fact for NTT
        B = [0] * ntt_size
        for t in range(N2 + 1):
            B[t] = stripped_fact[t]
        B_ntt = B[:]
        ntt(B_ntt, False)

        A = [0] * ntt_size
        C = [0] * ntt_size

        for m in range(1, N + 1):
            # Zero out C accumulator for this m
            k_max = N1 - m
            C_sum = [0] * ntt_size

            # Process each residue class separately
            for s in range(d):
                for i in range(ntt_size):
                    A[i] = 0
                base_m = idx(m, 1)
                
                # Fill A with only r where r % d == s
                for r in range(1, m + 1):
                    if r % d == s:
                        A[m - r] = H[base_m + r - 1] * inv_stripped[r] % MOD

                # Skip if A is all zeros
                has_nonzero = any(v != 0 for v in A[:m])
                if not has_nonzero:
                    continue

                # NTT for this residue class
                A_ntt = A[:]
                ntt(A_ntt, False)
                for i in range(ntt_size):
                    C[i] = A_ntt[i] * B_ntt[i] % MOD
                ntt(C, True)

                # Add valid k contributions
                coef_m = pow_b[m]
                for k in range(1, k_max + 1):
                    # Check if this (s, k) pair is valid
                    km1_mod = (k - 1) % d
                    if s + km1_mod >= d:
                        continue  # zero condition: qb = 0
                    
                    conv_idx = m + k - 1
                    val = coef_m * powbinom[k] % MOD * inv_stripped[k - 1] % MOD * C[conv_idx] % MOD
                    C_sum[conv_idx] = (C_sum[conv_idx] + val) % MOD

            # Write results back to H
            for k in range(1, k_max + 1):
                conv_idx = m + k - 1
                H[idx(m + k, k)] = C_sum[conv_idx]

    a_baseline = [0] * (N + 1)
    a_baseline[0] = 1
    for n in range(1, N + 1):
        a_baseline[n] = a_baseline[n - 1] * pow_a[n] % MOD

    result = []
    for n in range(1, N + 1):
        fn = a_baseline[n] * inv_pow_b[n] % MOD * H[idx(n + 1, 1)] % MOD
        result.append(fn)

    return result


# ============ Brute force for n <= 8 ============

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


# ============ Main Diagnostic ============

def main():
    print("=" * 70)
    print("  DIAGNOSTIC: Root Cause Analysis for solution_v14.cpp Bug")
    print("=" * 70)

    # Test 1: Find order of various a values
    print("\n--- Part 1: Order of a values ---")
    test_a_vals = [MOD - 1, MOD - 2, 2, 3, 5, 7, 123, 1, 0]
    for a in test_a_vals:
        if a > 0:
            small_i = smallest_i_with_a_pow_1(a, 100)
            order = find_order(a)
            print(f"  a={a}: order={order}, smallest_i_with_pow1(≤100)={small_i}")

    # Test 2: Verify that fact becomes 0 for a = MOD-1
    print("\n--- Part 2: fact array for a = MOD-1 ---")
    a = MOD - 1
    fact = [1] * 10
    for i in range(1, 10):
        pow_a_i = modpow(a, i)
        fact[i] = fact[i-1] * (pow_a_i - 1 + MOD) % MOD
        print(f"  a^{i}={pow_a_i}, a^{i}-1={(pow_a_i - 1 + MOD) % MOD}, fact[{i}]={fact[i]}")

    # Test 3: Compare C++v14, C++v14_fixed vs Reference for key cases
    print("\n--- Part 3: Compare algorithms for key cases ---")

    test_cases = [
        (8, MOD - 1, 2),
        (8, MOD - 1, 1),
        (8, MOD - 1, MOD - 2),
        (8, 2, 3),
        (8, 1, 1),
        (20, MOD - 1, 2),
        (30, MOD - 1, 2),
        (50, MOD - 1, 2),
    ]

    for N, a, b in test_cases:
        a_mod = a % MOD
        b_mod = b % MOD
        print(f"\n  N={N}, a={a_mod}, b={b_mod}:")

        F_ref = compute_Fn_reference(N, a, b)
        F_cpp = cpp_v14_solve(N, a, b)
        F_fixed = cpp_v14_fixed_solve(N, a, b)

        mm_cpp = [(i+1, F_cpp[i], F_ref[i]) for i in range(N) if F_cpp[i] != F_ref[i]]
        mm_fixed = [(i+1, F_fixed[i], F_ref[i]) for i in range(N) if F_fixed[i] != F_ref[i]]

        if mm_cpp:
            print(f"    C++v14: {len(mm_cpp)}/{N} mismatches (first 3: {mm_cpp[:3]})")
        else:
            print(f"    C++v14: ALL OK")

        if mm_fixed:
            print(f"    FIXED:  {len(mm_fixed)}/{N} mismatches (first 3: {mm_fixed[:3]})")
        else:
            print(f"    FIXED:  ALL OK")

        # Brute force verification for N <= 8
        if N <= 8:
            F_bf = brute_force_Fn(N, a, b)
            mm_ref_bf = [(i+1, F_ref[i], F_bf[i]) for i in range(N) if F_ref[i] != F_bf[i]]
            if mm_ref_bf:
                print(f"    WARNING: Reference vs BruteForce: {len(mm_ref_bf)} mismatches!")
            else:
                print(f"    Reference vs BruteForce: OK")

    # Test 4: Exhaustive small N for a=MOD-1 (order 2)
    print("\n--- Part 4: Exhaustive test for a=MOD-1, various b ---")
    a = MOD - 1
    for N in [5, 8, 10, 15]:
        for b in [2, 3, 5, MOD-1, MOD-2, 1]:
            F_ref = compute_Fn_reference(N, a, b)
            F_fixed = cpp_v14_fixed_solve(N, a, b)
            mm = [(i+1, F_fixed[i], F_ref[i]) for i in range(N) if F_fixed[i] != F_ref[i]]
            if mm:
                print(f"  FAIL N={N}, b={b%MOD}: {len(mm)} mismatches")
                for n, f_val, r_val in mm[:3]:
                    print(f"    n={n}: fixed={f_val}, ref={r_val}")
            else:
                pass  # print(f"  OK N={N}, b={b%MOD}")  # silent for OK

    # Test 5: Test with a having order 4
    print("\n--- Part 5: Find and test a with order 4 ---")
    # Find an element of order 4
    found = None
    for a_candidate in range(2, 100000):
        if modpow(a_candidate, 2) != 1 and modpow(a_candidate, 4) == 1:
            found = a_candidate
            break
    if found:
        print(f"  Found a with order 4: a={found}")
        for N in [8, 15, 30]:
            for b in [2, 3]:
                F_ref = compute_Fn_reference(N, found, b)
                F_fixed = cpp_v14_fixed_solve(N, found, b)
                mm = [(i+1, F_fixed[i], F_ref[i]) for i in range(N) if F_fixed[i] != F_ref[i]]
                if mm:
                    print(f"  FAIL N={N}, a={found}, b={b}: {len(mm)} mismatches")
                    for n, f_val, r_val in mm[:3]:
                        print(f"    n={n}: fixed={f_val}, ref={r_val}")
                else:
                    print(f"  OK N={N}, a={found}, b={b}")
    else:
        print("  No order-4 element found in small range")

    print("\n--- Done ---")


if __name__ == '__main__':
    main()
