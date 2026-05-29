#pragma GCC optimize("O3")
#pragma GCC optimize("unroll-loops")

#include <cstdio>
#include <cstdint>
#include <vector>
using namespace std;
typedef long long ll;
typedef unsigned int uint;
typedef unsigned long long ull;
const uint MOD = 998244353;

uint modpow(uint a, ll e) {
    uint r = 1;
    while (e) {
        if (e & 1) r = (ll)r * a % MOD;
        a = (ll)a * a % MOD;
        e >>= 1;
    }
    return r;
}

int main() {
    int N, a_val, b_val;
    if (scanf("%d%d%d", &N, &a_val, &b_val) != 3) return 1;
    a_val %= MOD; b_val %= MOD;
    if (N == 0) return 0;

    int N1 = N + 1;
    int N2 = N + 2;

    auto idx = [](int n, int k) { return n * (n + 1) / 2 + k; };
    int flat_size = idx(N2, N2) + 1;
    vector<uint> H(flat_size);

    vector<uint> pow_a(N2 + 1);
    pow_a[0] = 1;
    for (int i = 1; i <= N2; ++i)
        pow_a[i] = (ll)pow_a[i - 1] * a_val % MOD;

    vector<uint> pow_b(N2 + 1);
    pow_b[0] = 1;
    for (int i = 1; i <= N2; ++i)
        pow_b[i] = (ll)pow_b[i - 1] * b_val % MOD;

    uint inv_b = modpow(b_val, MOD - 2);
    vector<uint> inv_pow_b(N2 + 1);
    inv_pow_b[0] = 1;
    for (int i = 1; i <= N2; ++i)
        inv_pow_b[i] = (ll)inv_pow_b[i - 1] * inv_b % MOD;

    vector<uint> powbinom(N2 + 1);
    powbinom[0] = 1;
    for (int k = 1; k <= N2; ++k)
        powbinom[k] = (ll)powbinom[k - 1] * pow_a[k - 1] % MOD;

    vector<int> dk_start(N2 + 2);
    dk_start[1] = 0;
    for (int k = 2; k <= N2 + 1; ++k)
        dk_start[k] = dk_start[k - 1] + (N2 - (k - 1));

    vector<uint> qb_diag(dk_start[N2 + 1]);

    vector<uint> qb_prev(N2 + 1);
    vector<uint> qb_curr(N2 + 1);
    qb_prev[0] = 1;

    for (int n = 1; n <= N2; ++n) {
        qb_curr[0] = 1;
        if (n <= N2) qb_curr[n] = 1;
        uint *__restrict cur = qb_curr.data();
        uint *__restrict prv = qb_prev.data();
        for (int k = 1; k < n; ++k) {
            cur[k] = ((ll)prv[k - 1] + (ll)pow_a[k] * prv[k]) % MOD;
        }
        if (n < N2) {
            for (int r = 1; r <= n; ++r) {
                int c = n - r;
                qb_diag[dk_start[c + 1] + (r - 1)] = (ll)cur[r] * powbinom[c + 1] % MOD;
            }
        }
        qb_prev.swap(qb_curr);
    }
    {
        vector<uint>().swap(qb_prev);
        vector<uint>().swap(qb_curr);
    }

    H[idx(1, 1)] = powbinom[1];
    for (int n = 2; n <= N1; ++n)
        H[idx(n, n)] = powbinom[n];

    for (int d = 1; d <= N; ++d) {
        int h_base = d * (d + 1) / 2;
        const uint *__restrict h_ptr = &H[h_base + 1];
        const uint coef_d = pow_b[d];

        int k_max = N1 - d;
        int idx_cur = (d + 1) * (d + 2) / 2 + 1;
        int idx_inc = d + 3;
        int d16 = d & ~15;

        for (int k = 1; k <= k_max; ++k) {
            const uint *__restrict p = &qb_diag[dk_start[k]];
            const uint *__restrict q = h_ptr;

            unsigned __int128 sum0 = 0, sum1 = 0;
            int i = 0;

            for (; i < d16; i += 16) {
                ull a0 = (ull)p[i+0] * q[i+0];
                ull a1 = (ull)p[i+1] * q[i+1];
                ull a2 = (ull)p[i+2] * q[i+2];
                ull a3 = (ull)p[i+3] * q[i+3];
                sum0 += (unsigned __int128)(a0 + a1 + a2 + a3);

                ull a4 = (ull)p[i+4] * q[i+4];
                ull a5 = (ull)p[i+5] * q[i+5];
                ull a6 = (ull)p[i+6] * q[i+6];
                ull a7 = (ull)p[i+7] * q[i+7];
                sum0 += (unsigned __int128)(a4 + a5 + a6 + a7);

                ull b0 = (ull)p[i+8] * q[i+8];
                ull b1 = (ull)p[i+9] * q[i+9];
                ull b2 = (ull)p[i+10] * q[i+10];
                ull b3 = (ull)p[i+11] * q[i+11];
                sum1 += (unsigned __int128)(b0 + b1 + b2 + b3);

                ull b4 = (ull)p[i+12] * q[i+12];
                ull b5 = (ull)p[i+13] * q[i+13];
                ull b6 = (ull)p[i+14] * q[i+14];
                ull b7 = (ull)p[i+15] * q[i+15];
                sum1 += (unsigned __int128)(b4 + b5 + b6 + b7);
            }
            sum0 += sum1;
            for (i = d16; i < d; ++i)
                sum0 += (unsigned __int128)(ull)p[i] * q[i];

            H[idx_cur] = (ll)coef_d * (uint)(sum0 % MOD) % MOD;
            idx_cur += idx_inc;
            ++idx_inc;
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
