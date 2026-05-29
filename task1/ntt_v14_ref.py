"""
Python reference for v14 NTT convolution algorithm.
Mirrors solution_v14.cpp exactly for debugging.
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

def solve_v14_py(N, a_val, b_val):
    a_val %= MOD
    b_val %= MOD
    N1 = N + 1
    N2 = N + 2

    pow_a = [1] * (N2 + 1)
    pow_b = [1] * (N2 + 1)
    inv_pow_b = [1] * (N2 + 1)
    for i in range(1, N2 + 1):
        pow_a[i] = pow_a[i - 1] * a_val % MOD
        pow_b[i] = pow_b[i - 1] * b_val % MOD

    inv_b = modpow(b_val, MOD - 2)
    for i in range(1, N2 + 1):
        inv_pow_b[i] = inv_pow_b[i - 1] * inv_b % MOD

    powbinom = [1] * (N2 + 1)
    for k in range(1, N2 + 1):
        powbinom[k] = powbinom[k - 1] * pow_a[k - 1] % MOD

    fact = [1] * (N2 + 1)
    inv_fact = [0] * (N2 + 1)
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

    for m in range(1, N + 1):
        A = [0] * ntt_size
        base_m = idx(m, 1)
        for r in range(1, m + 1):
            A[m - r] = H[base_m + r - 1] * inv_fact[r] % MOD

        A_ntt = A[:]
        ntt(A_ntt, False)
        C = [A_ntt[i] * B_ntt[i] % MOD for i in range(ntt_size)]
        ntt(C, True)

        coef_m = pow_b[m]
        k_max = N1 - m
        for k in range(1, k_max + 1):
            conv_idx = m + k - 1
            val = coef_m * powbinom[k] % MOD * inv_fact[k - 1] % MOD * C[conv_idx] % MOD
            H[idx(m + k, k)] = val

    a_baseline = [1] * (N + 1)
    for n in range(1, N + 1):
        a_baseline[n] = a_baseline[n - 1] * pow_a[n] % MOD

    result = []
    for n in range(1, N + 1):
        fn = a_baseline[n] * inv_pow_b[n] % MOD * H[idx(n + 1, 1)] % MOD
        result.append(fn)
    return result


if __name__ == '__main__':
    import sys, random
    sys.path.insert(0, '.')
    from verify_bergeron import brute_force_Fn, compute_Fn_from_bergeron

    MOD_py = 998244353

    print("=== Python NTT v14 ref vs Bergeron O(N^3) ref ===")
    random.seed(42)
    failures = []
    for test_id in range(100):
        a = random.randint(1, MOD_py - 1)
        b = random.randint(1, MOD_py - 1)
        N = min(random.randint(2, 10), 8)  # keep small for speed
        v14_py = solve_v14_py(N, a, b)
        berg = compute_Fn_from_bergeron(N, a, b)
        ok = all(v14_py[i] == berg[i] for i in range(N))
        if not ok:
            print(f"FAIL test {test_id}: N={N}, a={a}, b={b}")
            for i in range(N):
                if v14_py[i] != berg[i]:
                    print(f"  n={i+1}: py_ntt={v14_py[i]} bergeron={berg[i]}")
            failures.append((N, a, b))
        else:
            print(f"  test {test_id}: N={N}, a={a%1000}..., b={b%1000}... OK")
        if len(failures) >= 5:
            break

    print(f"\nTotal failures: {len(failures)}")
    if failures:
        print("First few failure params:")
        for N, a, b in failures[:3]:
            print(f"  N={N}, a={a}, b={b}")
