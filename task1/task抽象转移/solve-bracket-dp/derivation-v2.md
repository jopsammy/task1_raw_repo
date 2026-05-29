# 📦 历史归档（2025-05-23 终判，2025-05-24 加固 → 2025-05-25 v15-b 更新）

> 🚨 **本文档为历史推导记录，内容已全部作废，不得引用为当前推导依据。**
>
> 本文为 x-seq 配对法则与 wrapping 修正推导记录。全部基于 pair_seq/wrapping 的路线均受阻于 wrapping 的全局性不可压缩。
> 当前方向已收敛至 (q,t)-Catalan 数的固定参数评值问题。详见 `spec.md`（当前权威真相）。
>
> **🆕 2025-05-24 v14 突破**：Garsia-Haglund + q-阶乘分离 + NTT 卷积 → O(N² log N)，N=5000 7.66s。详见 `spec.md` §四.4、`current-note.md` §十八。
> **🆕 2025-05-25 v15 升级**：通过 q-Lucas 分解 + 二维自适应 NTT 统一全 a,b 为 O(N² log N)，移除 O(N³/6) 回退路径。详见 `spec.md` §八、`current-note.md` §十九。
> **🆕 2025-05-25 v15-b 修复**：v15 判题 19/21 → v15-b 修复纯标量路径 signed int64 溢出（`ll sum`→`unsigned __int128 sum`），290/290 交叉验证全通 → **v15-b 判题 21/21 ✅**。详见 `spec.md` §8.7、`current-note.md` §19.7。
>
> **特别警告**：下文中任何关于「c-based wrapping 公式提供精确递推」「255/255 验证通过」等表述，均指对 pair_seq 的自洽验证，**不对真实 wrapping 成立**。该路线已于 2025-05-23 被证伪关闭（反例：T=`()(()())`，pair→bw=4,kw=3 vs real→bw=3,kw=2）。

---

## 第0章：符号约定与预备知识

### 0.1 符号表

| 符号 | 含义 |
|------|------|
| $\mathcal{D}_n$ | 所有长度为 $2n$ 的合法括号串（Dyck word）集合 |
| $\mathcal{P}_n$ | $\mathcal{D}_n$ 中所有**本原**（primitive）Dyck word 的集合 |
| $h_s(i)$ | Dyck word $s$ 在第 $i$ 个字符处的高度：$h_s(i)=\#\{j\le i:s_j=\texttt{`('}\}-\#\{j\le i:s_j=\texttt{`)'}\}$ |
| $X(s)=[x_1,\dots,x_k]$ | $s$ 的 x-sequence |
| $k(s)=|X(s)|$ | x-sequence 的长度（步数） |
| $\text{alice}(s)$ | $s$ 中等于 $\texttt{"()"}$ 的子序列个数 |
| $\text{bob}(s)$ | 按题目定义的 Bob 计数值 |
| $|s|$ | $s$ 的大小 = 长度的一半 = $n$ |

### 0.2 x-sequence 的严格定义

对 Dyck word $s$ 长度 $2n$：

```
l ← 0; X ← []
while l < n:
    x ← max{ t ≥ 1 : h_s(2l + t) = t }
    X.append(x)
    l ← l + x
```

等价刻画：对每一步 $j$，设累积进度 $\ell_{j-1}=\sum_{i<j}x_i$，则
$$x_j = \max\{t \ge 1 : h_s(2\ell_{j-1} + t) = t\}$$

因为 $h_s(2\ell_{j-1}+t)=t$ 意味着前缀 $s[1..2\ell_{j-1}+t]$ 中恰有 $\ell_{j-1}+t$ 个 `'('`。可证 $x_j$ 等于从位置 $2\ell_{j-1}+1$ 开始的**连续 `'('` 的个数**：位置 $2\ell_{j-1}+1$ 到 $2\ell_{j-1}+x_j$ 全是 `'('`，而位置 $2\ell_{j-1}+x_j+1$ 是 `')'`。

### 0.3 bob 的简洁公式

定义过程得到的步序列为 $X(s)=[x_1,\dots,x_k]$，每步后 $l$ 的累计值为
$$\ell_j = \sum_{i=1}^{j} x_i, \quad \ell_k = n$$

则
$$\text{bob}(s) = \sum_{j=1}^{k-1} (n - \ell_j) = \sum_{j=1}^{k} (j-1) \cdot x_j$$

证明：$\sum_{j=1}^{k-1}(n-\ell_j)=\sum_{j=1}^{k-1}\sum_{i=j+1}^{k}x_i=\sum_{i=2}^{k}(i-1)x_i=\sum_{j=1}^{k}(j-1)x_j$。∎

### 0.4 已成立的事实（不重新推导）

**(F1) 连接分解**：对任意 Dyck word $s = P \cdot Q$（$P$ 为本原），
$$\text{alice}(PQ) = \text{alice}(P) + \text{alice}(Q) + |P| \cdot |Q|$$
$$\text{bob}(PQ) = \text{bob}(P) + \text{bob}(Q) + k(P) \cdot |Q|$$
$$k(PQ) = k(P) + k(Q)$$

已在 `verify_concat.py` 中验证到 $n=8$，全部通过。

**(F2) alice 的包装公式**：对任意 Dyck word $A$（$|A|=m$）,
$$\text{alice}((A)) = \text{alice}(A) + 2m + 1$$

由 (F1) 及标准分解 $(A)B$ 可推出：
$$\text{alice}((A)B) = \text{alice}(A) + \text{alice}(B) + n + k(n-k)$$
其中 $n = |(A)B| = m+1+|B|$，$k = m+1 = |(A)|$。代入 (F1) 的连接公式并比较即得上式。具体推导略。

---

## 第1部分：x-sequence Wrapping 完整公式

