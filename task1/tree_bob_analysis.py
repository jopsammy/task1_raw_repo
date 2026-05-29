import sys
sys.path.insert(0, r'd:\2024备份和迁移\2024备份和迁移\f复旭文件\h彗星计划相关\其他资料\V6_wida_case\task1')
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

MOD = 998244353

def dyck_to_tree(s):
    n = len(s) // 2
    nodes = []
    root_node = len(nodes)
    nodes.append({'parent': -1, 'children': [], 'idx': root_node})
    cur = root_node
    for ch in s:
        if ch == '(':
            child = len(nodes)
            nodes.append({'parent': cur, 'children': [], 'idx': child})
            nodes[cur]['children'].append(child)
            cur = child
        else:
            cur = nodes[cur]['parent']
    return nodes, root_node

def compute_tree_params(nodes, root):
    depth = {}
    subtree_size = {}
    left_chain = {}
    child_count = {}
    sibling_index = {}

    def dfs(v):
        d = 0 if nodes[v]['parent'] == -1 else depth[nodes[v]['parent']] + 1
        depth[v] = d
        sz = 1
        ch = nodes[v]['children']
        child_count[v] = len(ch)
        for i, c in enumerate(ch):
            sibling_index[c] = i
            sz += dfs(c)
        subtree_size[v] = sz

        if len(ch) == 0:
            left_chain[v] = 1
        else:
            left_chain[v] = 1 + left_chain[ch[0]]
        return sz

    sibling_index[root] = 0
    depth[root] = 0
    dfs(root)
    return depth, subtree_size, left_chain, child_count, sibling_index

def pair_seq(seq):
    r = []; i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq):
            r.append(1+seq[i+1]); i += 2
        else: r.append(seq[i]); i += 1
    return r

N = 7

print("=" * 70)
print("TREE BOB ANALYSIS: n=1..{}".format(N))
print("=" * 70)

all_trees = []
for n in range(1, N+1):
    for s in generate_dyck(n):
        nodes, root = dyck_to_tree(s)
        depth, sz, lc, cc, si = compute_tree_params(nodes, root)
        X, bob = x_seq_and_bob(s)
        k = len(X)
        al = alice_of(s)

        x1 = X[0]
        tail = X[1:] if n > 1 else []
        Xt = pair_seq(tail) if tail else []
        kt = len(Xt)
        bobt = sum(j * Xt[j] for j in range(len(Xt))) if Xt else 0

        Xw = pair_seq([1] + X)
        kw = len(Xw)
        bobw = sum(j * Xw[j] for j in range(len(Xw)))

        X_R = pair_seq(X) if X else []
        k_R = len(X_R)
        bob_R = sum(j * X_R[j] for j in range(len(X_R))) if X_R else 0

        all_trees.append({
            's': s, 'n': n, 'al': al, 'bob': bob, 'k': k,
            'x1': x1, 'X': list(X),
            'kw': kw, 'bobw': bobw, 'Xw': list(Xw),
            'k_R': k_R, 'bob_R': bob_R, 'X_R': list(X_R),
            'kt': kt, 'bobt': bobt, 'Xt': list(Xt),
            'nodes': nodes, 'root': root,
            'depth': depth, 'sz': sz, 'lc': lc, 'cc': cc, 'si': si
        })

print(f"Total Dyck words enumerated: {len(all_trees)}")

print("\n" + "=" * 70)
print("CANDIDATE 3: x1 = lc[root] (left chain length) — VERIFY")
print("=" * 70)
all_ok = True
for t in all_trees:
    if t['x1'] != t['lc'][t['root']]:
        print(f"  MISMATCH: {t['s']} x1={t['x1']} lc(root)={t['lc'][t['root']]}")
        all_ok = False
if all_ok:
    print("  ALL MATCH: x1 = left_chain[root] for ALL Dyck words ✓")

print("\n" + "=" * 70)
print("CANDIDATE 4: x_j in tree terms = left_chain of j-th 'entering point'")
print("=" * 70)
print("After consuming a left-chain segment, we 'exit' and 'enter' the next sibling.")
print("The next x_j = left_chain of the next unvisited sibling.")
print()

