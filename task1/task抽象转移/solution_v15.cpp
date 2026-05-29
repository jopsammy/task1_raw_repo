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

int detect_order(uint a, int limit) {
    if (a == 1) return 1;
    uint cur = a;
    for (int d = 1; d <= limit; ++d) {
        if (cur == 1) return d;
        cur = (ll)cur * a % MOD;
    }
    return limit;
}

int main() {
    int N, a_val, b_val;
    if (scanf("%d%d%d", &N, &a_val, &b_val) != 3) return 1;
    a_val %= MOD; b_val %= MOD;

    int N1 = N + 1;
    int N2 = N + 2;
    int N3 = N + 3;

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

    int order_d = detect_order(a_val, N3);

    if (order_d > N + 2) {
        vector<uint> fact(N2 + 1);
        fact[0] = 1;
        if (a_val == 1) {
            for (int i = 1; i <= N2; ++i)
                fact[i] = (ll)fact[i - 1] * i % MOD;
        } else {
            for (int i = 1; i <= N2; ++i) {
                uint term = pow_a[i] - 1 + MOD;
                if (term >= MOD) term -= MOD;
                fact[i] = (ll)fact[i - 1] * term % MOD;
            }
        }

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
    } else if (order_d == 1) {
        if (b_val == 1) {
            vector<uint> fac(2 * N1 + 1), inv_fac(2 * N1 + 1);
            fac[0] = 1;
            for (int i = 1; i <= 2 * N1; ++i)
                fac[i] = (ll)fac[i - 1] * i % MOD;
            inv_fac[2 * N1] = modpow(fac[2 * N1], MOD - 2);
            for (int i = 2 * N1; i >= 1; --i)
                inv_fac[i - 1] = (ll)inv_fac[i] * i % MOD;
            auto binom = [&](int n, int k) -> uint {
                if (k < 0 || k > n) return 0;
                return (ll)fac[n] * inv_fac[k] % MOD * inv_fac[n - k] % MOD;
            };
            for (int n = 1; n <= N; ++n) {
                uint c = binom(2 * n, n);
                c = (ll)c * modpow(n + 1, MOD - 2) % MOD;
                printf("%u%c", c, n < N ? ' ' : '\n');
            }
            return 0;
        }

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
                cur[k] = (prv[k - 1] + prv[k]) % MOD;
            if (n < N2) {
                for (int r = 1; r <= n; ++r) {
                    int c = n - r;
                    qb_diag[dk_start[c + 1] + (r - 1)] = cur[r];
                }
            }
            qb_prev.swap(qb_curr);
        }
        { vector<uint>().swap(qb_prev); vector<uint>().swap(qb_curr); }

        for (int md = 1; md <= N; ++md) {
            int h_base = md * (md + 1) / 2;
            const uint *__restrict h_ptr = &H[h_base + 1];
            const uint coef_d = pow_b[md];
            int k_max = N1 - md;
            int idx_cur = (md + 1) * (md + 2) / 2 + 1;
            int idx_inc = md + 3;

            for (int k = 1; k <= k_max; ++k) {
                const uint *__restrict p = &qb_diag[dk_start[k]];
                const uint *__restrict q = h_ptr;
                int cnt = md;
                unsigned __int128 sum = 0;

                while (cnt >= 8) {
                    ull a0 = (ull)p[0] * q[0];
                    ull a1 = (ull)p[1] * q[1];
                    ull a2 = (ull)p[2] * q[2];
                    ull a3 = (ull)p[3] * q[3];
                    ull a4 = (ull)p[4] * q[4];
                    ull a5 = (ull)p[5] * q[5];
                    ull a6 = (ull)p[6] * q[6];
                    ull a7 = (ull)p[7] * q[7];
                    sum += (unsigned __int128)(a0 + a1 + a2 + a3 + a4 + a5 + a6 + a7);
                    p += 8; q += 8; cnt -= 8;
                }
                while (cnt--) sum += (unsigned __int128)(ull)(*p++) * (*q++);

                H[idx_cur] = (ll)coef_d * (uint)(sum % MOD) % MOD;
                idx_cur += idx_inc;
                ++idx_inc;
            }
        }
    } else {
        int d = order_d;

        vector<uint> qfact(d);
        qfact[0] = 1;
        for (int t = 1; t < d; ++t)
            qfact[t] = (ll)qfact[t - 1] * (pow_a[t] - 1 + MOD) % MOD;

        vector<uint> inv_qfact(d);
        inv_qfact[d - 1] = modpow(qfact[d - 1], MOD - 2);
        for (int t = d - 1; t >= 1; --t)
            inv_qfact[t - 1] = (ll)inv_qfact[t] * (pow_a[t] - 1 + MOD) % MOD;

        int max_quot = N2 / d + 2;
        int max_fac = N2 + 2;
        vector<uint> ord_fac(max_fac), ord_inv(max_fac);
        ord_fac[0] = 1;
        for (int i = 1; i < max_fac; ++i)
            ord_fac[i] = (ll)ord_fac[i - 1] * i % MOD;
        ord_inv[max_fac - 1] = modpow(ord_fac[max_fac - 1], MOD - 2);
        for (int i = max_fac - 1; i >= 1; --i)
            ord_inv[i - 1] = (ll)ord_inv[i] * i % MOD;
        auto ord_binom = [&](int n, int k) -> uint {
            if (k < 0 || k > n) return 0;
            return (ll)ord_fac[n] * ord_inv[k] % MOD * ord_inv[n - k] % MOD;
        };

        vector<vector<uint>> small_qbinom(d + 1, vector<uint>(d));
        for (int ko = 1; ko <= d; ++ko) {
            for (int ro = 0; ro < d; ++ro) {
                if (ro == 0) {
                    small_qbinom[ko][ro] = 1;
                } else if (ro + ko - 1 < d) {
                    uint num = qfact[ro + ko - 1];
                    uint den = (ll)qfact[ro] * qfact[ko - 1] % MOD;
                    small_qbinom[ko][ro] = (ll)num * modpow(den, MOD - 2) % MOD;
                } else {
                    small_qbinom[ko][ro] = 0;
                }
            }
        }

        bool use_residue_ntt = (d >= 64);
        bool use_quotient_ntt = (N / d >= 64);

        if (use_residue_ntt && use_quotient_ntt) {
            int ntt_rem_size = 1;
            while (ntt_rem_size < 2 * d) ntt_rem_size <<= 1;
            vector<uint> B_rem(ntt_rem_size);
            for (int t = 0; t < d; ++t) B_rem[t] = qfact[t];
            vector<uint> B_rem_ntt = B_rem;
            ntt(B_rem_ntt, false);

            vector<uint> A_rem(ntt_rem_size), A_rem_ntt(ntt_rem_size), C_rem(ntt_rem_size);

            int ntt_quot_size = 1;
            while (ntt_quot_size < 2 * max_quot) ntt_quot_size <<= 1;

            vector<uint> B_quot(ntt_quot_size);
            for (int t = 0; t < max_quot; ++t) B_quot[t] = ord_fac[t];
            vector<uint> B_quot_ntt = B_quot;
            ntt(B_quot_ntt, false);

            vector<uint> B_borrow(ntt_quot_size);
            B_borrow[0] = 0;
            for (int t = 1; t < max_quot; ++t) B_borrow[t] = ord_fac[t - 1];
            vector<uint> B_borrow_ntt = B_borrow;
            ntt(B_borrow_ntt, false);

            vector<uint> A_quot(ntt_quot_size), A_quot_ntt(ntt_quot_size), C_quot(ntt_quot_size);

            vector<vector<uint>> inner_store(max_quot, vector<uint>(d + 1));

            for (int m = 1; m <= N; ++m) {
                int max_r1 = m / d;
                uint coef_m = pow_b[m];

                for (int r1 = 0; r1 <= max_r1; ++r1) {
                    fill(A_rem.begin(), A_rem.end(), 0);
                    for (int t = 0; t < d; ++t) {
                        int r = r1 * d + t;
                        if (r >= 1 && r <= m)
                            A_rem[t] = (ll)H[idx(m, r)] * inv_qfact[t] % MOD;
                    }
                    for (int t = 0; t < d; ++t)
                        A_rem_ntt[d - 1 - t] = A_rem[t];
                    for (int t = d; t < ntt_rem_size; ++t)
                        A_rem_ntt[t] = 0;
                    ntt(A_rem_ntt, false);
                    for (int i = 0; i < ntt_rem_size; ++i)
                        C_rem[i] = (ll)A_rem_ntt[i] * B_rem_ntt[i] % MOD;
                    ntt(C_rem, true);

                    for (int ko = 1; ko <= d; ++ko) {
                        int conv_idx = d + ko - 2;
                        if (conv_idx < ntt_rem_size) {
                            uint val = C_rem[conv_idx];
                            val = (ll)val * inv_qfact[ko - 1] % MOD;
                            inner_store[r1][ko] = val;
                        }
                    }
                    inner_store[r1][0] = H[idx(m, r1 * d)];
                }

                for (int ko = 1; ko <= d; ++ko) {
                    if (ko > N1 - m) break;
                    fill(A_quot.begin(), A_quot.end(), 0);
                    for (int r1 = 0; r1 <= max_r1; ++r1) {
                        uint in_val = inner_store[r1][ko];
                        if (in_val)
                            A_quot[max_r1 - r1] = (ll)in_val * ord_inv[r1] % MOD;
                    }
                    copy(A_quot.begin(), A_quot.end(), A_quot_ntt.begin());
                    ntt(A_quot_ntt, false);
                    for (int i = 0; i < ntt_quot_size; ++i)
                        C_quot[i] = (ll)A_quot_ntt[i] * B_quot_ntt[i] % MOD;
                    ntt(C_quot, true);

                    int k1_max = (N1 - m - ko) / d;
                    for (int k1 = 0; k1 <= k1_max; ++k1) {
                        int conv_idx = max_r1 + k1;
                        if (conv_idx < ntt_quot_size) {
                            int k = k1 * d + ko;
                            uint val = (ll)C_quot[conv_idx] * ord_inv[k1] % MOD;
                            val = (ll)val * coef_m % MOD * powbinom[k] % MOD;
                            if (k >= 1 && k <= N1 - m)
                                H[idx(m + k, k)] = val;
                        }
                    }
                }

                {
                    fill(A_quot.begin(), A_quot.end(), 0);
                    for (int r1 = 0; r1 <= max_r1; ++r1) {
                        uint in_val = inner_store[r1][0];
                        if (in_val)
                            A_quot[max_r1 - r1] = (ll)in_val * ord_inv[r1] % MOD;
                    }
                    copy(A_quot.begin(), A_quot.end(), A_quot_ntt.begin());
                    ntt(A_quot_ntt, false);
                    for (int i = 0; i < ntt_quot_size; ++i)
                        C_quot[i] = (ll)A_quot_ntt[i] * B_borrow_ntt[i] % MOD;
                    ntt(C_quot, true);

                    int k1_max = (N1 - m) / d;
                    for (int k1 = 1; k1 <= k1_max; ++k1) {
                        int conv_idx = max_r1 + k1;
                        if (conv_idx < ntt_quot_size && k1 - 1 >= 0) {
                            int k = k1 * d;
                            uint val = (ll)C_quot[conv_idx] * ord_inv[k1 - 1] % MOD;
                            val = (ll)val * coef_m % MOD * powbinom[k] % MOD;
                            if (k >= 1 && k <= N1 - m)
                                H[idx(m + k, k)] = val;
                        }
                    }
                }
            }
        } else if (use_residue_ntt && !use_quotient_ntt) {
            int ntt_rem_size = 1;
            while (ntt_rem_size < 2 * d) ntt_rem_size <<= 1;
            vector<uint> B_rem(ntt_rem_size);
            for (int t = 0; t < d; ++t) B_rem[t] = qfact[t];
            vector<uint> B_rem_ntt = B_rem;
            ntt(B_rem_ntt, false);

            vector<uint> A_rem(ntt_rem_size), A_rem_ntt(ntt_rem_size), C_rem(ntt_rem_size);
            vector<vector<uint>> inner_store(max_quot, vector<uint>(d + 1));

            for (int m = 1; m <= N; ++m) {
                int max_r1 = m / d;
                uint coef_m = pow_b[m];

                for (int r1 = 0; r1 <= max_r1; ++r1) {
                    fill(A_rem.begin(), A_rem.end(), 0);
                    for (int t = 0; t < d; ++t) {
                        int r = r1 * d + t;
                        if (r >= 1 && r <= m)
                            A_rem[t] = (ll)H[idx(m, r)] * inv_qfact[t] % MOD;
                    }
                    for (int t = 0; t < d; ++t)
                        A_rem_ntt[d - 1 - t] = A_rem[t];
                    for (int t = d; t < ntt_rem_size; ++t)
                        A_rem_ntt[t] = 0;
                    ntt(A_rem_ntt, false);
                    for (int i = 0; i < ntt_rem_size; ++i)
                        C_rem[i] = (ll)A_rem_ntt[i] * B_rem_ntt[i] % MOD;
                    ntt(C_rem, true);

                    for (int ko = 1; ko <= d; ++ko) {
                        int conv_idx = d + ko - 2;
                        if (conv_idx < ntt_rem_size) {
                            uint val = C_rem[conv_idx];
                            val = (ll)val * inv_qfact[ko - 1] % MOD;
                            inner_store[r1][ko] = val;
                        }
                    }
                    int rr = r1 * d;
                    if (rr >= 1 && rr <= m)
                        inner_store[r1][0] = H[idx(m, rr)];
                }

                int k_max = N1 - m;
                for (int k = 1; k <= k_max; ++k) {
                    int k1 = k / d;
                    int k0 = k % d;
                    unsigned __int128 sum = 0;

                    if (k0 == 0) {
                        for (int r1 = 0; r1 <= max_r1 && r1 + k1 - 1 >= 0; ++r1) {
                            uint in_val = inner_store[r1][0];
                            if (in_val == 0) continue;
                            sum += (unsigned __int128)(ull)ord_binom(r1 + k1 - 1, r1) * in_val;
                        }
                    } else {
                        for (int r1 = 0; r1 <= max_r1; ++r1) {
                            uint in_val = inner_store[r1][k0];
                            if (in_val == 0) continue;
                            sum += (unsigned __int128)(ull)ord_binom(r1 + k1, r1) * in_val;
                        }
                    }
                    sum %= MOD;
                    H[idx(m + k, k)] = (ll)coef_m * powbinom[k] % MOD * (uint)(sum % MOD) % MOD;
                }
            }
        } else if (!use_residue_ntt && use_quotient_ntt) {
            int ntt_quot_size = 1;
            while (ntt_quot_size < 2 * max_quot) ntt_quot_size <<= 1;

            vector<uint> B_quot(ntt_quot_size);
            for (int t = 0; t < max_quot; ++t) B_quot[t] = ord_fac[t];
            vector<uint> B_quot_ntt = B_quot;
            ntt(B_quot_ntt, false);

            vector<uint> B_borrow(ntt_quot_size);
            B_borrow[0] = 0;
            for (int t = 1; t < max_quot; ++t) B_borrow[t] = ord_fac[t - 1];
            vector<uint> B_borrow_ntt = B_borrow;
            ntt(B_borrow_ntt, false);

            vector<uint> A_quot(ntt_quot_size), A_quot_ntt(ntt_quot_size), C_quot(ntt_quot_size);
            vector<uint> I_flat((max_quot + 2) * (d + 1));

            for (int m = 1; m <= N; ++m) {
                int max_r1 = m / d;
                uint coef_m = pow_b[m];

                int I_len = (max_r1 + 1) * (d + 1);
                fill(I_flat.begin(), I_flat.begin() + I_len, 0);

                for (int r1 = 0; r1 <= max_r1; ++r1) {
                    uint *__restrict ires = &I_flat[r1 * (d + 1)];
                    for (int r0 = 0; r0 < d; ++r0) {
                        int r = r1 * d + r0;
                        if (r < 1 || r > m) continue;
                        uint h_val = H[idx(m, r)];
                        for (int k0 = 1; k0 < d; ++k0) {
                            if (r0 + k0 > d) break;
                            ires[k0] = (ires[k0] + (ll)small_qbinom[k0][r0] * h_val) % MOD;
                        }
                    }
                    int rb = r1 * d;
                    if (rb >= 1 && rb <= m)
                        ires[0] = H[idx(m, rb)];
                }

                for (int k0 = 1; k0 < d; ++k0) {
                    if (k0 > N1 - m) break;
                    fill(A_quot.begin(), A_quot.end(), 0);
                    for (int r1 = 0; r1 <= max_r1; ++r1) {
                        uint in_val = I_flat[r1 * (d + 1) + k0];
                        if (in_val)
                            A_quot[max_r1 - r1] = (ll)in_val * ord_inv[r1] % MOD;
                    }
                    copy(A_quot.begin(), A_quot.end(), A_quot_ntt.begin());
                    ntt(A_quot_ntt, false);
                    for (int i = 0; i < ntt_quot_size; ++i)
                        C_quot[i] = (ll)A_quot_ntt[i] * B_quot_ntt[i] % MOD;
                    ntt(C_quot, true);

                    int k1_max = (N1 - m - k0) / d;
                    for (int k1 = 0; k1 <= k1_max; ++k1) {
                        int conv_idx = max_r1 + k1;
                        if (conv_idx < ntt_quot_size) {
                            int k = k1 * d + k0;
                            uint val = (ll)C_quot[conv_idx] * ord_inv[k1] % MOD;
                            val = (ll)val * coef_m % MOD * powbinom[k] % MOD;
                            if (k >= 1 && k <= N1 - m)
                                H[idx(m + k, k)] = val;
                        }
                    }
                }

                {
                    fill(A_quot.begin(), A_quot.end(), 0);
                    for (int r1 = 0; r1 <= max_r1; ++r1) {
                        uint in_val = I_flat[r1 * (d + 1)];
                        if (in_val)
                            A_quot[max_r1 - r1] = (ll)in_val * ord_inv[r1] % MOD;
                    }
                    copy(A_quot.begin(), A_quot.end(), A_quot_ntt.begin());
                    ntt(A_quot_ntt, false);
                    for (int i = 0; i < ntt_quot_size; ++i)
                        C_quot[i] = (ll)A_quot_ntt[i] * B_borrow_ntt[i] % MOD;
                    ntt(C_quot, true);

                    int k1_max = (N1 - m) / d;
                    for (int k1 = 1; k1 <= k1_max; ++k1) {
                        int conv_idx = max_r1 + k1;
                        if (conv_idx < ntt_quot_size) {
                            int k = k1 * d;
                            uint val = (ll)C_quot[conv_idx] * ord_inv[k1 - 1] % MOD;
                            val = (ll)val * coef_m % MOD * powbinom[k] % MOD;
                            if (k >= 1 && k <= N1 - m)
                                H[idx(m + k, k)] = val;
                        }
                    }
                }
            }
        } else {
            for (int m = 1; m <= N; ++m) {
                int max_r1 = m / d;
                uint coef_m = pow_b[m];
                int k_max = N1 - m;

                for (int k = 1; k <= k_max; ++k) {
                    int k1 = k / d;
                    int k0 = k % d;
                    unsigned __int128 sum = 0;

                    if (k0 == 0) {
                        for (int r1 = 0; r1 <= max_r1 && r1 + k1 - 1 >= 0; ++r1) {
                            int r = r1 * d;
                            if (r < 1 || r > m) continue;
                            sum += (unsigned __int128)(ull)ord_binom(r1 + k1 - 1, r1) * H[idx(m, r)];
                        }
                    } else {
                        for (int r1 = 0; r1 <= max_r1; ++r1) {
                            unsigned __int128 inner = 0;
                            for (int r0 = 0; r0 < d && r0 + k0 <= d; ++r0) {
                                int r = r1 * d + r0;
                                if (r < 1 || r > m) continue;
                                inner += (unsigned __int128)(ull)small_qbinom[k0][r0] * H[idx(m, r)];
                            }
                            if (inner == 0) continue;
                            inner %= MOD;
                            sum += (unsigned __int128)(ull)ord_binom(r1 + k1, r1) * (uint)(inner % MOD);
                        }
                    }
                    sum %= MOD;
                    H[idx(m + k, k)] = (ll)coef_m * powbinom[k] % MOD * (uint)(sum % MOD) % MOD;
                }
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