### 1.1 包装操作对高度的作用

设 $A \in \mathcal{D}_m$，其高度函数为 $h_A(\cdot)$。包装 $(A)=\texttt{`('}+A+\texttt{`)'}$ 的高度函数 $h'$ 满足：
$$h'(0) = 0,\quad h'(1) = 1,\quad h'(1+i) = 1 + h_A(i)\;(1 \le i \le 2m),\quad h'(2m+2) = 0$$

即：$h'(t) = 1 + h_A(t-1)$ 对 $1 \le t \le 2m+1$ 成立，$h'(0)=h'(2m+2)=0$。

用 $h'$ 表达包装后的 x-sequence 条件：在第 $j$ 步，设累积进度 $\ell'=\sum_{i<j}x'_i$，则
$$x'_j = \max\{t \ge 1 : h'(2\ell' + t) = t\}$$

代入 $h'$：
$$h'(2\ell' + t) = 1 + h_A(2\ell' + t - 1) = t$$
$$\iff h_A(2\ell' + t - 1) = t - 1$$

设 $p = 2\ell' + t - 1$（即 $A$ 内的位置），则 $t = p - 2\ell' + 1$，条件为
$$h_A(p) = p - 2\ell'$$

### 1.2 第一步的精确处理

$\ell'=0$，条件为 $h_A(p) = p$，即 $p$ 的取值是 $A$ 的 x-sequence 第一步值：
$$x'_1 = 1 + a_1 \quad \text{其中 } a_1 = x_1^A = \max\{t: h_A(t)=t\}$$

### 1.3 配对法则的导出（核心定理）

**定义**（配对序列）。对 $A$ 的 x-sequence $X(A)=[a_1,\dots,a_m]$，构造**增广序列**
$$S = [\mathbf{1}_{\text{outer}}, a_1, a_2, \dots, a_m]$$

其中 $\mathbf{1}_{\text{outer}}$ 代表外层 `'('` 贡献的一个单位。

**定理 1（x-sequence 包装配对法则）**。$X((A))$ 可由 $S$ 通过如下过程确定：

> 从左到右扫描 $S$。设当前指针 $i$（初始 $i=0$，$S_0=\mathbf{1}_{\text{outer}}$）：
> - 若 $S_i = 1$ 且 $i+1 \le |S|-1$（存在后继）：输出 $S_i + S_{i+1}$，$i \leftarrow i+2$。
> - 若 $S_i \ge 2$：输出 $S_i$，$i \leftarrow i+1$。
> - 若 $S_i = 1$ 且 $i+1 > |S|-1$（序列末尾的孤立 1）：输出 $1$，结束。

等价表述：将 $S$ 划分为若干对 $(1, v)$（$v \ge 1$）和若干孤立值 $v \ge 2$，每对 $(1,v)$ 合并为 $1+v$，孤立值保持不变。

**验证**（已通过枚举和手工验证）：
- $X(A)=[1,1,1] \to S=[1,1,1,1] \to$ 对 $(1,1)\to 2$，对 $(1,1)\to 2 \to X'=[2,2]$ ✓
- $X(A)=[1,1,1,1] \to S=[1,1,1,1,1] \to (1,1)\to 2,(1,1)\to 2,1\to 1 \to X'=[2,2,1]$ ✓
- $X(A)=[2,1,1] \to S=[1,2,1,1] \to (1,2)\to 3,(1,1)\to 2 \to X'=[3,2]$ ✓
- $X(A)=[1,2,1] \to S=[1,1,2,1] \to (1,1)\to 2,2\to 2,1\to 1 \to X'=[2,2,1]$ ✓
- $X(A)=[1,1,2] \to S=[1,1,1,2] \to (1,1)\to 2,(1,2)\to 3 \to X'=[2,3]$ ✓
- $X(A)=[2,1] \to S=[1,2,1] \to (1,2)\to 3,1\to 1 \to X'=[3,1]$ ✓

### 1.4 合并规律的精确定理

**推论 1.1（连续 1 的合并）**。若 $X(A)$ 始于 $c \ge 1$ 个连续的 1（即 $a_1=a_2=\dots=a_c=1$，且 $a_{c+1} \ge 2$ 或 $c=m$），则：

- **$c$ 为奇数**（$c=2p+1$）：$X'$ 的前 $p+1$ 个元素均为 $2$，之后 $a_{c+1}$ 保持不变（若存在）。
  即 $X'_{\text{lead}} = [\underbrace{2,2,\dots,2}_{p+1\text{ 个}}, a_{c+1}, \dots]$，$k'_{\text{lead}} = p+1 = \frac{c+1}{2}$。
  
- **$c$ 为偶数**（$c=2p$）：$X'$ 的前 $p$ 个元素均为 $2$，第 $p+1$ 个元素为 $a_{c+1}+1$（与后续第一个 $\ge 2$ 的值配对）。
  即 $X'_{\text{lead}} = [\underbrace{2,2,\dots,2}_{p\text{ 个}}, a_{c+1}+1, \dots]$，$k'_{\text{lead}} = p = \frac{c}{2}$。

对 $c \ge 3$ 的情况，与朴素版（仅将 $a_1$ 变为 $2$，其余不变，即 $X'_{\text{naive}}=[2,1^{c-1},a_{c+1},\dots]$）对比：

| 量 | 朴素版 | 实际版 | 差值 $\Delta$ |
|---|---|---|---|
| $k'_{\text{lead}}$（$c$奇） | $c$ | $\frac{c+1}{2}$ | $\frac{c-1}{2}$ |
| $k'_{\text{lead}}$（$c$偶） | $c$ | $\frac{c}{2}$ | $\frac{c}{2}$ |

---

## 第2部分：bob 与 k 的包装递推

### 2.1 基于配对法则的递推公式

给定 $X(A)=[a_1,\dots,a_m]$ 和按定理 1 导出的 $X'=X((A))=[x'_1,\dots,x'_{m'}]$：

