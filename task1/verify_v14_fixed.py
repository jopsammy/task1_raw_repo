"""
Verify the fixed v14 implementation.
Tests both NTT path (non-problematic a) and fallback path (problematic a).
"""
import sys, random
sys.path.insert(0, '.')
from verify_bergeron import brute_force_Fn, compute_Fn_from_bergeron, compute_Cn_bergeron
from ntt_v14_ref import modpow, ntt

MOD = 998244353

def solve_v14_py_fixed(N, a_val, b_val):
    """Mirror of the fixed solution_v14.cpp in Python"""
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

    def idx(n, k):
        return n * (n + 1) // 2 + k

    flat_size = idx(N2, N2) + 1
    H = [0] * flat_size

    for n in range(1, N2 + 1):
        H[idx(n, n)] = powbinom[n]

    ntt_ok = (a_val != 1)
    fact = [1] * (N2 + 1)
    if a_val == 1:
        for i in range(1, N2 + 1):
            fact[i] = fact[i - 1] * i % MOD
    else:
        for i in range(1, N2 + 1):
            term = (pow_a[i] - 1 + MOD) % MOD
            if term == 0:
                ntt_ok = False
            fact[i] = fact[i - 1] * term % MOD
            if not ntt_ok:
                break

    if ntt_ok:
        # NTT path
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
    else:
        # Fallback: q-binomial recurrence + direct sum
        max_qb_n = N2
        max_qb_k = N2
        dk_start = [0] * (max_qb_k + 2)
        dk_start[1] = 0
        for k in range(2, max_qb_k + 2):
            dk_start[k] = dk_start[k - 1] + (max_qb_n - (k - 1))

        qb_diag = [0] * dk_start[max_qb_k + 1]
        qb_prev = [0] * (max_qb_k + 1)
        qb_curr = [0] * (max_qb_k + 1)
        qb_prev[0] = 1

        for n in range(1, max_qb_n + 1):
            qb_curr[0] = 1
            if n <= max_qb_k:
                qb_curr[n] = 1
            for k in range(1, min(n, max_qb_k + 1)):
                qb_curr[k] = (qb_prev[k - 1] + pow_a[k] * qb_prev[k]) % MOD
            if n < max_qb_n:
                for r in range(1, n + 1):
                    c = n - r
                    if c + 1 > max_qb_k:
                        continue
                    qb_diag[dk_start[c + 1] + (r - 1)] = qb_curr[r] * powbinom[c + 1] % MOD
            qb_prev, qb_curr = qb_curr, [0] * (max_qb_k + 1)

        for d in range(1, N + 1):
            h_base = d * (d + 1) // 2
            coef_d = pow_b[d]
            k_max = N1 - d
            idx_cur = (d + 1) * (d + 2) // 2 + 1
            idx_inc = d + 3

            for k in range(1, k_max + 1):
                p_start = dk_start[k]
                p_slice = qb_diag[p_start:p_start + d]
                h_slice = H[h_base + 1:h_base + 1 + d]
                total = sum(p_slice[i] * h_slice[i] for i in range(d)) % MOD
                H[idx_cur] = coef_d * total % MOD
                idx_cur += idx_inc
                idx_inc += 1

    a_baseline = [1] * (N + 1)
    for n in range(1, N + 1):
        a_baseline[n] = a_baseline[n - 1] * pow_a[n] % MOD

    result = []
    for n in range(1, N + 1):
        fn = a_baseline[n] * inv_pow_b[n] % MOD * H[idx(n + 1, 1)] % MOD
        result.append(fn)
    return result


def test_all():
    print("=== Testing NTT path (random non-problematic a) ===")
    random.seed(42)
    for test_id in range(50):
        a = random.randint(1, MOD - 1)
        b = random.randint(1, MOD - 1)
        N = random.randint(2, 12)
        v14 = solve_v14_py_fixed(N, a, b)
        berg = compute_Fn_from_bergeron(N, a, b)
        ok = all(v14[i] == berg[i] for i in range(N))
        if not ok:
            print(f"FAIL test {test_id}: N={N}, a={a}, b={b}")
            for i in range(N):
                if v14[i] != berg[i]:
                    print(f"  n={i+1}: v14={v14[i]} berg={berg[i]}")
            return
        elif test_id % 10 == 0:
            print(f"  test {test_id}: N={N}, a={a%1000}..., b={b%1000}... OK")
    print("  All 50 NTT path tests passed!\n")

    print("=== Testing fallback path (problematic a) ===")
    problematic_a = [MOD - 1, 1]  # MOD-1 has order 2, 1 is a=1 special case
    for a in problematic_a:
        for test_id in range(20):
            b = random.randint(1, MOD - 1)
            N = random.randint(2, 12)
            v14 = solve_v14_py_fixed(N, a, b)
            berg = compute_Fn_from_bergeron(N, a, b)
            ok = all(v14[i] == berg[i] for i in range(N))
            if not ok:
                print(f"FAIL a={a%10000}..., b={b%10000}..., N={N}")
                for i in range(N):
                    if v14[i] != berg[i]:
                        print(f"  n={i+1}: v14={v14[i]} berg={berg[i]}")
                return
            elif test_id % 10 == 0:
                print(f"  a={a%10000}..., b={b%10000}..., N={N}: OK")
    print("  All fallback path tests passed!\n")

    print("=== Testing vs brute force (both paths) ===")
    for a in [2, 3, MOD-1, 1, 5, 7, 123, 456]:
        for b_val in [2, 3, 1, MOD-1, 7, 11]:
            v14 = solve_v14_py_fixed(8, a, b_val)
            bf = brute_force_Fn(8, a, b_val)
            ok = all(v14[i] == bf[i] for i in range(8))
            status = "OK" if ok else "FAIL"
            print(f"  a={a%1000}..., b={b_val%1000}...: {status}")
            if not ok:
                for i in range(8):
                    if v14[i] != bf[i]:
                        print(f"    n={i+1}: v14={v14[i]} bf={bf[i]}")
    print()

    print("=== Testing large N (both paths) ===")
    # NTT path with large N
    v14 = solve_v14_py_fixed(100, 2, 3)
    berg = compute_Fn_from_bergeron(100, 2, 3)
    ok = all(v14[i] == berg[i] for i in range(100))
    print(f"  NTT path N=100 a=2 b=3: {'OK' if ok else 'FAIL'}")
    
    # Fallback with N=30 (small enough for O(N^3) in Python)
    v14 = solve_v14_py_fixed(30, MOD - 1, 5)
    berg = compute_Fn_from_bergeron(30, MOD - 1, 5)
    ok = all(v14[i] == berg[i] for i in range(30))
    print(f"  Fallback N=30 a=MOD-1 b=5: {'OK' if ok else 'FAIL'}")

if __name__ == '__main__':
    test_all()
