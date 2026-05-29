import sys
sys.path.insert(0, '.')
from verify_bf import generate_dyck, x_seq_and_bob, alice_of
from collections import defaultdict
import math

MAX_N = 8
MOD = 998244353


def height_path(s):
    n = len(s) // 2
    h = [0] * (2 * n + 1)
    for i, ch in enumerate(s):
        h[i + 1] = h[i] + (1 if ch == '(' else -1)
    return h


def dyck_to_tree(s):
    n = len(s) // 2
    parent = [-1] * n
    children = [[] for _ in range(n)]
    depth = [0] * n
    sz = [0] * n
    leaf = [True] * n
    sibling_index = [0] * n
    node_id = 0
    stack = [-1]
    for ch in s:
        if ch == '(':
            p = stack[-1]
            if p >= 0:
                children[p].append(node_id)
                sibling_index[node_id] = len(children[p]) - 1
                leaf[p] = False
                depth[node_id] = depth[p] + 1
            parent[node_id] = p
            stack.append(node_id)
            node_id += 1
        else:
            stack.pop()

    def dfs(v):
        total = 1
        for c in children[v]:
            dfs(c)
            total += sz[c]
        sz[v] = total

    root = next(v for v in range(n) if parent[v] == -1)
    dfs(root)
    return parent, children, depth, sz, leaf, sibling_index, root


def x_seq_chain_indices(children, root):
    n = len(children)
    chain_idx = [-1] * n
    order = []
    cur = root
    idx = 0
    while True:
        c = cur
        chain = []
        while True:
            chain.append(c)
            if not children[c]:
                break
            c = children[c][0]
        for v in chain:
            chain_idx[v] = idx
            order.append(v)
        idx += 1
        nxt = None
        for v in reversed(chain):
            for pp, ch_list in enumerate(children):
                if v in ch_list:
                    si = ch_list.index(v)
                    if si + 1 < len(ch_list):
                        nxt = ch_list[si + 1]
                        break
            if nxt is not None:
                break
        if nxt is None:
            break
        cur = nxt
    return chain_idx, order


def compute_all_params(s):
    n = len(s) // 2
    X, bob = x_seq_and_bob(s)
    al = alice_of(s)
    k = len(X)
    x1 = X[0]
    h = height_path(s)
    h_max = max(h)
    h_sum = sum(h[1:2 * n])
    returns0 = sum(1 for i in range(1, 2 * n) if h[i] == 0)

    internal_ones = sum(1 for i, x in enumerate(X) if i > 0 and x == 1)

    parent, children, depth, sz, leaf, sibling_index, root = dyck_to_tree(s)

    sum_depths = sum(depth)
    sum_subtree_sizes = sum(sz)
    leaf_count = sum(1 for v in range(n) if leaf[v])
    max_depth_val = max(depth) if n > 0 else 0
    sum_sibling_indices = sum(sibling_index)
    root_children = len(children[root])

    leaf_depths = [depth[v] for v in range(n) if leaf[v]]
    sum_leaf_depths = sum(leaf_depths)

    sum_depth_times_sz = sum(depth[v] * sz[v] for v in range(n))
    sum_sz_times_sibling = sum(sz[v] * sibling_index[v] for v in range(n))
    sum_sq_subtree_sizes = sum(sz[v] * sz[v] for v in range(n))
    sum_depth_times_leaf = sum(depth[v] * (1 if leaf[v] else 0) for v in range(n))

    parents_before = [0] * n
    for v in range(n):
        cnt = 0
        cur_v = v
        while parent[cur_v] >= 0:
            cnt += sibling_index[cur_v]
            cur_v = parent[cur_v]
        parents_before[v] = cnt

    max_subtree_size = max(sz) if n > 0 else 0
    sum_internal_depths = sum(depth[v] for v in range(n) if not leaf[v])

    chain_idx, traversal_order = x_seq_chain_indices(children, root)
    max_chain_idx = max(chain_idx) if chain_idx else -1
    sum_chain_indices = sum(chain_idx)

    return {
        'n': n, 'bob': bob, 'alice': al, 'k': k, 'X': tuple(X), 'x1': x1,
        'h_max': h_max, 'h_sum': h_sum, 'returns0': returns0,
        'sum_depths': sum_depths, 'sum_subtree_sizes': sum_subtree_sizes,
        'leaf_count': leaf_count, 'max_depth': max_depth_val,
        'sum_sibling_indices': sum_sibling_indices,
        'root_children': root_children,
        'sum_leaf_depths': sum_leaf_depths,
        'sum_depth_times_sz': sum_depth_times_sz,
        'sum_sz_times_sibling': sum_sz_times_sibling,
        'n_sq': n * n,
        'n_choose_2': n * (n - 1) // 2,
        'internal_ones': internal_ones,
        'max_subtree_size': max_subtree_size,
        'sum_internal_depths': sum_internal_depths,
        'sum_depth_times_leaf': sum_depth_times_leaf,
        'sum_sq_subtree_sizes': sum_sq_subtree_sizes,
        'sum_parents_before': sum(parents_before),
        'max_chain_idx': max_chain_idx,
        'sum_chain_indices': sum_chain_indices,
    }


