import sys

MOD = 998244353

def generate_dyck(n):
    words = []
    def bt(s, op, cl):
        if cl > op or op > n:
            return
        if len(s) == 2*n:
            if op == n and cl == n:
                words.append(s)
            return
        bt(s + '(', op+1, cl)
        bt(s + ')', op, cl+1)
    bt('', 0, 0)
    return words

def alice_of(s):
    n = len(s)//2
    cnt = 0
    for i in range(2*n):
        if s[i] == '(':
            for j in range(i+1, 2*n):
                if s[j] == ')':
                    cnt += 1
    return cnt

def x_seq_and_bob(s):
    n = len(s)//2
    h = [0]*(2*n+1)
    for i in range(2*n):
        h[i+1] = h[i] + (1 if s[i]=='(' else -1)
    L = 0
    X = []
    while L < n:
        pos = 2*L
        t = 1
        best_x = 0
        while pos + t <= 2*n:
            if h[pos + t] == t:
                best_x = t
                t += 1
            elif h[pos + t] > t:
                t += 1
            else:
                break
        if best_x == 0:
            best_x = 1
        X.append(best_x)
        L += best_x
    bob = 0
    for j in range(len(X)):
        bob += j * X[j]
    return X, bob

def primitive_decompose(s):
    """Split s at height=0 returns into primitive blocks."""
    n = len(s)//2
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

