时间限制：10 秒
内存限制：1024 MB

## 题目描述
$\hspace{15pt}$Alice 和 Bob 喜欢研究括号串。
$\hspace{15pt}$称长度为 $2n$、仅由字符 $\texttt{`('}$ 与 $\texttt{`)'}$ 构成的括号串 $s = s_1s_2\cdots s_{2n}$ 为合法，当且仅当：
$\hspace{23pt}\bullet\,$对任意<u>前缀</u>$^\texttt{[1]}$，左括号数量不少于右括号数量；
$\hspace{23pt}\bullet\,$整串中左括号与右括号各有 $n$ 个。
$\hspace{15pt}$对一个长度为 $2n$ 的合法括号串 $s$，定义 ${\rm alice}(s)$ 为 $s$ 中等于字符串 $\texttt{"()"}$ 的<u>子序列</u>$^\texttt{[2]}$的个数。换句话说，${\rm alice}(s)$ 等于满足 $1 \le i < j \le 2n$、且 $s_i=\texttt{`('}$、$s_j=\texttt{`)'}$ 的二元组 $(i,j)$ 的数量。
$\hspace{15pt}$对于给定整数 $a$，Alice 定义 ${\rm SA}(s)=a^{{\rm alice}(s)}$。
$\hspace{15pt}$但是，Bob 觉得 ${\rm SA}$ 太简单，于是为同一个串 $s$ 设计了另一种计数方式。设两个变量初值为 $l=0$、${\rm bob}(s)=0$。当 $l<n$ 时依次重复以下过程：
${\hspace{20pt}}_\texttt{1.}\,$令 $x$ 为最大的正整数，使得第 $2 \times l + x$ 个前缀中，左括号 $\texttt{`('}$ 的个数恰好等于 $l+x$；
${\hspace{20pt}}_\texttt{2.}\,$更新 $l \leftarrow l+x$；
${\hspace{20pt}}_\texttt{3.}\,$更新 ${\rm bob}(s) \leftarrow {\rm bob}(s) + (n-l)$（注意执行顺序，要先更新 $l$）。
$\hspace{15pt}$可以证明该过程一定能进行下去，并最终得到 $l=n$，且每一步都能保证 $x\ge 1$。
$\hspace{15pt}$对于给定常数 $b$，Bob 定义 ${\rm SB}(s)=b^{{\rm bob}(s)}$。
$\hspace{15pt}$现在给出整数 $n$，对每个整数 $i \left(1\le i\le n\right)$，设 $\mathcal{D}_i$ 为所有长度 $2i$ 的合法括号串集合，要求计算：
$\displaystyle F_i=\sum_{s\in\mathcal{D}_i} {\rm SA}(s)\times {\rm SB}(s)
=\sum_{s\in\mathcal{D}_i} a^{{\rm alice}(s)}\times b^{{\rm bob}(s)}.$
$\hspace{15pt}$由于答案可能很大，你只需要输出 $F_i \bmod 998\,244\,353$ 即可。
【名词解释】
$\hspace{15pt}$字符串的<u>前缀</u>$^\texttt{[1]}$：从字符串的第一个字符开始，向后连续取若干个字符得到的字符串。更具体地，字符串 $s$ 前 $i$ 个字符构成的字符串被称为 $s$ 的第 $i$ 个前缀，也记为 $s[1..i]$。
$\hspace{15pt}$<u>子序列</u>$^\texttt{[2]}$：从原序列中删除任意个（可以为零，也可以为全部）元素，且保持剩余元素相对顺序不变得到的新序列。

## 输入描述
$\hspace{15pt}$在一行上输入三个整数 $n,a,b\left(1\le n\le 5000;\,1\le a,b<998\,244\,353\right)$。

## 输出描述
$\hspace{15pt}$在一行上输出 $n$ 个整数，第 $i$ 个整数表示 $F_i \bmod 998\,244\,353$ 的值。

## 样例
```text input:#1
3 1 1
```
```text output:#1
1 2 5
```
```text input:#2
4 2 3
```
```text output:#2
2 40 4544 2624512
```