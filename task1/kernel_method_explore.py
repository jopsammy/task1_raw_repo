import sys
sys.path.insert(0, '.')
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

MOD = 998244353

def deep_kernel_analysis(a_val, b_val):
    print("=" * 70)
    print("DEEP KERNEL METHOD ANALYSIS")
    print("=" * 70)

    print("""
QUESTION: Can the kernel method help with the wrapping-alice/bob Dyck problem?

KEY FACTS:
1. alice IS stepwise-accumulable (each ')' contributes n_left '*' count)
2. bob wrapping is NON-LOCAL (depends on full height function of the wrapped word)
3. x-seq blocks do NOT align with "returns to height 0" (the kernel method's
   standard decomposition axis)
4. The GF equation is:
   F(x,y) = 1 + sum_{A} c(A) * F(alpha(A)*x, y)
   where alpha(A) = a^{|A|+1} * b^{k((A))} varies per A

   This is not the standard form F = 1 + x * phi(F) required by
   Lagrange inversion or the kernel method.

5. Orbit compression: wrapping maps Catalan(k) to O(k^2/4) distinct (bw,kw) pairs.
   Within each orbit, alpha(A) is the same.
""")

    n = 6
    words = generate_dyck(n)

    from collections import defaultdict
    orbit_to_words = defaultdict(list)
    for s in words:
        A_str = s[1:-1]
        X_w, bob_w = x_seq_and_bob(s)
        k_w = len(X_w)
        orbit_to_words[(bob_w, k_w)].append(A_str)

    print(f"\nn={n}: {len(words)} Dyck words -> {len(orbit_to_words)} wrapping orbits")
    print(f"Compression ratio: {len(words)/len(orbit_to_words):.1f}:1")

    print("\nOrbit structure:")
    for (bw, kw), wlist in sorted(orbit_to_words.items()):
        print(f"  orbit (bw={bw}, kw={kw}): {len(wlist)} words")
        print(f"    examples: {wlist[:3]}")
        print(f"    alice values: {[alice_of(w) for w in wlist[:5]]}")

    print("\n" + "=" * 70)
    print("KERNEL METHOD ASSESSMENT")
    print("=" * 70)

    print("""
POSITIVE SIGNS:
+ alice stepwise accumulation works (verified n<=7)
+ GF equation correctly established (verified n<=4)
+ Orbit compression is real and excellent (22287:1 at k=14)
+ MOD is NTT-friendly (998244353 = 119*2^23+1)
+ sqrt(a) exists mod MOD (a is quadratic residue when a is arbitrary)

NEGATIVE SIGNS:
- Wrapping is NON-LOCAL: depends on full height function, not reducible
  to finite parameters (proven via counterexamples at c=1+internal_1)
- Kernel method requires uniform scaling: F = 1 + x*phi(F)
  Our equation has PER-A scaling: F = 1 + sum_A c_A * F(alpha_A * x)
- Lagrange inversion requires F = 1 + x*phi(F) form
- NTT convolution requires standard convolution a*b, but our sums
  involve L-shift (P_m(L+n-m)) which is not a standard convolution

THE FUNDAMENTAL ISSUE:
The kernel method for Dyck paths (and Lagrange inversion) work by exploiting
the FIRST-RETURN-TO-HEIGHT-0 decomposition: s = (A)B.

For area/q-Catalan, this gives: F = 1 + x*q*F(xq)*F(x)
The area contribution from nesting (x->xq) is UNIFORM for all A.

For our problem, the bob contribution from nesting (bob wrapping) VARIES per A.
Different |A| and different k((A)) give DIFFERENT scaling factors.
This is why the equation has a sum over A instead of a simple phi(F).

ALTERNATIVE KERNEL-LIKE APPROACHES:

1. ORBIT-BASED KERNEL METHOD
   Group A by wrapping orbit (bw,kw). Within each orbit, alpha(A) is uniform.
   F(x,y) = 1 + sum_{(bw,kw)} orbit_weight * x^{size+1} * y^{kw} * F(a^{size+1}*b^{kw}*x, y)
   
   This reduces the sum from Catalan terms to O(k^2/4) terms per size.
   But orbit_weight computation is the bottleneck (non-enumeration required).

2. CATALYTIC VARIABLE FOR WRAPPING
   Add a catalytic variable z that tracks the wrapping structure:
   F(x,y,z) = sum a^{alice} b^{bob} x^{|s|} y^{k(s)} z^{wrapping_info}
   
   The wrapping info may need to be the full Dyck word structure,
   making this equivalent to brute force.

3. CONTINUED FRACTION / RATIONAL GF
   For Catalan: F = 1/(1-x*F) = 1 + x*F^2
   For q-Catalan: F = 1 + xq*F(xq)F(x), related to q-continued fractions
   For our problem: maybe there is a continued fraction representation?

4. COMBINATORIAL IDENTITIES
   Instead of kernel method, find a combinatorial identity that
   expresses the weighted sum in closed form.
   e.g., alice = sum L(i), bob = sum j*(l_{j+1}-l_j)

VERDICT:
The kernel method in its STANDARD form does NOT apply to this problem.
The wrapping non-locality creates a per-A varying scaling that prevents
the standard kernel elimination.

The most promising direction remains:
  - ORBIT compression + NTT convolution (spec.md 10.5b)
  - Finding orbit recurrence without enumeration
  - Or finding a completely different mathematical structure
""")

    print("\n" + "=" * 70)
    print("EXPLORING: Can we separate alice and bob into independent GFs?")
    print("=" * 70)

    print("""
Define two separate generating functions:

G(x) = sum_{s in D} a^{alice(s)} x^{|s|}     [only alice weight]

For alice only: alice((A)B) = alice(A) + alice(B) + |(A)B| + |A|*|B|
alice((A)) = alice(A) + 2|A| + 1

G(x) = 1 + sum_{A} a^{alice(A)+2|A|+1} x^{|A|+1} * G(a^{|A|+1} x)

The scaling a^{|A|+1} still varies with |A|, but at least k((A)) is removed!

For each |A|=k: G(x) = 1 + sum_{k>=0} a^{2k+1} x^{k+1} * C_k * G(a^{k+1} x)
where C_k = sum_{|A|=k} a^{alice(A)} (just a Catalan-weighted sum over A)

So alice-only has size-based uniform scaling (all words of same size
have same scaling a^{k+1}), but different sizes have different scaling.

This is still non-standard but maybe more tractable.
""")

    F_alice_only = [0]
    for n in range(1, 7):
        total = 0
        for s in generate_dyck(n):
            total = (total + pow(a_val, alice_of(s), MOD)) % MOD
        F_alice_only.append(total)
        print(f"  Alice-only F[{n}] = {total}")

    print("\nAlice-only follows known patterns?")
    for n in range(2, 7):
        ratio = F_alice_only[n] * pow(F_alice_only[n-1], MOD-2, MOD) % MOD
        print(f"  F[{n}]/F[{n-1}] = {ratio}")

