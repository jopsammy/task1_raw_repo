"""
Verify q-Lucas theorem for the (q,t)-Catalan recurrence.
When a has order d (a^d = 1):
    qbin(n, k)_a = C(n/d, k/d) * qbin(n%d, k%d)_a

Test numerically against Pascal-recurrence-computed qbin.
"""
MOD = 998244353

def modpow(a, e):
    r = 1
    while e:
        if e & 1: r = r * a % MOD
        a = a * a % MOD
        e >>= 1
    return r

def find_order(a):
    v = a % MOD
    for d in range(1, MOD):
        if v == 1: return d
        v = v * a % MOD
    return MOD - 1

def qbin_table(n_max, a):
    """Compute qbin[n][k] for n,k <= n_max using Pascal recurrence"""
    qb = [[0] * (n_max + 1) for _ in range(n_max + 1)]
    for i in range(n_max + 1):
        qb[i][0] = qb[i][i] = 1
    for n in range(2, n_max + 1):
        ak = a % MOD
        for k in range(1, n):
            qb[n][k] = (qb[n-1][k-1] + ak * qb[n-1][k]) % MOD
            ak = ak * a % MOD
    return qb

def test_q_lucas(a, max_n=20):
    """Test q-Lucas theorem for given a"""
    d = find_order(a)
    print(f"a={a%1000}..., order d={d}")
    
    if d > max_n * 3:
        print(f"  d too large to test, skip")
        return True
    
    qb = qbin_table(max_n + d, a)
    qb_small = qbin_table(d, a)
    
    import math
    def C(n, k):
        if k < 0 or k > n: return 0
        return math.comb(n, k) % MOD
    
    errors = []
    for n in range(max_n + d + 1):
        for k in range(n + 1):
            nd, nr = n // d, n % d
            kd, kr = k // d, k % d
            if nd == 0 and kd == 0:
                continue  # trivial
            ql_val = C(nd, kd) * qb_small[nr][kr] % MOD
            if qb[n][k] != ql_val:
                errors.append((n, k, qb[n][k], ql_val))
                if len(errors) <= 5:
                    print(f"  FAIL n={n},k={k}: Pascal={qb[n][k]}, q-Lucas={ql_val}")
    
    if errors:
        print(f"  TOTAL FAILURES: {len(errors)}/{sum(1 for n in range(max_n+d+1) for k in range(n+1))}")
        return False
    else:
        print(f"  ALL OK for n,k up to {max_n+d}")
        return True

