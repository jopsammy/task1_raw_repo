import sys
sys.path.insert(0, r'd:\2024备份和迁移\2024备份和迁移\f复旭文件\h彗星计划相关\其他资料\V6_wida_case\task1')
from verify_bf import generate_dyck, alice_of, x_seq_and_bob
from collections import defaultdict, Counter

def pair_seq(seq):
    r = []; i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq):
            r.append(1+seq[i+1]); i += 2
        else: r.append(seq[i]); i += 1
    return r

N = 8

all_trees = []
for n in range(1, N+1):
    for s in generate_dyck(n):
        X, bob = x_seq_and_bob(s)
        Xw = pair_seq([1] + X)
        bobw = sum(j * Xw[j] for j in range(len(Xw)))
        kw = len(Xw)
        all_trees.append({
            's': s, 'n': n, 'bob': bob, 'k': len(X), 'x1': X[0],
            'bobw': bobw, 'kw': kw, 'X': list(X), 'Xw': list(Xw)
        })

print("="*70)
print("SIGNATURE ANALYSIS: distinct (bobw, kw, first, last) per size")
print("="*70)

for n in range(1, N+1):
    data_n = [t for t in all_trees if t['n'] == n]
    sigs = Counter()
    for t in data_n:
        Xw = t['Xw']
        first = Xw[0] if Xw else 0
        last = Xw[-1] if Xw else 0
        sigs[(t['bobw'], t['kw'], first, last)] += 1
    print(f"  n={n}: Catalan={len(data_n):5d}  distinct sigs={len(sigs):3d}  "
          f"distinct (bobw,kw)={len(set((t['bobw'],t['kw']) for t in data_n))}")

print()
print("="*70)
print("SIGNATURE 5-PARAM: (bobw, kw, first, last, x1)")
print("="*70)

for n in range(1, N+1):
    data_n = [t for t in all_trees if t['n'] == n]
    sigs = Counter()
    for t in data_n:
        Xw = t['Xw']
        first = Xw[0] if Xw else 0
        last = Xw[-1] if Xw else 0
        sigs[(t['bobw'], t['kw'], first, last, t['x1'])] += 1
    print(f"  n={n}: Catalan={len(data_n):5d}  distinct 5-sigs={len(sigs):3d}")

print()
print("="*70)
print("KEY: Can we build wrapped signatures from concatenation?")
print("="*70)
print("Given wrapped child signatures (bobw_i, kw_i, first_i, last_i, size_i),")
print("we want to compute the wrapping signature of their concatenation.")
print()

def concat_signatures(child_sigs):
    """
    child_sigs: list of (bobw, kw, first, last, size, full_Xw)
    Returns: (bob, k, first, last) for the RAW concat of children's Xw
    (This is X(T) for non-primitive T)
    """
    if not child_sigs:
        return 0, 0, 0, 0

    bob_total = 0
    k_total = 0
    cumul_size = 0

    for bobw_i, kw_i, first_i, last_i, size_i, _ in child_sigs:
        bob_total += bobw_i + kw_i * cumul_size
        k_total += kw_i
        cumul_size += size_i

    first = child_sigs[0][2]
    last = child_sigs[-1][3]
    return bob_total, k_total, first, last

print("Testing concat of wrapped children signatures:")

total_ok = 0
total_fail = 0
for n in range(2, N+1):
    data_n = [t for t in all_trees if t['n'] == n]
    ok_n = 0
    for t in data_n:
        s = t['s']
        nodes = [{'parent': -1, 'children': [], 'idx': 0}]
        cur = 0
        for ch in s:
            if ch == '(':
                child = len(nodes)
                nodes.append({'parent': cur, 'children': [], 'idx': child})
                nodes[cur]['children'].append(child)
                cur = child
            else:
                cur = nodes[cur]['parent']

        def compute_sz(v):
            s_val = 1
            for c in nodes[v]['children']:
                s_val += compute_sz(c)
            return s_val
        sz = {}
        for v in range(len(nodes)):
            sz[v] = compute_sz(v)

        children = nodes[0]['children']
        child_sigs = []
        pos = 0
        for c in children:
            c_sz = sz[c]
            c_word = s[pos:pos+2*(c_sz+1)]
            c_X, _ = x_seq_and_bob(c_word)
            c_Xw = pair_seq([1] + c_X)
            c_bobw = sum(j * c_Xw[j] for j in range(len(c_Xw)))
            c_kw = len(c_Xw)
            c_first = c_Xw[0] if c_Xw else 0
            c_last = c_Xw[-1] if c_Xw else 0
            child_sigs.append((c_bobw, c_kw, c_first, c_last, c_sz+1, c_Xw))
            pos += 2*(c_sz+1)

        bob_c, k_c, first_c, last_c = concat_signatures(child_sigs)

        if bob_c == t['bob'] and k_c == t['k']:
            ok_n += 1
        else:
            if total_fail < 3:
                print(f"  FAIL n={n}: {s}")
                print(f"    children Xw: {[cs[5] for cs in child_sigs]}")
                print(f"    concat computed: bob={bob_c} k={k_c}, true: bob={t['bob']} k={t['k']}")

    total_ok += ok_n
    total_fail += len(data_n) - ok_n
    print(f"  n={n}: {ok_n}/{len(data_n)} passed")