for n in range(1, min(N+1, 6)):
    data_n = [t for t in all_trees if t['n'] == n]
    print(f"\nn={n}:")
    for t in data_n:
        print(f"  {t['s']:20s} X={str(t['X']):20s} bob={t['bob']}  lc_list={[(v, t['lc'][v], t['depth'][v], t['si'][v]) for v in sorted(range(len(t['nodes'])), key=lambda v: (t['depth'][v], t['si'][v]))]}")

print("\n" + "=" * 70)
print("CANDIDATE 5: Simulate x-seq traversal on tree DIRECTLY")
print("=" * 70)
print("The x-seq algorithm walks the tree in a specific order.")
print("Starting from root, go down leftmost path -> that's one x-step.")
print("Then go to the next unvisited node and repeat.")
print()

def x_seq_from_tree(nodes, root):
    x_steps = []
    visited = set()
    cur = root
    visited.add(cur)

    while len(visited) < len(nodes):
        step_nodes = 0
        while cur not in visited or True:
            step_nodes += 1
            visited.add(cur)
            children = nodes[cur]['children']
            unvisited_children = [c for c in children if c not in visited]
            if unvisited_children:
                cur = unvisited_children[0]
            else:
                break
        x_steps.append(step_nodes)
        parent = nodes[cur]['parent']
        if parent == -1:
            break
        siblings = nodes[parent]['children']
        my_idx = siblings.index(cur)
        unvisited_sibs = [s for s in siblings[my_idx+1:] if s not in visited]
        if unvisited_sibs:
            cur = unvisited_sibs[0]
        else:
            cur = parent
            while cur != -1:
                gp = nodes[cur]['parent']
                if gp == -1:
                    return x_steps, sum(j * x for j, x in enumerate(x_steps))
                gsibs = nodes[gp]['children']
                gidx = gsibs.index(cur)
                unvisited_gsibs = [s for s in gsibs[gidx+1:] if s not in visited]
                if unvisited_gsibs:
                    cur = unvisited_gsibs[0]
                    break
                cur = gp

    return x_steps, sum(j * x for j, x in enumerate(x_steps))

for n in range(1, min(N+1, 6)):
    data_n = [t for t in all_trees if t['n'] == n]
    print(f"\nn={n}:")
    for t in data_n:
        X_tree, bob_tree = x_seq_from_tree(t['nodes'], t['root'])
        match = X_tree == t['X']
        print(f"  {t['s']:20s} X={str(t['X']):20s} X_tree={str(X_tree):20s} {'✓' if match else '✗'}")

print("\n" + "=" * 70)
print("CANDIDATE 6: bob = Σ depth[v]·(something about subtree)")
print("This is the most promising direction. Let's compute bob per depth level.")
print("=" * 70)

print("\nContribution to bob by depth:")
for n in range(1, min(N+1, 6)):
    data_n = [t for t in all_trees if t['n'] == n]
    for t in data_n:
        nodes = t['nodes']
        depth = t['depth']
        sz = t['sz']
        lc = t['lc']
        si = t['si']

        depth_counts = {}
        depth_sz_sum = {}
        for v in range(len(nodes)):
            d = depth[v]
            depth_counts[d] = depth_counts.get(d, 0) + 1
            depth_sz_sum[d] = depth_sz_sum.get(d, 0) + sz[v]

        max_depth = max(depth.values())
        print(f"  {t['s']:20s} bob={t['bob']:3d}  per_depth_sz={[(d, depth_sz_sum.get(d, 0)) for d in range(max_depth+1)]}")

print("\n" + "=" * 70)
print("CANDIDATE 7: Subtree wrapping catalog — what makes bobw unique?")
print("=" * 70)
print("For each subtree (viewed as standalone tree), compute (bobw, kw, n, m, lc)")
print("Group by (n, m, lc) and see if bobw+kw is determined.")
print()

from collections import defaultdict

