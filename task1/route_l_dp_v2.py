"""
Route L: L(i) sequence generative DP - CORRECT implementation.

Key insight:
  Jump chain: l_0=0, l_{j+1}=L(l_j+1), l_k=n
  Segment from jump x to next jump x' (where x'=L(x+1)):
    Positions x+1 .. x' (length d = x'-x)
    - Position x+1: L(x+1)=x' (trigger, determines next jump)
    - Positions x+2 .. x'-1: L in [x', L(x')] (middle, monotonic non-decreasing)
    - Position x': L(x')=y' (new jump point's L value)
    
  Total alice contribution:
    a^{(d-1)*x' + y'} * H[d-2][y'-x']
    Where H[m][u] = sum over 0<=w1<=...<=wm<=u of a^{sum wi}
    
  For d=1 (x'=x+1): only one position, y'=x' forced, alice=a^{x'}
  
  bob contribution: b^{n-x} (for x>0); 1 (for x=0)

DP: dp[x][y] = weighted sum reaching jump point x with L(x)=y.
"""
import sys
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

MOD = 998244353


def compute_L_seq(s):
    n = len(s) // 2
    L = [0] * n
    rc = 0
    for i, ch in enumerate(s):
        if ch == ')':
            L[rc] = (i + 1) - (rc + 1)
            rc += 1
    return L


def alice_from_L(L):
    return sum(L)


def jump_chain(L):
    n = len(L)
    jumps = [0]
    pos = 0
    while pos < n:
        pos = L[pos]
        jumps.append(pos)
    return jumps


def bob_from_L(L):
    n = len(L)
    jumps = jump_chain(L)
    return sum(n - jumps[j] for j in range(1, len(jumps) - 1))


def precompute_H_and_pow(N, a):
    """H[d][u] for d>=0, u>=0."""
    pow_a = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_a[i] = (pow_a[i - 1] * a) % MOD

    H = [[1] * (N + 1) for _ in range(N + 1)]
    for u in range(N + 1):
        H[0][u] = 1

    for d in range(1, N + 1):
        for u in range(N + 1):
            if u == 0:
                H[d][0] = 1
            else:
                H[d][u] = (H[d][u - 1] + pow_a[u] * H[d - 1][u]) % MOD

    return H, pow_a


def solve_route_l_bruteforce(N, a_val, b_val):
    """
    O(N^4) brute-force DP for verification.
    dp[x][y] for 0 <= x <= N, x <= y <= N.
    """
    H, pow_a = precompute_H_and_pow(N, a_val)
    pow_b = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_b[i] = (pow_b[i - 1] * b_val) % MOD

    dp = [[0] * (N + 1) for _ in range(N + 1)]
    dp[0][0] = 1

    for x in range(N):
        for y in range(x, N + 1):
            cur = dp[x][y]
            if cur == 0:
                continue

            bob_factor = 1 if x == 0 else pow_b[N - x]

            x_min = max(y, x + 1)
            for xp in range(x_min, N + 1):
                d = xp - x

                if d == 1:
                    yp = xp
                    alice_factor = pow_a[xp]
                    contribution = cur * alice_factor % MOD * bob_factor % MOD
                    dp[xp][yp] = (dp[xp][yp] + contribution) % MOD
                else:
                    base_alice = pow(pow_a[xp], d - 1, MOD)
                    for yp in range(xp, N + 1):
                        alice_factor = base_alice * pow_a[yp] % MOD * H[d - 2][yp - xp] % MOD
                        contribution = cur * alice_factor % MOD * bob_factor % MOD
                        dp[xp][yp] = (dp[xp][yp] + contribution) % MOD

    return dp[N][N]


def solve_route_l_fast(N, a_val, b_val):
    """
    Optimized O(N^3) or O(N^2) DP.
    """
    H, pow_a = precompute_H_and_pow(N, a_val)
    pow_b = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_b[i] = (pow_b[i - 1] * b_val) % MOD

    dp = [[0] * (N + 1) for _ in range(N + 1)]
    dp[0][0] = 1

    ans = [0] * (N + 1)

    for x in range(N):
        for y in range(x, N + 1):
            cur = dp[x][y]
            if cur == 0:
                continue

            bob_factor = 1 if x == 0 else pow_b[N - x]
            contrib_base = cur * bob_factor % MOD

            x_min = max(y, x + 1)
            for xp in range(x_min, N + 1):
                d = xp - x

                if d == 1:
                    yp = xp
                    alice_factor = pow_a[xp]
                    dp[xp][yp] = (dp[xp][yp] + contrib_base * alice_factor) % MOD
                    if xp == N:
                        ans[N] = (ans[N] + contrib_base * alice_factor) % MOD
                else:
                    base_alice = pow(pow_a[xp], d - 1, MOD)
                    for yp in range(xp, N + 1):
                        alice_factor = base_alice * pow_a[yp] % MOD * H[d - 2][yp - xp] % MOD
                        val = contrib_base * alice_factor % MOD
                        dp[xp][yp] = (dp[xp][yp] + val) % MOD
                        if xp == N:
                            ans[N] = (ans[N] + val) % MOD

    return ans[N]