def solve_2param(v1, v2, targets, n_items, use_const):
    for i in range(min(10, n_items)):
        for j in range(min(10, n_items)):
            if i == j:
                continue
            if use_const:
                det = v1[i] * v2[j] - v1[j] * v2[i] - v1[i] + v1[j] + v2[i] - v2[j]
                if det == 0:
                    continue
                det2 = (v1[i] - v1[j]) * targets[j] - (v2[i] - v2[j]) * targets[i]
                if det2 % det != 0:
                    continue
                c2 = det2 // det
                num_a = targets[i] * v2[j] - targets[j] * v2[i] - c2 * (v2[j] - v2[i])
                denom_a = v1[i] * v2[j] - v1[j] * v2[i]
                if denom_a == 0:
                    continue
                if num_a % denom_a != 0:
                    continue
                a = num_a // denom_a
                num_b = v1[i] * targets[j] - v1[j] * targets[i] - c2 * (v1[i] - v1[j])
                if num_b % denom_a != 0:
                    continue
                b = num_b // denom_a
                ok = True
                for t in range(n_items):
                    if a * v1[t] + b * v2[t] + c2 != targets[t]:
                        ok = False
                        break
                if ok:
                    return (a, b, c2)
            else:
                det = v1[i] * v2[j] - v1[j] * v2[i]
                if det == 0:
                    continue
                num_a = targets[i] * v2[j] - targets[j] * v2[i]
                if num_a % det != 0:
                    continue
                a = num_a // det
                num_b = v1[i] * targets[j] - v1[j] * targets[i]
                if num_b % det != 0:
                    continue
                b = num_b // det
                ok = True
                for t in range(n_items):
                    if a * v1[t] + b * v2[t] != targets[t]:
                        ok = False
                        break
                if ok:
                    return (a, b, None)
    return None