subtree_catalog = defaultdict(list)
for t in all_trees:
    nodes = t['nodes']
    root = t['root']
    s = t['s']

    def process_node(v, sp):
        children = nodes[v]['children']
        subsz = 1 + sum(t['sz'][c] for c in children)
        subs = s[sp:sp+2*subsz]

        Xs, bobs = x_seq_and_bob(subs) if subs else ([], 0)
        Xws = pair_seq([1] + Xs) if Xs else [1]
        kws = len(Xws)
        bobws = sum(j * Xws[j] for j in range(len(Xws)))

        subtree_catalog[subsz].append({
            's': subs,
            'lc': t['lc'][v],
            'm': len(children),
            'bob': bobs, 'k': len(Xs),
            'bobw': bobws, 'kw': kws,
            'x1': Xs[0] if Xs else 0,
        })

        nxt = sp + 1
        for c in children:
            process_node(c, nxt)
            nxt += 2 * t['sz'][c]

    process_node(root, 0)

print("Subtree catalog by size:")
for sz in range(1, min(N+1, 7)):
    entries = subtree_catalog[sz]
    groups = defaultdict(list)
    for e in entries:
        key = (e['lc'], e['m'])
        groups[key].append(e)

    print(f"\nsize={sz}: {len(entries)} subtrees")
    for (lc, m), grp in sorted(groups.items()):
        bobw_vals = set(e['bobw'] for e in grp)
        kw_vals = set(e['kw'] for e in grp)
        bob_vals = set(e['bob'] for e in grp)
        k_vals = set(e['k'] for e in grp)
        print(f"  (lc={lc}, m={m}): {len(grp)} trees, bobw∈{bobw_vals}, kw∈{kw_vals}, bob∈{bob_vals}, k∈{k_vals}")

print("\n" + "=" * 70)
print("CANDIDATE 8: Direct wrapping formula from tree params")
print("We know wrapping formulas per-word. Can we derive tree-param versions?")
print("=" * 70)
print()
print("x1 >= 2 case (lc >= 2):")
print("  Xw = [lc, Xt[0], ..., Xt[kt-1]]")
print("  bobw = bobt + (n - lc)  where bobt = bob of tail[1:]")
print("  kw = 1 + kt")
print()
print("  In tree terms: after removing leftmost leaf, process remaining children.")
print("  The 'tail' Xt = X of tree with leftmost leaf removed.")
print("  bobt = bob of the tree with leftmost leaf removed (bob_rem).")
print()
print("x1 == 1 case (lc == 1, root's first child is a leaf):")
print("  bobw = bob_R(forest of remaining children) + (n - 1)")
print("  kw = 1 + k_R(forest of remaining children)")
print("  Here bob_R = bob of pair_seq = 'compressed bob'")
print()
print("Key question: can bob_R(forest) be computed from tree params of the forest?")
print()

print("--- Verifying bob_R(forest) = some function of forest tree params ---")
for n in range(2, min(N+1, 7)):
    data_n = [t for t in all_trees if t['n'] == n]
    for t in data_n:
        if t['x1'] != 1:
            continue
        nodes = t['nodes']
        root = t['root']
        children = nodes[root]['children']
        first_child = children[0]

        remaining_forest_s = t['s'][2:]  # remove first "()"

        forest_nodes, forest_root = dyck_to_tree(remaining_forest_s)
        f_depth, f_sz, f_lc, f_cc, f_si = compute_tree_params(forest_nodes, forest_root)

        X_f, bob_f = x_seq_and_bob(remaining_forest_s)
        Xr_f = pair_seq(X_f)
        k_R_f = len(Xr_f)
        bob_R_f = sum(j * Xr_f[j] for j in range(len(Xr_f)))

        sum_f_lc = sum(f_lc[v] for v in range(len(forest_nodes)))
        sum_f_depth = sum(f_depth[v] for v in range(len(forest_nodes)))

        print(f"  {t['s']:20s}  bob_R(forest)={bob_R_f:3d}  Σlc(forest)={sum_f_lc:3d}  Σdepth={sum_f_depth:3d}")

