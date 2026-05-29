"""
Compute H[k][L] = Σ_{A:|A|=k} a^{alice(A)} × b^{bob((A)) + k((A))×L}

using a DP on L-sequences.

Key insight: H[k][L] treats L as a parameter that can be factored into
the final exponent of b. We compute h[k][t] where t = b^L, then
H[k][L] = h[k][b^L].

Strategy: compute h[k] directly for all k up to MAX_K using DP.

For a fixed k, the DP builds L(1..k) incrementally, tracking:
- Position i
- Current L value v = L(i)
- Last wrapped jump point l'_prev and its associated bob contribution
- Current kw count

But this is too many states. Let me simplify by separating the
"wrapped" bob/kw computation from the alice computation.

L-sequence→wrapped mapping:
  L'(i) = L(i) + 1 for i=1..k, L'(k+1)=k+1
  l'_0=0, l'_{j+1}=L'(l'_j+1)

We can precompute for each (k, prev_jump, next_jump) the per-segment
contribution, then do DP over jump chains.

For a segment from jump p to jump p' (in wrapped):
  - Trigger at position p+1: L(p+1)=p'-1
  - Positions p+2..p': L values in [p'-1, next_L_val] (upper bound from next trigger)
  - alice contribution depends on L values in [p+1, p']
  - bob contribution: (k+1-p) for this jump

Upper bound for L values in [p+1, p']:
  L(p'+1) = next_jump_L_val - 1 (next trigger value)
  Since L is non-decreasing, L(p') ≤ L(p'+1) = next_L_val - 1.

So within [p+1, p']: L values from p'-1 to next_L_val-1.

Length of middle segment (positions p+2..p'): d = p' - p - 1
Lower bound: p'-1
Upper bound: next_L_val - 1

alice contribution = (p'-1) [position p+1] + Σ_{pos=p+2}^{p'} L(pos)
                  = (p'-1) + d*(p'-1) + Σ_{i=1}^{d} w_i  [shift by p'-1]
                  = d'*(p'-1) + Σ w_i  where d' = d+1 = p'-p

Wait, the trigger position p+1 has L(p+1)=p'-1 which is fixed.
The d middle positions have L values in [p'-1, next_L-1].

Total L contribution = (p'-1) × (d+1) + Σ w_i for middle positions only.

Actually let me just include the trigger in the middle:
All positions p+1..p': L values in [p'-1, next_L_val-1], with L(p+1)=p'-1 fixed (minimum).
Length = d+1 = p'-p.

Hmm, this constraint (L(p+1) = p'-1 specifically) makes it harder. Let me just do it differently.

Instead of trying to derive closed forms, let me implement a simpler DP:

dp_pos_based[i][v] where:
  i = current position (1..k)
  v = L(i)

At each position i, we either:
  A) Trigger a jump (v determines next wrapped jump point)
  B) Just accumulate alice

But determining whether v triggers a jump requires comparing with the
wrapped jump chain, which depends on future positions.

This is the fundamental issue: the wrapped jump chain depends on the
COMPLETE L sequence, not just the prefix. You can't decide locally.

OK let me try the OPPOSITE approach: enumerate all possible WRAPPED JUMP CHAINS
and for each, sum over compatible L sequences.

For fixed k, a wrapped jump chain is: 0 = l'_0 < l'_1 < ... < l'_{kw} = k+1.

Number of such chains = 2^k (each of k positions can be a jump or not).
For k=5000, 2^5000 is impossibly large.

BUT: each jump chain corresponds to ONE specific (bw, kw) pair! And we saw
that the number of distinct (bw, kw) pairs is much smaller.

So can I count how many jump chains give a specific (bw, kw)?

For given (bw, kw):
  kw = m+1 (m non-final jumps)
  bw = Σ_{j=1}^{m} (k+1 - l'_j)

We need l'_1 < l'_2 < ... < l'_m < k+1 (strictly increasing) such that
Σ_{j=1}^{m} (k+1 - l'_j) = bw.

This is: Σ l'_j = m(k+1) - bw.

So for given (bw, kw), we need m = kw-1 integers 0 < l'_1 < ... < l'_m < k+1
such that Σ l'_j = m(k+1) - bw.

The number of such sequences equals the number of STRICT compositions of
(m(k+1) - bw) into m parts with each part in [1, k] and strictly increasing.

This is equivalent to the number of partitions of (m(k+1)-bw - m(m+1)/2) into
at most m parts each at most (k-m). By partition theory, this is a restricted
partition count.

This still doesn't give us a simple formula. But it tells us that for EACH
(bw, kw) pair, we need to count partitions. The total work might be
O(orbits × k) which gets us back to the same complexity issue.

OK, I think the best approach is to accept that H[k][L] can't be computed in
O(N²) through known combinatorial identities, and instead try the Route L DP
approach with optimization.

Let me try a completely different tactic: compute F[n] directly using
the Route L DP but optimized via "convolution" over the distance d.

From Route L DP:
dp[x'][y'] = Σ_d b^{n-x'+d} × a^{(d-1)x'+y'} × Σ_y dp[x'-d][y] × H[d-2][y'-x']

For fixed n (the target size), this is O(N³) time.

But we need F[n] for ALL n=1..N. Computing each independently would be O(N⁴).

Idea: instead of computing each F[n] independently, compute ALL F[n]
simultaneously by treating n as a parameter.

Define:
dp_gen[x][y][exp_n] where exp_n tracks the exponent of b that depends on n.

But this adds another dimension and is worse.

Hmm, let me try one final thing: compute H[k][L] for a RANGE of k values
(not all 5000) using the orbit enumeration approach, and see if there's
a pattern that can be extended.

Actually, let me go back to the Route D approach with a hybrid strategy:
- For k ≤ 14: use full orbit enumeration (Catalan(k) manageable)
- For k > 14: approximate or use a different method

But for k > 14 (from 15 to 4999), that's 4985 values of k. Can I interpolate?

No, H[k][L] doesn't seem to have a simple closed form.

OK let me try the simplest possible approach and see if it's fast enough:
compute H[k][L] using a modified Route L DP that's O(k³) per k.
For k up to 5000, that's (5000⁴)/24 ≈ 2.6×10¹³ — definitely too slow.

For k up to 500: (500⁴)/24 ≈ 2.6×10⁹ — maybe borderline in PyPy?

Let me just implement it and benchmark.
"""
import time
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

