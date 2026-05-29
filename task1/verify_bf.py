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
    l = 0
    X = []
    while l < n:
        pos = 2*l
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
        l += best_x
    bob = 0
    for j in range(len(X)):
        bob += j * X[j]
    return X, bob

def k_of(X):
    return len(X)

def solve_brute(N, a_val, b_val):
    res = []
    for n in range(1, N+1):
        words = generate_dyck(n)
        total = 0
        for s in words:
            alice = alice_of(s)
            X, bob = x_seq_and_bob(s)
            total = (total + pow(a_val, alice, MOD) * pow(b_val, bob, MOD)) % MOD
        res.append(total)
    return res

def verify(N, a_val, b_val):
    print(f"N={N}, a={a_val}, b={b_val}")
    brute = solve_brute(N, a_val, b_val)
    print(f"Brute-force: {brute}")

    import solution
    dp = list(map(int, solution.solve(N, a_val, b_val)))
    print(f"DP:          {dp}")

    match = all(b == d for b, d in zip(brute, dp))
    print(f"Match: {match}")
    if not match:
        for i, (b, d) in enumerate(zip(brute, dp)):
            if b != d:
                print(f"  n={i+1}: brute={b}, dp={d}")
    return match

if __name__ == '__main__':
    if len(sys.argv) >= 4:
        N, a, b = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
        verify(N, a, b)
    else:
        for N in range(3, 7):
            ok = verify(N, 2, 3)
            if not ok:
                print(f"FAIL at N={N}")
                break
