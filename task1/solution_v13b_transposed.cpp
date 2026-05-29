#pragma GCC optimize("O3")
#pragma GCC optimize("unroll-loops")

#include <cstdio>
#include <cstdint>
#include <vector>
#include <cstring>
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

    vector<int> row_start(N2 + 1);
    row_start[0] = 0;
    for (int r = 1; r <= N2; ++r)
        row_start[r] = row_start[r - 1] + (N2 - (r - 1));

    vector<uint> qb_diag_T(row_start[N2]);

    {
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
                    qb_diag_T[row_start[r - 1] + (c)] = (ll)cur[r] * powbinom[c + 1] % MOD;
                }
            }
            qb_prev.swap(qb_curr);
        }
    }

    H[idx(1, 1)] = powbinom[1];
    for (int n = 2; n <= N1; ++n)
        H[idx(n, n)] = powbinom[n];

    unsigned __int128 *accum = new unsigned __int128[N2 + 1]();

    for (int d = 1; d <= N; ++d) {
        int h_base = d * (d + 1) / 2;
        const uint *__restrict h_ptr = &H[h_base + 1];
        const uint coef_d = pow_b[d];

        int k_max = N1 - d;

        for (int i = 1; i <= k_max; ++i) accum[i] = 0;

        for (int r = 0; r < d; ++r) {
            ull hr = h_ptr[r];
            if (hr == 0) continue;
            const uint *__restrict row = &qb_diag_T[row_start[r]];
            unsigned __int128 *__restrict acc = accum + 1;

            int k = 0;
            for (; k + 7 < k_max; k += 8) {
                acc[k+0] += (unsigned __int128)(ull)row[k+0] * hr;
                acc[k+1] += (unsigned __int128)(ull)row[k+1] * hr;
                acc[k+2] += (unsigned __int128)(ull)row[k+2] * hr;
                acc[k+3] += (unsigned __int128)(ull)row[k+3] * hr;
                acc[k+4] += (unsigned __int128)(ull)row[k+4] * hr;
                acc[k+5] += (unsigned __int128)(ull)row[k+5] * hr;
                acc[k+6] += (unsigned __int128)(ull)row[k+6] * hr;
                acc[k+7] += (unsigned __int128)(ull)row[k+7] * hr;
            }
            for (; k < k_max; ++k)
                acc[k] += (unsigned __int128)(ull)row[k] * hr;
        }

        int idx_cur = (d + 1) * (d + 2) / 2 + 1;
        int idx_inc = d + 3;

        for (int k = 1; k <= k_max; ++k) {
            H[idx_cur] = (ll)coef_d * (uint)(accum[k] % MOD) % MOD;
            idx_cur += idx_inc;
            ++idx_inc;
        }
    }

    delete[] accum;

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
