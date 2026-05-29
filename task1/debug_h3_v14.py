# Quick debug: trace H[3] primitive c=0
MOD = 998244353

def dyck_from_xseq(X):
    s = ''
    for xx in X:
        s += '(' * xx + ')' * xx
    return s

def x_seq_and_bob(s):
    n = len(s)//2
    h = [0]*(2*n+1)
    for i in range(2*n): h[i+1] = h[i] + (1 if s[i]=='(' else -1)
    l = 0; X = []
    while l < n:
        pos = 2*l; t = 1; best_x = 0
        while pos + t <= 2*n:
            if h[pos + t] == t: best_x = t; t += 1
            elif h[pos + t] > t: t += 1
            else: break
        if best_x == 0: best_x = 1
        X.append(best_x); l += best_x
    return X, sum(j*X[j] for j in range(len(X)))

def compute_XwT_real(x_seq_T):
    s_T = dyck_from_xseq(x_seq_T)
    T_wrapped = '(' + s_T + ')'
    X_real, _ = x_seq_and_bob(T_wrapped)
    return tuple(X_real)

# H[2] entry for '()' wrapped: X(`(())`)
# T = `()`, X(T)=[1], t1=1
# X((T)) = x_seq of `(())` = [2]
xs_T = (2,)  # X((`()`)) = [2]
print("H[2] c_flag=1 all1 entry: xseq=%s" % (xs_T,))

# H[3] primitive c=0: s_T=2 (k=3, k-1=2)
# For T=`()`, we'd need T in D_2. But `()` is in D_1, not D_2.
# Hmm, actually T ∈ D_{k-1} = D_2. T=`()` is not in D_2.

# The H[2] entry represents A=`()`? No, H[2] entries represent words A ∈ D_2.
# A=`(())` ∈ D_2: X(A)=[2], X((A))=[3]. bw=0,kw=1,c_flag=0.
# A=`()()` ∈ D_2: X(A)=[1,1], X((A))=[2,1]. bw=1,kw=2,c_flag=1.

# So for H[3] primitive c=0, T ∈ D_2:
# T=`(())`: H[2] xseq = X((T)) = [3]. t1 = x₁(T) = 2.
# T=`()()`: H[2] xseq = X((T)) = [2,1]. t1 = x₁(T) = 1.

# For T=`(())`: xs=(3,), t1=2
xs = (3,)
t1 = 2
print("\nT=`(())`: xs=%s, t1=%d, t1+1=%d, xs[0]=%d match=%s" % (xs, t1, t1+1, xs[0], xs[0]==t1+1))
if xs[0] == t1 + 1:
    Xw = compute_XwT_real(xs)
    print("  compute_XwT_real(%s) = %s" % (xs, Xw))
    print("  Xw_list=%s, bw=%d, kw=%d" % (list(Xw), sum(j*list(Xw)[j] for j in range(len(Xw))), len(Xw)))

# For T=`()()`: xs=(2,1), t1=1
xs2 = (2,1)
t12 = 1
print("\nT=`()()`: xs=%s, t1=%d, t1+1=%d, xs[0]=%d match=%s" % (xs2, t12, t12+1, xs2[0], xs2[0]==t12+1))
if xs2[0] == t12 + 1:
    Xw2 = compute_XwT_real(xs2)
    print("  compute_XwT_real(%s) = %s" % (xs2, Xw2))
    print("  Xw_list=%s, bw=%d, kw=%d" % (list(Xw2), sum(j*list(Xw2)[j] for j in range(len(Xw2))), len(Xw2)))
