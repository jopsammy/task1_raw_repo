"""
Route L: L(i) sequence generative DP.
alice = sum(L(i)), bob = sum(n - l_j) where l_0=0, l_{j+1}=L(l_j+1), l_k=n.

DP state: dp[x][y] = weighted sum of all partial L-sequences ending at jump point x
with L(x)=y. Transition to next jump point y+1 via L(y+1)=y'.
"""
import sys
from verify_bf import generate_dyck, alice_of, x_seq_and_bob

MOD = 998244353


def compute_L_seq(s):
    n = len(s) // 2
    L = [0] * n
    right_count = 0
    for i, ch in enumerate(s):
        if ch == ')':
            pos = i + 1
            L[right_count] = pos - (right_count + 1)
            right_count += 1
    return L


def alice_from_L(L):
    return sum(L)


def jump_chain(L):
    n = len(L)
    jumps = [0]
    pos = 0
    while pos < n:
        next_pos = L[pos]
        jumps.append(next_pos)
        pos = next_pos
    return jumps


def bob_from_L(L):
    n = len(L)
    jumps = jump_chain(L)
    bob = 0
    for j in range(1, len(jumps) - 1):
        bob += n - jumps[j]
    return bob


def verify_formulas(max_n=8):
    """Cross-validate L-sequence formulas against brute-force."""
    print("=== Cross-validating L-sequence formulas ===\n")
    for n in range(1, max_n + 1):
        words = generate_dyck(n)
        all_ok = True
        for s in words:
            L = compute_L_seq(s)

            alice_bf = alice_of(s)
            alice_L = alice_from_L(L)
            if alice_bf != alice_L:
                print(f"FAIL alice: n={n} s={s} bf={alice_bf} L={alice_L}")
                all_ok = False

            X, bob_bf = x_seq_and_bob(s)
            bob_L = bob_from_L(L)
            if bob_bf != bob_L:
                print(f"FAIL bob: n={n} s={s} bf={bob_bf} L={bob_L} X={X}")
                all_ok = False

            jumps = jump_chain(L)
            x_seq = [jumps[i + 1] - jumps[i] for i in range(len(jumps) - 1)]
            if x_seq != X:
                print(f"FAIL xseq: n={n} s={s} X_bf={X} X_L={x_seq}")
                all_ok = False

        label = "OK" if all_ok else "FAIL"
        print(f"  n={n}: {label} ({len(words)} words)")


def precompute_H(N, a):
    """
    H[d][u] = sum over non-decreasing sequences 0 <= w1 <= ... <= wd <= u
              of a^{sum w_i}.
    Recurrence:
      H[0][u] = 1
      H[d][u] = H[d][u-1] + a^u * H[d-1][u]
    """
    H = [[0] * (N + 1) for _ in range(N + 1)]
    pow_a = [1] * (N + 1)
    for i in range(1, N + 1):
        pow_a[i] = (pow_a[i - 1] * a) % MOD

    for u in range(N + 1):
        H[0][u] = 1

    for d in range(1, N + 1):
        for u in range(N + 1):
            if u == 0:
                H[d][0] = 1
            else:
                H[d][u] = (H[d][u - 1] + pow_a[u] * H[d - 1][u]) % MOD

    return H, pow_a


def C_mid(d, y, delta, pow_a, H):
    """
    Middle segment contribution:
    Positions x+1..y (length d = y-x) with L values in [y, y+delta].
    Contribution = a^{d*y} * H[d][delta]
    """
    if d < 0:
        return 0
    return (pow(pow_a[y], d, MOD) * H[d][delta]) % MOD