def test_bob_expressions(entries):
    n_entries = len(entries)
    all_keys = list(entries[0].keys())

    scalars = [k for k in all_keys if isinstance(entries[0][k], (int,)) and k not in
               ('n', 'bob', 'alice', 'k', 'x1', 'n_sq', 'n_choose_2', 'internal_ones')]

    print("=" * 80)
    print("路线 J：bob 等效表达刺探")
    print(f"总词数: {n_entries} (n<={MAX_N})")
    print("=" * 80)

    print("\n--- Section 1: 单参数直接等于 bob ---")
    single_matches = []
    for key in scalars:
        if not isinstance(entries[0][key], int):
            continue
        ok = all(e[key] == e['bob'] for e in entries)
        if ok:
            single_matches.append(key)
            print(f"  ✅ bob == {key} 对所有 {n_entries} 个词成立!")
        else:
            match_count = sum(1 for e in entries if e[key] == e['bob'])
            if match_count > n_entries * 0.5:
                print(f"     bob == {key}: {match_count}/{n_entries} ({100*match_count/n_entries:.1f}%)")
    if not single_matches:
        print("  ❌ 无单参数等于 bob")

    bobs = [e['bob'] for e in entries]

    print("\n--- Section 2: 双参数组合搜索 ---")
    basis_params = ['h_sum', 'sum_depths', 'sum_subtree_sizes', 'leaf_count',
                    'max_depth', 'sum_sibling_indices', 'root_children',
                    'sum_leaf_depths', 'sum_depth_times_sz', 'sum_sz_times_sibling',
                    'max_subtree_size', 'sum_internal_depths', 'sum_depth_times_leaf',
                    'sum_sq_subtree_sizes', 'sum_parents_before',
                    'sum_chain_indices', 'max_chain_idx',
                    'alice', 'k', 'x1', 'internal_ones', 'n_sq', 'n_choose_2',
                    'h_max', 'returns0', 'n']

    found_2 = False
    best_2 = None
    best_2_match = 0
    for i, p1 in enumerate(basis_params):
        for p2 in basis_params[i + 1:]:
            v1 = [e[p1] for e in entries]
            v2 = [e[p2] for e in entries]
            result = solve_2param(v1, v2, bobs, n_entries, use_const=False)
            if result:
                print(f"    ✅ bob == {result[0]}*{p1} + {result[1]}*{p2}")
                found_2 = True
            result = solve_2param(v1, v2, bobs, n_entries, use_const=True)
            if result:
                print(f"    ✅ bob == {result[0]}*{p1} + {result[1]}*{p2} + {result[2]}")
                found_2 = True
    if not found_2:
        print("  ❌ 无 2 参数组合等于 bob")

    print("\n--- Section 3: n^2 - alice ---")
    diff = [e['n_sq'] - e['alice'] for e in entries]
    match = sum(1 for j in range(n_entries) if diff[j] == bobs[j])
    print(f"  bob == n^2 - alice: {match}/{n_entries} ({100*match/n_entries:.1f}%)")

    print("\n--- Section 4: n*(n-1)/2 - 参数 ---")
    nC2 = [e['n_choose_2'] for e in entries]
    for key in basis_params:
        if key == 'n_choose_2':
            continue
        vals = [e[key] for e in entries]
        diff_vals = [nC2[j] - vals[j] for j in range(n_entries)]
        match = sum(1 for j in range(n_entries) if diff_vals[j] == bobs[j])
        if match == n_entries:
            print(f"  ✅ bob == n*(n-1)/2 - {key} 对所有词成立!")
        elif match > n_entries * 0.5:
            print(f"     bob == n*(n-1)/2 - {key}: {match}/{n_entries} ({100*match/n_entries:.1f}%)")

    print("\n--- Section 5: n^2 - 参数 ---")
    for key in basis_params:
        if key == 'n_sq':
            continue
        vals = [e[key] for e in entries]
        diff_vals = [e['n_sq'] - vals[j] for j, e in enumerate(entries)]
        match = sum(1 for j in range(n_entries) if diff_vals[j] == bobs[j])
        if match == n_entries:
            print(f"  ✅ bob == n^2 - {key} 对所有词成立!")
        elif match > n_entries * 0.5:
            print(f"     bob == n^2 - {key}: {match}/{n_entries} ({100*match/n_entries:.1f}%)")

    print("\n--- Section 6: 非线性候选表达式 ---")
    candidates = {}
    candidates['h_sum - n*n'] = [e['h_sum'] - e['n_sq'] for e in entries]
    candidates['h_sum - sum_depths'] = [e['h_sum'] - e['sum_depths'] for e in entries]
    candidates['h_sum - sum_subtree_sizes'] = [e['h_sum'] - e['sum_subtree_sizes'] for e in entries]
    candidates['sum_subtree_sizes - sum_depths'] = [e['sum_subtree_sizes'] - e['sum_depths'] for e in entries]
    candidates['sum_subtree_sizes - h_sum'] = [e['sum_subtree_sizes'] - e['h_sum'] for e in entries]
    candidates['(h_sum - n) // 2'] = [(e['h_sum'] - e['n']) // 2 for e in entries]
    candidates['(sum_depths - n) // 2'] = [(e['sum_depths'] - e['n']) // 2 for e in entries]
    candidates['sum_parents_before'] = [e['sum_parents_before'] for e in entries]
    candidates['sum_chain_indices'] = [e['sum_chain_indices'] for e in entries]
    candidates['n*n - h_sum*2'] = [e['n_sq'] - e['h_sum'] * 2 for e in entries]
    candidates['h_sum // 2'] = [e['h_sum'] // 2 for e in entries]
    candidates['h_sum // 3'] = [e['h_sum'] // 3 for e in entries]
    candidates['sum_depths // 2'] = [e['sum_depths'] // 2 for e in entries]
    candidates['(n*n - sum_depths*2)'] = [e['n_sq'] - e['sum_depths'] * 2 for e in entries]
    candidates['n*(n-1)//2 - h_sum//2'] = [e['n_choose_2'] - e['h_sum'] // 2 for e in entries]
    candidates['n*(n-1)//2 - sum_depths//2'] = [e['n_choose_2'] - e['sum_depths'] // 2 for e in entries]
    candidates['h_sum - returns0*n'] = [e['h_sum'] - e['returns0'] * e['n'] for e in entries]
    candidates['sum_depths - returns0*n'] = [e['sum_depths'] - e['returns0'] * e['n'] for e in entries]
    candidates['returns0 * n'] = [e['returns0'] * e['n'] for e in entries]
    candidates['(n - returns0 - 1) * n'] = [(e['n'] - e['returns0'] - 1) * e['n'] for e in entries]
    candidates['leaf_count * (n - leaf_count)'] = [e['leaf_count'] * (e['n'] - e['leaf_count']) for e in entries]
    candidates['root_children * (n - root_children)'] = [e['root_children'] * (e['n'] - e['root_children']) for e in entries]
    candidates['max_depth * (n - 1)'] = [e['max_depth'] * (e['n'] - 1) for e in entries]
    candidates['n*n - sum_depth_times_sz'] = [e['n_sq'] - e['sum_depth_times_sz'] for e in entries]

    best_candidate = None
    best_c_match = 0
    for name, vals in candidates.items():
        match = sum(1 for j in range(n_entries) if vals[j] == bobs[j])
        if match > best_c_match:
            best_c_match = match
            best_candidate = (name, match)
        if match == n_entries:
            print(f"  ✅ bob == {name} 对所有 {n_entries} 个词成立!")
        elif match > n_entries * 0.7:
            print(f"  ⚠️ bob == {name}: {match}/{n_entries} ({100*match/n_entries:.1f}%)")

    if best_candidate and best_c_match < n_entries:
        print(f"  最佳候选: bob == {best_candidate[0]} → {best_candidate[1]}/{n_entries} "
              f"({100*best_candidate[1]/n_entries:.1f}%)")

    print("\n--- Section 7: 按 n 分组分析 ---")
    by_n = defaultdict(list)
    for e in entries:
        by_n[e['n']].append(e)

    print(f"  {'n':>3} {'count':>6} {'bob范围':>14} {'h_sum范围':>14} {'sum_depths':>14} "
          f"{'sum_subtree':>14} {'sum_chain_idx':>14}")
    for n_val in sorted(by_n):
        group = by_n[n_val]
        b_min, b_max = min(e['bob'] for e in group), max(e['bob'] for e in group)
        h_min_v, h_max_v = min(e['h_sum'] for e in group), max(e['h_sum'] for e in group)
        d_min, d_max_v = min(e['sum_depths'] for e in group), max(e['sum_depths'] for e in group)
        s_min, s_max_v = min(e['sum_subtree_sizes'] for e in group), max(e['sum_subtree_sizes'] for e in group)
        c_min, c_max_v = min(e['sum_chain_indices'] for e in group), max(e['sum_chain_indices'] for e in group)
        print(f"  {n_val:>3} {len(group):>6} [{b_min:>4}, {b_max:>4}] [{h_min_v:>4}, {h_max_v:>4}] "
              f"[{d_min:>4}, {d_max_v:>4}] [{s_min:>4}, {s_max_v:>4}] [{c_min:>4}, {c_max_v:>4}]")

    print("\n--- Section 8: bob + alice 关系 ---")
    bob_alice = [(e['bob'], e['alice'], e['n']) for e in entries]
    sums_ba = [b + a for b, a, _ in bob_alice]
    print(f"  bob + alice 唯一值数: {len(set(sums_ba))} / {n_entries}")
    print(f"  范围: [{min(sums_ba)}, {max(sums_ba)}]")

    by_n_ba = defaultdict(list)
    for b, a, n_val in bob_alice:
        by_n_ba[n_val].append(b + a)

    for n_val in sorted(by_n_ba):
        vals_n = by_n_ba[n_val]
        print(f"    n={n_val}: bob+alice ∈ [{min(vals_n)}, {max(vals_n)}], "
              f"唯一值 {len(set(vals_n))} (n²={n_val*n_val})")

    print("\n--- Section 9: 相关性排名 ---")
    correlations = []
    for key in basis_params:
        if key in ('bob', 'X'):
            continue
        vals = [e[key] for e in entries]
        mean_b = sum(bobs) / n_entries
        mean_v = sum(vals) / n_entries
        cov = sum((bobs[i] - mean_b) * (vals[i] - mean_v) for i in range(n_entries))
        std_b = math.sqrt(sum((x - mean_b) ** 2 for x in bobs))
        std_v = math.sqrt(sum((x - mean_v) ** 2 for x in vals))
        if std_b > 0 and std_v > 0:
            corr = cov / (std_b * std_v)
            correlations.append((abs(corr), corr, key))
    correlations.sort(reverse=True)
    print(f"  {'排名':>4} {'参数':<28} {'相关系数':>10}")
    for rank, (_, c, key) in enumerate(correlations[:20], 1):
        print(f"  {rank:>4} {key:<28} {c:>10.6f}")

    print("\n--- Section 10: 每个 n 内 bob vs 最佳相关参数 ---")
    for n_val in sorted(by_n):
        group = by_n[n_val]
        if len(group) < 2:
            continue
        n_groups = len(group)
        g_bobs = [e['bob'] for e in group]
        top_key = correlations[0][2]
        g_vals = [e[top_key] for e in group]
        uniq = len(set(zip(g_vals, g_bobs)))
        print(f"  n={n_val}: bob vs {top_key}: {uniq}/{n_groups} 唯一对 "
              f"({100*uniq/n_groups:.1f}%)")

    print("\n--- Section 11: 穷举搜索 3 参数线性组合 ---")
    top_params = [corr[2] for corr in correlations[:8]]
    top_params = [p for p in top_params if p not in ('bob', 'X')]

    found_3 = False
    for i, p1 in enumerate(top_params):
        for j, p2 in enumerate(top_params[i + 1:], i + 1):
            for p3 in top_params[j + 1:]:
                v1 = [e[p1] for e in entries]
                v2 = [e[p2] for e in entries]
                v3 = [e[p3] for e in entries]
                for a in range(min(10, n_entries)):
                    for b in range(a + 1, min(10, n_entries)):
                        for c in range(b + 1, min(10, n_entries)):
                            A = [[v1[a], v2[a], v3[a]],
                                 [v1[b], v2[b], v3[b]],
                                 [v1[c], v2[c], v3[c]]]
                            det = (A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1])
                                   - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
                                   + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]))
                            if det == 0:
                                continue
                            B = [bobs[a], bobs[b], bobs[c]]
                            c0 = (B[0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1])
                                  - A[0][1] * (B[1] * A[2][2] - A[1][2] * B[2])
                                  + A[0][2] * (B[1] * A[2][1] - A[1][1] * B[2]))
                            if c0 % det != 0:
                                continue
                            c0 //= det
                            c1 = (A[0][0] * (B[1] * A[2][2] - A[1][2] * B[2])
                                  - B[0] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
                                  + A[0][2] * (A[1][0] * B[2] - B[1] * A[2][0]))
                            if c1 % det != 0:
                                continue
                            c1 //= det
                            c2 = (A[0][0] * (A[1][1] * B[2] - B[1] * A[2][1])
                                  - A[0][1] * (A[1][0] * B[2] - B[1] * A[2][0])
                                  + B[0] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]))
                            if c2 % det != 0:
                                continue
                            c2 //= det
                            ok = True
                            for t in range(n_entries):
                                if c0 * v1[t] + c1 * v2[t] + c2 * v3[t] != bobs[t]:
                                    ok = False
                                    break
                            if ok:
                                print(f"  ✅ bob == {c0}*{p1} + {c1}*{p2} + {c2}*{p3}")
                                found_3 = True
                            if found_3:
                                break
                        if found_3:
                            break
                    if found_3:
                        break
                if found_3:
                    break
            if found_3:
                break
        if found_3:
            break
    if not found_3:
        print("  ❌ 无 3 参数线性组合能表达 bob")

    print("\n--- Section 12: 每个 n 内 bob 唯一性分析 ---")
    for n_val in sorted(by_n):
        group = by_n[n_val]
        bobs_n = [e['bob'] for e in group]
        unique_bobs = len(set(bobs_n))
        print(f"  n={n_val}: {unique_bobs} 个不同 bob 值 / {len(group)} 棵树 "
              f"(压缩比 {len(group)/max(1,unique_bobs):.1f}:1)")

    print("\n--- Section 13: 展示反例：相同几何参数但不同 bob ---")
    for n_val in sorted(by_n):
        if n_val < 3:
            continue
        group = by_n[n_val]
        key_params = [corr[2] for corr in correlations[:3] if corr[2] not in ('bob',)]
        seen = {}
        for e in group:
            sig = tuple(e[p] for p in key_params)
            if sig in seen:
                prev = seen[sig]
                if prev['bob'] != e['bob']:
                    print(f"  n={n_val}: 相同 ({', '.join(f'{p}={e[p]}' for p in key_params)})")
                    print(f"    词1: bob={prev['bob']}, alice={prev['alice']}, X={prev['X']}")
                    print(f"    词2: bob={e['bob']}, alice={e['alice']}, X={e['X']}")
                    break
            else:
                seen[sig] = e

    print("\n" + "=" * 80)
    print("路线 J 实验完成。")
    print("=" * 80)


def main():
    entries = []
    for n in range(1, MAX_N + 1):
        for s in generate_dyck(n):
            entries.append(compute_all_params(s))
    test_bob_expressions(entries)


if __name__ == '__main__':
    main()
