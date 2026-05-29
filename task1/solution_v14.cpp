#pragma GCC optimize("O3")
#pragma GCC optimize("unroll-loops")

#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
using namespace std;

typedef long long ll;
typedef unsigned int uint;
typedef unsigned long long ull;
const uint MOD = 998244353;
const uint PRIMITIVE_ROOT = 3;

uint modpow(uint a, ll e) {
    uint r = 1;
    while (e) {
        if (e & 1) r = (ll)r * a % MOD;
        a = (ll)a * a % MOD;
        e >>= 1;
    }
    return r;
}

void ntt(vector<uint>& a, bool invert) {
    int n = a.size();
    for (int i = 1, j = 0; i < n; ++i) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) swap(a[i], a[j]);
    }
    for (int len = 2; len <= n; len <<= 1) {
        uint wlen = modpow(PRIMITIVE_ROOT, (MOD - 1) / len);
        if (invert) wlen = modpow(wlen, MOD - 2);
        for (int i = 0; i < n; i += len) {
            uint w = 1;
            for (int j = 0; j < len / 2; ++j) {
                uint u = a[i + j];
                uint v = (ll)a[i + j + len / 2] * w % MOD;
                a[i + j] = u + v; if (a[i + j] >= MOD) a[i + j] -= MOD;
                a[i + j + len / 2] = u - v + MOD; if (a[i + j + len / 2] >= MOD) a[i + j + len / 2] -= MOD;
                w = (ll)w * wlen % MOD;
            }
        }
    }
    if (invert) {
        uint inv_n = modpow(n, MOD - 2);
        for (int i = 0; i < n; ++i)
            a[i] = (ll)a[i] * inv_n % MOD;
    }
}