$$k((A)) = m' = |X'|$$
$$\text{bob}((A)) = \sum_{j=1}^{m'} (j-1) \cdot x'_j$$

### 2.2 无合并情况的标准递推

若 $a_1 \ge 2$（第一条不是 1），则不会发生合并。此时：
$$X' = [a_1+1,\; a_2,\; a_3,\; \dots,\; a_m]$$
$$k((A)) = k(A) = m$$
$$\text{bob}((A)) = \text{bob}(A) \quad (\text{因为 }(j-1)\cdot(a_1+1) = (j-1)\cdot a_1|_{j=1}=0)$$

即：首个元素 $+1$ 不影响 bob（系数为 $0$），步数不变。

### 2.3 合并情况下的递推公式

设 $X(A)=[1^c, a_{c+1}, \dots, a_m]$ 且 $a_{c+1} \ge 2$（或 $c=m$），$c \ge 2$。

#### 情况 A：$c$ 为奇数 $(c=2p+1)$

$$X' = [2^{p+1}, a_{c+1}, a_{c+2}, \dots, a_m]$$
$$k' = (p+1) + (m - c) = m - p$$
$$\text{bob}((A)) = \underbrace{\sum_{j=1}^{p+1}(j-1)\cdot 2}_{\text{合并部分}} \;+\; \underbrace{\sum_{j=c+1}^{m}\big(j - (p+1) + (c-1)\big) \cdot a_j}_{\text{尾部，需修正索引}}$$

合并部分化简：
$$\sum_{j=1}^{p+1}(j-1)\cdot 2 = 2 \cdot \frac{p(p+1)}{2} = p(p+1)$$

朴素版合并部分（$[2,1^{c-1}]$）：
$$0\cdot 2 + \sum_{j=2}^{c} (j-1)\cdot 1 = \frac{c(c-1)}{2}$$

合并部分 bob 变化量：
$$\Delta_{\text{bob}}^{\text{lead}} = p(p+1) - \frac{c(c-1)}{2}$$

#### 情况 B：$c$ 为偶数 $(c=2p)$

$$X' = [2^{p}, a_{c+1}+1, a_{c+2}, \dots, a_m]$$
$$k' = p + 1 + (m - c) = m - p + 1$$
$$\text{bob}((A)) = \sum_{j=1}^{p}(j-1)\cdot 2 \;+\; p\cdot(a_{c+1}+1) \;+\; \sum_{j=c+2}^{m}\big(j - (p+1) + c\big) \cdot a_j$$

合并部分：
$$\sum_{j=1}^{p}(j-1)\cdot 2 = p(p-1)$$

朴素版合并部分：$\frac{c(c-1)}{2}$

合并部分 bob 变化量（不含 $a_{c+1}$ 交叉项）：
$$\Delta_{\text{bob}}^{\text{lead}} = p(p-1) - \frac{c(c-1)}{2}$$

而 $a_{c+1}$ 的 bob 贡献从朴素版的 $(c)\cdot a_{c+1}$ 变为 $p\cdot(a_{c+1}+1) = p\cdot a_{c+1} + p$，差值为 $(p-c)\cdot a_{c+1} + p$。

### 2.4 $\Delta k$ 与 $\Delta\text{bob}$ 的紧凑闭合式

$\Delta k = k_{\text{naive}} - k_{\text{actual}} = (c+1) - k'_{\text{lead}}$（因为朴素版 $k_{\text{naive}}$ 中领先部分有 $c$ 个 1 加上包装给的一项，共 $c+1$? 不，朴素版 $X'_{\text{naive}}=[2,1^{c-1},\dots]$，领先 $k=c$。实际版的 $k'_{\text{lead}}$ 为：

$$k'_{\text{lead}} = \begin{cases}
\frac{c+1}{2} & c\text{ 奇} \\
\frac{c}{2} & c\text{ 偶}
\end{cases}$$

$$\Delta k = c - k'_{\text{lead}} = \begin{cases}
\frac{c-1}{2} & c\text{ 奇} \\
\frac{c}{2} & c\text{ 偶}
\end{cases}$$

合并部分的 bob 朴素值为 $\frac{c(c-1)}{2}$，实际值为：

$$\text{bob}_{\text{lead}}^{\text{actual}} = \begin{cases}
p(p+1) = \frac{c-1}{2} \cdot \frac{c+1}{2} = \frac{c^2-1}{4} & c=2p+1\text{ 奇} \\
p(p-1) = \frac{c}{2} \cdot \frac{c-2}{2} = \frac{c(c-2)}{4} & c=2p\text{ 偶}
\end{cases}$$

$$\Delta_{\text{bob}}^{\text{lead}} = \frac{c(c-1)}{2} - \text{bob}_{\text{lead}}^{\text{actual}}$$

---

## 第3部分：DP 状态定义与转移方程

### 3.1 状态设计思路

由于连接和包装操作都需要知道 $k$（步数），而 $k$ 又由 x-sequence 决定，DP 状态必须跟踪 x-sequence 的信息。

关键的观察：连接公式 $\text{bob}(PQ)=\text{bob}(P)+\text{bob}(Q)+k(P)\cdot|Q|$ 表明，当我们将一个本原词 $P$ 连接到 $Q$ 之前时，$Q$ 的 bob 被 $k(P)\cdot|Q|$ 增量放大。这可以用一个参数 $L$ 来吸收：若在定义中把 $\text{bob}(s)+k(s)\cdot L$ 作为一个整体来 DP，则连接和包装都是局部的。

### 3.2 DP 定义

定义 **加权生成函数**：

$$\boxed{G_n(L) = \sum_{s \in \mathcal{D}_n} a^{\text{alice}(s)} \cdot b^{\text{bob}(s) + k(s) \cdot L} \pmod{M}}$$

其中 $L \ge 0$ 是「未来 bob 贡献参数」。含义：若 $s$ 之后还要连接 $L$ 对括号（即后续词总大小为 $L$），则当前 $s$ 的 $k$ 对后续 bob 的贡献为 $k \cdot L$，已预乘在状态中。

类似地，定义**本原词的生成函数**：

$$P_n(L) = \sum_{s \in \mathcal{P}_n} a^{\text{alice}(s)} \cdot b^{\text{bob}(s) + k(s) \cdot L}$$

注意：$n \ge 1$ 时 $P_n(L) = G_n(L)_{\text{restricted to primitive}}$。

### 3.3 基本递推：连接分解

对 $n \ge 2$，每个 Dyck word $s \in \mathcal{D}_n$ 可分解为 $s = P \cdot Q$ 其中 $P \in \mathcal{P}_m$（$1 \le m \le n$）、$Q \in \mathcal{D}_{n-m}$。

由 (F1)：
$$\text{alice}(s) = \text{alice}(P) + \text{alice}(Q) + m \cdot (n-m)$$
$$\text{bob}(s) = \text{bob}(P) + \text{bob}(Q) + k(P) \cdot (n-m)$$
$$k(s) = k(P) + k(Q)$$

则：
$$\begin{aligned}
a^{\text{alice}(s)} \cdot b^{\text{bob}(s) + k(s)L}
&= a^{\text{alice}(P)+\text{alice}(Q)+m(n-m)} \cdot b^{\text{bob}(P)+\text{bob}(Q)+k(P)(n-m)+(k(P)+k(Q))L} \\
&= a^{m(n-m)} \cdot \left[a^{\text{alice}(P)}b^{\text{bob}(P)+k(P)(L+n-m)}\right] \cdot \left[a^{\text{alice}(Q)}b^{\text{bob}(Q)+k(Q)L}\right] \\
&= a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L)
\end{aligned}$$

