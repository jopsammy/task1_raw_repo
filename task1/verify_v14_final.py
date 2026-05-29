"""
Full Python verification of the q-Lucas + residue NTT algorithm.
Tests Good path (original NTT), Bad path (q-Lucas), and final F[n] output.
"""
MOD = 998244353

def modpow(a, e):
    r = 1
    while e:
        if e & 1: r = r * a % MOD
        a = a * a % MOD
        e >>= 1
    return r

def find_order(a_val):
    if a_val == 1: return 1
    v = a_val % MOD
    for d in range(1, 20000):
        if v == 1: return d
        v = v * a_val % MOD
    return MOD - 1

def ntt(a, invert):
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit: j ^= bit; bit >>= 1
        j ^= bit
        if i < j: a[i], a[j] = a[j], a[i]
    len_ = 2
    while len_ <= n:
        wlen = modpow(3, (MOD - 1) // len_)
        if invert: wlen = modpow(wlen, MOD - 2)
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
        for i in range(n): a[i] = a[i] * inv_n % MOD

def solve_v14_final(N, a_val, b_val):
    """Mirror of the final solution_v14.cpp"""
    a_val %= MOD; b_val %= MOD
    N1 = N + 1; N2 = N + 2

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

    def idx(n, k):
        return n * (n + 1) // 2 + k
    H = [0] * (idx(N2, N2) + 1)
    for n in range(1, N2 + 1):
        H[idx(n, n)] = powbinom[n]

    ord_fact = [1] * (N2 + 3)
    for i in range(1, N2 + 3):
        ord_fact[i] = ord_fact[i - 1] * i % MOD
    inv_ord_fact = [0] * (N2 + 3)
    inv_ord_fact[N2 + 2] = modpow(ord_fact[N2 + 2], MOD - 2)
    for i in range(N2 + 2, 0, -1):
        inv_ord_fact[i - 1] = inv_ord_fact[i] * i % MOD

    order_d = -1
    fact = [1] * (N2 + 1)
    if a_val == 1:
        for i in range(1, N2 + 1):
            fact[i] = fact[i - 1] * i % MOD
    else:
        for i in range(1, N2 + 1):
            term = (pow_a[i] - 1 + MOD) % MOD
            if term == 0 and order_d < 0:
                order_d = i
            fact[i] = fact[i - 1] * term % MOD

    is_bad = (order_d > 0 and order_d <= N2)

    if not is_bad:
        # Good path: original NTT
        inv_fact = [0] * (N2 + 1)
        inv_fact[N2] = modpow(fact[N2], MOD - 2)
        if a_val == 1:
            for i in range(N2, 0, -1):
                inv_fact[i - 1] = inv_fact[i] * i % MOD
        else:
            for i in range(N2, 0, -1):
                term = (pow_a[i] - 1 + MOD) % MOD
                inv_fact[i - 1] = inv_fact[i] * term % MOD

        ntt_size = 1
        while ntt_size <= 2 * N + 1: ntt_size <<= 1

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
                val = coef_m * powbinom[k] % MOD * inv_fact[k - 1] % MOD * C[m + k - 1] % MOD
                H[idx(m + k, k)] = val
    else:
        # Bad path: q-Lucas + residue NTT
        d = order_d
        
        qb_small = [[0] * (d + 1) for _ in range(d + 1)]
        for n in range(d + 1):
            qb_small[n][0] = qb_small[n][n] = 1
        
        qb_prev = [0] * (d + 1)
        qb_curr = [0] * (d + 1)
        qb_prev[0] = 1
        for n in range(1, d + 1):
            qb_curr[0] = 1
            qb_curr[n] = 1
            ak = a_val
            for k in range(1, n):
                qb_curr[k] = (qb_prev[k - 1] + ak * qb_prev[k]) % MOD
                ak = ak * a_val % MOD
            for k in range(n + 1):
                qb_small[n][k] = qb_curr[k]
            qb_prev, qb_curr = qb_curr, [0] * (d + 1)

        K_max = N // d + 2
        ntt_size = 1
        while ntt_size <= 2 * N // d + 5: ntt_size <<= 1

        B_ntt = [ord_fact[j] if j <= N2 + 2 else 0 for j in range(ntt_size)]
        ntt(B_ntt, False)

        for m in range(1, N + 1):
            contrib = [[0] * d for _ in range(K_max)]

            for r_rem in range(d):
                r_div_start = 1 if r_rem == 0 else 0
                M_div = (m - r_rem) // d
                if M_div < r_div_start: continue
                cnt = M_div - r_div_start + 1

                A_flip = [0] * ntt_size
                base_m = idx(m, r_div_start * d + r_rem)
                offset = r_div_start
                for i in range(cnt):
                    A_flip[cnt - 1 - i] = H[base_m + i * d] * inv_ord_fact[offset + i] % MOD

                ntt(A_flip, False)
                conv = [A_flip[i] * B_ntt[i] % MOD for i in range(ntt_size)]
                ntt(conv, True)

                base_pos = r_div_start + cnt - 1
                for X in range(K_max):
                    pos = base_pos + X
                    if pos < ntt_size:
                        contrib[X][r_rem] = inv_ord_fact[X] * conv[pos] % MOD

            coef_m = pow_b[m]
            k_max_m = N1 - m

            for K in range(K_max):
                sum_d = [0] * d
                C_K = contrib[K]
                C_K1 = contrib[K + 1] if K + 1 < K_max else None

                for r_rem in range(d):
                    c0 = C_K[r_rem]
                    c1 = C_K1[r_rem] if C_K1 else 0
                    qb_col = qb_small

                    lim0 = d - r_rem
                    for k1 in range(lim0):
                        sum_d[k1] = (sum_d[k1] + qb_col[r_rem + k1][r_rem] * c0) % MOD
                    for k1 in range(lim0, d):
                        sum_d[k1] = (sum_d[k1] + qb_col[r_rem + k1 - d][r_rem] * c1) % MOD

                for k1 in range(d):
                    k = K * d + k1 + 1
                    if k < 1 or k > k_max_m: continue
                    if sum_d[k1] == 0: continue
                    H[idx(m + k, k)] = coef_m * powbinom[k] % MOD * sum_d[k1] % MOD

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

    random.seed(42)
    
    print("=== Test 1: Good path (random a, N ≤ 12) vs Bergeron ===")
    for i in range(20):
        a = random.randint(1, MOD - 1)
        b = random.randint(1, MOD - 1)
        N = random.randint(2, 12)
        d = find_order(a)
        if d <= N + 2: continue  # skip bad
        v14 = solve_v14_final(N, a, b)
        berg = compute_Fn_from_bergeron(N, a, b)
        ok = all(v14[j] == berg[j] for j in range(N))
        if not ok:
            print(f"FAIL: N={N}, a={a}, b={b}")
            for j in range(N):
                if v14[j] != berg[j]:
                    print(f"  n={j+1}: v14={v14[j]} berg={berg[j]}")
            break
    else:
        print("ALL OK")
    
    print("\n=== Test 2: Bad path d=2 (a=MOD-1) vs Bergeron ===")
    a = MOD - 1
    for i in range(10):
        b = random.randint(1, MOD - 1)
        N = random.randint(2, 15)
        v14 = solve_v14_final(N, a, b)
        berg = compute_Fn_from_bergeron(N, a, b)
        ok = all(v14[j] == berg[j] for j in range(N))
        if not ok:
            print(f"FAIL d=2: N={N}, b={b}")
            for j in range(N):
                if v14[j] != berg[j]:
                    print(f"  n={j+1}: v14={v14[j]} berg={berg[j]}")
            break
    else:
        print("ALL OK (d=2)")

    print("\n=== Test 3: Bad path d=1904 (a=281849776) vs Bergeron ===")
    a = 281849776 % MOD
    for i in range(10):
        b = random.randint(1, MOD - 1)
        N = random.randint(2, 15)
        v14 = solve_v14_final(N, a, b)
        berg = compute_Fn_from_bergeron(N, a, b)
        ok = all(v14[j] == berg[j] for j in range(N))
        if not ok:
            print(f"FAIL d=1904: N={N}, b={b}")
            for j in range(N):
                if v14[j] != berg[j]:
                    print(f"  n={j+1}: v14={v14[j]} berg={berg[j]}")
            break
    else:
        print("ALL OK (d=1904)")

    print("\n=== Test 4: Bad path vs brute force (n≤8) ===")
    for a in [MOD-1, 1, 281849776 % MOD]:
        for b in [2, 3, 5, 7]:
            v14 = solve_v14_final(8, a, b)
            bf = brute_force_Fn(8, a, b)
            ok = all(v14[j] == bf[j] for j in range(8))
            print(f"  a={a%1000}..., b={b}: {'OK' if ok else 'FAIL'}")

    print("\n=== Test 5: Sample outputs ===")
    for a, b in [(2, 3), (5, 7), (MOD-1, 5)]:
        v14 = solve_v14_final(5, a, b)
        berg = compute_Fn_from_bergeron(5, a, b)
        ok = all(v14[j] == berg[j] for j in range(5))
        print(f"  N=5, a={a%1000}..., b={b}: {'OK' if ok else 'FAIL'}")

    print("\n=== Test 6: N=30 Bad path d=1904 vs Bergeron ===")
    a = 281849776 % MOD
    b = 998244352 % MOD
    v14 = solve_v14_final(30, a, b)
    berg = compute_Fn_from_bergeron(30, a, b)
    ok = all(v14[j] == berg[j] for j in range(30))
    print(f"  {'OK' if ok else 'FAIL'}")