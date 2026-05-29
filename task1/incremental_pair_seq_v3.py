import sys
sys.path.insert(0, r'd:\2024备份和迁移\2024备份和迁移\f复旭文件\h彗星计划相关\其他资料\V6_wida_case\task1')
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

def pair_seq(seq):
    r = []; i = 0
    while i < len(seq):
        if seq[i] == 1 and i + 1 < len(seq):
            r.append(1+seq[i+1]); i += 2
        else: r.append(seq[i]); i += 1
    return r

def pair_seq_boundary(blocks):
    """
    blocks: list of sequences that are already pair_seq-compressed (no internal (1,v) merges, no consecutive 1s)
    Returns: pair_seq on the concatenation of blocks
    """
    result = []
    pending_1 = False
    for blk in blocks:
        s = list(blk)
        if pending_1 and s:
            result[-1] = 1 + s[0]
            s = s[1:]
            pending_1 = False
        if pending_1:
            result.append(1)
            pending_1 = False
        result.extend(s)
        if s and s[-1] == 1:
            pending_1 = True
            result.pop()
        else:
            pending_1 = False
    if pending_1:
        result.append(1)
    return result

def compute_wrapping_from_children(child_xws):
    """
    child_xws: list of Xw(C_i) sequences for children C_1..C_m
    Each Xw(C_i) = pair_seq([1]+X(C_i)) is already compressed.
    Returns (Xw(T), bobw, kw, first, last) for X((T))
    where T = root[C_1,...,C_m]
    """
    if not child_xws:
        return [2], 0, 1, 2, 2

    first_child_seq = child_xws[0]

    result = [2 + first_child_seq[0]]

    remaining_blocks = [first_child_seq[1:]] + child_xws[1:]
    remaining_blocks = [b for b in remaining_blocks if b]

    tail = pair_seq_boundary(remaining_blocks)
    result.extend(tail)

    bobw = sum(j * result[j] for j in range(len(result)))
    kw = len(result)
    first = result[0]
    last = result[-1]
    return result, bobw, kw, first, last

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
print("CORRECTED DECOMPOSITION: X(T) = [1+X(F)[0], X(F)[1:], ...]")
print("where X(F) = concat of children's Xw")
print("and X((T)) = pair_seq([1, 1+X(F)[0], X(F)[1:], ...])")
print("="*70)

total_pass = 0
total_fail = 0
for n in range(1, N+1):
    data_n = [t for t in all_trees if t['n'] == n]
    pass_n = 0
    fail_examples = []
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

        children = nodes[1]['children']
        child_xws = []
        pos = 1
        for c in children:
            c_sz = sz[c]
            c_word = s[pos:pos+2*(c_sz+1)]
            c_X, _ = x_seq_and_bob(c_word)
            c_Xw = pair_seq([1] + c_X)
            child_xws.append(c_Xw)
            pos += 2*(c_sz+1)

        _, bobw_c, kw_c, _, _ = compute_wrapping_from_children(child_xws)

        if bobw_c == t['bobw'] and kw_c == t['kw']:
            pass_n += 1
        else:
            if len(fail_examples) < 3:
                fail_examples.append((s, t['X'], t['Xw'], child_xws, bobw_c, kw_c, t['bobw'], t['kw']))

    for s, X, Xw, c_xws, bc, kc, bt, kt in fail_examples:
        print(f"  FAIL n={n}: {s}")
        print(f"    X={X}, Xw_true={Xw}")
        print(f"    children Xw: {c_xws}")
        print(f"    computed: bobw={bc} kw={kc}, true: bobw={bt} kw={kt}")

    print(f"  n={n}: {pass_n}/{len(data_n)} passed")
    total_pass += pass_n
    total_fail += len(data_n) - pass_n

print(f"\nTOTAL: {total_pass} passed, {total_fail} failed out of {total_pass+total_fail}")