def test_residue_ntt(a, d, N=100):
    """Test the residue-class NTT approach against direct computation"""
    print(f"\n=== Residue NTT test: a order {d}, N={N} ===")
    
    qb_small = qbin_table(d, a)
    ord_fact = [1] * (N + 3)
    for i in range(1, N + 3):
        ord_fact[i] = ord_fact[i - 1] * i % MOD
    inv_ord_fact = [0] * (N + 3)
    inv_ord_fact[N+2] = modpow(ord_fact[N+2], MOD - 2)
    for i in range(N+2, 0, -1):
        inv_ord_fact[i-1] = inv_ord_fact[i] * i % MOD
    
    # Simulate H (random)
    import random
    random.seed(42)
    b_val = random.randint(1, MOD - 1)
    
    def idx(n, k):
        return n * (n + 1) // 2 + k
    
    H = [0] * idx(N + 3, N + 3)
    powbin = [1]
    for k in range(1, N + 5):
        powbin.append(powbin[-1] * modpow(a, k - 1) % MOD)
    for n in range(1, N + 3):
        H[idx(n, n)] = powbin[n]
    
    pow_b = [1]
    for i in range(1, N + 3):
        pow_b.append(pow_b[-1] * b_val % MOD)
    
    # Direct computation (reference)
    H_ref = H[:]
    qb_full = qbin_table(N + 3, a)
    for m in range(1, N + 1):
        for k in range(1, N - m + 1):
            total = 0
            for r in range(1, m + 1):
                total = (total + qb_full[r + k - 1][r] * H_ref[idx(m, r)]) % MOD
            H_ref[idx(m + k, k)] = pow_b[m] * powbin[k] % MOD * total % MOD
    
    # q-Lucas + residue NTT approach
    H_new = H[:]
    
    # Precompute B for NTT (B[j] = j!)
    ntt_size = 1
    while ntt_size <= N + 3: ntt_size <<= 1
    B = [0] * ntt_size
    for j in range(N + 3):
        B[j] = ord_fact[j]
    
    # NTT function (from ntt_v14_ref)
    def ntt(a_vec, invert):
        n = len(a_vec)
        j = 0
        for i in range(1, n):
            bit = n >> 1
            while j & bit: j ^= bit; bit >>= 1
            j ^= bit
            if i < j: a_vec[i], a_vec[j] = a_vec[j], a_vec[i]
        len_ = 2
        while len_ <= n:
            wlen = modpow(3, (MOD - 1) // len_)
            if invert: wlen = modpow(wlen, MOD - 2)
            for i in range(0, n, len_):
                w = 1
                for jj in range(len_ // 2):
                    u = a_vec[i + jj]
                    v = a_vec[i + jj + len_ // 2] * w % MOD
                    a_vec[i + jj] = (u + v) % MOD
                    a_vec[i + jj + len_ // 2] = (u - v + MOD) % MOD
                    w = w * wlen % MOD
            len_ <<= 1
        if invert:
            inv_n = modpow(n, MOD - 2)
            for i in range(n): a_vec[i] = a_vec[i] * inv_n % MOD
    
    B_ntt = B[:]
    ntt(B_ntt, False)
    
    # Precompute M0 and M1 transition matrices
    K_max = N // d
    M0 = [[0] * d for _ in range(d)]  # M0[k1][r_rem] for carry=0
    M1 = [[0] * d for _ in range(d)]  # M1[k1][r_rem] for carry=1
    
    for k1 in range(d):
        for r_rem in range(d):
            if r_rem + k1 < d:
                M0[k1][r_rem] = qb_small[r_rem + k1][r_rem]
            else:
                M1[k1][r_rem] = qb_small[r_rem + k1 - d][r_rem]
    
    for m in range(1, N + 1):
        # Compute contrib[K][r_rem]
        contrib = [[0] * d for _ in range(K_max + 2)]
        
        for r_rem in range(d):
            r_div_start = 1 if r_rem == 0 else 0
            M_div = (m - r_rem) // d
            if M_div < r_div_start:
                continue
            count = M_div - r_div_start + 1
            
            V = [0] * count
            for i in range(count):
                rr = (r_div_start + i) * d + r_rem
                if 1 <= rr <= m:
                    V[i] = H_new[idx(m, rr)]
            
            a_flip = [0] * ntt_size
            for i in range(count):
                a_flip[count - 1 - i] = V[i] * inv_ord_fact[r_div_start + i] % MOD
            
            ntt(a_flip, False)
            conv = [a_flip[i] * B_ntt[i] % MOD for i in range(ntt_size)]
            ntt(conv, True)
            
            for X in range(K_max + 2):
                pos = r_div_start + count - 1 + X
                if pos < len(conv):
                    contrib[X][r_rem] = inv_ord_fact[X] * conv[pos] % MOD
        
        # Apply transition matrices
        k_max_m = N - m
        for K in range(K_max + 1):
            k1_start = 0 if K > 0 else 0  # K=0 means k in [1, min(d-1, k_max_m)]
            for k1 in range(d):
                k = K * d + k1 + 1
                if k < 1 or k > k_max_m: continue
                
                sum_val = 0
                for r_rem in range(d):
                    sum_val = (sum_val + M0[k1][r_rem] * contrib[K][r_rem]) % MOD
                    sum_val = (sum_val + M1[k1][r_rem] * contrib[K + 1][r_rem]) % MOD
                
                H_new[idx(m + k, k)] = pow_b[m] * powbin[k] % MOD * sum_val % MOD
    
    # Compare
    errors = 0
    for n in range(1, N + 3):
        for k in range(1, n + 1):
            if H_ref[idx(n, k)] != H_new[idx(n, k)]:
                if errors < 5:
                    print(f"  H[{n}][{k}]: ref={H_ref[idx(n,k)]} new={H_new[idx(n,k)]}")
                errors += 1
    
    if errors == 0:
        print(f"  ALL OK (H matrix verified for N={N})")
    else:
        print(f"  {errors} ERRORS in H matrix")
    
    return errors == 0

# Test
print("=== q-Lucas Theorem Verification ===\n")
test_q_lucas(998244352, 15)  # a=MOD-1, order 2
test_q_lucas(281849776 % MOD, 15)  # the problem case (order 1904, but verify small n)
# Test with small order values
test_q_lucas(pow(3, (MOD-1)//4096, MOD), 10)  # order 4096

print("\n=== Residue NTT Verification ===\n")
test_residue_ntt(998244352, 2, 20)  # order 2