于是：
$$\boxed{G_n(L) = \sum_{m=1}^{n} a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L)}$$

这是 $O(N^3)$ 的核心方程（三重循环：$n, L, m$）。

### 3.4 包装递推：$P_n$ 的计算

由于 $\mathcal{P}_n$ 恰由 $(A)$ 组成，其中 $A \in \mathcal{D}_{n-1}$。所以我们只需从 $G_{n-1}$ 推导出 $P_n$。

#### 3.4.1 朴素包装（忽略合并）

若忽略 x-sequence 合并（即假设所有 $A$ 的 $a_1 \ge 2$，或 $c \le 2$ 时恰巧修正无需额外处理）：

$$\text{alice}((A)) = \text{alice}(A) + 2(n-1) + 1 = \text{alice}(A) + 2n - 1$$

而在无合并的情况下：$k((A)) = k(A)$，$\text{bob}((A)) = \text{bob}(A)$。

故：
$$\begin{aligned}
a^{\text{alice}((A))} \cdot b^{\text{bob}((A)) + k((A))L}
&= a^{\text{alice}(A) + 2n - 1} \cdot b^{\text{bob}(A) + k(A)L} \\
&= a^{2n-1} \cdot \left[a^{\text{alice}(A)}b^{\text{bob}(A)+k(A)L}\right] \\
&= a^{2n-1} \cdot G_{n-1}(L)
\end{aligned}$$

因此**朴素 $P_n$**：
$$\boxed{P_n^{\text{naive}}(L) = a^{2n-1} \cdot G_{n-1}(L)}$$

#### 3.4.2 修正项：处理 $c \ge 3$ 的合并

当 $A$ 的 x-sequence 前 $c \ge 3$ 项都是 1 时，朴素公式错误。需要为这种 $A$ 添加修正。

将 $\mathcal{D}_{n-1}$ 中的词按「前导连续 1 的个数」分解：

$$A = \underbrace{()()\dots()}_{c\text{ 个}} \cdot A_{\text{rest}}$$

其中 $c \ge 0$，$A_{\text{rest}} \in \mathcal{D}_{n-1-c}$ 且 $A_{\text{rest}}$ 的 x-sequence 第一项 $\ge 2$（或 $A_{\text{rest}}$ 为空）。

设 $m = n-1$（$A$ 的大小），$c \ge 3$ 是要修正的前导 1 的个数，$r = m - c$ 为 $A_{\text{rest}}$ 的大小。

以 $X(A)=[1^c, v, \dots]$ 为例（$v \ge 2$ 为 $A_{\text{rest}}$ 的第一个 x 项）。应用配对法则后：

**实际** $X'$ 的领先部分：
- $c$ 奇（$c=2p+1$）：$X'_{\text{lead}} = [2^{p+1}, v, \dots]$，$k'_{\text{lead}} = p+1$
- $c$ 偶（$c=2p$）：$X'_{\text{lead}} = [2^{p}, v+1, \dots]$，$k'_{\text{lead}} = p$

领先部分的 bob：
$$\text{bob}_{\text{lead}}^{\text{actual}} = \begin{cases}
p(p+1) = \dfrac{c^2-1}{4} & c\text{ 奇} \\
p(p-1) = \dfrac{c(c-2)}{4} & c\text{ 偶}
\end{cases}$$

**朴素** $X'_{\text{naive}}$ 领先部分：$[2, 1^{c-1}]$，$k_{\text{lead}}^{\text{naive}} = c$，$\text{bob}_{\text{lead}}^{\text{naive}} = \dfrac{c(c-1)}{2}$。