def verify_route_i(max_n=8):
    print("=" * 70)
    print("ROUTE I PROBE: x-seq decomposition data verification")
    print("=" * 70)

    all_dyck = {}
    for n in range(1, max_n+1):
        all_dyck[n] = generate_dyck(n)

    total_trees = sum(len(v) for v in all_dyck.values())
    print(f"\nTotal Dyck words (n=1..{max_n}): {total_trees}")

    print("\n" + "=" * 70)
    print("TEST 1: x-seq vs primitive block sizes")
    print("  Claim: x_j = size of j-th primitive block at height 0")
    print("=" * 70)

    xseq_eq_prim = 0
    xseq_neq_prim = 0
    xseq_neq_examples = []

    for n in range(1, max_n+1):
        for s in all_dyck[n]:
            X, bob = x_seq_and_bob(s)
            blocks = primitive_decompose(s)
            block_sizes = [len(b)//2 for b in blocks]

            if len(X) == len(block_sizes) and all(x == b for x, b in zip(X, block_sizes)):
                xseq_eq_prim += 1
            else:
                xseq_neq_prim += 1
                if len(xseq_neq_examples) < 15:
                    xseq_neq_examples.append((s, X, block_sizes))

    print(f"  Equal: {xseq_eq_prim}/{total_trees} (x-seq == primitive block sizes)")
    print(f"  NOT equal: {xseq_neq_prim}/{total_trees}")
    if xseq_neq_examples:
        print("  Counterexamples (first 15):")
        for s, X, bs in xseq_neq_examples:
            print(f"    s={s:16s}  X={str(X):12s}  prim_sizes={bs}")

    print("\n" + "=" * 70)
    print("TEST 2: bob = Σ(j-1)·x_j  (definitional, should always pass)")
    print("=" * 70)
    bob_ok = 0
    bob_fail = 0
    for n in range(1, max_n+1):
        for s in all_dyck[n]:
            X, bob = x_seq_and_bob(s)
            bob_formula = sum((j)*x for j, x in enumerate(X))
            if bob == bob_formula:
                bob_ok += 1
            else:
                bob_fail += 1
    print(f"  Pass: {bob_ok}/{total_trees}  Fail: {bob_fail}")

    print("\n" + "=" * 70)
    print("TEST 3: alice concat formula for primitive decomposition")
    print("  alice(s) = Σ alice(Pⱼ) + Σ_{i<j} |Pᵢ|·|Pⱼ|")
    print("=" * 70)
    alice_ok = 0
    alice_fail = 0
    for n in range(1, max_n+1):
        for s in all_dyck[n]:
            alice_s = alice_of(s)
            blocks = primitive_decompose(s)
            block_sizes = [len(b)//2 for b in blocks]

            alice_internal = sum(alice_of(b) for b in blocks)
            alice_cross = 0
            for i in range(len(blocks)):
                for j in range(i+1, len(blocks)):
                    alice_cross += block_sizes[i] * block_sizes[j]
            alice_formula = alice_internal + alice_cross

            if alice_s == alice_formula:
                alice_ok += 1
            else:
                alice_fail += 1
    print(f"  Pass: {alice_ok}/{total_trees}  Fail: {alice_fail}")

    print("\n" + "=" * 70)
    print("TEST 4: alice(s) expressed via x-seq decomposition")
    print("  Claim: s = (Q₁)(Q₂)...(Qₖ) where |Qⱼ| = xⱼ-1")
    print("  alice((Qⱼ)) = alice(Qⱼ) + 2xⱼ-1")
    print("  alice(s) = Σ alice((Qⱼ)) + Σ_{i<j} xᵢ·xⱼ")
    print("=" * 70)

    alice_xseq_ok = 0
    alice_xseq_fail = 0
    alice_xseq_examples = []

    for n in range(1, max_n+1):
        for s in all_dyck[n]:
            X, bob = x_seq_and_bob(s)
            k = len(X)

            bob_check = sum((j - 1) * x for j, x in zip(range(1, k+1), X))
            if bob != bob_check:
                continue

            blocks = primitive_decompose(s)
            alice_s = alice_of(s)

            alice_via_xseq = 0
            for j, (xj, Pj) in enumerate(zip(X, blocks)):
                alice_Pj = alice_of(Pj)
                alice_via_xseq += alice_Pj + 2*xj - 1

            for i in range(k):
                for j in range(i+1, k):
                    alice_via_xseq += X[i] * X[j]

            if alice_s == alice_via_xseq:
                alice_xseq_ok += 1
            else:
                alice_xseq_fail += 1
                if len(alice_xseq_examples) < 10:
                    alice_xseq_examples.append((s, X, blocks, alice_s, alice_via_xseq))

    print(f"  Pass: {alice_xseq_ok}/{total_trees}  Fail: {alice_xseq_fail}")

    print("\n" + "=" * 70)
    print("TEST 5: Wrapping doesn't change bob for primitive blocks")
    print("  For each primitive Dyck word P: bob((P)) == bob(P)?")
    print("  Actually: (P) has x-seq [1+|P|] → bob((P)) = 0 (single block)")
    print("  While bob(P) may be nonzero.")
    print("  So the claim 'wrapping不改变bob' needs reinterpretation...")
    print("=" * 70)
    print("  Let's check: for primitive P, what is bob((P))?")
    prim_counter = 0
    bob_change_counter = 0
    for n in range(1, max_n+1):
        for s in all_dyck[n]:
            blocks = primitive_decompose(s)
            if len(blocks) > 1:
                continue
            prim_counter += 1
            X_raw, bob_raw = x_seq_and_bob(s)
            wrapped = '(' + s + ')'
            X_w, bob_w = x_seq_and_bob(wrapped)
            if bob_raw != bob_w:
                bob_change_counter += 1
    print(f"  Primitive words: {prim_counter}")
    print(f"  bob changes after wrapping: {bob_change_counter}")
    print(f"  bob unchanged: {prim_counter - bob_change_counter}")
    if bob_change_counter > 0:
        print("  This means wrapping DOES change bob for primitive blocks.")
        print("  Need to rethink Route I claims.")

    print("\n" + "=" * 70)
    print("TEST 5b: What IS the relationship between bob(P) and bob((P))?")
    print("=" * 70)
    for n in range(1, 5):
        for s in all_dyck[n]:
            blocks = primitive_decompose(s)
            if len(blocks) > 1:
                continue
            X_raw, bob_raw = x_seq_and_bob(s)
            wrapped = '(' + s + ')'
            X_w, bob_w = x_seq_and_bob(wrapped)
            print(f"  s={s:16s}  X={str(X_raw):12s}  bob(P)={bob_raw}  X((P))={str(X_w):12s}  bob((P))={bob_w}")

    print("\n" + "=" * 70)
    print("TEST 6: x-seq decomposition via return-to-height-0 blocks")
    print("  For each Dyck word, find the blocks where x-seq values \"consume\"")
    print("  the word. What substrings correspond to each x_j?")
    print("=" * 70)

    for n in range(1, 5):
        for s in all_dyck[n]:
            X, bob = x_seq_and_bob(s)
            L = 0
            substrings = []
            for xj in X:
                substrings.append(s[2*L : 2*(L+xj)])
                L += xj
            blocks = primitive_decompose(s)
            if X != [len(b)//2 for b in blocks]:
                print(f"  s={s:16s}  X={str(X):12s}  substrings={substrings}  prim_blocks={blocks}")

    print("\n" + "=" * 70)
    print("TEST 7: Structural analysis — what IS the x-seq decomposition?")
    print("  For each Dyck word s:")
    print("  - x-seq X = [x₁,...,xₖ]")
    print("  - Each xⱼ corresponds to a substring s[2ℓ:2(ℓ+xⱼ)]")
    print("  - Is each such substring a wrapped Dyck word (i.e., a primitive)?")
    print("  - If yes, bob can be expressed purely in terms of block sizes")
    print("=" * 70)

    is_wrapped = 0
    is_not_wrapped = 0
    not_wrapped_examples = []

    for n in range(1, max_n+1):
        for s in all_dyck[n]:
            X, bob = x_seq_and_bob(s)
            L = 0
            all_wrapped = True
            for xj in X:
                sub = s[2*L : 2*(L+xj)]
                if not (sub.startswith('(') and sub.endswith(')')):
                    all_wrapped = False
                if len(sub) >= 2:
                    inner = sub[1:-1]
                    inner_blocks = primitive_decompose(inner) if inner else []
                L += xj

            if all_wrapped:
                is_wrapped += 1
            else:
                is_not_wrapped += 1
                if len(not_wrapped_examples) < 10:
                    not_wrapped_examples.append((s, X))

    print(f"  All x-seq blocks are wrapped (start with '(' end with ')'): {is_wrapped}/{total_trees}")
    print(f"  NOT all wrapped: {is_not_wrapped}/{total_trees}")
    if not_wrapped_examples:
        print("  Examples where blocks are NOT all wrapped:")
        for s, X in not_wrapped_examples:
            L = 0
            subs = []
            for xj in X:
                subs.append(s[2*L : 2*(L+xj)])
                L += xj
            print(f"    s={s:16s}  X={str(X):12s}  subs={subs}")

    print("\n" + "=" * 70)
    print("TEST 8: Key insight — bob in primitive decomposition vs x-seq")
    print("  For a Dyck word decomposed as primitive blocks P₁·P₂·...·Pₘ:")
    print("  - bob_prim = Σ(j-1)·|Pⱼ|")
    print("  - bob_xseq = Σ(j-1)·xⱼ")
    print("  When are these equal?")
    print("=" * 70)

    bob_eq = 0
    bob_neq = 0
    bob_neq_examples = []

    for n in range(1, max_n+1):
        for s in all_dyck[n]:
            X, bob_xseq = x_seq_and_bob(s)
            blocks = primitive_decompose(s)
            bs = [len(b)//2 for b in blocks]
            m = len(bs)
            bob_prim = sum((j-1)*bs[j-1] for j in range(1, m+1))

            if bob_xseq == bob_prim:
                bob_eq += 1
            else:
                bob_neq += 1
                if len(bob_neq_examples) < 15:
                    bob_neq_examples.append((s, X, bs, bob_xseq, bob_prim))

    print(f"  Equal: {bob_eq}/{total_trees}")
    print(f"  NOT equal: {bob_neq}/{total_trees}")
    if bob_neq_examples:
        print("  Counterexamples:")
        for s, X, bs, bxs, bpr in bob_neq_examples:
            print(f"    s={s:16s}  X={str(X):12s}  prim_sizes={str(bs):12s}  bob_x={bxs}  bob_prim={bpr}")

    print("\n" + "=" * 70)
    print("TEST 9: Can alice(s) be expressed via x-seq + per-block internals?")
    print("  s = P₁·P₂·...·Pₖ (primitive decomposition, sizes = pⱼ)")
    print("  alice(s) = Σ alice(Pⱼ) + Σ_{i<j} pᵢ·pⱼ")
    print("  Each Pⱼ is a primitive word of size pⱼ.")
    print("  Question: can we express Σ alice(Pⱼ) in terms of pⱼ ONLY?")
    print("=" * 70)

    from collections import defaultdict
    alice_by_size = defaultdict(list)
    for n in range(1, max_n+1):
        for s in all_dyck[n]:
            blocks = primitive_decompose(s)
            if len(blocks) == 1:
                alice_by_size[n].append(alice_of(s))

    print(f"  alice values for primitive words, by size:")
    for sz in sorted(alice_by_size.keys()):
        vals = alice_by_size[sz]
        print(f"    n={sz}: alice ∈ {sorted(set(vals))}  (Catalan({sz})={len(vals)} words)")

    print("\n" + "=" * 70)
    print("TEST 10: Total weight F[n] via x-seq enumeration")
    print("  F[n] = Σ_{x-seq with sum n} contribution(X)")
    print("  where contribution(X) = a^{alice(s)} · b^{bob(s)}")
    print("  summed over all Dyck words s with x-seq X")
    print("=" * 70)

    for a_val, b_val in [(2, 3), (1, 1), (3, 5)]:
        print(f"\n  --- a={a_val}, b={b_val} ---")
        for n in range(1, min(6, max_n+1)):
            all_s = all_dyck[n]
            total_brute = 0
            for s in all_s:
                alice = alice_of(s)
                X, bob = x_seq_and_bob(s)
                total_brute = (total_brute + pow(a_val, alice, MOD) * pow(b_val, bob, MOD)) % MOD
            print(f"    F[{n}] = {total_brute}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Test 1 (x-seq == prim sizes): {xseq_eq_prim}/{total_trees} equal")
    print(f"  Test 2 (bob definition): {bob_ok}/{total_trees} pass")
    print(f"  Test 3 (alice prim concat): {alice_ok}/{total_trees} pass")
    print(f"  Test 4 (alice via x-seq): {alice_xseq_ok}/{total_trees} pass")
    print(f"  Test 8 (bob_xseq == bob_prim): {bob_eq}/{total_trees} equal")
    print(f"  Test 7 (all blocks wrapped): {is_wrapped}/{total_trees}")


if __name__ == '__main__':
    max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    verify_route_i(max_n)