MOD = 998244353


def precompute_Hdp(N, a_val):
    pow_a = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_a[i] = (pow_a[i - 1] * a_val) % MOD

    H = [[1] * (N + 1) for _ in range(N + 1)]
    for d in range(1, N + 1):
        for u in range(N + 1):
            if u == 0:
                H[d][0] = 1
            else:
                H[d][u] = (H[d][u - 1] + pow_a[u] * H[d - 1][u]) % MOD
    return H, pow_a


def compute_HkL_l_seq(k, a_val, b_val, H, pow_a):
    """
    Compute H[k][L] for L=0..MAX_L using L-sequence DP.
    Returns list of length MAX_L+1.
    
    This is an O(k⁴) DP - SLOW but correct.
    """
    N = k + 1

    pow_b = [1] * (N * N + 5)
    for i in range(1, len(pow_b)):
        pow_b[i] = (pow_b[i - 1] * b_val) % MOD

    dp = [[0] * (N + 1) for _ in range(N + 1)]
    dp[0][0] = 1

    for x in range(k):
        for y in range(x, k + 1):
            cur = dp[x][y]
            if cur == 0:
                continue

            x_min = max(y, x + 1)
            for xp in range(x_min, k + 1):
                d = xp - x

                bob_factor = pow_b[N - x]
                contrib_base = cur * bob_factor % MOD

                if d == 1:
                    dp[xp][xp] = (dp[xp][xp] + contrib_base * pow_a[xp]) % MOD
                else:
                    base_alice = pow(pow_a[xp], d - 1, MOD)
                    for yp in range(xp, k + 1):
                        alice_factor = base_alice * pow_a[yp] % MOD * H[d - 2][yp - xp] % MOD
                        dp[xp][yp] = (dp[xp][yp] + contrib_base * alice_factor) % MOD

    result = {}
    total = 0
    for bw in range(k * k + 1):
        for kw in range(1, k // 2 + 3):
            pass

    return dp[k][k]


def benchmark_lseq_dp(max_k=30):
    """Benchmark how fast L-sequence DP is for each k."""
    a_val, b_val = 2, 3
    
    H, pow_a = precompute_Hdp(max_k, a_val)
    
    times = []
    for k in range(1, min(max_k + 1, 15)):
        t0 = time.time()
        result = compute_HkL_l_seq(k, a_val, b_val, H, pow_a)
        t1 = time.time()
        times.append(t1 - t0)
        print(f"k={k:2d}: result={result} time={t1-t0:.4f}s")
    
    if len(times) >= 2:
        ratio = times[-1] / times[-2]
        print(f"\nGrowth ratio (last two): {ratio:.2f}")
        est_30 = times[-1] * (ratio ** (30 - max_k + 1))
        print(f"Estimated time for k=30: {est_30:.1f}s")
        est_500 = times[-1] * (ratio ** (500 - max_k + 1))
        print(f"Estimated time for k=500: {est_500:.1e}s")


if __name__ == '__main__':
    benchmark_lseq_dp(30)