print("\n" + "=" * 70)
print("CANDIDATE 9: KEY INSIGHT — The pair_seq compression")
print("=" * 70)
print("pair_seq compresses X by merging (1,v) pairs.")
print("In tree terms: x_j=1 means a leaf-only step (a single '()' pair).")
print("pair_seq merges a leaf-step with the FOLLOWING step's left chain.")
print()
print("This is equivalent to: 'skip standalone leaves when they precede larger structures'")
print()
print("For a forest of siblings, the x-seq traversal produces:")
print("  x_1 = lc(T1)  (left chain of first sibling)")
print("  x_2 = lc(T2)")
print("  x_3 = lc(T3)")
print("  ...")
print()
print("pair_seq on this: if x_i=1 (a leaf sibling), merge with x_{i+1}.")
print()
print("So bob_R(forest) can be computed by:")
print("  1. Take the list of left-chain lengths of siblings: [lc1, lc2, ..., lcm]")
print("  2. Apply pair_seq: (1,lc_i+1) -> lc_i+1+1 = lc_i+2? No...")
print("     Actually pair_seq operates on the x-seq, not on lc.")
print("  3. Wait — for a forest of m siblings:")
print("     X(forest) = [lc(T1), lc(T2), ..., lc(Tm)]  (concat of x-seq's)")
print("     But pair_seq((T1)(T2)...(Tm)) compresses across sibling boundaries!")
print()
print("     If lc(Ti)=1 followed by lc(Ti+1)>=2: they merge in pair_seq!")
print("     If lc(Ti)=1 followed by lc(Ti+1)=1: (1,1)->2, then check if merges with next...")
print()

print("Verify: for a forest of m trees, X(forest) = concat of X(tree_i)")
for n in range(2, min(N+1, 7)):
    data_n = [t for t in all_trees if t['n'] == n]
    for t in data_n:
        nodes = t['nodes']
        root = t['root']
        children = nodes[root]['children']
        if len(children) <= 1:
            continue

        all_X = []
        all_lc = []
        for c in children:
            subsz = t['sz'][c]
            all_lc.append(t['lc'][c])

        forest_s = t['s'][1:-1]
        X_f, _ = x_seq_and_bob(forest_s)

        if all_lc != X_f[:len(all_lc)]:
            pass

print("\n" + "=" * 70)
print("CRITICAL INSIGHT: X of a forest of children")
print("=" * 70)
print("For a forest of children C1, C2, ..., Cm of a node:")
print("The Dyck word of the forest is (C1)(C2)...(Cm)")
print()
print("X(forest) = X((C1)) ++ X((C2)) ++ ... ++ X((Cm))")
print("         = pair_seq([1]++X(C1)) ++ pair_seq([1]++X(C2)) ++ ...")
print()
print("But X(Ci) starts with lc(Ci). So:")
print("  If lc(Ci) >= 2: X((Ci)) = [lc(Ci), X_tail(Ci)]")
print("  If lc(Ci) == 1: X((Ci)) = pair_seq of [1, 1, X_tail(Ci)]")
print("      = [2, X_R_tail(Ci)]  where X_R_tail(Ci) = pair_seq(X_tail(Ci))")
print()
print("This means X(forest) can have 1's only at specific positions,")
print("and the pair_seq compression across sibling boundaries needs careful handling.")
print()

print("=" * 70)
print("CANDIDATE 10: Dynamic programming on tree shapes directly")
print("=" * 70)
print("Since we can enumerate all subtrees of size ≤ 7 and compute their")
print("(bobw, kw) pairs, we can do a bottom-up tree DP:")
print()
print("G[n] = answer for size n, considering all possible tree shapes.")
print()
print("For a root with m children, sizes s1,...,sm summing to n-1:")
print("  The contribution = Σ over all assignments of children of sizes s_i,")
print("  each child's subtree provides (bobw_i, kw_i, size_i=s_i+1)")
print("  bob(T) = Σ_i bobw_i + Σ_{i<j} kw_i * size_j")
print()
print("The challenge: we need to enumerate all subtrees of size k.")
print("But the number of distinct (bobw, kw) pairs per size may be SMALLER")
print("than the Catalan number!")
print()

print("Distinct (bobw, kw) counts per size in the wrapping catalog:")
from collections import Counter
for sz in range(1, N+1):
    entries = subtree_catalog[sz]
    pairs = Counter((e['bobw'], e['kw']) for e in entries)
    catalan = len(entries)
    print(f"  size={sz}: Catalan={catalan:5d}  distinct (bobw,kw)={len(pairs):3d}  "
          f"distinct (bob,k)={len(Counter((e['bob'], e['k']) for e in entries)):3d}")

print()
print("KEY QUESTION: Is the number of distinct (bobw, kw) pairs polynomial in n?")
print("If yes, we can do DP over (bobw, kw) pairs instead of over all trees!")
