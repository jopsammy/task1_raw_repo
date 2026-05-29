"""
Compare v14 NTT approach vs direct O(N^3) Bergeron, step by step.
Check intermediate H values, not just final F[n] output.
"""
MOD = 998244353
PRIMITIVE_ROOT = 3
import random, sys
sys.path.insert(0, '.')
from verify_bergeron import compute_Cn_bergeron, precompute_qbinom
from ntt_v14_ref import solve_v14_py, modpow, ntt

def compute_H_bergeron(N, a_val, b_val):
    """Return full H matrix using O(N^3) Bergeron method"""
    qb = precompute_qbinom(N + 2, a_val)
    powbinom = [1] * (N + 3)
    for k in range(1, N + 3):
        powbinom[k] = pow(a_val, k * (k - 1) // 2, MOD)
    powb = [1] * (N + 3)
    for d in range(1, N + 3):
        powb[d] = powb[d - 1] * b_val % MOD

    H = [[0] * (N + 4) for _ in range(N + 4)]
    for n in range(1, N + 3):
        H[n][n] = powbinom[n]
        for k in range(1, n):
            d = n - k
            total = 0
            for r in range(1, d + 1):
                total = (total + qb[r + k - 1][r] * H[d][r]) % MOD
            H[n][k] = powb[d] * powbinom[k] % MOD * total % MOD
    return H

def compute_H_ntt(N, a_val, b_val):
    """Return full H matrix using NTT method (mirrors v14 C++)"""
    a_val %= MOD
    b_val %= MOD
    N1 = N + 1
    N2 = N + 2

    pow_a = [1] * (N2 + 1)
    for i in range(1, N2 + 1):
        pow_a[i] = pow_a[i - 1] * a_val % MOD

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
    H_flat = [0] * flat_size

    for n in range(1, N2 + 1):
        H_flat[idx(n, n)] = powbinom[n]

    pow_b = [1] * (N2 + 1)
    for i in range(1, N2 + 1):
        pow_b[i] = pow_b[i - 1] * b_val % MOD

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
            A[m - r] = H_flat[base_m + r - 1] * inv_fact[r] % MOD

        A_ntt = A[:]
        ntt(A_ntt, False)
        C = [A_ntt[i] * B_ntt[i] % MOD for i in range(ntt_size)]
        ntt(C, True)

        coef_m = pow_b[m]
        k_max = N1 - m
        for k in range(1, k_max + 1):
            conv_idx = m + k - 1
            val = coef_m * powbinom[k] % MOD * inv_fact[k - 1] % MOD * C[conv_idx] % MOD
            H_flat[idx(m + k, k)] = val

    # Convert flat H to 2D for comparison
    H_2d = [[0] * (N + 3) for _ in range(N + 3)]
    for n in range(1, N + 3):
        for k in range(1, n + 1):
            H_2d[n][k] = H_flat[idx(n, k)]
    return H_2d

def test_H_matrix():
    """Compare intermediate H values between NTT and direct methods"""
    print("=== H Matrix Comparison ===\n")
    random.seed(98765)
    for test_id in range(200):
        a = random.randint(1, MOD - 1)
        b = random.randint(1, MOD - 1)
        N = random.randint(3, 12)
        
        try:
            H_ntt = compute_H_ntt(N, a, b)
            H_berg = compute_H_bergeron(N, a, b)
            
            ok = True
            for n in range(1, N + 2):
                for k in range(1, n + 1):
                    if H_ntt[n][k] != H_berg[n][k]:
                        if ok:  # first failure
                            print(f"FAIL test {test_id}: N={N}, a={a%1000}..., b={b%1000}...")
                        print(f"  H[{n}][{k}]: ntt={H_ntt[n][k]} berg={H_berg[n][k]}")
                        ok = False
            if not ok:
                print(f"  First failure at N={N}, a={a}, b={b}")
                return
            else:
                if test_id % 20 == 0:
                    print(f"  test {test_id}: N={N}, a={a%1000}..., b={b%1000}... OK")
        except Exception as e:
            print(f"  test {test_id}: ERROR: {e}")
    
    print("\nAll H matrix tests passed!")

def test_convolution_step():
    """Debug a specific convolution step"""
    print("\n=== Convolution Step Debug ===")
    # Use a specific parameter set
    a, b = 2, 3
    N = 5
    
    H_ntt = compute_H_ntt(N, a, b)
    H_berg = compute_H_bergeron(N, a, b)
    
    print(f"\na={a}, b={b}, N={N}")
    for n in range(1, N + 2):
        for k in range(1, n + 1):
            n_val = H_ntt[n][k]
            b_val = H_berg[n][k]
            status = "OK" if n_val == b_val else "MISMATCH"
            if status != "OK":
                print(f"  H[{n}][{k}]: ntt={n_val} berg={b_val} <<< {status}")

def test_edge_cases():
    """Test specific edge cases"""
    print("\n=== Edge Case Tests ===")
    test_params = [
        (1, 1), (1, MOD-1), (MOD-1, 1), (MOD-1, MOD-1),
        (2, 2), (MOD-2, MOD-2), (3, MOD-3),
        (MOD//2, MOD//2), (MOD//2+1, MOD//2-1),
        (2, 998244352), (998244352, 2),
    ]
    for a, b in test_params:
        N = 8
        H_ntt = compute_H_ntt(N, a, b)
        H_berg = compute_H_bergeron(N, a, b)
        
        ok = True
        for n in range(1, N + 2):
            for k in range(1, n + 1):
                if H_ntt[n][k] != H_berg[n][k]:
                    print(f"FAIL a={a%10000}..., b={b%10000}...: H[{n}][{k}]: ntt={H_ntt[n][k]} berg={H_berg[n][k]}")
                    ok = False
        if ok:
            print(f"  a={a%10000}..., b={b%10000}...: ALL OK")
        else:
            return
    
    print("\nAll edge case tests passed!")

if __name__ == '__main__':
    test_H_matrix()
    test_convolution_step()
    test_edge_cases()