def solve_single_n(n, a_val, b_val, H, pow_a, pow_b):
    """Compute F[n] for specific n using Route L DP."""
    dp = [[0] * (n + 1) for _ in range(n + 1)]
    dp[0][0] = 1

    for x in range(n):
        for y in range(x, n + 1):
            cur = dp[x][y]
            if cur == 0:
                continue

            bob_factor = 1 if x == 0 else pow_b[n - x]
            contrib_base = cur * bob_factor % MOD

            x_min = max(y, x + 1)
            for xp in range(x_min, n + 1):
                d = xp - x

                if d == 1:
                    yp = xp
                    alice_factor = pow_a[xp]
                    dp[xp][yp] = (dp[xp][yp] + contrib_base * alice_factor) % MOD
                else:
                    base_alice = pow(pow_a[xp], d - 1, MOD)
                    for yp in range(xp, n + 1):
                        alice_factor = base_alice * pow_a[yp] % MOD * H[d - 2][yp - xp] % MOD
                        dp[xp][yp] = (dp[xp][yp] + contrib_base * alice_factor) % MOD

    return dp[n][n]


def solve_route_l_all(N, a_val, b_val):
    """Compute F[1..N] using Route L DP (computes each n independently)."""
    H, pow_a = precompute_H_and_pow(N, a_val)
    pow_b = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_b[i] = (pow_b[i - 1] * b_val) % MOD

    results = []
    for n in range(1, N + 1):
        results.append(solve_single_n(n, a_val, b_val, H, pow_a, pow_b))

    return results


def verify_against_brute_force(max_n=8):
    """Verify Route L DP against brute-force L-sequence enumeration."""
    from verify_bf import solve_brute

    print("=== Verifying Route L DP against brute force ===\n")

    for a_val, b_val in [(2, 3), (5, 7), (1, 1), (3, 2)]:
        print(f"\n--- a={a_val}, b={b_val} ---")
        bf_results = solve_brute(max_n, a_val, b_val)
        dp_results = solve_route_l_all(max_n, a_val, b_val)

        for n in range(1, max_n + 1):
            bf = bf_results[n - 1]
            dp = dp_results[n - 1]
            status = "OK" if bf == dp else f"FAIL (bf={bf}, dp={dp})"
            if bf != dp:
                print(f"  n={n}: {status}")
                return False

        print(f"  All n=1..{max_n}: OK")

    return True


def verify_step_by_step(n=3, a_val=2, b_val=3):
    """Trace through DP step by step for verification."""
    from verify_bf import solve_brute

    bf = solve_brute(n, a_val, b_val)[n - 1]
    dp_result = solve_route_l_all(n, a_val, b_val)[n - 1]

    print(f"n={n}, a={a_val}, b={b_val}")
    print(f"  Brute force: {bf}")
    print(f"  Route L DP:  {dp_result}")
    print(f"  Match: {bf == dp_result}")

    words = generate_dyck(n)
    print(f"\n  Per-word breakdown:")
    total = 0
    for s in words:
        L = compute_L_seq(s)
        alice = alice_from_L(L)
        bob = bob_from_L(L)
        jumps = jump_chain(L)
        contrib = pow(a_val, alice, MOD) * pow(b_val, bob, MOD) % MOD
        total = (total + contrib) % MOD
        print(f"    {s:12s} L={str(L):15s} alice={alice} bob={bob} jumps={jumps} contrib={contrib}")
    print(f"    Total: {total}")


if __name__ == '__main__':
    if len(sys.argv) >= 1:
        verify_against_brute_force(8)
    else:
        verify_step_by_step(3, 2, 3)
        verify_step_by_step(4, 2, 3)
        verify_step_by_step(5, 2, 3)