int main() {
    int N, a_val, b_val;
    if (scanf("%d%d%d", &N, &a_val, &b_val) != 3) return 1;
    a_val %= MOD; b_val %= MOD;

    int N1 = N + 1;
    int N2 = N + 2;

    vector<uint> pow_a(N2 + 1), pow_b(N2 + 1), inv_pow_b(N2 + 1);
    pow_a[0] = pow_b[0] = inv_pow_b[0] = 1;
    for (int i = 1; i <= N2; ++i) {
        pow_a[i] = (ll)pow_a[i - 1] * a_val % MOD;
        pow_b[i] = (ll)pow_b[i - 1] * b_val % MOD;
    }
    uint inv_b = modpow(b_val, MOD - 2);
    for (int i = 1; i <= N2; ++i)
        inv_pow_b[i] = (ll)inv_pow_b[i - 1] * inv_b % MOD;

    vector<uint> powbinom(N2 + 1);
    powbinom[0] = 1;
    for (int k = 1; k <= N2; ++k)
        powbinom[k] = (ll)powbinom[k - 1] * pow_a[k - 1] % MOD;

    auto idx = [](int n, int k) { return n * (n + 1) / 2 + k; };
    int flat_size = idx(N2, N2) + 1;
    vector<uint> H(flat_size);

    for (int n = 1; n <= N2; ++n)
        H[idx(n, n)] = powbinom[n];

    vector<uint> fact(N2 + 1);
    fact[0] = 1;
    int order_d = -1;
    if (a_val == 1) {
        for (int i = 1; i <= N2; ++i)
            fact[i] = (ll)fact[i - 1] * i % MOD;
    } else {
        for (int i = 1; i <= N2; ++i) {
            uint term = pow_a[i] - 1 + MOD;
            if (term >= MOD) term -= MOD;
            if (term == 0 && order_d < 0) order_d = i;
            fact[i] = (ll)fact[i - 1] * term % MOD;
        }
    }
    
    bool is_bad = (order_d > 0 && order_d <= N2);

    if (!is_bad) {
        vector<uint> inv_fact(N2 + 1);
        inv_fact[N2] = modpow(fact[N2], MOD - 2);
        if (a_val == 1) {
            for (int i = N2; i >= 1; --i)
                inv_fact[i - 1] = (ll)inv_fact[i] * i % MOD;
        } else {
            for (int i = N2; i >= 1; --i) {
                uint term = pow_a[i] - 1 + MOD;
                if (term >= MOD) term -= MOD;
                inv_fact[i - 1] = (ll)inv_fact[i] * term % MOD;
            }
        }

        int ntt_size = 1;
        while (ntt_size <= 2 * N + 1) ntt_size <<= 1;

        vector<uint> B(ntt_size);
        for (int t = 0; t <= N2; ++t) B[t] = fact[t];
        vector<uint> B_ntt = B;
        ntt(B_ntt, false);

        vector<uint> A(ntt_size), A_ntt(ntt_size), C(ntt_size);

        for (int m = 1; m <= N; ++m) {
            fill(A.begin(), A.end(), 0);
            int base_m = idx(m, 1);
            for (int r = 1; r <= m; ++r)
                A[m - r] = (ll)H[base_m + r - 1] * inv_fact[r] % MOD;

            copy(A.begin(), A.end(), A_ntt.begin());
            ntt(A_ntt, false);
            for (int i = 0; i < ntt_size; ++i)
                C[i] = (ll)A_ntt[i] * B_ntt[i] % MOD;
            ntt(C, true);

            uint coef_m = pow_b[m];
            int k_max = N1 - m;
            for (int k = 1; k <= k_max; ++k) {
                int conv_idx = m + k - 1;
                ll val = (ll)coef_m * powbinom[k] % MOD * inv_fact[k - 1] % MOD * C[conv_idx] % MOD;
                H[idx(m + k, k)] = (uint)val;
            }
        }
    } else {
        vector<int> dk_start(N2 + 2);
        dk_start[1] = 0;
        for (int k = 2; k <= N2 + 1; ++k)
            dk_start[k] = dk_start[k - 1] + (N2 - (k - 1));

        vector<uint> qb_diag(dk_start[N2 + 1]);
        vector<uint> qb_prev(N2 + 1), qb_curr(N2 + 1);
        qb_prev[0] = 1;

        for (int n = 1; n <= N2; ++n) {
            qb_curr[0] = 1;
            if (n <= N2) qb_curr[n] = 1;
            uint *__restrict cur = qb_curr.data();
            uint *__restrict prv = qb_prev.data();
            for (int k = 1; k < n; ++k)
                cur[k] = ((ll)prv[k - 1] + (ll)pow_a[k] * prv[k]) % MOD;
            if (n < N2) {
                for (int r = 1; r <= n; ++r) {
                    int c = n - r;
                    qb_diag[dk_start[c + 1] + (r - 1)] = (ll)cur[r] * powbinom[c + 1] % MOD;
                }
            }
            qb_prev.swap(qb_curr);
        }
        { vector<uint>().swap(qb_prev); vector<uint>().swap(qb_curr); }

        for (int d = 1; d <= N; ++d) {
            int h_base = d * (d + 1) / 2;
            const uint *__restrict h_ptr = &H[h_base + 1];
            const uint coef_d = pow_b[d];
            int k_max = N1 - d;
            int idx_cur = (d + 1) * (d + 2) / 2 + 1;
            int idx_inc = d + 3;

            for (int k = 1; k <= k_max; ++k) {
                const uint *__restrict p = &qb_diag[dk_start[k]];
                const uint *__restrict q = h_ptr;
                int cnt = d;
                __int128 sum = 0;

                while (cnt >= 8) {
                    ull a0 = (ull)p[0] * q[0];
                    ull a1 = (ull)p[1] * q[1];
                    ull a2 = (ull)p[2] * q[2];
                    ull a3 = (ull)p[3] * q[3];
                    ull a4 = (ull)p[4] * q[4];
                    ull a5 = (ull)p[5] * q[5];
                    ull a6 = (ull)p[6] * q[6];
                    ull a7 = (ull)p[7] * q[7];
                    sum += (__int128)(a0 + a1 + a2 + a3 + a4 + a5 + a6 + a7);
                    p += 8; q += 8; cnt -= 8;
                }
                while (cnt--) sum += (ull)(*p++) * (*q++);

                H[idx_cur] = (ll)coef_d * (uint)(sum % MOD) % MOD;
                idx_cur += idx_inc;
                ++idx_inc;
            }
        }
    }

    vector<uint> a_baseline(N + 1);
    a_baseline[0] = 1;
    for (int n = 1; n <= N; ++n)
        a_baseline[n] = (ll)a_baseline[n - 1] * pow_a[n] % MOD;

    for (int n = 1; n <= N; ++n) {
        ll fn = (ll)a_baseline[n] * inv_pow_b[n] % MOD * H[idx(n + 1, 1)] % MOD;
        printf("%u%c", (uint)fn, n < N ? ' ' : '\n');
    }

    return 0;
}