#### 3.4.3 修正的核心量

$$\Delta k = k_{\text{lead}}^{\text{naive}} - k'_{\text{lead}}$$

$$\Delta\text{bob} = \text{bob}_{\text{lead}}^{\text{naive}} - \text{bob}_{\text{lead}}^{\text{actual}}$$

具体值：

| $c$ | $\Delta k$ | $\Delta\text{bob}$（领先部分） |
|---|---|---|
| $3$ | $1$ | $1$ |
| $4$ | $2$ | $4$ |
| $5$ | $2$ | $4$ |
| $6$ | $3$ | $9$ |
| $7$ | $3$ | $9$ |
| $8$ | $4$ | $16$ |
| 奇 $c=2p+1$ | $p$ | $p(p+1)$ |
| 偶 $c=2p$ | $p$ | $p^2$ |

也就是：
$$\Delta k = \left\lfloor \frac{c-1}{2} \right\rfloor$$
$$\Delta\text{bob}_{\text{lead}} = \begin{cases}
\dfrac{c-1}{2} \cdot \dfrac{c+1}{2} & c\text{ 奇} \\
\dfrac{c}{2} \cdot \dfrac{c}{2} & c\text{ 偶}
\end{cases}$$

### 3.5 完整的修正公式

定义辅助 DP：

$$G^{\ge 2}_n(L) = \sum_{\substack{s \in \mathcal{D}_n \\ x_1^s \ge 2}} a^{\text{alice}(s)} \cdot b^{\text{bob}(s) + k(s)L}$$

即：使得 x-sequence 第一项 $\ge 2$ 的 Dyck word 的生成函数。

$G^{\ge 2}_n(L)$ 可通过连接公式从 $P_m$（$m \ge 2$，因为 $x_1 \ge 2$ 当且仅当本原块大小 $\ge 2$）递推得到：

$$G^{\ge 2}_n(L) = \sum_{m=2}^{n} a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L)$$

注意 $G_{n-m}(L)$ 用的是全体词（因为连接后面的可以是任意词）。

现在包装修正：

$$\boxed{P_n(L) = a^{2n-1} \cdot G_{n-1}(L) \;+\; a^{2n-1} \cdot \sum_{c=3}^{n-1} \delta_c(L) \cdot G^{\ge 2}_{n-1-c}(L)}$$

其中修正因子 $\delta_c(L)$ 表示将 $[1^c, A_{\text{rest}}]$ 中领先 $c$ 个 1 的实际贡献与朴素贡献之间的**差值**。

**推导 $\delta_c(L)$**：

对于 $A = 1^c \cdot A_{\text{rest}}$（$|A_{\text{rest}}| = r$），考虑在生成函数 $G_{n-1}(L)$ 中该项（朴素）的贡献 vs 实际贡献。两者都在 $P_n(L)$ 的定义中：

朴素贡献（已包含在 $a^{2n-1}\cdot G_{n-1}(L)$ 中）：
$$a^{\text{alice}(A)+2n-1} \cdot b^{\text{bob}(A) + k(A)L}$$

其中 $\text{bob}(A)$ 和 $k(A)$ 是原始 $A$ 的朴素值，可分解为领先部分 + $A_{\text{rest}}$ 部分：

设 $A_{\text{rest}}$ 的生成函数贡献为 $G^{\ge 2}_r(L)$（此处 $L$ 需注意，因为领先部分消耗了一些 $k$ 累积，从而改变了 $A_{\text{rest}}$ 的索引偏移——但这已在 $G$ 的递推中通过正确的 $L$ 参数处理）。

**关键**：在朴素公式中，领先 $c$ 个 1 对 bob 贡献为 $\frac{c(c-1)}{2}$，对 $\text{alice}$ 无影响（前面已经通过 $A$ 的整体 alice 乘 $a^{2n-1}$ 处理了）。朴素公式把 $k((A))$ 当作 $k(A) = c + k(A_{\text{rest}})$，bob 当作 $\text{bob}(A)$。

实际贡献中，领先 $c$ 个 1 加上外层 `'('` 合并后，对 bob 的贡献为上述实际 $\text{bob}_{\text{lead}}$，$k$ 减少了 $\Delta k$。

因此修正因子为：

$$\delta_c(L) = b^{-\Delta k \cdot L} \cdot b^{-\Delta\text{bob}} - 1$$

解释：朴素版将该项计入了 $a^{2n-1}\cdot G_{n-1}(L)$。要替换为实际贡献需乘以 $b^{-\Delta k \cdot L} \cdot b^{-\Delta\text{bob}}$（因为朴素高估了 bob 和 k 对 $L$ 的依赖），再减去 $1$ 以消除朴素版中的该项。

**修正项的精确定量推导**：

考虑 $A = 1^c \cdot A_{\text{rest}}$（$c$ 个 `"()"` + $A_{\text{rest}}$），$|A| = m = c + r$，$|A_{\text{rest}}| = r$。

**朴素版**（在 $a^{2n-1} \cdot G_{n-1}(L)$ 中的贡献）：

将 $A$ 本身的生成函数贡献拆分为两部分：

1. 领先 $c$ 个 `"()"` 块对 alice 的贡献：每个 `"()"` 贡献 1，加上块间交叉 $c(c-1)/2$。但这些已计入 $G_{n-1}(L)$（通过 $\sum_{s} a^{\text{alice}(s)} \dots$ 中的 alice 项）。

2. $A = (1^c) \cdot A_{\text{rest}}$ 的连接交叉项 alice：$c \cdot r$。

3. $A$ 对 bob 的和 k：

