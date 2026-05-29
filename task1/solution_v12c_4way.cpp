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

        for (int k = 1; k <= k_max; ++k) {
            const uint *__restrict p = &qb_diag[dk_start[k]];
            const uint *__restrict q = h_ptr;
            int cnt = d;

            __int128 sum = 0;

            while (cnt >= 4) {
                ull t0 = (ull)p[0] * q[0];
                ull t1 = (ull)p[1] * q[1];
                ull t2 = (ull)p[2] * q[2];
                ull t3 = (ull)p[3] * q[3];
                sum += (__int128)(t0 + t1 + t2 + t3);
                p += 4; q += 4; cnt -= 4;
            }
            while (cnt--)
                sum += (ull)(*p++) * (*q++);

            H[idx_cur] = (ll)coef_d * (uint)(sum % MOD) % MOD;
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