def solve_route_l(N, a_val, b_val):
    """
    Route L DP: the generative DP on L(i) sequences.

    dp[x][y] = sum over all partial L(1..y) sequences where position x
               is a jump point and L(x)=y.

    Explanation of the jump chain structure:
      - Jump points: l_0=0, l_1=L(1), l_2=L(l_1+1), ..., l_k=n
      - Between jump point x=l_j and next trigger position x+1:
        * Position x+1 has L(x+1) = l_{j+1} (the next jump point)
        * Positions x+1 through l_{j+1} form a segment
        * Within this segment, positions after x+1 (up to l_{j+1})
          have L values bounded by [y, L(x+1)] where y=L(x)

    Actually, the correct structure:
      Jump point: x = l_j.  L(x) = y.
      Next position: x+1.  L(x+1) = l_{j+1} = y_next.
      Middle segment: positions x+1 through y_next have L values...
      Wait - the middle segment should be x+1..L(x) = x+1..y.

    Let me re-derive more carefully.

    Given jump point x and L(x)=y:
      - The next jump is determined by L(x+1)
      - But L(x+1) can be anything >= L(x)+1 >= y+1 (since L is non-decreasing
        and L(x)=y, the next value must be at least y+1)
      - Actually L(x+1) >= L(x) = y, but since x is a JUMP POINT,
        we need L(x+1) > y? Not necessarily... actually L can stay the same.

    Hmm wait. Let me think about this differently.

    The L sequence L[0], L[1], ..., L[n-1] (0-indexed) has:
      - L is non-decreasing
      - L[i] in [i+1, n]  (1-indexed view)
      - L[n-1] = n

    Jump chain: j_0=0, j_{i+1}=L[j_i] (0-indexed: L at position j_i)

    For a jump point j_i (which is a position in the L array):
      - j_i is both an index and a value of L at some position
      - L[j_i] is the L value at that position
      - The next jump j_{i+1} = L[j_i+1]

    Let me re-examine with 0-indexed positions for clarity.

    Positions: 0, 1, ..., n-1
    L[0], L[1], ..., L[n-1] with constraints.

    Jump: j_0 = 0 (conceptual index 0)
          j_1 = L[0]  (L at position 0, 1-indexed would be L(1))
          j_2 = L[j_1]  (L at position j_1)

    Wait, the formula from the spec is:
      l_0 = 0, l_{j+1} = L(l_j + 1)

    With 1-indexed positions: L(1), L(2), ..., L(n).
      l_0 = 0
      l_1 = L(1)  → L at position 1
      l_2 = L(l_1 + 1)  → L at position l_1 + 1

    With 0-indexed: L[0..n-1].
      l_0 = -1 (or conceptually before position 0)
      l_1 = L[0]  → jump determined by L at position 0

    Hmm, this is getting confusing. Let me use the 0-indexed version consistently.

    Positions: 0, 1, ..., n-1
    L[i] = position of (i+1)-th ')' - (i+1)

    The jump chain (0-indexed):
      Start: cum = 0  (number of positions processed)
      Jump 1: cum = L[0]  (jump to position L[0]-1? Or L[0]?)

    Actually, let me just re-derive from first principles.

    For a Dyck word s of length 2n:
      - P(i) = position of i-th ')' (1-indexed)
      - L(i) = P(i) - i

    The x-seq is computed as:
      cum = 0
      for each step:
        x = max{t >= 1: h[2*cum + t] == t}
        cum += x

    Now, in terms of L:
      After consuming `cum` right parentheses, we've seen `cum` right parens
      and `P(cum)` characters total. The current "position" in terms of
      right paren count is `cum`.

      The x-seq step looks at the next characters starting from position
      2*cum+1 in the string. The first `x` steps are all '(' characters.

      In the L-sequence framework, L(cum + 1) = P(cum+1) - (cum+1).
      P(cum+1) is the position of the (cum+1)-th ')'.
      Between positions 2*cum+1 and P(cum+1), there are
        P(cum+1) - 2*cum characters.
      The first (cum+1) right parens have consumed P(cum+1) characters,
      of which cum+1 are ')' and the rest are '('.
      So L(cum+1) = P(cum+1) - (cum+1) = number of '(' before the (cum+1)-th ')'.
      
      The characters from 2*cum+1 to P(cum+1):
        Total chars: P(cum+1) - 2*cum
        Number of '(': P(cum+1) - (cum+1) - cum = P(cum+1) - 2*cum - 1
        Wait, no. Before position P(cum+1), we have cum+1 ')' chars.
        Total chars so far: P(cum+1).
        Number of '(': P(cum+1) - (cum+1) = L(cum+1).
        From position 2*cum+1 to P(cum+1):
          '(' count = L(cum+1) - cum
          ')' count = 1 (the (cum+1)-th ')')
        Total chars in this span: L(cum+1) - cum + 1 = P(cum+1) - 2*cum

    The x-seq step x is the number of consecutive '(' from position 2*cum+1.
    The characters from 2*cum+1 are all '(' until the next ')'.
    So x = L(cum+1) - cum.

    This verifies: x_{j+1} = L(cum+1) - cum where cum = l_j.

    So l_{j+1} = cum + x_{j+1} = cum + L(cum+1) - cum = L(cum+1).

    Wait, that gives l_{j+1} = L(cum+1). But cum is l_j, and we're looking
    at L at position cum+1 (which is the (l_j+1)-th right parenthesis).

    So l_{j+1} = L(l_j + 1). ✓ (This matches but uses 1-indexed L.)

    Now, bob = Σ_{j=1}^{k-1} (n - l_j). Let's verify:
      x_{j+1} = l_{j+1} - l_j
      bob = Σ_{j=0}^{k-1} j * x_{j+1} = Σ_{j=0}^{k-1} j*(l_{j+1}-l_j)
      = Σ_{j=1}^{k-1} (l_{k+1}... no this doesn't simplify cleanly.

    Let me just trust that bob = Σ(n-l_j) was verified and focus on the DP.

    **DP Design (corrected):**

    We want to generate L(1), L(2), ..., L(n) incrementally, tracking
    jump points as we go.

    A jump point is an index x where L(x) determines the L value at a
    position that IS part of the jump chain. Specifically:
      - If x=0 (conceptual), L(1) determines the first jump l_1
      - If x=l_j, L(x+1)=L(l_j+1) determines the next jump l_{j+1}

    DP state: dp_pos[pos][y] where:
      - We've processed L values for positions 1..pos
      - The last position processed (pos) is a JUMP POINT
      - L(pos) = y
      - This captures all partial sequences where pos is in the jump chain

    From state (pos, y):
      - The NEXT position to process is pos+1
      - L(pos+1) can be any value y' >= y (monotonicity)
      - If we choose L(pos+1) = y', then:
        * pos+1 becomes the next jump point (since L(pos+1) determines
          the next jump in the chain)
        * But wait - not EVERY position is a jump point. Jump points are
          only positions that are in the jump chain.

    Hmm, I think the DP design from the spec might need refinement.
    Let me think about this differently.

    The jump chain: 0, l_1, l_2, ..., l_k = n

    For each jump l_j → l_{j+1}:
      - Trigger: L(l_j + 1) = l_{j+1}
      - Positions l_j+1 .. l_{j+1}: these have L values that...
        * L(l_j+1) = l_{j+1} (trigger)
        * L(l_j+2) >= L(l_j+1), etc.

    But the spec's DP says:
      - Current jump point: x (where x=l_j)
      - L(x) = y
      - Next trigger: y+1 (but this claims y+1 = x+1?)
      - Middle segment: x+1..y

    This only works if x = y, i.e., L(l_j) = l_j. Is this always true?

    Let me check with examples:
    - "()()()": L=[1,2,3], jump points: 0,1,2,3. L(1)=1 ✓, L(2)=2 ✓
    - "(()())": L=[2,3,3], jump points: 0,2,3. L(2)=3 ≠ 2 ✗
    - "((()))": L=[3,3,3], jump points: 0,3. L(3)=3 ✓

    So L(x)=x is NOT always true at jump points. The equation L(l_j)=l_j
    only holds sometimes.

    But the spec claims: "如果当前跳跃点是x，L(x)=y，下一触发位置=y+1"
    And "中间段位置=x+1..y"

    Wait... maybe the claim is that the next triggering position after jump
    point x is y+1 where y = L(x). Let me check:

    For "(()())": jump at x=2, L(2)=3. The spec says next trigger = y+1 = 4.
    But n=3, so this would be the end. Is this correct?

    Jump chain: 0, 2, 3. After jump point 2, the next jump point is 3.
    How is 3 determined? l_2 = L(l_1+1) = L(3) = 3. So L at position 3
    determines the last jump point.

    The spec says trigger = y+1 = 4 > n. But the actual trigger position
    should be x+1 = 3. And L(3)=3 determines the jump.

    So there's a mismatch. The spec says "trigger = y+1" but the actual
    trigger position is x+1.

    Unless there's a different interpretation...

    Actually wait. Let me re-read the original note more carefully.
    From `blind-spot-analysis-note0523.md`, the key claim:

    "l₀=0, lⱼ₊₁ = L(lⱼ+1)" — this we've verified.

    The DP then claims:
    "当前跳跃点x，L(x)=y" — x is a jump point, L(x)=y

    But is x=l_j necessarily a position where L is defined? If x=0, then
    L(0) is undefined (L is 1-indexed). So perhaps "x" in dp[x][y] doesn't
    mean position-in-L, but rather the JUMP VALUE itself.

    Let me reinterpret: dp[x][y] where:
      - x is the jump point VALUE (l_j), not the position in L
      - y = L(x) ... but L is only defined for positions 1..n, and x can be 0

    Hmm, for x=0: L(0) is undefined. But dp[0][0] is initialized to 1.
    This is a conceptual starting point.

    For x=l_1: the jump from 0 to l_1. How is l_1 determined?
    l_1 = L(1). So the first trigger position is 1.

    From dp[0][0]:
      - Trigger position: 0+1 = 1
      - L(1) = y (the first jump value)
      - Middle: positions 1..0 = empty (since y=0, x=0, middle is x+1..y = 1..0 = empty)

    Then dp[l_1][L(l_1)] gets the contribution. But L(l_1) = L(L(1)) is NOT
    necessarily equal to l_1. For "(()())": L(1)=2, so dp[2][L(2)]=dp[2][3].

    Now from dp[2][3] (x=2, y=3):
      - Next trigger: x+1 = 3
      - L(3) = 3 = n
      - Middle: positions 3..3 = position 3 with L(3)=3

    But the spec says trigger = y+1 = 4, middle = x+1..y = 3..3. Hmm,
    middle 3..3 is position 3 only, which is the trigger position.
    
    I think the confusion is: in the spec's DP, "x+1..y" as the middle
    segment only makes sense when y > x+1 (multiple middle positions).
    When y = x+1, there's only one position and it's the trigger.
    
    Actually, I think the spec's claim might be that at a jump point x
    with L(x)=y, the positions between x+1 and y (inclusive) form a segment
    where L values are all between y and the next jump value. Position y+1
    is then the next trigger.

    Wait, that doesn't work for "(()())" where x=2, y=3. Middle: 3..3.
    Position 3 is L(3)=3 which IS the next jump point.

    OK I think there's a fundamental issue with the DP design as described
    in the spec. Let me instead try to derive the DP from scratch using
    the jump chain.

    **Derivation from scratch:**

    The jump chain partitions the L sequence:
      Jumps: l_0=0, l_1, l_2, ..., l_k=n
      
    For each segment [l_j + 1, l_{j+1}] (positions in L, 1-indexed):
      - Position l_j + 1: L(l_j+1) = l_{j+1} (trigger)
      - Positions l_j + 2, ..., l_{j+1}: L values between L(l_j) and l_{j+1}
        (monotonic non-decreasing, bounded by known values)

    So the DP needs to handle:
      1. Choosing the next jump position l_{j+1} = L(l_j + 1)
      2. Filling the middle positions l_j + 2 .. l_{j+1} with valid L values
      3. bob contribution: n - l_j

    Let me define dp[jump][y] where:
      - jump = l_j (the current jump point value)
      - y = L(l_j) (the L value at the jump point)
      - For the initial state: jump=0, y=0 (conceptual)

    From (jump, y):
      - The next trigger is at position jump+1
      - We choose L(jump+1) = next_jump (the next jump point value)
      - next_jump must satisfy: next_jump >= y+1 (L is non-decreasing, and
        since L(jump) = y, L(jump+1) >= y+1? Actually L(jump) could equal y
        and L(jump+1) could equal y too if y > jump... no, L is non-decreasing
        so L(jump+1) >= L(jump) = y)
      - Actually, the constraint is L(jump+1) >= y (since L is non-decreasing and
        L(jump) = y). But if jump+1 > l_j, then the next trigger is a new position,
        so it can be >= L(jump) = y.
      
      Wait, but the jump positions are: l_0=0, l_1, l_2, ...
      And l_{j+1} = L(l_j + 1). So L at position (l_j+1) is the next jump.
      
      If current jump is at value x (l_j = x), then:
        L(x+1) = next jump value = x'
        And L(x) = y (the L value at current jump point)

      The middle segment: positions x+2, ..., x'
        These have L values between y and x' (monotonicity)
        Length: x' - x - 1

      But wait, the trigger position x+1 has L(x+1) = x', and this position
      also contributes to alice via L(x+1) = x'. Does L(x+1) get counted
      in the middle segment or separately?

      If we include it in the middle segment: positions x+1, ..., x'
      Length: x' - x
      Values: all >= y (from L(x)=y), all <= x' (from L(x') >= x'), but
      L(x+1) = x' is the maximum.

    Actually, I think the middle segment is x+1..x' (including the trigger),
    and all values are in [y, x']. The trigger has value x'.

    So the middle segment contribution:
    C(x, y, x') = sum over y ≤ v_{x+1} ≤ v_{x+2} ≤ ... ≤ v_{x'} ≤ x'
                  of a^{sum of all v_i}
    Length: d = x' - x
    Lower bound: y
    Upper bound: x'

    Using the shift trick:
    Let w_i = v_i - y. Then w_i ∈ [0, x' - y].
    Sum of v_i = d*y + sum of w_i.
    Contribution = a^{d*y} * H[d][x'-y]

    Where H[d][u] = sum over 0 ≤ w_1 ≤ ... ≤ w_d ≤ u of a^{sum w_i}.

    And bob contribution: b^{n - x} (for the jump at x).

    If next_jump = x' = n (final jump), then:
      - Bob contribution is already included (n - prev_jump)
      - No further transitions needed
      - The middle segment completes the sequence

    Let me verify this DP on "()()()" (n=3, L=[1,2,3]):

    dp[0][0] = 1

    From (0, 0): x' = L(1) = 1
      d = x' - x = 1
      Middle: positions 1..1, one position with value v ∈ [0, 1]
      H[1][1] = a^0 + a^1 = 1 + a
      Contribution: a^{1*0} * (1+a) * b^{n-0} = (1+a) * b^3
      → dp[1][1] += (1+a) * b^3

    Wait, the DP transition needs a^{L(1)} * b^{n-0} where L(1)=l_1=1.
    But the middle segment gives a^0 + a^1 = 1 + a. And L(1) should be 1,
    so a^1 = a. But 1+a is wrong — it includes the case where L(1)=0
    which is invalid (L(1) must be at least 1, the constraint L(i) >= i).

    Ah, I see the issue! The lower bound for L(x+1) is not y (= L(x)).
    The lower bound is actually x+1 (the position constraint)!

    Constraint: L(i) >= i for all i.

    So for position x+1: L(x+1) >= x+1.
    And since L(x) = y, we have L(x+1) >= max(y, x+1) = y (because if x+1 > y,
    the lower bound is x+1; if y > x+1, the lower bound is y).

    For "(())" (n=2, L=[2,2]):
    dp[0][0] → L(1) = 2
    Middle: positions 1..2, values in [max(0, 1)=1, 2]
    Hmm, L(1) >= 1 (position constraint), and L(2) >= 2.
    
    Actually, the constraint is per-position. For position p: L(p) ∈ [p, n].
    So the lower bound varies by position within the middle segment.

    This makes the middle segment more complex! The lower bound for position
    x+1 is max(y, x+1), for position x+2 is max(y, x+2), etc.

    Actually no. Since L is non-decreasing, if L(x) = y and y >= x+1,
    then L(x+1) >= y >= x+1, so the effective lower bound is y.
    If L(x) = y and y < x+1, then L(x+1) >= x+1 > y, so the effective
    lower bound is x+1.

    More generally, for position i in (x, x']: L(i) >= max(y, i).
    
    This is getting complicated. Let me instead think about whether there's
    a cleaner formulation.

    **Alternative formulation:**

    Instead of trying to handle all positions as a middle segment,
    let me generate L values position by position, tracking jump points.

    Given current position i (1-indexed) and current L value L(i) = y:
      - Next position i+1 has L(i+1) = y' where y' >= max(y, i+1)
      - If i+1 is in the jump chain: i+1 = l_j for some j.
        This depends on whether L(i+1) is "determined by" position (i+1).
      
    Actually, every position determines a jump: position p determines
    L(p) which is a candidate jump point. But the jump chain only
    includes positions that are actually "reached" via the chain.

    Hmm, I think the issue is that the jump chain gives us a natural
    partition of the L sequence. For each jump:
      l_j → l_{j+1}: positions l_j+1 .. l_{j+1} are processed
      Position l_j+1 has L = l_{j+1} (determines next jump)
      Other positions have L in [L(l_j), l_{j+1}]

    This partition covers all positions 1..n because the jumps go from
    0 to n and are strictly increasing.

    OK so let me just try to implement a DP that works position-by-position,
    then optimize later.

    Actually, let me look at this from yet another angle. Maybe the DP should
    be on the L sequence DIRECTLY, treating each position as either:
      A) A "jump trigger" (position x+1 where x was a jump point)
      B) A "middle" position (between jump points)

    For each transition, we know which positions are triggers and which are middle.

    DP approach: dp[x][y] as described in the spec, but with proper middle
    segment handling.

    Let me try yet another formulation. The constraint L(i) ∈ [i, n] means
    that when we shift by the position:

    Define L'(i) = L(i) - i. Then:
      - L'(i) ∈ [0, n-i]
      - L'(i+1) >= L'(i) - 1 (since L(i+1) >= L(i) and i+1 > i? No...)
      
    Actually L'(i+1) = L(i+1) - (i+1) >= L(i) - (i+1) = L'(i) - 1.

    This doesn't seem to simplify things.

    Let me just go with the following approach and verify empirically:

    1. Define dp[x][y] where x is a jump point and L(x)=y.
    2. For each dp[x][y], compute transitions to dp[y+1][y'].
    3. The middle segment positions x+1..y have values in [max(y, pos_min), y'].
    4. Verify against brute force for n≤8.

    But first I need to understand: does the spec's claim "next trigger at y+1"
    hold? Let me check with examples.

    Jump point x = l_j. The next jump l_{j+1} = L(x+1). The claim is that
    the trigger position is y+1 = L(x)+1.

    But L(x+1) is determined by position x+1 in the L sequence. The spec
    seems to claim that between x and y there are "middle" positions, and
    the trigger is at y+1. That implies L(x+1) through L(y) are the middle.

    This interpretation means: given x and L(x)=y, the positions x+1, x+2, ...,
    y are NOT jump points (they're part of the middle segment). Position y+1
    IS the next trigger.

    But how can we know L(x+1)..L(y) without knowing x+1 first? The spec
    says they contribute only to alice. And L(y+1) determines the next jump.

    Let me check this claim empirically: for a jump point x with L(x)=y,
    does the next jump always start from position y+1?

    For "(()())" (n=3): jump point x=2, L(2)=3=y.
      Next trigger according to spec: y+1 = 4.
      But n=3, so there is no position 4.
      Actual jump chain: next jump at position 3 (x+1=3, L(3)=3).

    So the spec's claim doesn't hold here. x=2, y=3, but the trigger is at
    3 (not 4).

    For "()()()" (n=3): jump point x=1, L(1)=1=y.
      Next trigger: y+1 = 2.
      Actual next trigger: x+1 = 2.
      These match because y=x here.

    For "((()))" (n=3): jump point x=3, L(3)=3=y.
      Next trigger: y+1 = 4 > n.
      Chain ends (x=3=n).

    So the spec's claim that trigger = y+1 works when y = x, but not when y > x.

    I think the spec might have an error, or I'm misreading it. Let me just
    go with the direct jump chain approach and implement the DP properly.

    **CORRECT DP (position-by-position):**

    Let dp[pos][y] = sum over partial sequences where we've processed positions
    1..pos, L(pos)=y, and pos is the most recent jump point.

    Initial: dp[0][0] = 1 (conceptual, before any positions)

    For each dp[pos][y]:
      Choose next_jump = L(pos+1) = y' ∈ [max(y, pos+1), n]
      The transition processes positions pos+1 .. y' (inclusive).
      - Position pos+1 has L(pos+1) = y' (trigger, determines next jump)
      - Positions pos+2 .. y' form the "middle" segment
      - All positions' L values contribute to alice
      - Bob contribution: b^{n-pos} (for the jump at pos)

      Wait, but position pos+1 IS the trigger. Its L value = y' determines
      the new jump point. Positions pos+2..y' are additional positions
      that get "swept along" to the new jump point.

    So the transition goes from (pos, y) to (y', y'') where:
      - y' = L(pos+1) (this becomes the new jump position)
      - But we don't know y'' = L(y') yet
      - Between pos+1 and y': we fill L values

    Actually, the DP should be two-step:
      1. From (pos, y), choose L(pos+1) = next_pos
      2. Fill positions pos+2..next_pos with valid L values
      3. Now we're at jump point next_pos with some L(next_pos) = new_y
      4. new_y ∈ [max(L(pos+1), next_pos), n]

    Let me define intermediate states.

    dp[pos][y] → choose L(pos+1) = next ∈ [max(y, pos+1), n]
      → middle[pos][next] stores the contribution after step 1
      → dp[next][y''] gets contribution after step 2

    Hmm, this is getting complex. Let me try a different DP formulation.

    **TWO-LAYER DP:**

    Layer 1 - main DP: dp[jump][L_val] where:
      - jump = current position in the jump chain
      - L_val = L(jump)

    Layer 2 - transition: from dp[x][y], choose next_jump = x'.
    The middle segment is positions x+1 .. x' (all of them).

    Wait, this includes position x+1 (trigger) in the middle segment.
    The trigger position x+1 has value ≥ y (from monotonicity) and
    ≤ x' (since L(x+1) = x'? No, L(x+1) determines x', not the other way).

    Actually, L(x+1) = x' (the next jump value). So the trigger's L value
    IS x'. And the middle positions x+2..x' have values in [y, x'].

    No, that's wrong too. L(x+1) = x' means L at position x+1 equals x'.
    And x' is the next jump point. So the middle segment is positions
    x+2 .. x' with values in [y, min(x', n)]? Actually they should be
    ≤ L(x') = next_L_val but we don't know that yet.

    I think I'm overcomplicating this. Let me try a different strategy:
    just implement the DP where we treat each position independently,
    tracking whether we're at a jump point or in the middle.

    **State machine approach:**

    State: (pos, L_val, is_jump)
      where pos is the current position, L_val = L(pos).

    At position pos:
      - If we're at a jump point (pos is in the jump chain):
        * We've already accounted for bob contribution of previous jump
        * Next position pos+1: L(pos+1) = next_L
        * next_L >= max(L_val, pos+1) (constraint)
        
      - If we're in the middle (between jump points):
        * Next jump point is already determined
        * We're filling L(pos+1) constrained by [L_val, target_L]

    This is essentially a position-by-position DP, which would be O(N^3).

    Let me try a completely different approach. Since the problem is that
    the DP state needs to track two things (jump position and L value),
    and the transition is complicated, let me just try to enumerate all
    valid L sequences directly for small n, see the pattern, and build
    the DP from that.

    Actually, let me just write the verification code for the formulas
    and then brute-force enumerate L sequences to understand the structure.
    """
    pass


def verify_jump_structure(max_n=7):
    """Analyze jump structure for each L sequence."""
    print("\n=== Analyzing jump structure ===\n")
    for n in range(1, max_n + 1):
        words = generate_dyck(n)
        for s in words:
            L = compute_L_seq(s)
            jumps = jump_chain(L)
            print(f"n={n} s={s} L={L} jumps={jumps}")


def brute_force_L_dp(N, a_val, b_val):
    """Compute F[1..N] by enumerating all L sequences for verification."""
    res = []
    for n in range(1, N + 1):
        words = generate_dyck(n)
        total = 0
        for s in words:
            L = compute_L_seq(s)
            alice = alice_from_L(L)
            bob = bob_from_L(L)
            total = (total + pow(a_val, alice, MOD) * pow(b_val, bob, MOD)) % MOD
        res.append(total)
    return res


if __name__ == '__main__':
    verify_formulas(8)
    print()
    print("=== Brute-force L-sequence enumeration ===")
    for N in range(1, 7):
        res = brute_force_L_dp(N, 2, 3)
        print(f"  N={N}: {res}")