朴素观点下，包装中 $k((A))_{\text{naive}} = k(A)$，$\text{bob}((A))_{\text{naive}} = \text{bob}(A)$。而在生成函数 $G_{n-1}(L)$ 中，$A$ 已经带有正确的 $\text{alice}(A)$、$\text{bob}(A)$、$k(A)$。

因此朴素版对 $P_n(L)$ 的贡献（在乘以 $a^{2n-1}$ 后）匹配了 $1^c \cdot A_{\text{rest}}$ 所有项的**连接形式**贡献。

**实际版**（需要替换为的值）：

应用包装配对后，领先 $c$ 个 1 的合并改变了 $k$ 和 bob：
- $k_{\text{actual}} = k_{\text{naive}} - \Delta k$
- $\text{bob}_{\text{actual}} = \text{bob}_{\text{naive}} - \Delta\text{bob}_{\text{lead}}$

此外，$A_{\text{rest}}$ 到包装的连接交叉项 alice 从 $c \cdot r$（朴素）变为 $(k'_{\text{lead}}) \cdot r$（实际，因为领先部分步长变为 $k'_{\text{lead}}$），而连接交叉项 bob 从 $c \cdot r$（朴素，$c$ 是 k）变为 $k'_{\text{lead}} \cdot r$。

**完整修正项**（对照 solution.py 的实现）：

设 $\Delta k = \lfloor (c-1)/2 \rfloor$，$k_{\text{val}} = \lfloor c/2 \rfloor$，$\Delta\text{bob} = k_{\text{val}}^2$（$c$ 偶）或 $k_{\text{val}}(k_{\text{val}}+1)$ 若另有修正。

朴素版与正确版之间的因子差异在生成函数 $G^{\ge 2}_r(L)$ 上的乘数为：

$$\text{correct\_factor} = a^{c \cdot m - c(c-1)/2} \cdot b^{cL + cm - c(c+1)/2} \cdot b^{-(\Delta k \cdot L + \Delta\text{bob})}$$

$$\text{naive\_factor} = a^{c \cdot m - c(c-1)/2} \cdot b^{cL + cm - c(c+1)/2}$$

其中 $a^{c \cdot m}$ 是 alice 交叉项（$c$ 个 `"()"` 与整体 $m$ 大小的交叉），$a^{-c(c-1)/2}$ 修正 `"()"` 内部交叉的重复计数，$b^{cL + cm}$ 是 bob 及其 $L$ 依赖，$b^{-c(c+1)/2}$ 修正领先部分的 bob 重复。

修正量为：
$$\text{corr}_c(L) = \big( b^{-(\Delta k \cdot L + \Delta\text{bob})} - 1 \big) \cdot a^{cm - c(c-1)/2} \cdot b^{cL + cm - c(c+1)/2} \cdot G^{\ge 2}_r(L)$$

将此项乘以 $a^{2n-1}$ 后加入 $P_n(L)$。

### 3.6 完整的 O(N³) 递推体系

**初始化**：
- $G_0(L) = 1$（空词），对所有 $0 \le L \le N$
- $G_1(L) = a \cdot b^L$（词 `"()"`：$\text{alice}=1$，$\text{bob}=0$，$k=1$，所以 $\text{bob}+kL = L$）
- $P_1(L) = G_1(L)$

**主循环**（$n = 2,3,\dots,N$）：

1. 计算 $P_n^{\text{naive}}(L) = a^{2n-1} \cdot G_{n-1}(L)$（朴素包装）
2. 计算 $G^{\ge 2}_n(L) = \sum_{m=2}^{n} a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L)$
3. 修正 $P_n(L) = P_n^{\text{naive}}(L) + a^{2n-1} \cdot \sum_{c=3}^{n-1} \text{corr}_c(L) \cdot G^{\ge 2}_{n-1-c}(L)$
4. 计算以 `"()"` 开头的词的贡献：$G^{\text{starts1}}_n(L) = a^n \cdot b^{L+n-1} \cdot G_{n-1}(L)$
   （包装 $G_{n-1}$ 的第一个本原块就是从 `"()"` 开始的 $(())...$ 形式，此处分出来单独处理）
5. $G_n(L) = G^{\ge 2}_n(L) + G^{\text{starts1}}_n(L)$

---

## 第4部分：前缀和优化 — O(N³) → O(N²)

### 4.1 瓶颈分析

主递推中的连接求和：
$$G^{\ge 2}_n(L) = \sum_{m=2}^{n} a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L)$$

对每个 $(n, L)$ 需要 $O(n)$ 时间，总共 $O(N^3)$。必须优化。

### 4.2 双变量分离

注意到求和式中的 $m$ 和 $(n-m)$ 分别出现在 $P_m$ 和 $G_{n-m}$ 中。定义：
$$S_n(L) = \sum_{m=2}^{n} a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L)$$

这可以通过**对角线卷积**优化。关键观察：

$$a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L)$$

其中 $P_m$ 的第二个参数是 $L+n-m$，$G_{n-m}$ 的第二个参数是 $L$。这是一个带权卷积。

**方法一：逐 $L$ 的卷积**

对每个固定的 $L$，考虑多项式：
$$F_{n,L}(x) = \sum_{m} P_m(L+n-m) \cdot a^{m(n-m)} \cdot x^{m}$$

但 $a^{m(n-m)}$ 同时依赖 $m$ 和 $n$，不是标准卷积。需要拆分：
$$a^{m(n-m)} = a^{mn - m^2}$$

所以：
$$S_n(L) = \sum_{m=2}^{n} \underbrace{a^{-m^2} \cdot P_m(L+n-m)}_{\text{依赖 } m \text{ 和 } L+n-m} \cdot \underbrace{a^{mn} \cdot G_{n-m}(L)}_{\text{依赖 } n-m}}$$

但这还不是标准卷积，因为 $a^{mn}$ 同时依赖 $m$ 和 $n$。

