import sys
sys.path.insert(0, r'd:\2024备份和迁移\2024备份和迁移\f复旭文件\h彗星计划相关\其他资料\V6_wida_case\task1')
from verify_bf import generate_dyck, alice_of, x_seq_and_bob
from collections import Counter

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
print("SIGNATURE COUNTS per size")
print("="*70)

for n in range(1, N+1):
    data_n = [t for t in all_trees if t['n'] == n]
    sig4 = Counter()
    sig5 = Counter()
    for t in data_n:
        Xw = t['Xw']
        f = Xw[0] if Xw else 0
        l = Xw[-1] if Xw else 0
        sig4[(t['bobw'], t['kw'], f, l)] += 1
        sig5[(t['bobw'], t['kw'], f, l, t['x1'])] += 1
    print(f"  n={n}: C={len(data_n):4d}  sig4={len(sig4):3d}  sig5={len(sig5):3d}  "
          f"(bobw,kw)={len(set((t['bobw'],t['kw']) for t in data_n))}")

print()
print("="*70)
print("CONCAT FORMULA VERIFICATION: X(PQ) = X(P) ++ X(Q)")
print("="*70)

for n in range(2, N+1):
    data_n = [t for t in all_trees if t['n'] == n]
    ok_n = 0
    for t in data_n:
        s = t['s']
        n_pairs = len(s)//2

        nodes = [{'parent': -1, 'children': []}]
        cur = 0
        open_positions = {}
        pair_end = {}
        stack = []
        for ci, ch in enumerate(s):
            if ch == '(':
                child = len(nodes)
                nodes.append({'parent': cur, 'children': []})
                nodes[cur]['children'].append(child)
                cur = child
                stack.append(ci)
            else:
                start = stack.pop()
                pair_end[start] = ci
                cur = nodes[cur]['parent']

        def sz(v):
            s_val = 1
            for c in nodes[v]['children']:
                s_val += sz(c)
            return s_val

        children = nodes[0]['children']
        child_x_list = []
        child_sizes = []
        pos = 0
        for c in children:
            c_sz = sz(c)
            child_sizes.append(c_sz)
            c_word = s[pos:pos+2*c_sz]
            c_X, _ = x_seq_and_bob(c_word)
            child_x_list.append(c_X)
            pos += 2*c_sz

        concat_X = sum(child_x_list, [])

        if concat_X == t['X']:
            ok_n += 1
        elif ok_n == 0:
            print(f"  FAIL n={n}: {s}")
            print(f"    child words: {[s[p:p+2*sz(c)] for p,c in zip([0]+[sum(child_sizes[:i])*2 for i in range(1,len(children))], children)]}")
            print(f"    child X: {child_x_list}")
            print(f"    concat X: {concat_X}, true X: {t['X']}")

    print(f"  n={n}: {ok_n}/{len(data_n)} OK")

print()
print("="*70)
print("CONCAT BOB VERIFICATION: bob(PQ) = bob(P) + bob(Q) + k(P)·|Q|")
print("="*70)

for n in range(2, N+1):
    data_n = [t for t in all_trees if t['n'] == n]
    ok_n = 0
    for t in data_n:
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

        children = nodes[0]['children']
        pos = 0
        bob_calc = 0
        k_calc = 0
        for c in children:
            c_sz = sz(c)
            c_word = s[pos:pos+2*c_sz]
            c_X, c_bob = x_seq_and_bob(c_word)
            c_k = len(c_X)
            bob_calc += c_bob + k_calc * c_sz
            k_calc += c_k
            pos += 2*c_sz

        if bob_calc == t['bob'] and k_calc == t['k']:
            ok_n += 1
        elif ok_n == 0 and n <= 4:
            print(f"  FAIL n={n}: {s} bob_calc={bob_calc} true={t['bob']} k_calc={k_calc} true={t['k']}")

    print(f"  n={n}: bob concat {ok_n}/{len(data_n)} OK")