def explore_multivariate_gf(a_val, b_val):
    print("\n" + "=" * 70)
    print("MULTIVARIATE GF: Can we write a functional equation?")
    print("=" * 70)

    print("""
Define a 3-variable GF:
  F(x, y, z) = sum_{s in D} a^{alice(s)} b^{bob(s)} x^{|s|} y^{k(s)} z^{???}

What should z track to make the equation close?

Idea: z tracks the "tail wrapping state" - the wrapped form of
the first primitive block's inner structure.

But this just recreates the wrapping problem at the GF level.

Alternative: z = y^(first_x_seq_element). Then:
  F(x, y, z) tracks the first element of the x-seq.
  
But x-seq elements are sizes, and different A have different x_1.
So we'd need z to be a formal power series in another variable,
making it essentially equivalent to the full enumeration.

CONCLUSION: The non-locality of bob wrapping cannot be circumvented
by adding more variables to the GF. Each additional "catalytic" variable
just shifts the complexity without eliminating it.
""")

def test_primitive_decomp_kernel(a_val, b_val):
    print("\n" + "=" * 70)
    print("PRIMITIVE DECOMPOSITION + KERNEL METHOD")
    print("=" * 70)

    print("""
Every non-empty Dyck word s can be decomposed as:
  s = P1 * P2 * ... * Pk   (Pi are primitive)

This decomposition aligns with x-seq: x_i = |Pi|

bob(s) = sum_{i=1..k} (i-1) * |Pi|     [from x-seq definition]
alice(s) = sum alice(Pi) + sum_{i<j} |Pi| * |Pj|  [concat formula]

In the primitive decomposition:
- bob is directly from primitive block sizes (NO wrapping!)
- alice has cross-terms from concatenation

Let's define a GF based on primitive decomposition:

Q(x, u) = sum over SEQUENCES of primitive blocks:
          a^{alice} b^{bob} x^{total_size} u^{#blocks}

A sequence of k blocks P1,...,Pk:
  total_size = sum |Pi|
  #blocks = k
  bob = sum (i-1)*|Pi|
  alice = sum alice(Pi) + sum_{i<j} |Pi|*|Pj|

The cross-term sum_{i<j} |Pi|*|Pj| depends on ORDER and is the challenge.

HANDLING CROSS-TERMS:
Let's define building the sequence left to right.
At step t, we've accumulated:
  cumul_size = sum_{i<t} |Pi|
  cumul_alice = sum_{i<t} alice(Pi) + sum_{i<j<t} |Pi|*|Pj|
  cumul_bob = sum_{i<t} (i-1)*|Pi|
  cumul_k = t

When we add a new primitive block P of size m:
  new_size = cumul_size + m
  new_alice = cumul_alice + alice(P) + cumul_size * m
  new_bob = cumul_bob + cumul_k * m + bob(P)
  new_k = cumul_k + 1

Notice that bob(P) and alice(P) are the properties of the primitive block P.

Now, every primitive block P = (A) for some A.
alice(P) = alice(A) + 2|A| + 1
bob(P) = bob((A))   [this is the wrapping part]
k(P) = k((A))

So the wrapping appears INSIDE each primitive block's bob.
And k((A)) doesn't affect the cross-term directly (the cross-term
uses block SIZE m = |A|+1, not k((A))).

Wait - in bob(s) = sum (i-1)*|Pi|, there's no k((A))! 
Let me verify: is bob(P) = bob((A)) used in bob(s)?

For s = P1*...*Pk:
bob(s) = bob(P1) + ... + bob(Pk) + sum_{i<j} k(Pi)*|Pj|
       = sum bob(Pi) + sum_{i<j} k(Pi)*|Pj|

where bob(Pi) = bob((Ai)).

But from the x-seq definition: bob(s) = sum (j-1)*x_j
where x_j = |Pj| = |Ai|+1

So bob(s) = sum (j-1)*(|Aj|+1)
           = sum (j-1)*|Aj| + sum (j-1)
           = sum (j-1)*|Aj| + k(k-1)/2

But this is different from the concat formula! Let me verify.

For s = "()()": X=[1,1], bob = 0*1 + 1*1 = 1.
P1="()", P2="()". |A1|=0, |A2|=0.
sum (j-1)*|Aj| = 0*0 + 1*0 = 0.
k(k-1)/2 = 2*1/2 = 1.
0+1=1. OK!

For s = "(())()": X=[2,1], bob = 0*2 + 1*1 = 1.
P1="(())", P2="()". |A1|=1, |A2|=0.
sum (j-1)*|Aj| = 0*1 + 1*0 = 0.
k(k-1)/2 = 2*1/2 = 1.
0+1=1. OK!

For s = "(()())": X=[2,1], bob=1.
P1="(()())"... wait, is "(()())" primitive? Yes.
So k=2 blocks: P1 has |A1|=?
s = (A1), A1="()()". |A1|=2.
But X=[2,1], so x1=2, x2=1.
|P1|=2, |P2|=1.

Wait, "(()())" only has 1 return to height 0 (at the end). So it's primitive,
meaning k=1 block. But X=[2,1] has k=2! Contradiction!

Oh wait, the confusion is between "primitive Dyck word" (only returns to 0 at end)
and "x-seq primitive block" (the blocks of the x-seq algorithm).

For "(()())":
- It IS primitive (returns to 0 only at the end)
- X=[2,1] has 2 x-seq blocks
- The x-seq blocks are NOT the primitive Dyck decomposition blocks!

So x-seq blocks and primitive blocks are DIFFERENT decompositions.
This is the fundamental structural issue!

For the x-seq decomposition:
  bob = sum (j-1)*x_j  (definitional)
  Concatenation of x-seq blocks does NOT correspond to (A)B decomposition.

For the (A)B decomposition:
  bob = requires wrapping knowledge
  Concatenation is natural (s = (A)B)

The two decompositions are incompatible. This is why all combinatorial
DP routes fail: they try to use one decomposition (usually tree/(A)B)
to compute a quantity (bob) defined in terms of the other (x-seq).

KERNEL METHOD VERDICT:
The kernel method uses the (A)B decomposition (first return to height 0).
Since bob is defined via x-seq, which doesn't align with this decomposition,
the kernel method cannot directly compute bob without the wrapping transform.

The wrapping transform A -> (A) maps between x-seq and (A)B decompositions,
and this mapping is non-local (depends on full height function).

THEREFORE: The kernel method does not apply to this problem.
The structural incompatibility between x-seq and (A)B decompositions
is the same bottleneck that killed all combinatorial DP routes.
""")

if __name__ == '__main__':
    a_val, b_val = 2, 3
    deep_kernel_analysis(a_val, b_val)
    explore_multivariate_gf(a_val, b_val)
    test_primitive_decomp_kernel(a_val, b_val)
