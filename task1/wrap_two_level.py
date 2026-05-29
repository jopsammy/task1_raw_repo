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

def wrap_boundary(blocks):
    """pair_seq([1] + concat(blocks)). Blocks are raw x-sequences."""
    if not blocks:
        return [2]
    assembled = [1 + blocks[0][0]]
    for i in range(len(blocks)):
        seq = list(blocks[i])
        if i == 0:
            seq = seq[1:]
        if i > 0 and assembled and assembled[-1] == 1:
            assembled[-1] = 1 + seq[0]
            seq = seq[1:]
        assembled.extend(seq)
    return pair_seq(assembled)

def compute_xw_from_forest(blocks, is_primitive):
    """
    blocks: X(P_i) for children of root (x-seq of primitives).
    For non-primitive T: X(T) = concat(blocks), X((T)) = wrap_boundary(blocks).
    For primitive T: X(T) = wrap_boundary(blocks), X((T)) = pair_seq([1] + X(T)).
    """
    if is_primitive:
        x_t = wrap_boundary(blocks)
        xw_t = pair_seq([1] + x_t)
    else:
        x_t = sum(blocks, [])
        xw_t = wrap_boundary(blocks)
    return xw_t

N = 8

all_trees = []
for n in range(1, N+1):
    for s in generate_dyck(n):
        X, bob = x_seq_and_bob(s)
        Xw = pair_seq([1] + X)
        all_trees.append({'s': s, 'n': n, 'X': list(X), 'Xw': list(Xw)})

total_ok = 0
total_fail = 0

for t in all_trees:
    s = t['s']
    nodes = [{'parent': -1, 'children': []}]
    cur = 0
    for ch in s:
        if ch == '(':
            child = len(nodes)
            nodes.append({'parent': cur, 'children': []})
            nodes[cur]['children'].append(child)
            cur = child
        else:
            cur = nodes[cur]['parent']

    def sz(v):
        s_val = 1
        for c in nodes[v]['children']:
            s_val += sz(c)
        return s_val

    root_children = nodes[0]['children']
    is_primitive = (len(root_children) == 1)

    blocks = []
    pos = 0

    if is_primitive:
        root_node = root_children[0]
        inner_children = nodes[root_node]['children']
        pos = 1  # skip root's '('
        for c in inner_children:
            c_sz = sz(c)
            inner_sz = c_sz - 1
            inner_word = s[pos+1:pos+1+2*inner_sz] if inner_sz > 0 else ''
            inner_X, _ = x_seq_and_bob(inner_word)
            X_P = pair_seq([1] + inner_X)
            blocks.append(X_P)
            pos += 2 * c_sz
    else:
        for c in root_children:
            c_sz = sz(c)
            inner_sz = c_sz - 1
            inner_word = s[pos+1:pos+1+2*inner_sz] if inner_sz > 0 else ''
            inner_X, _ = x_seq_and_bob(inner_word)
            X_P = pair_seq([1] + inner_X)
            blocks.append(X_P)
            pos += 2 * c_sz

    our_Xw = compute_xw_from_forest(blocks, is_primitive)
    gt_Xw = t['Xw']

    if our_Xw == gt_Xw:
        total_ok += 1
    elif total_fail < 10:
        print(f"  FAIL: {s} (primitive={is_primitive})")
        print(f"    blocks={blocks}")
        print(f"    GT={gt_Xw}, Our={our_Xw}")
    total_fail += (0 if our_Xw == gt_Xw else 1)

print(f"\nTOTAL: {total_ok} ok, {total_fail} fail out of {total_ok+total_fail}")