### 4.3 重新参数化技巧

定义变换后的量：
$$\widetilde{P}_m(L') = a^{-m^2} \cdot P_m(L')$$

其中 $L' = L + n - m$。注意 $L'$ 依赖于 $n$ 和 $m$，所以 $\widetilde{P}_m(L')$ 无法脱离 $n$ 预计算。

这个依赖来源于连接时的交叉项 $m(n-m)$ 在 alice 中。由于 alice 的交叉项是 **乘法性** 的（$a^{m(n-m)}$），可以先分离 alice 和 bob 的贡献。

### 4.4 优化方案：增量递推

每个 $n$ 固定时，$S_n(L)$ 对 $m=2$ 到 $n$ 求和。注意到：

$$S_n(L) = S_{n-1}(L+1) \cdot (\text{修正项}) + P_n(L) \cdot G_0(L)$$

但这不直接，因为 $G_{n-m}(L)$ 是 $G$ 在同一个 $L$ 上的值，而 $P_m$ 的第二个参数是 $L+n-m$。

**实际可行的优化**：利用 $G_0(L)=1$ 的边界和 $G_{n-m}$ 的 $L$ 不变性。

重新排列求和。对每个 $m$，$P_m$ 的参数 $L' = L + n - m$ 随 $L$ 的减小而增大。这提示我们沿 $L$ 的**反对角线**做 DP。

### 4.5 实际 O(N²) 方案（参考 solution.py 的实现）

在 solution.py 中，通过以下方式实现 O(N²)：

1. $G^{\ge 2}_n(L)$ 的计算实际上是 $O(N^3)$ 的三重循环（n, L, m），但 $N=5000$ 下 $N^3$ 不可接受。
2. 实际实现中，内层循环 $m$ 从 2 到 $n$ 对所有 $(n,L)$ 都跑，看起来是 $O(N^3)$。
3. **但** solution.py 使用 PyPy3，在 $N=5000$ 的实际约束下可能需要进一步优化。

**真正的 O(N²) 优化路径**：

对于连接公式：
$$G_n(L) = \sum_{m=1}^{n} a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L)$$

预处理：

$$H_m(T) = a^{-m^2} \cdot P_m(T)$$

其中 $T = L + n - m$。这个变换消去了对 $n$ 的显式依赖（仅通过 $T$ 间接）。

但 $a^{mn} \cdot H_m(T) \cdot G_{n-m}(L)$ 中 $a^{mn}$ 仍同时含 $m$ 和 $n$。这需要**前缀和**或**递推**技巧。

**递推观点**：
$$\begin{aligned}
G_n(L) - a^n \cdot b^{L+n-1} \cdot G_{n-1}(L) &= \sum_{m=2}^{n} a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L) \\
&= \sum_{t=0}^{n-2} a^{(n-t)t} \cdot P_{n-t}(L+t) \cdot G_t(L)
\end{aligned}$$

这里令 $t = n-m$。这不是标准卷积。

**关键**：固定 $L$，定义序列 $\{F_n\}$ 满足某种递推。观察到：
$$G_n(L) = P_n(L) + \sum_{m=1}^{n-1} a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L)$$
$$G_{n-1}(L+1) = P_{n-1}(L+1) + \sum_{m=1}^{n-2} a^{m(n-1-m)} \cdot P_m(L+1+n-1-m) \cdot G_{n-1-m}(L+1)$$

不好直接建立递推。

**实际解决方案**：利用 $N=5000$ 时 $\frac{N(N+1)}{2} \approx 12.5\times 10^6$ 个状态，每个状态内部 $O(N) \to$ 总 $O(N^3) \approx 125\times 10^9$ 不可接受。必须降为 $O(N^2)$。

考虑**分治 NTT** 或**生成函数**方法。由于模数 $M=998244353$ 是 NTT-friendly 素数（$M = 119 \times 2^{23} + 1$），可使用多项式方法。

但这里给出**纯组合的 $O(N^2)$ 优化**：

### 4.6 组合 $O(N^2)$ 优化

**核心观察**：$G_n(L)$ 中 $L$ 的依赖仅通过 $b^{k(s)L}$ 出现。当 $L$ 变化时，同一个 $s$ 的贡献随 $L$ 线性变化（在指数意义上）。因此可以**同时**对所有 $L$ 计算。

具体做法：对每个 $n$，用 $O(n \cdot N)$ 时间（总 $O(N^2)$）计算某条反对角线上的值。

固定 $n$，$L$ 从 $0$ 到 $N-n$。对于连接：

$$G_n(L) = \sum_{m=1}^{n} a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L)$$

对**给定 $n$ 和 $m$**，$P_m$ 的参数是 $L' = L + n - m$。当 $L$ 在 $[0, N-n]$ 变化时，$L'$ 在 $[n-m, N-m]$ 变化。这意味着 $P_m$ 在一条固定长度为 $N-n+1$ 的「斜线」上被访问。

如果对每个 $m$ 预计算 $P_m(*)$ 在所需范围内的值，则 $G_n(L)$ 对每个 $L$ 的求和是 $O(n)$。总复杂度仍然是 $O(N^3)$。

**真正的优化**在于把 $G_n(L)$ 写成 $G_{n-1}$ 和 $P$ 的递推，利用**前缀和**。

定义辅助量：
$$A_n(L) = \sum_{m=2}^{n} a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L)$$

注意到 $A_n(L)$ 与 $A_{n-1}(L+1)$ 的关系：
$$\begin{aligned}
A_{n-1}(L+1) &= \sum_{m=2}^{n-1} a^{m(n-1-m)} \cdot P_m(L+1+n-1-m) \cdot G_{n-1-m}(L+1) \\
&= \sum_{m=2}^{n-1} a^{m(n-1-m)} \cdot P_m(L+n-m) \cdot G_{n-1-m}(L+1)
\end{aligned}$$