print(f"\nConcat TOTAL: {total_ok} ok, {total_fail} fail")

print()
print("="*70)
print("CRITICAL: If concat works, then NON-PRIMITIVE tree wrapping is solved")
print("For non-primitive T = T1·T2·...·Tm:")
print("  X(T) = Xw(T1) ++ Xw(T2) ++ ... ++ Xw(Tm)  --- concat works!")
print("  X((T)) = pair_seq([1] ++ X(T))")
print()
print("For PRIMITIVE T = root[C1,...,Cm]:")
print("  X(T) = ???  --- THIS IS THE HARD PART")
print("  But X((T)) = pair_seq([1] ++ X(T))  --- once we have X(T), wrapping works")
print()
print("Maybe we can compute X(T) for primitive T from children's Xw using")
print("the same concat formula, if we treat the root's '(' differently?")
print("X(T) for primitive T ~= X(F) but with first element incremented by 1?")
print()

print("Testing: X(T) = [1 + X(F)[0]] ++ X(F)[1:] for primitive T")
print("where X(F) = Xw(C1) ++ Xw(C2) ++ ... ++ Xw(Cm)")

for n in range(2, min(N+1, 7)):
    data_n = [t for t in all_trees if t['n'] == n]
    ok_n = 0
    for t in data_n:
        s = t['s']
        if s[0] != '(': 
            continue
        if s.count('(') != s.count(')'):
            continue

        nodes = [{'parent': -1, 'children': [], 'idx': 0}]
        cur = 0
        for ch in s:
            if ch == '(':
                child = len(nodes)
                nodes.append({'parent': cur, 'children': [], 'idx': child})
                nodes[cur]['children'].append(child)
                cur = child
            else:
                cur = nodes[cur]['parent']

        def compute_sz(v):
            s_val = 1
            for c in nodes[v]['children']:
                s_val += compute_sz(c)
            return s_val
        sz = {}
        for v in range(len(nodes)):
            sz[v] = compute_sz(v)

        if len(nodes[0]['children']) == 1:
            is_primitive = True
            root_node = nodes[0]['children'][0]
        else:
            is_primitive = False
            root_node = 0

        if not is_primitive:
            continue

        children = nodes[root_node]['children']
        child_sigs = []
        pos = 1
        for c in children:
            c_sz = sz[c]
            c_word = s[pos:pos+2*(c_sz+1)]
            c_X, _ = x_seq_and_bob(c_word)
            c_Xw = pair_seq([1] + c_X)
            c_bobw = sum(j * c_Xw[j] for j in range(len(c_Xw)))
            c_kw = len(c_Xw)
            c_first = c_Xw[0] if c_Xw else 0
            c_last = c_Xw[-1] if c_Xw else 0
            child_sigs.append((c_bobw, c_kw, c_first, c_last, c_sz+1, c_Xw))
            pos += 2*(c_sz+1)

        forest_bob, forest_k, forest_first, forest_last = concat_signatures(child_sigs)
        
        if child_sigs:
            computed_XT_first = 1 + child_sigs[0][4][0] if child_sigs[0][4] else 1
        else:
            computed_XT_first = 1

        if t['X'][0] == computed_XT_first:
            ok_n += 1
        else:
            pass

    data_n_prim = [t for t in data_n if len(nodes[0]['children']) == 1]
    print(f"  n={n} primitive trees: x1 prediction test done (see above)")
