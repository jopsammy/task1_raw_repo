"""
Analyze orbit evolution pattern for wrapping of Dyck words.
Goal: find recurrence for orbit statistics without full Catalan enumeration.
"""
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


def compute_orbits(max_k, a_val):
    """Compute detailed orbit information for each k."""
    pow_a = [1] * (max_k * max_k + 10)
    for i in range(1, len(pow_a)):
        pow_a[i] = (pow_a[i-1] * a_val) % MOD

    orbits = []
    for k in range(max_k + 1):
        words = generate_dyck(k)
        orbit_map = {}
        for s in words:
            L = compute_L_seq(s)
            al = sum(L)
            ws = '(' + s + ')'
            Xw, bobw = x_seq_and_bob(ws)
            kw = len(Xw)
            
            c = 0
            for val in L:
                if val == c + 1:
                    c += 1
                else:
                    break
            
            key = (bobw, kw)
            if key not in orbit_map:
                orbit_map[key] = {
                    'alpha': 0,
                    'words': [],
                    'c_dist': {}
                }
            orbit_map[key]['alpha'] = (orbit_map[key]['alpha'] + pow_a[al]) % MOD
            orbit_map[key]['words'].append(s)
            orbit_map[key]['c_dist'][c] = orbit_map[key]['c_dist'].get(c, 0) + 1

        orbits.append(orbit_map)
    return orbits


def print_orbit_analysis(orbits):
    for k, orbit_map in enumerate(orbits):
        print(f"\n=== k={k}: {len(orbit_map)} orbits ===")
        for (bw, kw), info in sorted(orbit_map.items()):
            alpha = info['alpha']
            c_dist = dict(sorted(info['c_dist'].items()))
            words = info['words']
            sample = words[0] if len(words) <= 3 else f"{words[0]} + {len(words)-1} more"
            print(f"  ({bw},{kw}): α={alpha}, c_dist={c_dist}, words={len(words)} [{sample}]")


if __name__ == '__main__':
    orbits = compute_orbits(10, 2)
    print_orbit_analysis(orbits)