对比 $A_n(L)$：
$$\begin{aligned}
A_n(L) &= \sum_{m=2}^{n} a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L) \\
&= a^{2(n-2)} \cdot P_2(L+n-2) \cdot G_{n-2}(L) + \sum_{m=3}^{n} a^{m(n-m)} \cdot P_m(L+n-m) \cdot G_{n-m}(L)
\end{aligned}$$

直接递推困难。**需要前缀和维护**。

### 4.7 实用前缀和优化

对固定 $L$，$G_n(L)$ 的计算需要 $n$ 的完整扫描。$O(N^2)$ 复杂度意味着对每个 $(n, L)$ 对（共 $O(N^2)$ 个）用 $O(1)$ 时间计算。

**方法**：预计算 $a^{m(n-m)}$ 和 $P_m(*)$，然后转化为标准卷积。

令 $t = n-m$（剩余长度），则：
$$G_n(L) = P_n(L) + \sum_{t=0}^{n-2} a^{(n-t)t} \cdot P_{n-t}(L+t) \cdot G_t(L)$$

对每个 $L$，这是在序列上的卷积（但权重 $a^{(n-t)t}$ 不是平移不变的）。这需要**在线卷积**技术。

**分块前缀和**（无 NTT 的 $O(N^2)$ 方案）：

由于 $a^{(n-t)t} = a^{nt - t^2}$，可以写成：
$$G_n(L) = P_n(L) + \sum_{t=0}^{n-2} a^{nt} \cdot \left[a^{-t^2} \cdot P_{n-t}(L+t) \cdot G_t(L)\right]$$

对固定 $n$ 和 $L$，定义 $\widetilde{Q}_{t}^{(n,L)} = a^{-t^2} \cdot P_{n-t}(L+t) \cdot G_t(L)$（注意 $P_{n-t}(L+t)$ 依赖于 $n$）。

这不是标准卷积。但可以**按 $L$ 的对角线**批处理：

对每个固定的差值 $d = n - L$（沿反对角线），$P_{n-t}(L+t) = P_{(d+L)-t}(L+t) = P_{d + (L-t)}(L+t)$。仍不是平移不变的。

**最终实用方案**：

由于 $N=5000$ 下 $\sum_{n=1}^{N} \sum_{L=0}^{N-n} n \approx \frac{N^3}{3} \approx 4.2 \times 10^{10}$ 在 PyPy3 下仍需优化。但 $G^{\ge 2}$ 只对 $m \ge 2$ 求和，并且 $P_m$ 的修正只涉及 $c \ge 3$，这使得实际需要的 $m$ 范围缩小。

实际可行的做法：

1. **预处理幂表**：$a^k, b^k, b^{-k}$ 对 $k=0$ 到 $N^2$ 提前计算（$O(N^2)$ 空间和时间）。
2. **减少内层循环**：$G^{\ge 2}_n(L)$ 的内层 $m$ 循环中，$P_m(L+n-m)$ 是一个从 $m=2$ 到 $n$ 的求和。对固定 $n$，这是对 $P$ 的「加窗」求和，可用滚动前缀和维护。
3. **滚动前缀和**：对每个 $n$，维护
   $$T_{n,L}(m) = \sum_{i=2}^{m} a^{i(n-i)} \cdot P_i(L+n-i) \cdot G_{n-i}(L)$$
   但这需要在每个 $(n,L)$ 上从 $m=2$ 累加到 $n$，依然是 $O(N^3)$。

**结论**：在 $N=5000$ 下，纯组合的 $O(N^2)$ 优化需要在实现层面做精细的递推展开和前缀和缓存，或者引入生成函数 + NTT 来加速卷积部分。当前 solution.py 使用的结构是 $O(N^3)$ 的，在 PyPy3 下对 $N=5000$ 可能不够。本节给出了优化方向的完整数学推导。

---

## 附录A：关键公式速查

### A.1 x-sequence 配对法则
$$S = [\mathbf{1}_{\text{outer}}] \mathbin{+\!\!+} X(A)$$
左起扫描，邻接对 $(1, v) \to 1+v$，孤立 $v \ge 2$ 保持不变。

### A.2 alice 包装公式
$$\text{alice}((A)) = \text{alice}(A) + 2|A| + 1$$

### A.3 连接公式
$$\text{alice}(PQ) = \text{alice}(P) + \text{alice}(Q) + |P| \cdot |Q|$$
$$\text{bob}(PQ) = \text{bob}(P) + \text{bob}(Q) + k(P) \cdot |Q|$$
$$k(PQ) = k(P) + k(Q)$$

### A.4 DP 定义
$$G_n(L) = \sum_{s \in \mathcal{D}_n} a^{\text{alice}(s)} \cdot b^{\text{bob}(s) + k(s) \cdot L}$$

### A.5 修正量 ($c \ge 3$)
$$\Delta k = \left\lfloor \frac{c-1}{2} \right\rfloor, \quad \Delta\text{bob}_{\text{lead}} = \begin{cases} \frac{c^2-1}{4} & c\text{ 奇} \\ \frac{c^2}{4} & c\text{ 偶} \end{cases}$$

---

## 附录B：样例验证表

对 $n=1,2,3,4,5$ 的验证（$a=2, b=3$）：

| $n$ | $F_n \bmod M$ (暴力) | 备注 |
|-----|----------------------|------|
| 1 | $2$ | 词 `"()"` |
| 2 | $40$ | `"()()"`, `"(())"` |
| 3 | $4544$ | 5 个 Dyck word |
| 4 | $2624512$ | 14 个 Dyck word |
