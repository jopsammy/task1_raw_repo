# Verification: concat decomposition for bob and alice
# Check that for all Dyck words s = p1 p2 (p1 primitive):
# alice(s) = alice(p1) + alice(p2) + |p1| * |p2|
# bob(s) = bob(p1) + bob(p2) + k1 * |p2|
# x-seq(s) = x-seq(p1) ++ x-seq(p2)  (concatenation)

def gen_dyck(n):
    res = []
    def dfs(o, c, s):
        if len(s) == 2 * n:
            res.append(s)
            return
        if o < n:
            dfs(o + 1, c, s + '(')
        if c < o:
            dfs(o, c + 1, s + ')')
    dfs(0, 0, '')
    return res

def alice(s):
    ans = 0
    for i, ci in enumerate(s):
        if ci == '(':
            for j in range(i + 1, len(s)):
                if s[j] == ')':
                    ans += 1
    return ans

def x_seq(s):
    n = len(s) // 2
    l = 0
    xs = []
    while l < n:
        best = 0
        for x in range(1, n - l + 1):
            if s[:2*l+x].count('(') == l + x:
                best = x
        xs.append(best)
        l += best
    return xs

def bob(s):
    xs = x_seq(s)
    return sum((j - 1) * x for j, x in enumerate(xs, 1))

def is_primitive(s):
    bal = 0
    for i, c in enumerate(s):
        bal += 1 if c == '(' else -1
        if bal == 0 and i < len(s) - 1:
            return False
    return True

def test_concat(n):
    words = gen_dyck(n)
    all_ok = True
    for s in words:
        if is_primitive(s):
            continue
        # find first primitive prefix
        bal = 0
        for i, c in enumerate(s):
            bal += 1 if c == '(' else -1
            if bal == 0:
                p1 = s[:i+1]
                p2 = s[i+1:]
                break
        n1 = len(p1) // 2
        n2 = len(p2) // 2
        k1 = len(x_seq(p1))

        a1 = alice(p1)
        a2 = alice(p2)
        b1 = bob(p1)
        b2 = bob(p2)

        pred_alice = a1 + a2 + n1 * n2
        pred_bob = b1 + b2 + k1 * n2

        actual_alice = alice(s)
        actual_bob = bob(s)

        ok = (pred_alice == actual_alice and pred_bob == actual_bob)
        if not ok:
            print(f"FAIL: s={s}, p1={p1}, p2={p2}")
            print(f"  alice: pred={pred_alice}, actual={actual_alice}")
            print(f"  bob:   pred={pred_bob}, actual={actual_bob}")
            all_ok = False
    return all_ok

for n in range(1, 9):
    ok = test_concat(n)
    print(f"n={n}: {'PASS' if ok else 'FAIL'}")