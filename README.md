# Task1 — Bracket String Weighted Counting / 括号串加权计数

[![AC Nowcoder](https://img.shields.io/badge/AC%20Nowcoder-21%2F21-brightgreen)](https://ac.nowcoder.com/acm/contest/129209/F)
[![Complexity](https://img.shields.io/badge/Complexity-O(N%C2%B2%20log%20N)-blue)](#)
[![Language](https://img.shields.io/badge/Language-C%2B%2B17-orange)](#)
[![Status](https://img.shields.io/badge/Status-Closed-9cf)](#)

---

## 📖 题目简述 / Problem Summary

给定整数 `n, a, b` (1 ≤ n ≤ 5000)，对每个 `i = 1..n`，计算：

$$F[i] = \sum_{s \in \mathcal{D}_i} a^{\,\text{alice}(s)} \times b^{\,\text{bob}(s)} \pmod{998244353}$$

其中 $\mathcal{D}_i$ 为所有长度为 $2i$ 的合法括号串的集合。`alice(s)` 为 s 中 `"()"` 子序列个数（有序对 `(i,j)`, `s[i]='('`, `s[j]=')'`, `i<j`）；`bob(s)` 由一种前缀高度回零迭代算法计算。

> Given integers `n, a, b` (1 ≤ n ≤ 5000), for each `i = 1..n`, compute the formula above, where $\mathcal{D}_i$ is all valid bracket strings of length $2i$. `alice(s)` counts `"()"` subsequences; `bob(s)` is computed via a prefix-height-reset iterative algorithm.

---

## 🎯 核心洞察 / Key Insight

本问题等价于求 **(q,t)-Catalan 数**在参数 `a,b` 下的评值：`alice(s) = area(π) + n(n+1)/2`，`bob(s) = bounce(π)`（精确相等）。模数 `998244353 = 119 × 2²³ + 1` 是 NTT 友好素数——出题人的强烈暗示。

> The problem is equivalent to evaluating the **(q,t)-Catalan polynomial** with parameters `a`, `b`. The modulus is NTT-friendly — a strong hint from the problem setter that NTT convolution is intended.

---

## 🧠 算法方案 / Solution

**最终算法** — [`solution.cpp`](solution.cpp)：**q-Lucas 分解 + 四子路径混合自适应 NTT**。二维 NTT（余数层 + 商层），全 `(a,b)` 统一 O(N² log N)，纯标量无 SIMD/OpenMP，内存 ~100–200 MB。

> **Final algorithm**: q-Lucas decomposition + 4-sub-path hybrid adaptive NTT. Two-dimensional NTT (residue-layer + quotient-layer), unified O(N² log N) for all (a,b), pure scalar, ~100–200 MB.

---

## ✅ 判题结果 / Result

| 指标 | 值 |
|------|-----|
| 正确性 / Correctness | **21/21** all passed |
| 用时 / Time | 7.76s (好a) / 6.33s (坏a) |
| 内存 / Memory | ~100–200 MB |
| 评测链接 / Verdict | [牛客网 All Accepted](https://ac.nowcoder.com/acm/contest/129209/F) |

---

## 📁 仓库结构 / Repository Structure

此为**原始研究仓**——全部过程文件、验证文件、锚点文件均保留于此。

> This is the **original research repository** — all process files, verification scripts, and anchor documents are preserved here.

```text
task1/
├── solution.cpp               # 🔥 最终算法 / Final solution (21/21)
├── task1.md                   # 题目原文 / Problem statement (Chinese)
│
├── .trae/                     # AC范式规则体系与研究锚点系统
│   ├── specs/solve-bracket-dp/     # 任务级锚点文件 / Task-level anchors
│   │   ├── spec.md                 # ★ 当前权威真相源 / Authoritative source of truth
│   │   ├── tasks.md                # 任务列表 / Task list
│   │   ├── checklist.md            # 验证清单 GATE-1~5 / Verification checklist
│   │   ├── current-note.md         # 完整研究日志 1550+行 / Full research log
│   │   ├── derivation.md           # 早期推导（归档） / Early derivation (archived)
│   │   ├── derivation-v2.md        # x-seq 推导（归档） / x-seq derivation (archived)
│   │   ├── stage2-tree-strategy.md # 阶段档案 / Stage archive
│   │   └── blind-spot-analysis-note-*.md  # 盲点分析笔记 / Blind-spot notes
│   └── documents/
│       └── 20260524_解题_任务闭合交付.md  # 闭合交付记录 / Closure delivery
│
├── orbit_dp.py → orbit_dp_v14.py    # DP 迭代版本 v1~v14 / DP iterations
├── ntt_v14_ref.py                   # NTT 参考实现 / NTT reference
├── analyze_*.py                     # 分析脚本 / Analysis scripts
├── debug_*.py                       # 调试脚本 / Debug scripts
├── verify_*.py                      # 验证脚本 / Verification scripts
├── bench_*.exe / bench_*.py         # 性能基准 / Benchmarks
├── route_*_probe.py                 # 路线探索 / Route probes
├── derive_*.py                      # 数学推导 / Derivation scripts
└── ...
```

---

## 🗺️ 研究历程 / Research Journey

历时约 102 小时 (2026.05.20–25)，五阶段突破。13+ 条失败路线被严格 brute-force 反例永久关闭，共同死因：wrapping `A→(A)` 等价于完整高度函数，信息维度 O(2ᵏ) 不可低维压缩。

> ~102 hours over 5 phases. 13+ failed routes permanently closed — the wrapping `A→(A)` requires the full height function (O(2ᵏ) info dimension), incompressible.

| 阶段 / Phase | 描述 / Description | 结果 / Outcome |
|------|------|------|
| **阶段一** Phase 1 | 组合分解路线 A–K，13+ 条尝试 / Combinatorial decomposition | 全部受阻——wrapping 不可压缩 / All failed |
| **阶段二** Phase 2 | 范式转换：(q,t)-Catalan Garsia-Haglund 递推 / Paradigm shift | 建立 O(N³/6) 基线 / Baseline established |
| **阶段三** Phase 3 | 纯标量极限优化 v1–v13 / Pure scalar optimization | v11 8路ILP 8.89s@Zen4，但判题机慢 12–15% |
| **阶段四** Phase 4 | **NTT 代数降维 v14** / NTT reduction | q-阶乘 + NTT 卷积 → O(N² log N), 7.66s |
| **阶段五** Phase 5 | **q-Lucas 零因子修复 v15→v15-b** / q-Lucas fix | 二维自适应 NTT 统一全 a,b；**21/21 全部通过** ✅ |

---

## 🔬 技术要点 / Technical Deep Dive

- **13+ 条失败路线**已被严格 brute-force 反例永久关闭 / 13+ failed routes permanently closed with rigorous counter-evidence
- **Garsia-Haglund 内层求和**通过 q-阶乘展开化为 NTT 卷积，O(N) → O(log N) / Inner loop reduced via q-factorial expansion + NTT convolution
- **q-二项式恒等式** $\binom{n}{k}_a = \frac{(a; a)_n}{(a; a)_k (a; a)_{n-k}}$ 解耦交叉项 / q-binomial identity decouples cross-terms
- **q-Lucas 定理**处理小乘法阶 `a` 导致分母零因子 / q-Lucas theorem handles zero-divisors for small-order `a`
- **`unsigned __int128`** 消除纯标量路径 signed int64 溢出 / eliminates signed int64 overflow in scalar fallback

---

## 🔗 链接 / Links

| Link | Description |
|------|-------------|
| [Nowcoder Problem F](https://ac.nowcoder.com/acm/contest/129209/F) | 在线评测页面 / Online judge |
| [Garsia & Haglund (2002)](https://doi.org/10.1006/jcta.2001.3199) | (q,t)-Catalan 原始递推 / Original recurrence |
| [`solution.cpp`](solution.cpp) | 最终通过算法（本仓） / Final accepted solution |
