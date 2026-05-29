import sys
from collections import defaultdict
from itertools import combinations

sys.path.insert(0, r'd:\2024备份和迁移\2024备份和迁移\f复旭文件\h彗星计划相关\其他资料\V6_wida_case\task1')
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

MOD = 998244353
MAX_N = 8


def height_function(s):
    n = len(s) // 2
    h = [0] * (2 * n + 1)
    for i in range(2 * n):
        h[i + 1] = h[i] + (1 if s[i] == '(' else -1)
    return h


def height_stats(s):
    h = height_function(s)
    n = len(s) // 2
    h_max = max(h)
    h_sum = sum(h)
    h_mean = h_sum / (2 * n + 1)
    h_var = sum((hi - h_mean) ** 2 for hi in h) / (2 * n + 1)
    returns_to_zero = sum(1 for hi in h[1:-1] if hi == 0)
    peaks = 0
    for i in range(1, 2 * n):
        if h[i] > h[i - 1] and h[i] > h[i + 1]:
            peaks += 1
    valleys = 0
    for i in range(1, 2 * n):
        if h[i] < h[i - 1] and h[i] < h[i + 1]:
            valleys += 1
    return {
        'n': n,
        'h_max': h_max,
        'h_sum': h_sum,
        'h_mean': round(h_mean, 6),
        'h_var': round(h_var, 6),
        'h_std': round(h_var ** 0.5, 6),
        'returns0': returns_to_zero,
        'peaks': peaks,
        'valleys': valleys,
    }


def tree_params(s):
    n = len(s) // 2
    stack = []
    parent = [-1] * (2 * n)
    pos_to_node = {}
    node_count = 0

    for i, ch in enumerate(s):
        if ch == '(':
            pos_to_node[i] = node_count
            if stack:
                parent[node_count] = stack[-1]
            stack.append(node_count)
            node_count += 1
        else:
            stack.pop()

    children = defaultdict(list)
    for v in range(node_count):
        p = parent[v]
        if p != -1:
            children[p].append(v)

    def subtree_size(v):
        sz = 1
        for c in children[v]:
            sz += subtree_size(c)
        return sz

    def depth(v):
        d = 0
        cur = v
        while parent[cur] != -1:
            d += 1
            cur = parent[cur]
        return d

    sizes = [subtree_size(v) for v in range(node_count)]
    depths = [depth(v) for v in range(node_count)]

    leaf_count = sum(1 for v in range(node_count) if len(children[v]) == 0)
    max_depth = max(depths) if depths else 0
    sum_depths = sum(depths)
    max_subtree_size = max(sizes) if sizes else 0
    sum_subtree_sizes = sum(sizes)

    root_children = len(children[0]) if node_count > 0 else 0

    return {
        'n_nodes': node_count,
        'leaf_count': leaf_count,
        'max_depth': max_depth,
        'sum_depths': sum_depths,
        'max_subtree_size': max_subtree_size,
        'sum_subtree_sizes': sum_subtree_sizes,
        'root_children': root_children,
    }


def pair_seq(seq):
    r = []
    i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq):
            r.append(1 + seq[i + 1])
            i += 2
        else:
            r.append(seq[i])
            i += 1
    return r


def primitive_decompose(s):
    n = len(s) // 2
    h = 0
    blocks = []
    cur = []
    for ch in s:
        cur.append(ch)
        h += 1 if ch == '(' else -1
        if h == 0:
            blocks.append(''.join(cur))
            cur = []
    return blocks


def make_sig(t, params):
    return tuple(t[p] for p in params)


def test_wrapping_uniqueness(group, params):
    sig_map = defaultdict(list)
    for entry in group:
        sig = make_sig(entry, params)
        sig_map[sig].append(entry)
    collisions = 0
    for sig, entries in sig_map.items():
        bw_set = set(e['bobw_real'] for e in entries)
        kw_set = set(e['kw_real'] for e in entries)
        if len(bw_set) > 1 or len(kw_set) > 1:
            collisions += 1
    return collisions, len(sig_map)


