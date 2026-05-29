"""
Route D: Orbit-compressed DP Solution
=====================================
Strategy: 
1. For each size k, precompute wrapping orbit statistics: {(bw,kw): Σ a^{alice}}
2. Use DP: F[n] = Σ_{m=1..n} a^{2m-1+m(n-m)} * F[n-m] * H[m-1][n-m]
3. H[k][L] = Σ_{orbit} α * b^{bw} * (b^{kw})^L

Performance: O(N * total_orbits) for computing H values + O(N²) for DP
For N=5000, total_orbits across all k might be ~O(N² log N) in practice.
"""
import sys
import time

MOD = 998244353

from verify_bf import generate_dyck, alice_of, x_seq_and_bob

class OrbitDP:
    def __init__(self, max_k, a_val, b_val):
        self.a_val = a_val % MOD
        self.b_val = b_val % MOD
        self.max_k = max_k
        
        max_exp = max_k * max_k + 5
        self.pa = [1] * (max_exp + 1)
        self.pb = [1] * (max_exp + 1)
        for i in range(1, max_exp + 1):
            self.pa[i] = self.pa[i-1] * a_val % MOD
            self.pb[i] = self.pb[i-1] * b_val % MOD
        
        self._build_orbit_stats()
    
    def _build_orbit_stats(self):
        """Precompute wrapping orbit statistics for all sizes."""
        self.orbit_stats = [{} for _ in range(self.max_k + 1)]
        
        for k in range(self.max_k + 1):
            words = generate_dyck(k)
            stats = {}
            for s in words:
                alice_v = alice_of(s)
                ws = '(' + s + ')'
                Xw, bobw = x_seq_and_bob(ws)
                kw = len(Xw)
                key = (bobw, kw)
                val = self.pa[alice_v]
                stats[key] = (stats.get(key, 0) + val) % MOD
            self.orbit_stats[k] = stats
        
        self._precompute_orbit_lists()
    
    def _precompute_orbit_lists(self):
        """Convert orbit dicts to lists for faster iteration."""
        self.orbit_lists = []
        for k in range(self.max_k + 1):
            items = [(bw, kw, coeff) for (bw, kw), coeff in self.orbit_stats[k].items()]
            self.orbit_lists.append(items)
    
    def _compute_H(self, k, L):
        """H[k][L] = Σ α * b^{bw + kw*L}"""
        total = 0
        for bw, kw, coeff in self.orbit_lists[k]:
            exp = bw + kw * L
            term = coeff * self.pb[exp] % MOD
            total = (total + term) % MOD
        return total
    
    def solve(self, N):
        """Compute F[1..N] using orbit-compressed DP."""
        if N > self.max_k + 1:
            raise ValueError(f"N={N} > max_k+1={self.max_k+1}")
        
        F = [0] * (N + 1)
        F[0] = 1
        
        for n in range(1, N + 1):
            total = 0
            for m in range(1, n + 1):
                k = m - 1
                idx = n - m
                
                H_val = self._compute_H(k, idx)
                
                exp_a = 2*m - 1 + m * idx
                term = self.pa[exp_a] * H_val % MOD * F[idx] % MOD
                total = (total + term) % MOD
            F[n] = total
        
        return [str(F[i]) for i in range(1, N + 1)]
    
    def solve_fast(self, N):
        """
        Faster version: precompute H[k][L] for all (k,L) pairs.
        O(total_orbits * N) space/time for H.
        """
        if N > self.max_k + 1:
            raise ValueError(f"N={N} > max_k+1={self.max_k+1}")
        
        H_table = [[0] * (N - k) for k in range(N)]
        
        for k in range(N):
            max_L = N - k - 1
            if max_L < 0:
                continue
            for bw, kw, coeff in self.orbit_lists[k]:
                base = coeff * self.pb[bw] % MOD
                step = self.pb[kw]
                cur = base
                for L in range(max_L + 1):
                    H_table[k][L] = (H_table[k][L] + cur) % MOD
                    cur = cur * step % MOD
        
        F = [0] * (N + 1)
        F[0] = 1
        
        for n in range(1, N + 1):
            total = 0
            for m in range(1, n + 1):
                k = m - 1
                idx = n - m
                exp_a = 2*m - 1 + m * idx
                term = self.pa[exp_a] * H_table[k][idx] % MOD * F[idx] % MOD
                total = (total + term) % MOD
            F[n] = total
        
        return [str(F[i]) for i in range(1, N + 1)]
    
    def get_orbit_counts(self):
        """Return the number of orbits at each size."""
        return [len(items) for items in self.orbit_lists]

def benchmark():
    import solution
    
    for max_k in [8, 10, 12, 14]:
        print(f"\n--- Building orbits up to k={max_k} ---")
        t0 = time.time()
        dp = OrbitDP(max_k, 2, 3)
        t1 = time.time()
        
        orbit_counts = dp.get_orbit_counts()
        total_orbits = sum(orbit_counts)
        print(f"  Total orbits: {total_orbits}, Build time: {t1-t0:.2f}s")
        print(f"  Orbit counts per k: {orbit_counts}")
        
        N = min(max_k + 1, 8)
        print(f"  Solving N={N}...")
        t2 = time.time()
        result = dp.solve(N)
        t3 = time.time()
        print(f"  DP time: {t3-t2:.4f}s")
        
        ref = solution.solve(N, 2, 3)
        match = all(r == ref[i] for i, r in enumerate(result))
        print(f"  Match ref: {match}")
        
        t4 = time.time()
        result2 = dp.solve_fast(N)
        t5 = time.time()
        print(f"  Fast DP time: {t5-t4:.4f}s")
        match2 = all(r == ref[i] for i, r in enumerate(result2))
        print(f"  Fast match: {match2}")

if __name__ == '__main__':
    print("=== Orbit DP Benchmark ===\n")
    benchmark()
    
    print("\n\n=== Large N estimate ===")
    for max_k in [16, 18, 20]:
        dp = OrbitDP(max_k, 2, 3)
        orbit_counts = dp.get_orbit_counts()
        total = sum(orbit_counts)
        growth_ratio = orbit_counts[-1] / orbit_counts[-2] if len(orbit_counts) >= 2 else 0
        print(f"  max_k={max_k}: total_orbits={total}, largest k orbits={orbit_counts[-1]}, "
              f"growth ratio={growth_ratio:.3f}")