def run():
    print("=" * 70)
    print("ROUTE G RESTART: Real Wrapping Parameter Dependency Analysis")
    print("Using x_seq_and_bob (height function) as GROUND TRUTH")
    print("=" * 70)

    all_entries = []

    for n in range(1, MAX_N + 1):
        for s in generate_dyck(n):
            X_raw, bob_raw = x_seq_and_bob(s)
            k_raw = len(X_raw)
            x1 = X_raw[0]

            sum_X_raw = sum(X_raw)
            last_X = X_raw[-1]
            last2_X = X_raw[-2] if k_raw >= 2 else 0

            num_ones = sum(1 for v in X_raw if v == 1)
            leading_ones = 0
            for v in X_raw:
                if v == 1:
                    leading_ones += 1
                else:
                    break

            wrapped = '(' + s + ')'
            Xw_real, bobw_real = x_seq_and_bob(wrapped)
            kw_real = len(Xw_real)

            Xw_pairseq = pair_seq([1] + X_raw)
            bobw_pairseq = sum(j * Xw_pairseq[j] for j in range(len(Xw_pairseq)))
            kw_pairseq = len(Xw_pairseq)

            pairseq_match = (Xw_real == Xw_pairseq and bobw_real == bobw_pairseq)

            hs = height_stats(s)
            tp = tree_params(s)

            prim_blocks = primitive_decompose(s)
            prim_sizes = [len(b) // 2 for b in prim_blocks]
            num_prim_blocks = len(prim_blocks)

            alice = alice_of(s)

            entry = {
                's': s,
                'n': n,
                'X': tuple(X_raw),
                'X_str': str(X_raw),
                'bob': bob_raw,
                'k': k_raw,
                'x1': x1,
                'last_X': last_X,
                'last2_X': last2_X,
                'sum_X': sum_X_raw,
                'num_ones': num_ones,
                'leading_ones': leading_ones,

                'Xw_real': tuple(Xw_real),
                'bobw_real': bobw_real,
                'kw_real': kw_real,
                'Xw_pairseq': tuple(Xw_pairseq),
                'bobw_pairseq': bobw_pairseq,
                'kw_pairseq': kw_pairseq,
                'pairseq_match': pairseq_match,

                'num_prim_blocks': num_prim_blocks,
                'prim_sizes': tuple(prim_sizes),
                'alice': alice,

                'h_max': hs['h_max'],
                'h_sum': hs['h_sum'],
                'h_mean': hs['h_mean'],
                'h_var': hs['h_var'],
                'h_std': hs['h_std'],
                'returns0': hs['returns0'],
                'peaks': hs['peaks'],
                'valleys': hs['valleys'],

                'n_nodes': tp['n_nodes'],
                'leaf_count': tp['leaf_count'],
                'max_depth': tp['max_depth'],
                'sum_depths': tp['sum_depths'],
                'max_subtree_size': tp['max_subtree_size'],
                'sum_subtree_sizes': tp['sum_subtree_sizes'],
                'root_children': tp['root_children'],
            }
            all_entries.append(entry)

    total = len(all_entries)
    print(f"\nTotal Dyck words (n=1..{MAX_N}): {total}")

    pairseq_fail = sum(1 for e in all_entries if not e['pairseq_match'])
    print(f"pair_seq match real wrapping: {total - pairseq_fail}/{total}")
    if pairseq_fail:
        print(f"pair_seq FAILS on: {pairseq_fail}/{total} ({100 * pairseq_fail / total:.1f}%)")

    print("\n" + "=" * 70)
    print("SECTION 1: Group by x-seq X — which groups have wrapping ambiguity?")
    print("=" * 70)

    by_xseq = defaultdict(list)
    for e in all_entries:
        by_xseq[e['X']].append(e)

    ambiguous_groups = []
    unambiguous_groups = []
    for X, group in by_xseq.items():
        bobw_set = set(e['bobw_real'] for e in group)
        kw_set = set(e['kw_real'] for e in group)
        if len(bobw_set) > 1 or len(kw_set) > 1:
            ambiguous_groups.append((X, group))
        else:
            unambiguous_groups.append((X, group))

    print(f"Total x-seq groups: {len(by_xseq)}")
    print(f"  Unambiguous (same X → same wrapping): {len(unambiguous_groups)}")
    print(f"  Ambiguous (same X → different wrapping): {len(ambiguous_groups)}")
    print(f"  Ambiguous groups / total groups: {len(ambiguous_groups)}/{len(by_xseq)} = {100*len(ambiguous_groups)/len(by_xseq):.1f}%")

    if ambiguous_groups:
        print("\n  Ambiguous x-seq groups (showing first 10):")
        for i, (X, group) in enumerate(ambiguous_groups[:10]):
            bobw_vals = sorted(set(e['bobw_real'] for e in group))
            kw_vals = sorted(set(e['kw_real'] for e in group))
            members = len(group)
            distinct_wraps = len(set((e['bobw_real'], e['kw_real']) for e in group))
            print(f"    X={str(list(X)):30s}  members={members}  bobw∈{bobw_vals}  kw∈{kw_vals}  distinct_wraps={distinct_wraps}")

    print("\n" + "=" * 70)
    print("SECTION 2: For ambiguous groups, find MINIMAL O(1) extra params")
    print("  Goal: What's the smallest set of height/tree params that resolves")
    print("  wrapping ambiguity within same-x-seq groups?")
    print("=" * 70)

    candidate_params = [
        'h_max',
        'h_sum',
        'h_mean',
        'h_var',
        'h_std',
        'returns0',
        'peaks',
        'valleys',
        'leaf_count',
        'max_depth',
        'sum_depths',
        'max_subtree_size',
        'sum_subtree_sizes',
        'root_children',
    ]

    print("\n  Individual O(1) parameters — can any alone distinguish wrapping?")
    for p in candidate_params:
        ok = 0
        fail = 0
        for X, group in ambiguous_groups:
            vals = set(round(e[p], 6) if isinstance(e[p], float) else e[p] for e in group)
            bobw_set = set(e['bobw_real'] for e in group)
            kw_set = set(e['kw_real'] for e in group)
            param_groups = defaultdict(list)
            for e in group:
                key = round(e[p], 6) if isinstance(e[p], float) else e[p]
                param_groups[key].append(e)
            all_ok = True
            for pg in param_groups.values():
                bw = set(e['bobw_real'] for e in pg)
                kw = set(e['kw_real'] for e in pg)
                if len(bw) > 1 or len(kw) > 1:
                    all_ok = False
                    break
            if all_ok:
                ok += 1
            else:
                fail += 1
        status = "✅ PERFECT" if fail == 0 else f"fails on {fail}/{len(ambiguous_groups)} groups"
        print(f"    {p:25s} → {status}")

    print("\n  Pairs of O(1) parameters — exhaustively test ALL pairs on ambiguous groups")
    best_pairs = []
    for p1, p2 in combinations(candidate_params, 2):
        ok = 0
        fail = 0
        for X, group in ambiguous_groups:
            sig_map = defaultdict(list)
            for e in group:
                v1 = round(e[p1], 6) if isinstance(e[p1], float) else e[p1]
                v2 = round(e[p2], 6) if isinstance(e[p2], float) else e[p2]
                sig = (v1, v2)
                sig_map[sig].append(e)
            all_ok = True
            for sig, entries in sig_map.items():
                bw = set(e['bobw_real'] for e in entries)
                kw = set(e['kw_real'] for e in entries)
                if len(bw) > 1 or len(kw) > 1:
                    all_ok = False
                    break
            if all_ok:
                ok += 1
            else:
                fail += 1
        best_pairs.append(((p1, p2), ok, fail))

    best_pairs.sort(key=lambda x: (-x[1], x[2]))
    print("  Top 10 parameter pairs:")
    for (p1, p2), ok, fail in best_pairs[:10]:
        status = "✅ PERFECT" if fail == 0 else f"resolves {ok}/{len(ambiguous_groups)}, fails {fail}"
        print(f"    ({p1}, {p2}) → {status}")

    print("\n  Triples of O(1) parameters — best candidates")
    good_pairs = [(p, ok) for p, ok, fail in best_pairs if fail == 0]
    if good_pairs:
        print(f"  Found {len(good_pairs)} perfect pairs (resolve all ambiguous groups)")
    else:
        best_pair_names = [p for p, _, _ in best_pairs[:5]]
        for (p1, p2), ok, fail in best_pairs[:3]:
            remaining_fails = []
            for X, group in ambiguous_groups:
                for e in group:
                    pass
        all_triples = []
        for (p1_p2), _, _ in best_pairs[:5]:
            p1, p2 = p1_p2
            for p3 in candidate_params:
                if p3 in (p1, p2):
                    continue
                ok = 0
                fail = 0
                for X, group in ambiguous_groups:
                    sig_map = defaultdict(list)
                    for e in group:
                        v1 = round(e[p1], 6) if isinstance(e[p1], float) else e[p1]
                        v2 = round(e[p2], 6) if isinstance(e[p2], float) else e[p2]
                        v3 = round(e[p3], 6) if isinstance(e[p3], float) else e[p3]
                        sig = (v1, v2, v3)
                        sig_map[sig].append(e)
                    all_ok = True
                    for sig, entries in sig_map.items():
                        bw = set(e['bobw_real'] for e in entries)
                        kw = set(e['kw_real'] for e in entries)
                        if len(bw) > 1 or len(kw) > 1:
                            all_ok = False
                            break
                    if all_ok:
                        ok += 1
                    else:
                        fail += 1
                all_triples.append(((p1, p2, p3), ok, fail))
        all_triples.sort(key=lambda x: (-x[1], x[2]))
        print("\n  Top 10 triples:")
        for params, ok, fail in all_triples[:10]:
            status = "✅ PERFECT" if fail == 0 else f"resolves {ok}/{len(ambiguous_groups)}, fails {fail}"
            print(f"    {params} → {status}")

    print("\n" + "=" * 70)
    print("SECTION 3: Detailed analysis of ambiguous groups")
    print("  For each ambiguous x-seq group, show all members and their wrapping")
    print("=" * 70)

    for X, group in ambiguous_groups[:15]:
        print(f"\n  X = {list(X)}  ({len(group)} members)")
        print(f"  {'s':30s} {'bobw':>6s} {'kw':>3s} {'Xw':30s} {'h_max':>5s} {'h_sum':>6s} {'peaks':>5s} {'leaves':>6s}")
        print(f"  {'-'*30} {'-'*6} {'-'*3} {'-'*30} {'-'*5} {'-'*6} {'-'*5} {'-'*6}")
        for e in sorted(group, key=lambda x: (x['bobw_real'], x['kw_real'])):
            print(f"  {e['s']:30s} {e['bobw_real']:6d} {e['kw_real']:3d} {str(list(e['Xw_real'])):30s} {e['h_max']:5d} {e['h_sum']:6d} {e['peaks']:5d} {e['leaf_count']:6d}")

    print("\n" + "=" * 70)
    print("SECTION 4: Is wrapping ambiguity related to specific x-seq patterns?")
    print("=" * 70)

    pattern_stats = defaultdict(lambda: {'total': 0, 'ambiguous': 0})
    for X, group in by_xseq.items():
        bobw_set = set(e['bobw_real'] for e in group)
        kw_set = set(e['kw_real'] for e in group)
        is_amb = len(bobw_set) > 1 or len(kw_set) > 1
        has_1 = 1 in X
        k = len(X)
        first = X[0]
        pattern_stats['all']['total'] += 1
        if is_amb:
            pattern_stats['all']['ambiguous'] += 1
        if has_1:
            pattern_stats['has_1']['total'] += 1
            if is_amb:
                pattern_stats['has_1']['ambiguous'] += 1
        if not has_1:
            pattern_stats['no_1']['total'] += 1
            if is_amb:
                pattern_stats['no_1']['ambiguous'] += 1
        if first == 1:
            pattern_stats['first=1']['total'] += 1
            if is_amb:
                pattern_stats['first=1']['ambiguous'] += 1
        if first >= 2:
            pattern_stats['first>=2']['total'] += 1
            if is_amb:
                pattern_stats['first>=2']['ambiguous'] += 1

    for name in ['all', 'has_1', 'no_1', 'first=1', 'first>=2']:
        s = pattern_stats[name]
        if s['total'] > 0:
            pct = 100 * s['ambiguous'] / s['total']
            print(f"  {name:15s}: {s['ambiguous']:3d}/{s['total']:3d} ambiguous ({pct:.1f}%)")

    print("\n" + "=" * 70)
    print("SECTION 5: Group by (X, h_max) — can height alone resolve wrapping?")
    print("=" * 70)

    by_x_hmax = defaultdict(list)
    for e in all_entries:
        key = (e['X'], e['h_max'])
        by_x_hmax[key].append(e)

    hmax_ambiguous = 0
    hmax_total = len(by_x_hmax)
    for key, group in by_x_hmax.items():
        bobw_set = set(e['bobw_real'] for e in group)
        kw_set = set(e['kw_real'] for e in group)
        if len(bobw_set) > 1 or len(kw_set) > 1:
            hmax_ambiguous += 1

    print(f"  Groups with (X, h_max): {hmax_total}")
    print(f"  Still ambiguous: {hmax_ambiguous}")
    print(f"  Resolved by h_max: {hmax_total - hmax_ambiguous} / {hmax_total}")
    if hmax_ambiguous > 0:
        print(f"  h_max alone is NOT sufficient to resolve all ambiguity")

    print("\n" + "=" * 70)
    print("SECTION 6: Group by (X, h_max, h_sum) — height + area")
    print("=" * 70)

    by_x_hmax_hsum = defaultdict(list)
    for e in all_entries:
        key = (e['X'], e['h_max'], e['h_sum'])
        by_x_hmax_hsum[key].append(e)

    h3_ambiguous = 0
    for key, group in by_x_hmax_hsum.items():
        bobw_set = set(e['bobw_real'] for e in group)
        kw_set = set(e['kw_real'] for e in group)
        if len(bobw_set) > 1 or len(kw_set) > 1:
            h3_ambiguous += 1

    print(f"  Groups with (X, h_max, h_sum): {len(by_x_hmax_hsum)}")
    print(f"  Still ambiguous: {h3_ambiguous}")
    if h3_ambiguous == 0:
        print("  ✅ (X, h_max, h_sum) UNIQUELY determines wrapping!")
    else:
        print(f"  Still need more parameters to resolve {h3_ambiguous} groups")

    print("\n" + "=" * 70)
    print("SECTION 7: Exhaustive search — minimal O(1) param set over ALL data")
    print("  (not just ambiguous groups — over all 2055 trees)")
    print("=" * 70)

    all_o1_params = candidate_params.copy()

    def test_o1_params(all_entries, params):
        sig_map = defaultdict(list)
        for e in all_entries:
            sig = tuple(round(e[p], 6) if isinstance(e[p], float) else e[p] for p in params)
            sig_map[sig].append(e)
        collisions = 0
        for sig, entries in sig_map.items():
            bw = set(e['bobw_real'] for e in entries)
            kw = set(e['kw_real'] for e in entries)
            if len(bw) > 1 or len(kw) > 1:
                collisions += 1
        return collisions, len(sig_map)

    base_xseq_coll, base_xseq_groups = test_o1_params(all_entries, ['X'])
    print(f"\n  Baseline (X only): {base_xseq_coll} collisions, {base_xseq_groups} groups")

    for p in all_o1_params:
        coll, groups = test_o1_params(all_entries, ['X', p])
        status = "✅ PERFECT" if coll == 0 else f"{coll} coll"
        print(f"    (X, {p:25s}) → {status:20s} ({groups} groups)")

    good_singles = [p for p in all_o1_params if test_o1_params(all_entries, ['X', p])[0] == 0]
    if good_singles:
        print(f"\n  ★★★ Single O(1) params that resolve ALL wrapping ambiguity: {good_singles}")
    else:
        print(f"\n  No single O(1) param resolves all ambiguity. Testing pairs...")
        best_pairs_all = []
        for p1, p2 in combinations(all_o1_params, 2):
            coll, groups = test_o1_params(all_entries, ['X', p1, p2])
            best_pairs_all.append(((p1, p2), coll, groups))

        best_pairs_all.sort(key=lambda x: x[1])
        print("  Top pairs:")
        for (p1, p2), coll, groups in best_pairs_all[:10]:
            status = "✅ PERFECT" if coll == 0 else f"{coll} coll"
            print(f"    (X, {p1}, {p2}) → {status} ({groups} groups)")

        perfect_pairs = [(ps, g) for ps, c, g in best_pairs_all if c == 0]
        if perfect_pairs:
            print(f"\n  ★★★ {len(perfect_pairs)} parameter pairs achieve PERFECT resolution")
            for ps, g in perfect_pairs[:5]:
                print(f"    (X, {ps[0]}, {ps[1]}) → {g} groups")
        else:
            print(f"\n  No pair resolves all. Testing triples...")
            best_triples_all = []
            for (p1_p2), _, _ in best_pairs_all[:5]:
                p1, p2 = p1_p2
                for p3 in all_o1_params:
                    if p3 in (p1, p2):
                        continue
                    coll, groups = test_o1_params(all_entries, ['X', p1, p2, p3])
                    best_triples_all.append(((p1, p2, p3), coll, groups))
            best_triples_all.sort(key=lambda x: x[1])
            print("  Top triples:")
            for ps, coll, groups in best_triples_all[:10]:
                status = "✅ PERFECT" if coll == 0 else f"{coll} coll"
                print(f"    (X, {ps[0]}, {ps[1]}, {ps[2]}) → {status} ({groups} groups)")

    print("\n" + "=" * 70)
    print("SECTION 8: Analysis of per-n growth of ambiguity")
    print("=" * 70)

    for n in range(1, MAX_N + 1):
        entries_n = [e for e in all_entries if e['n'] == n]
        by_x_n = defaultdict(list)
        for e in entries_n:
            by_x_n[e['X']].append(e)
        amb = sum(1 for X, g in by_x_n.items()
                  if len(set(e['bobw_real'] for e in g)) > 1 or len(set(e['kw_real'] for e in g)) > 1)
        total_groups = len(by_x_n)
        cat = len(entries_n)
        print(f"  n={n}: Catalan={cat:4d}, x-seq groups={total_groups:3d}, ambiguous={amb:3d}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)


if __name__ == '__main__':
    run()
