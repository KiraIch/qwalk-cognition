# Explain.md：把這個專案從零講到懂

> **更新說明（2026-10-31）**：本檔的 E4、E5 章節及部分數字已過時，下列結論已撤回：E5「deadline $T=20$ 時 $p\approx0.2$ 最佳、最高 $12\times$」，以及 E4「非單調選擇機率、對稱三選項 $0.333\to0.966$」。以下標示「已過時」的段落僅保留作為歷史脈絡。**新版解說以 `Explain_v2.md` 為準**（§5.4 E4、§5.5 E5），論文與 `code/results/` 為最終依據。
>
> 主要變更：
> 1. 所有 Szegedy/AGJK 實驗統一為 lazy walk $P_\eta=(1-\eta)P+\eta I$，$\eta=0.1$（adversarial torus 為 0.2）。
> 2. E5 改為「讀出模型」與「偵測模型」兩種定義；`max_steps` 由 60 改為 120。
> 3. E5 的 12× 結論撤回（振盪相位假象；lazy 後僅約 1.6×，平均掉 deadline 後消失）。短 deadline 下純量子最好；群聚目標在 $T\gtrsim20$ 時 $p\approx0.2$–$0.3$ 同時勝過純量子與古典。
> 4. E4 改為隨機停止、偵測（$p=0.2$）、古典吸收三種讀出；非單調結論撤回，偵測讀出下耦合單調偏向未耦合選項。
> 5. 測試由 47 增為 61，再增為 71（目前數量）。
> 6. **2026-11 更新**：E2 改用 seeds 0–19 並去除重複集合（distinct sets），E3 改用窗口 $\tau\le50$ 的全域峰值（AUC 取 $\tau\le8$），新增 E6（small-world／scale-free），E1 附 95% CI。§10.2、§10.3 已依 `E2_marked.csv`、`E3_semantic_metrics.csv` 更新；舊的 34.7／79.5、CTQW 0.237／0.247、CRW 0.046 等數字已作廢。

> 這份文件是寫給「覺得自己很笨、但願意慢慢讀」的人。
> 你不需要先學過量子力學、不需要先會 LaTeX、也不需要先會 Python 的高階技巧。
> 我會盡量用生活化的比喻，把每一個符號、每一行程式、每一個實驗、每一張圖都拆開來講。
>
> 這份文件很長。你可以把它當成一本小書，不需要一次讀完。
> 建議讀法：
> 1. 先讀 §0–§2，知道這個專案到底在幹嘛。
> 2. 再讀 §3–§4，理解 classical walk 與 Szegedy walk。
> 3. 再讀 §5–§9，理解量子認知、語意圖、決策圖、雜訊。
> 4. 最後讀 §10–§15，對照程式、實驗、報告與常見問題。
>
> 如果你讀到某個公式卡住，先看公式下面的「白話翻譯」，再回去看公式。
> 如果還是不懂，先跳過，往後讀；很多觀念會在後面的例子裡再出現一次。

---

## 目錄

- [0. 一句話：這個專案在做什麼](#0-一句話這個專案在做什麼)
- [1. 先備知識：圖、機率、線性代數、量子力學](#1-先備知識圖機率線性代數量量子力學)
- [2. Classical random walk 與 hitting time](#2-classical-random-walk-與-hitting-time)
- [3. Szegedy quantum walk](#3-szegedy-quantum-walk)
- [4. AGJK：finding marked vertices 與 HT⁺](#4-agjkfinding-marked-vertices-與-ht)
- [5. Quantum cognition：量子認知到底在說什麼](#5-quantum-cognition量子認知到底在說什麼)
- [6. CTQW 與 CRW：語意圖上的連續時間漫步](#6-ctqw-與-crw語意圖上的連續時間漫步)
- [7. 多選項決策：decision graph 與 choice probability](#7-多選項決策decision-graph-與-choice-probability)
- [8. Partial measurement：退相干與「內省」](#8-partial-measurement退相干與內省)
- [9. Metrics：所有數字的意思](#9-metrics所有數字的意思)
- [10. 實驗 E1–E5（及補充 E6）逐一拆解](#10-實驗-e1e5及補充-e6逐一拆解)
- [11. 程式碼導覽：每個檔案在做什麼](#11-程式碼導覽每個檔案在做什麼)
- [12. 報告導覽：每一節、每一張圖表](#12-報告導覽每一節每一張圖表)
- [13. 常見誤解與 FAQ](#13-常見誤解與-faq)
- [14. 符號與名詞表](#14-符號與名詞表)
- [15. 七天讀書計畫與自我測驗](#15-七天讀書計畫與自我測驗)
- [16. 口頭報告與 Q&A 準備](#16-口頭報告與-qa-準備)

---

## 0. 一句話：這個專案在做什麼

### 0.1 超短版

> 我們把「在圖上找被標記的頂點」這個量子演算法，當成一個「認知搜尋」的過程模型：
> 圖上的點是概念或選項，被標記的點是目標記憶或決定，
> 量子漫步是思考時的證據累積，古典漫步是對照組。
> 然後用數值實驗問：圖的長相、目標的數量與排列、以及雜訊，如何改變搜尋時間與選擇機率？

### 0.2 三層架構

整個專案可以想成三層：

```
┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│  第一層：QIS 核心     │      │  第二層：圖模型       │      │  第三層：認知量       │
│  AGJK quantum walk   │ ───> │  semantic / decision │ ───> │  response time       │
│  W(s), HT, HT⁺       │      │  graph, marked sets  │      │  choice probability  │
└─────────────────────┘      └─────────────────────┘      └─────────────────────┘
```

- **第一層**是課程的量子資訊核心：Szegedy walk、AGJK 的 marked-vertex search、hitting time、extended hitting time。
- **第二層**是把圖解讀成語意網絡或決策網絡：點是概念／選項，邊是關聯，marked set 是目標或決策邊界。
- **第三層**是把漫步的統計量翻成認知量：反應時間、選擇機率、目標活化、語意距離效應。

### 0.3 三個研究問題

- **RQ1（映射）**：`HT`、`HT⁺`、spectral gap、success probability 分別對應到什麼認知量？
- **RQ2（結構）**：single / independent / clustered marked set 如何改變量子優勢？
- **RQ3（雜訊）**：partial measurement / decoherence 如何侵蝕優勢？是否存在最佳測量強度？

### 0.4 三個最重要的結果（先看結論）

1. **Scaling**：在 complete graph、cycle、grid、hypercube 上，量子搜尋時間大致滿足
   $T_q \sim \mathrm{HT}^{0.44\text{--}0.52}$，也就是接近 $\sqrt{\mathrm{HT}}$。
2. **多目標**：independent targets 比 clustered targets 容易；`HT⁺` 的巨大 penalty 只在 AGJK 的 adversarial torus 構造中出現，不是「只要有多個目標」就會發生。
3. **認知與雜訊**：語意距離會改變活化時間；選項耦合會造成很強的 context effect；在群聚目標與較長 deadline（`T ≳ 20`）下，`p ≈ 0.2–0.3` 的弱測量可以同時勝過純量子與古典；但若追求全域最大成功率，純量子 (`p=0`) 仍然最好。

---

## 1. 先備知識：圖、機率、線性代數、量子力學

這一節是「如果你什麼都不會，先看這裡」。已經會的人可以快速掃過。

### 1.1 圖（Graph）

一個圖 $G=(V,E)$ 由兩件事組成：

- $V$：頂點（vertices）的集合。可以想成城市、概念、或選項。
- $E$：邊（edges）的集合。每一條邊連接兩個頂點，代表「有關聯」或「可以一步走過去」。

例子：

```
animal ── dog
  │       │
 cat ─── wolf
```

- `animal`、`dog`、`cat`、`wolf` 是頂點。
- 連線是邊。
- `animal` 的 degree（度數）是 3，因為它連到 dog、cat、wolf。
- `animal` 到 `wolf` 的距離是 1（直接相連）；`cat` 到 `wolf` 的距離是 1；`dog` 到 `cat` 的距離是 1。
- 如果每個點都可以走到其他點，這個圖是 **connected（連通）**。

在程式裡我們用 `networkx` 建圖：

```python
import networkx as nx
G = nx.Graph()
G.add_edge("animal", "dog")
```

但在數值計算時，我們會把圖轉成 **adjacency matrix（鄰接矩陣）** $A$：

$$
A_{xy} =
\begin{cases}
1, & \text{如果 } x \text{ 和 } y \text{ 有邊}\\
0, & \text{否則}
\end{cases}
$$

如果邊有權重（weight），$A_{xy}$ 就是權重，不一定是 1。

### 1.2 機率（Probability）

一個機率分布 $\pi$ 是一個向量，每個分量非負，總和為 1：

$$
\pi = (\pi_1,\pi_2,\dots,\pi_n),\qquad \pi_i\ge 0,\qquad \sum_i\pi_i=1.
$$

「隨機漫步」的意思是：每一步根據某個機率分布選擇下一個點。例如在 `animal` 這個點，如果有 3 個鄰居，簡單隨機漫步會以 $1/3$ 的機率走到每個鄰居。

**期望值** $\mathbb{E}[X]$ 是「平均而言會是多少」。例如丟一顆公平骰子，點數期望值是 $3.5$。

### 1.3 Markov chain（馬可夫鏈）

Markov chain 是「下一步只跟現在在哪裡有關，跟過去怎麼來無關」的隨機過程。

我們用一個 **transition matrix（轉移矩陣）** $P$ 表示：

$$
P_{xy} = \Pr(\text{下一步到 } y \mid \text{現在在 } x).
$$

因為從 $x$ 出發，下一步一定要到某個地方，所以每一列的總和是 1：

$$
\sum_y P_{xy}=1.
$$

#### 小例子：兩點圖

假設只有兩個點 0 和 1，規則是：

- 在 0：有 0.8 機率留在 0，0.2 機率到 1。
- 在 1：有 0.3 機率到 0，0.7 機率留在 1。

則

$$
P=\begin{pmatrix}
0.8 & 0.2\\
0.3 & 0.7
\end{pmatrix}.
$$

如果一開始在 0，分布是 $\rho_0=(1,0)$。走一步後：

$$
\rho_1=\rho_0P=(1,0)\begin{pmatrix}0.8&0.2\\0.3&0.7\end{pmatrix}=(0.8,0.2).
$$

走兩步後：

$$
\rho_2=\rho_1P=(0.8,0.2)\begin{pmatrix}0.8&0.2\\0.3&0.7\end{pmatrix}=(0.7,0.3).
$$

注意：機率向量是**左乘**矩陣，$\rho_{t+1}=\rho_tP$。這和程式裡的寫法一致。

#### Stationary distribution（平穩分布）

如果一個分布 $\pi$ 滿足

$$
\pi P=\pi,
$$

我們稱它是 stationary distribution。意思是：如果現在按照 $\pi$ 分布，走一步之後仍然是 $\pi$。

上面的兩點例子，解 $\pi P=\pi$ 會得到 $\pi=(0.6,0.4)$。

#### Reversible（可逆）與 detailed balance

如果存在 $\pi$ 使得對所有 $x,y$：

$$
\pi_xP_{xy}=\pi_yP_{yx},
$$

我們說這個 chain 是 reversible，這個條件叫 detailed balance（細緻平衡）。

白話：在平穩狀態下，「從 $x$ 走到 $y$ 的流量」等於「從 $y$ 走到 $x$ 的流量」。

對無向圖上的簡單隨機漫步，$\pi_x\propto \deg(x)$，且 detailed balance 自動成立。

### 1.4 線性代數（Linear algebra）

你只需要先知道以下幾件事：

- **向量**：一排數字，例如 $(1,2,3)$。
- **矩陣**：一個二維表格，例如 $P$。
- **轉置（transpose）** $P^T$：把矩陣的行與列交換。
- **共軛（conjugate）** $P^*$：把複數的虛部變號。實數矩陣的共軛就是自己。
- **特徵值／特徵向量（eigenvalue / eigenvector）**：如果
  $$
  Mv=\lambda v,
  $$
  則 $\lambda$ 是特徵值，$v$ 是對應的特徵向量。
  白話：矩陣 $M$ 作用在 $v$ 上，只會把 $v$ 伸長或縮短 $\lambda$ 倍，不會改變方向。
- **對稱矩陣**：$M=M^T$。對稱矩陣的特徵值都是實數，特徵向量可以選成互相垂直。
- **么正矩陣（unitary）**：$U^\dagger U=I$，其中 $U^\dagger$ 是共軛轉置。么正矩陣的作用是「旋轉」向量，不會改變長度。量子演化必須是么正的，因為機率總和要保持 1。

為什麼特徵值重要？因為很多動力學都可以寫成「沿著特徵向量方向各自演化」。量子漫步的譜、古典 chain 的 mixing、hitting time，都可以用特徵值來理解。

### 1.5 量子力學的最小版本

這一小節只講這個專案用得到的部分。

#### 量子態（quantum state）

一個量子態可以用一個複數向量表示：

$$
|\psi\rangle = \alpha|0\rangle+\beta|1\rangle,
\qquad |\alpha|^2+|\beta|^2=1.
$$

- $|0\rangle$ 和 $|1\rangle$ 是基底狀態，可以想成「硬幣是正面」和「硬幣是反面」。
- $\alpha,\beta$ 是**振幅（amplitudes）**，可以是複數。
- 量測時，看到 0 的機率是 $|\alpha|^2$，看到 1 的機率是 $|\beta|^2$。

注意：**振幅不是機率**，振幅的絕對值平方才是機率。振幅有正負號或相位，這就是干涉的來源。

#### 疊加（superposition）

$$
|\psi\rangle=\frac{1}{\sqrt2}|0\rangle+\frac{1}{\sqrt2}|1\rangle
$$

表示「0 和 1 各有一半機率」。但在量測之前，它不是「已經決定是 0 或 1，只是我們不知道」；它是真正的疊加態。這句話在哲學上有很多爭論，但在計算上，你只需要知道：**用振幅相加，最後平方取機率**。

#### 相位（phase）與干涉（interference）

如果一個振幅是 $\frac{1}{\sqrt2}$，另一個是 $-\frac{1}{\sqrt2}$，相加會是 0。這就是**破壞性干涉**：兩條路徑互相抵消。

如果兩個都是 $+\frac{1}{\sqrt2}$，相加會是 $\sqrt2$，平方後機率變成 2 倍。這就是**建設性干涉**。

量子漫步比古典漫步多出來的能力，本質上就是「多條路徑的振幅可以互相干涉」。

#### 么正演化（unitary evolution）

量子態的演化是

$$
|\psi(t)\rangle=U(t)|\psi(0)\rangle,
$$

其中 $U(t)$ 是么正矩陣。么正保證 $\||\psi(t)\rangle\|=1$，也就是總機率永遠是 1。

#### 量測（measurement）

如果我們在基底 $\{|x\rangle\}$ 量測，看到 $x$ 的機率是

$$
\Pr(x)=|\langle x|\psi\rangle|^2.
$$

量測之後，狀態會「塌縮」到 $|x\rangle$（在這個專案裡，我們還會把它重置成 $|\bar0\rangle|x\rangle$，後面會解釋）。

#### 兩個 register（暫存器）與 tensor product

量子漫步需要兩個 vertex register，可以想成兩個抽屜：

- 第一個抽屜放「上一個位置」或「ancilla」。
- 第二個抽屜放「現在的位置」。

數學上寫成

$$
|a\rangle\otimes|x\rangle \equiv |a,x\rangle.
$$

在程式裡，我們用一個形狀為 `(2, n, n)` 的陣列表示：

- 第一個維度：ancilla（0 或 1）。
- 第二個維度：第一個 register。
- 第三個維度：第二個 register（vertex）。

### 1.6 為什麼量子漫步可能比較快？

古典隨機漫步在圖上是「擴散」的：走 $t$ 步，典型距離是 $\sqrt{t}$。

量子漫步是「波動」的：不同路徑的振幅可以建設性干涉，讓機率集中到某些點，典型距離是 $t$。

因此，如果古典需要 $T$ 步才能碰到目標，量子可能只需要 $\sqrt{T}$ 步。這就是 quadratic speedup 的直覺。

但要注意：**量子漫步不是萬能加速**。它需要正確的 initial state、正確的 walk operator、正確的測量方式。Szegedy walk 的「detection」與「finding」之差，就是這個專案的核心之一。

---

## 2. Classical random walk 與 hitting time

### 2.1 定義

給定圖 $G$、transition matrix $P$、marked set $M\subset V$。

**Hitting time** 是「從平穩分布出發，第一次碰到 $M$ 的期望步數」：

$$
\mathrm{HT}(P,M)=\mathbb{E}_{X_0\sim\pi}\left[\min\{t\ge0:X_t\in M\}\right].
$$

如果你覺得「從平穩分布出發」很抽象，可以想成： random walker 已經在圖上晃了很久，現在隨機選一個點開始，問「平均還要幾步才會碰到目標」。

### 2.2 怎麼算？

對每個不在 $M$ 的點 $x$，令 $h_x$ 是「從 $x$ 出發，第一次碰到 $M$ 的期望步數」。顯然 $h_x=0$ 若 $x\in M$。

從 $x$ 出發走一步，會到某個鄰居 $y$，所以

$$
h_x=1+\sum_yP_{xy}h_y.
$$

這是一個線性方程組。把所有不在 $M$ 的點排成一個向量 $h_U$，可以把方程寫成

$$
(I-P_{UU})h_U=\mathbf 1,
$$

其中 $P_{UU}$ 是 $P$ 限制在 unmarked 點的子矩陣。解這個線性系統就得到所有 $h_x$。

最後，對平穩分布取平均（且條件在「起點不在 $M$」）：

$$
\mathrm{HT}(P,M)=\frac{\sum_{x\notin M}\pi_xh_x}{1-p_M},
\qquad p_M=\sum_{x\in M}\pi_x.
$$

### 2.3 三個標準例子

- **Complete graph $K_N$**：每個點都連到其他所有點。從任一個 unmarked 點出發，每次有 $1/(N-1)$ 的機率直接跳到目標，期望步數是 $N-1$。所以 $\mathrm{HT}=N-1$。
- **Cycle $C_N$**：環狀圖。從距離目標 $i$ 步的點出發，期望時間是 $i(N-i)$。對所有 unmarked 點平均，得到
  $$
  \mathrm{HT}=\frac{N(N+1)}{6}.
  $$
- **2D grid $L\times L$**：$\mathrm{HT}=\Theta(N\log N)$，其中 $N=L^2$。
- **Hypercube $Q_d$**：$N=2^d$，$\mathrm{HT}=\Theta(N\log N)$（在這個專案的尺寸範圍內看起來像 $N\log N$）。

這些公式在 `tests/test_classical.py` 裡被當作 sanity check。

### 2.4 程式怎麼實作？

在 `src/classical.py`：

- `stationary_distribution(P)`：解 $\pi P=\pi$ 且 $\sum\pi_i=1$。程式用最小平方法解一個線性系統。
- `hitting_times(P, marked)`：解 $(I-P_{UU})h=\mathbf1$。
- `mean_hitting_time(P, marked)`：把 $h$ 用平穩分布平均，並除以 $1-p_M$。
- `monte_carlo_hitting_time(...)`：用模擬的方式估計 hitting time，用來驗證線性解。
- `hit_probability_curve(...)`：計算「在 $t$ 步內碰到目標」的累積機率。
- `diffusion(...)`、`diffusion_trajectory(...)`：單純的古典擴散，沒有吸收邊界。

### 2.5 白話總結

Classical hitting time 就是「平均要走幾步才找到目標」。它是一個**古典 baseline**。如果量子漫步真的有用，它的搜尋時間應該比這個 baseline 小，而且 scaling 要更好。

---

## 3. Szegedy quantum walk

### 3.1 為什麼需要兩個 register？

古典 walker 只有一個位置 $x$。量子 walker 需要記住「從哪裡來」或「上一個位置」，因為量子演化是可逆的；如果只記現在位置，很多資訊會丟失。

Szegedy walk 用兩個 register：

- 第一個 register：可以想成「邊的上端」或「上一個位置」。
- 第二個 register：現在的位置。

初始時，第一個 register 固定在 $|\bar0\rangle$，第二個 register 是位置的疊加。

### 3.2 三個基本操作

#### (1) $V(P)$：把「位置」變成「鄰居的疊加」

$$
V(P)|\bar0\rangle|x\rangle
=\sum_y\sqrt{P_{xy}}|y,x\rangle.
$$

白話：如果你現在在 $x$，$V(P)$ 會把第一個 register 變成「從 $x$ 出發，以 $\sqrt{P_{xy}}$ 的振幅走到 $y$」的疊加，第二個 register 仍然記著 $x$。

#### (2) Shift：交換兩個 register

$$
\mathrm{Shift}|x,y\rangle=|y,x\rangle.
$$

白話：把「上一步」和「現在」交換。

#### (3) Ref：對第一個 register 的 $|\bar0\rangle$ 做反射

$$
\mathrm{Ref}=(2|\bar0\rangle\langle\bar0|-I)\otimes I.
$$

白話：如果第一個 register 是 $|\bar0\rangle$，保持不變；如果不是，乘上 $-1$。這是一個「相位翻轉」，是量子搜尋中常用的技巧。

#### (4) 組合起來：$W(P)$

$$
W(P)=V^\dagger(P)\,\mathrm{Shift}\,V(P)\,\mathrm{Ref}.
$$

這就是 Szegedy walk operator。它是么正的，因為每個因子都是么正的。

### 3.3 Discriminant matrix $D$

定義

$$
D_{xy}=\sqrt{P_{xy}P_{yx}}.
$$

對 reversible chain，$D$ 是對稱的，且

$$
D=\mathrm{diag}(\pi)^{1/2}P\,\mathrm{diag}(\pi)^{-1/2}.
$$

最重要的性質是：

$$
\langle\bar0|\langle x|W(P)|\bar0\rangle|y\rangle=D_{xy}.
$$

白話：如果你把 $W(P)$ 的「第一個 register 是 $\bar0$」的那一塊切出來，它剛好就是 $D$。這也是為什麼 $D$ 被叫做 discriminant matrix：它把 quantum walk 的資訊壓縮成一個 $n\times n$ 矩陣。

### 3.4 Spectral lemma（譜引理）

如果 $D$ 的特徵分解是

$$
D=\sum_k\lambda_k|v_k\rangle\langle v_k|,
$$

則 $W(P)$ 的非平凡特徵值是 $e^{\pm i\theta_k}$，其中

$$
\lambda_k=\cos\theta_k.
$$

白話：$D$ 的特徵值 $\lambda_k$ 控制 $W(P)$ 的振盪頻率。$\lambda_k$ 越接近 1，對應的振盪越慢；$\lambda_k$ 越接近 -1，振盪越快。

這個引理是 Szegedy walk 的譜分析基礎，也是 AGJK 定義 $\mathrm{HT}^+$ 的起點。

### 3.5 Detection 與 finding 的差別

Szegedy 的搜尋演算法可以在 $O(\sqrt{\mathrm{HT}})$ 步內**偵測**「有 marked vertex」。但「偵測到有」不等於「找到是哪一個」。

打個比方：你在一棟大樓裡聞到咖啡香，知道有人在泡咖啡（detection），但你不一定知道是哪一間房間（finding）。

對單一 marked vertex，detection 和 finding 差不多；但對多個 marked vertices，detection 可能很快，finding 卻可能很慢。這就是 AGJK 要解決的問題。

### 3.6 一個重要的陷阱：$W(0)$ 的 fixed point

如果你直接從 $|\bar0\rangle|\sqrt{\pi}\rangle$ 開始，跑 $W(P)$，你會發現 marked 的機率**完全不變**：

$$
p_M(t)=\sum_{x\in M}\pi_x=p_M.
$$

為什麼？我們可以一步一步推：

1. $\mathrm{Ref}$ 對 $|\bar0\rangle|\sqrt\pi\rangle$ 沒有作用，因為第一個 register 已經是 $\bar0$。
2. $V(P)$ 把它變成
   $$
   \sum_x\sqrt{\pi_x}\sum_y\sqrt{P_{xy}}|y,x\rangle.
   $$
3. $\mathrm{Shift}$ 交換 register：
   $$
   \sum_{x,y}\sqrt{\pi_x}\sqrt{P_{xy}}|x,y\rangle.
   $$
4. 利用 detailed balance $\pi_xP_{xy}=\pi_yP_{yx}$，可以把係數改寫成
   $$
   \sqrt{\pi_y}\sqrt{P_{yx}}.
   $$
5. 再作用 $V^\dagger$，會把第一個 register 收回 $|\bar0\rangle$，得到
   $$
   |\bar0\rangle\sum_y\sqrt{\pi_y}|y\rangle
   =|\bar0\rangle|\sqrt\pi\rangle.
   $$

也就是說，$|\bar0\rangle|\sqrt\pi\rangle$ 是 $W(0)$ 的特徵向量，特徵值 1。這就是為什麼「plain Szegedy walk + stationary initial state」不能用來搜尋：它根本不會動。

**這個專案的做法**：
- E1/E2 使用 **interpolated walk** $W(s)$，$s>0$，打破這個 fixed point。
- E5 使用 **cue initial state**（不是 stationary），所以 $W(0)$ 也不是 fixed point。

這個陷阱是很多人第一次實作 Szegedy walk 會卡住的地方。

### 3.7 程式碼對照：`src/szegedy.py`

#### `discriminant_matrix(P)`

```python
return np.sqrt(P * P.T)
```

- `P * P.T` 是 element-wise 相乘，不是矩陣乘法。
- 所以 $(P * P^T)_{xy}=P_{xy}P_{yx}$。
- 再開根號就是 $D_{xy}=\sqrt{P_{xy}P_{yx}}$。

#### `_householder_completion(p)`

這個函數的任務是：給定一個單位向量 $p$，造一個么正矩陣 $A$，使得 $A|0\rangle=p$。

我們需要這個，是因為 $V(P)$ 只定義了 $|\bar0\rangle|x\rangle$ 的動作，其他基底狀態的動作可以任意補完，只要保持么正。Householder reflection 是一種標準補法。

白話：我們需要一個「旋轉」，把 $|0\rangle$ 轉到 $p$，而且不改變長度。

#### `walk_operator_blocks(P)`

```python
blocks = np.empty((n, n, n), dtype=complex)
for vertex in range(n):
    blocks[:, :, vertex] = _householder_completion(np.sqrt(P[vertex]))
```

`blocks[:, :, x]` 就是 $A_x$，也就是「從 $x$ 出發」的那個么正矩陣。形狀 `(n,n,n)` 是因為我們對每個 vertex 都存一個 $n\times n$ 矩陣。

#### `apply_v(state, blocks, adjoint=False)`

```python
np.einsum("ijx,jx->ix", blocks, state)
```

`state` 的形狀是 `(n,n)`，`state[j,x]` 是第一個 register 在 $j$、第二個 register 在 $x$ 的振幅。`blocks[i,j,x]` 是 $A_x$ 的 $(i,j)$ 元素。這個 einsum 對每個 $x$ 做一次矩陣乘法：

$$
\text{out}[i,x]=\sum_j A_x[i,j]\,\text{state}[j,x].
$$

#### `apply_reflection(state)`

```python
reflected = state.copy()
reflected[1:, :] *= -1.0
```

第一個 register 是 0 的列保持不變，其他列乘 -1。這就是 $\mathrm{Ref}$。

#### `apply_walk(state, P, blocks)`

```python
reflected = apply_reflection(state)
stepped = apply_v(reflected, blocks)
shifted = stepped.T
return apply_v(shifted, blocks, adjoint=True)
```

順序是：Ref → V → Shift → V†。`stepped.T` 就是交換兩個 register。`adjoint=True` 表示作用 $V^\dagger$。

#### `walk_matrix(P)`

這個函數把 $W(P)$ 組成一個 $n^2\times n^2$ 的 dense matrix，主要是給測試用。真正跑大圖時，我們用 `apply_walk` 的函數形式，避免爆記憶體。

#### `initial_state(P)`

```python
state[0, :] = np.sqrt(distribution)
```

把第一個 register 設為 0，第二個 register 設為 $\sqrt{\pi}$ 的振幅。這正是 $|\bar0\rangle|\sqrt\pi\rangle$。

#### `success_probability_curve(...)`

每一步計算

$$
p_M(t)=\sum_{x\in M}\sum_{a}|\text{state}[a,x]|^2,
$$

其中 $a$ 是第一個 register。因為 marked 的條件只看第二個 register（vertex register）。

#### `chebyshev_lower_bound(...)`

這是用 Chebyshev recurrence 計算 $q_t$ 的下界，不需要跑完整的 $W(P)$。公式是

$$
T_0(D)=I,\quad T_1(D)=D,\quad T_{t+1}(D)=2DT_t(D)-T_{t-1}(D).
$$

程式用向量版本：

```python
following = 2.0 * (matrix @ current) - previous
```

這樣只需要 $O(n^2)$ 每步，比完整 $W(P)$ 的 $O(n^3)$ 快很多。

#### `spectral_gap(P)`

程式定義為

$$
1-\max_{k\ne1}|\lambda_k|.
$$

這是 absolute spectral gap。注意：對 bipartite graph，$\lambda=-1$ 會讓 gap 變成 0；這不是 bug，而是 absolute gap 的定義。

### 3.8 測試在測什麼？

`tests/test_quantum.py` 裡的測試：

- `test_walk_matrix_is_unitary`：$W^\dagger W=I$。
- `test_top_left_block_is_discriminant_matrix`：$W$ 的左上角 $n\times n$ 塊等於 $D$。
- `test_apply_walk_matches_dense_matrix`：函數版與 dense matrix 版結果一致。
- `test_norm_is_preserved`：走很多步後 norm 仍然是 1。
- `test_success_curve_is_bounded_by_chebyshev_bound`：$q_t\le p_M(t)$。
- `test_interpolated_walk_is_unitary`：$W(s)$ 也是么正的。
- `test_interpolated_walk_is_stationary_at_zero_interpolation`：$s=0$ 時 success 曲線是常數 $\pi_M$（就是上面說的 fixed point）。
- `test_interpolation_amplifies_the_marked_vertex`：$s>0$ 時 marked 機率會上升。
- `test_ht_extended...`：單一 marked 時 $\mathrm{HT}^+\approx\mathrm{HT}$；多個 marked 時 $\mathrm{HT}^+\ge\mathrm{HT}$（在容許誤差內）。

這些測試的目的不是「證明定理」，而是「確定程式沒有寫錯」。

---

## 4. AGJK：finding marked vertices 與 HT⁺

### 4.1 AGJK 想解決什麼？

Szegedy 可以**偵測** marked vertex，但量測最終狀態不一定會給你 marked vertex。AGJK 的問題是：

> 給定任意圖、任意 marked set，能不能用量子漫步**找到**一個 marked vertex，而且時間是 $\widetilde O(\sqrt{\mathrm{HT}})$？

答案是：可以，up to log factors。

### 4.2 吸收漫步 $P'$

首先定義 **absorbing walk**：

$$
P'=\begin{pmatrix}
P_{UU} & P_{UM}\\
0 & I
\end{pmatrix}.
$$

白話：一旦走到 marked vertex，就永遠留在那裡（吸收）。$U$ 是 unmarked set，$M$ 是 marked set。

### 4.3 Interpolated walk $P(s)$

$$
P(s)=(1-s)P+sP',\qquad s\in[0,1).
$$

白話：在「正常走」和「走到目標就停」之間插值。
- $s=0$：完全是原本的 $P$。
- $s\to1$：越來越接近吸收漫步。
- $s$ 可以想成「承諾／吸收強度」。

### 4.4 量子版 $W(s)$

量子版需要一個 ancilla qubit 記錄「現在是否 marked」。對於 $x\notin M$，$V(P,s)$ 和原本的 $V(P)$ 一樣；對於 $x\in M$，它會把状態映射成

$$
|0\rangle|\bar0\rangle|x\rangle
\mapsto
\sqrt{1-s}|0\rangle V(P)|\bar0\rangle|x\rangle
+\sqrt{s}|1\rangle|\bar0\rangle|x\rangle.
$$

白話：如果走到 marked vertex，有 $\sqrt{s}$ 的振幅跑到 ancilla=1 的分支（停住），有 $\sqrt{1-s}$ 的振幅繼續走。

然後

$$
W(s)=V^\dagger(P,s)\,\mathrm{Shift}'\,V(P,s)\,\mathrm{Ref}'.
$$

在程式裡，state 的形狀是 `(2, n, n)`：`state[0]` 是 ancilla=0，`state[1]` 是 ancilla=1。

### 4.5 Extended hitting time $\mathrm{HT}^+$

AGJK 定義

$$
\mathrm{HT}(s)=\frac{1}{1-p_M}
\sum_{k=1}^{n-1}
\frac{|\langle v_k(s)|\sqrt{\pi_U}\rangle|^2}{1-\lambda_k(s)},
$$

其中 $D(s)$ 的特徵分解是 $\sum_k\lambda_k(s)|v_k(s)\rangle\langle v_k(s)|$，且 $\lambda_n(s)=1$。

然後

$$
\mathrm{HT}^+=\lim_{s\to1}\mathrm{HT}(s).
$$

白話：
- $\mathrm{HT}$ 是「古典要走多久」。
- $\mathrm{HT}^+$ 是「interpolated walk 在 $s\to1$ 時的 effective hitting time」。
- 如果只有一個 marked vertex，$\mathrm{HT}^+=\mathrm{HT}$。
- 如果有多個 marked vertices，$\mathrm{HT}^+$ 可能遠大於 $\mathrm{HT}$。

### 4.6 為什麼 $\mathrm{HT}^+$ 會很大？

AGJK 構造了一個 $N\times N$ torus 上的 marked set：

$$
M=M_1\cup M_2,
$$

其中 $M_1$ 是一個密集的小方格，$M_2$ 是一個稀疏的週期性格點。這個排列會讓 discriminant matrix 出現非常接近 1 的特徵值，導致 $\mathrm{HT}^+$ 的分母 $1-\lambda_k$ 很小，所以 $\mathrm{HT}^+$ 很大。

在我們的程式裡，`adversarial_torus_marked` 就是造這個 marked set：

```python
dense = [(row * d1) * length + (column * d1)
         for row in range(k1) for column in range(k1)]
sparse = [(row * d) * length + (column * d)
          for row in range(length // d) for column in range(length // d)]
return sorted(set(dense) | set(sparse))
```

`dense` 是 $M_1$，`sparse` 是 $M_2$。參數必須滿足 `d1 | d | length`，程式會檢查。

### 4.7 演算法 1（AGJK Algorithm 1）

1. 準備 $|\bar0\rangle|\sqrt\pi\rangle$。
2. 作用 $W(s)$ 共 $t$ 步。
3. 量測 ancilla。
4. 如果 ancilla=1，量測 vertex register，輸出結果；否則輸出「沒找到」。

AGJK 的 Conjecture 3 說：存在 $s$ 和 $t=O(\sqrt{\mathrm{HT}})$，使得成功率是 $\Omega(1)$。這是數值 conjecture，不是已證定理。

AGJK 的另一個演算法用 **quantum fast-forwarding**，證明了 $\widetilde O(\sqrt{\mathrm{HT}})$ 的保證（Theorem 5）。我們沒有實作 fast-forwarding，只引用它。

### 4.8 Chebyshev 下界 $q_t(s)$

$$
q_t(s)=\left\|\Pi_M T_t(D(s))|\sqrt\pi\rangle\right\|^2.
$$

這個量是「如果你只保留第一個 register 是 $\bar0$ 的那一部分，成功機率的下界」。因為投影到子空間只會讓 norm 變小，所以

$$
q_t(s)\le p_{\text{success}}(t).
$$

在程式裡：
- `interpolated_lower_bound` 用 Chebyshev recurrence 算 $q_t(s)$，$O(n^2)$ 每步。
- `interpolated_success_curve` 用完整 $W(s)$ 算真正的 $p_M(t)$，$O(n^3)$ 每步。
- 我們先掃 $s$ 找 $q_t(s)$ 最大的值，再用完整 $W(s)$ 驗證。

### 4.9 為什麼要掃 $s$？

因為 Conjecture 3 只說「存在某個 $s$」，沒有告訴你怎麼選。文獻裡有不同選擇，例如 $r=1/(1-s)$、$r\sim d^2$、$r\sim k^2$ 等。我們的做法是：

- 在 `configs/base.yaml` 給一個 $s$ 的 grid。
- 對每個 $s$ 算 $q_t(s)$，$t\le3\sqrt{\mathrm{HT}}+5$。
- 選 $q_t$ 最大的 $s$。
- 用這個 $s$ 跑完整 $W(s)$，記錄 $p_{\max}$ 和 $T_q$。

這是一個數值 protocol，不是定理。但它的好處是：我們不需要猜 $s$，而且結果可以重現。

### 4.10 程式碼對照：`src/agjk.py`

#### `absorbing_transition(P, marked)`

把 marked 的列改成「留在自己」：

```python
absorbing[marked, :] = 0.0
absorbing[marked, marked] = 1.0
```

#### `interpolated_transition(P, marked, s)`

```python
return (1.0 - s) * P + s * absorbing_transition(P, marked)
```

就是 $P(s)=(1-s)P+sP'$。

#### `interpolated_stationary(...)`

這是 $P(s)$ 的平穩分布：

$$
\pi(s)=\frac{(1-s)\pi_U+\pi_M}{1-s(1-p_M)}.
$$

程式直接照公式寫。

#### `ht_spectral(P, marked, s)`

用 `np.linalg.eigh` 對 $D(s)$ 做特徵分解，然後照 $\mathrm{HT}(s)$ 的公式加總。`ht_extended` 就是取 $s=1-10^{-6}$。

#### `_coin(s)`

這是 ancilla 的 2×2 么正矩陣：

$$
C_s=\begin{pmatrix}
\sqrt{1-s} & -\sqrt{s}\\
\sqrt{s} & \sqrt{1-s}
\end{pmatrix}.
$$

它把 $|0\rangle$ 映射到 $\sqrt{1-s}|0\rangle+\sqrt{s}|1\rangle$，就是「以 $\sqrt{s}$ 的振幅停住」。

#### `interpolated_initial_state(P, distribution)`

建立 `(2,n,n)` 的 state，`state[0,0,:]=sqrt(distribution)`。第一個 0 是 ancilla，第二個 0 是第一個 register。

#### `apply_interpolated_reflection`、`apply_interpolated_shift`

和 Szegedy 版類似，只是多了 ancilla 維度。Reflection 對 `(ancilla=0, first=0)` 保持 +1，其他乘 -1。Shift 只在 ancilla=0 時交換兩個 register。

#### `apply_interpolated_v`

這是最容易看錯的函數。它的邏輯是：
- 對所有 vertex 先做一般的 $V(P)$。
- 對 marked vertex，套用 coin，然後只對 ancilla=0 的分支做 $V(P)$；ancilla=1 的分支保持不動。
- `adjoint=True` 時反過來：先做 $V^\dagger$，再套 coin†。

程式用 `np.einsum` 和 advanced indexing 完成。如果你要修改，請先看 `tests/test_quantum.py` 的 unitarity 測試。

#### `interpolated_success_curve(...)`

每一步計算

$$
p_M(t)=\sum_{a}\sum_{x\in M}|\text{state}[a,x]|^2.
$$

注意這裡的 `state` 形狀是 `(2,n,n)`，所以 `state[:, :, marked]` 取出 marked 的所有 ancilla 與 first register。

#### `interpolated_lower_bound(...)`

用 $D(s)$ 和 Chebyshev recurrence 算 $q_t(s)$。這個函數不需要 `blocks`，因為它只用到 $D(s)$。

### 4.11 白話總結

- Szegedy walk 是「量子版的隨機漫步」。
- 直接跑 $W(0)$ 從 stationary state 出發不會動，因為它是 fixed point。
- AGJK 用 interpolated walk $W(s)$ 打破 fixed point，讓我們可以找到 marked vertex。
- $\mathrm{HT}^+$ 是「interpolated walk 的 effective hitting time」，多個 marked vertices 時可能很大。
- 我們用 Chebyshev 下界選 $s$，再用完整 $W(s)$ 驗證。

## 5. Quantum cognition：量子認知到底在說什麼

### 5.1 先講清楚：不是「大腦是量子電腦」

量子認知（quantum cognition）是一個**數學模型**的學派。它借用希爾伯特空間、疊加、投影、干涉這些量子力學的數學工具，來描述判斷、記憶、決策等心理現象。

它**不是**說：

- 大腦裡真的有量子位元。
- 神經元在跑量子電路。
- 人類有量子加速。

它說的是：

> 有些認知現象用古典機率描述起來很彆扭，但用「振幅相加、最後平方」的量子機率會很自然。

所以我們的報告從頭到尾都把「algorithmic advantage」和「biological plausibility」分開。這是報告 Discussion 很重要的一段。

### 5.2 古典機率 vs 量子機率

古典機率：

$$
\Pr(A\cup B)=\Pr(A)+\Pr(B)\quad\text{若 }A,B\text{ 互斥}.
$$

量子機率：

$$
\Pr(A\cup B)=\left|\alpha_A+\alpha_B\right|^2
=|\alpha_A|^2+|\alpha_B|^2+2\Re(\alpha_A^*\alpha_B).
$$

最後一項 $2\Re(\alpha_A^*\alpha_B)$ 就是**干涉項**。它可以是正的（建設性干涉），也可以是負的（破壞性干涉）。

打個比方：
- 古典機率像「兩條水管的水量相加」。
- 量子機率像「兩道水波疊加」，波峰碰波峰會變大，波峰碰波谷會抵消。

### 5.3 為什麼這對認知有用？

古典機率很難自然解釋的現象包括：

- **順序效應（order effects）**：先問 A 再問 B，和先問 B 再問 A，答案的機率不同。因為第一個問題的「量測」改變了心理狀態。
- **脈絡效應（context effects）**：同一個選項，在 different choice set 下，被選中的機率不同。
- **相似性效應（similarity effect）**：兩個選項越相似，它們之間的競爭越強，第三個選項可能反而得利。
- **干涉與洞察（insight）**：多條思考路徑互相干涉，可能突然產生一個高機率的答案。

量子認知的模型通常長這樣：

- 心理狀態 = 一個向量 $|\psi\rangle$。
- 問題 / 判斷 = 一個投影算子 $\Pi$。
- 回答「是」的機率 = $\|\Pi|\psi\rangle\|^2$。
- 回答之後，狀態塌縮到 $\Pi|\psi\rangle$，所以下一個問題的答案會受影響。

### 5.4 量子漫步在認知裡的角色

量子漫步是「過程模型」：它不是只有一個靜態的機率分布，而是描述**隨時間展開的證據累積**。

- 圖的頂點 = 概念、證據狀態、或選項。
- 邊 = 語意關聯、注意力轉移、或證據路徑。
- marked set = 目標記憶、被選擇的選項、或決策邊界。
- 初始態 = cue、問題、初始注意力。
- 演化 = deliberation（思考）。
- 量測 / 吸收 = 做出決定。
- success probability $p_M(t)$ = 在時間 $t$ 已經找到目標的機率。
- response time = 第一次達到門檻的時間，或 success probability 最高的時間。

### 5.5 認知映射表

| 漫步物件 | 認知解釋 |
|---|---|
| 頂點 $x\in V$ | 概念、證據狀態、選項 |
| 邊 $(x,y)\in E$ | 語意關聯、證據轉移 |
| marked set $M$ | 目標記憶、決策邊界 |
| 初始態 $|\psi_0\rangle$ | cue、問題、初始注意力 |
| $W(s)$ 或 $e^{-iLt}$ | 思考 / 證據累積 |
| 量測 | 做出回答或決定 |
| $p_M(t)$ | 目標活化 / 成功率 |
| $T_q=\arg\max_t p_M(t)$ | 峰值反應時間 |
| 第一次超過門檻 | deadline 下的反應時間 |
| 多個 option sets $M_i$ | 多選項決策 |
| $P_i$ | 選擇機率 |
| $\mathrm{HT}$、$\mathrm{HT}^+$ | 搜尋困難度、脈絡困難度 |
| spectral gap $\lambda_1$ | 思考 / 鬆弛速度 |
| 插值參數 $s$ | 承諾 / 吸收強度 |
| 測量率 $p$ | 內省 / 雜訊強度 |

### 5.6 五個建模假設

1. **Process level**：模型描述的是搜尋或決策的統計過程，不是生物物理實現。
2. **Interference = 多條路徑**：量子干涉代表多條證據路徑或語意關聯的交互作用，不是神經元裡的量子態。
3. **Classical baseline**：古典對照組是同一張圖上的 Markov random walk，使用同樣的初始分布與 marked set。這樣才能把「圖結構」和「干涉」分開。
4. **Defined, not fitted**：反應時間、選擇機率、活化、熵、半徑都是從漫步統計量**定義**出來的，不是 fit 真人資料。
5. **Graph as prior**：圖是模型的語意或決策先驗。改邊或權重，就會改變預測的脈絡效應。

### 5.7 這個專案的三個認知實驗

- **E3（語意）**：cue `animal`，目標 `dog`（近）與 `violin`（遠）。比較 CTQW 與 CRW 的目標活化。
- **E4（決策）**：多分支決策圖，選項之間有耦合。比較 CTQW 與 absorbing CRW 的選擇機率與決策時間。
- **E5（雜訊）**：在 grid $6\times6$ 與 toy semantic graph 上加入 partial measurement（讀出模型與偵測模型），掃描測量率 $p$ 與 deadline $T$。

---

## 6. CTQW 與 CRW：語意圖上的連續時間漫步

### 6.1 為什麼要用連續時間？

E1/E2 用的是 **discrete-time** Szegedy walk：一步、一步、一步。

E3 用的是 **continuous-time** walk：時間 $t$ 是連續的，狀態隨時間平滑演化。

連續時間的好處是：不需要選「一步」有多長，可以直接用物理時間或擴散時間比較。Pavone–Faro 的語意圖論文也是用 continuous-time quantum walk（CTQW）。

### 6.2 圖 Laplacian

給定 adjacency matrix $A$ 和 degree matrix $D=\mathrm{diag}(\deg)$：

- **Combinatorial Laplacian**：
  $$
  L=D-A.
  $$
- **Symmetric normalized Laplacian**：
  $$
  L_{\mathrm{sym}}=I-D^{-1/2}AD^{-1/2}.
  $$
- **Random-walk Laplacian**：
  $$
  L_{\mathrm{rw}}=I-D^{-1}A.
  $$

$L_{\mathrm{sym}}$ 是對稱的，所以可以當作 Hermitian Hamiltonian。$L_{\mathrm{rw}}$ 不是對稱的，但它和 $L_{\mathrm{sym}}$ 有相同的特徵值（相似變換）。

### 6.3 CTQW 與 CRW 的定義

CTQW：

$$
|\psi(t)\rangle=e^{-iL_{\mathrm{sym}}t}|c\rangle,
\qquad
p_T(t)=|\langle T|\psi(t)\rangle|^2.
$$

CRW：

$$
\rho(t)=\rho(0)e^{-L_{\mathrm{rw}}t},
\qquad
p_T(t)=\rho_T(t).
$$

其中 $c$ 是 cue vertex，$T$ 是 target。

白話：
- CTQW 是「量子波」從 cue 出發，沿著圖傳播，目標的振幅平方就是活化。
- CRW 是「古典機率」從 cue 出發，沿著圖擴散，目標的機率就是活化。

### 6.4 特徵分解與程式實作

對對稱矩陣 $L_{\mathrm{sym}}$ 做特徵分解：

$$
L_{\mathrm{sym}}=V\Lambda V^T,
\qquad
\Lambda=\mathrm{diag}(\lambda_1,\dots,\lambda_n).
$$

則

$$
e^{-iL_{\mathrm{sym}}t}=V\,\mathrm{diag}(e^{-i\lambda_1t},\dots,e^{-i\lambda_nt})\,V^T.
$$

CTQW 的程式就是：

```python
eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
coefficients = eigenvectors.T @ initial
phases = np.exp(-1j * np.outer(eigenvalues, times))
return eigenvectors @ (phases * coefficients[:, None])
```

逐行解釋：
- `np.linalg.eigh` 是「對稱矩陣專用的特徵分解」，比一般 `eig` 穩定。
- `coefficients` 是把初始態寫成特徵向量的線性組合。
- `phases` 是每個特徵向量隨時間的相位 $e^{-i\lambda_k t}$。
- 最後乘回去，得到每個時間點的状态。

CRW 比較麻煩，因為 $L_{\mathrm{rw}}$ 不是對稱的。程式用相似變換：

$$
L_{\mathrm{rw}}=D^{-1/2}L_{\mathrm{sym}}D^{1/2},
$$

所以

$$
e^{-L_{\mathrm{rw}}t}=D^{-1/2}e^{-L_{\mathrm{sym}}t}D^{1/2}.
$$

程式：

```python
root_degree = np.sqrt(degree)
coefficients = eigenvectors.T @ (initial / root_degree)
decay = np.exp(-np.outer(eigenvalues, times))
trajectory = root_degree[:, None] * (eigenvectors @ (decay * coefficients[:, None]))
```

白話：
- 先把初始分布除以 $\sqrt{\deg}$。
- 用 $L_{\mathrm{sym}}$ 的特徵分解做衰減。
- 再乘回 $\sqrt{\deg}$。
- 最後 clip 掉極小的負值（數值誤差），再 normalize。

### 6.5 為什麼要 normalized？

如果直接用 combinatorial Laplacian，degree 很大的點會主導動力學。Normalized Laplacian 會把 degree 的影響部分消掉，讓不同 degree 的圖比較公平。對語意圖來說，這通常比較合理。

### 6.6 時間正規化：$\tau=\lambda_1t$

不同圖的 spectral gap $\lambda_1$ 不同。$\lambda_1$ 越小，圖越難混合，relaxation time $1/\lambda_1$ 越大。

如果我們直接比較 $t$，大圖和小圖的時間尺度會不一樣。所以我們用

$$
\tau=\lambda_1t
$$

把時間除以 relaxation time。這樣 $\tau=1$ 大約代表「一個 relaxation time」，不同圖可以在同一個尺度上比較。

在 E3 的 toy graph 中，$\lambda_1=0.03335$，所以 relaxation time 約 $30$ 步。

### 6.7 Toy semantic graph

`toy_semantic_graph()` 建一個 19 節點的圖：

- **animal 社群**：animal, dog, cat, wolf, horse, cow, bird
- **vehicle 社群**：vehicle, car, bus, train, bicycle, airplane
- **instrument 社群**：instrument, piano, guitar, violin, drum, flute
- **bridge**：bird 連到 airplane 和 flute，把三個社群連起來。

每個節點都有一個 `concept` attribute，程式用

```python
nx.convert_node_labels_to_integers(graph, label_attribute="concept")
```

把字串標籤轉成整數，但保留 concept 名稱。

### 6.8 語意實驗的 metrics

- **$p_{\text{peak}}$**：目標活化曲線的最高點。
- **$\tau_{\text{peak}}$**：最高點出現的時間（用 $\tau$ 表示）。
- **AUC**：曲線下面積，代表「整體活化量」。
- **entropy**：峰值時整個分布有多分散。熵越大越分散。
- **coverage_half_peak**：有多少比例的節點，其機率至少是峰值的一半。
- **expected_radius_peak**：峰值時，離 cue 的期望 graph distance。半徑越大，代表活化越往遠處跑。

### 6.9 CTQW vs DTQW：不要混用

- **CTQW**：continuous time，Hamiltonian $H=L_{\mathrm{sym}}$，演化 $e^{-iHt}$，沒有 coin。
- **DTQW / Szegedy**：discrete time，有 coin、有 register、有 $W(P)$。

這兩個 formalism 的 time scale 不一樣，不能直接把 CTQW 的 $t$ 和 Szegedy 的步數放在同一張圖上比較。我們的報告明確區分：
- E1/E2/E4/E5 用 discrete-time Szegedy walk。
- E3 用 continuous-time CTQW/CRW。

### 6.10 程式碼對照：`src/semantic.py`

- `normalized_laplacian(graph)`：回傳 $L_{\mathrm{sym}}$、degree、stationary distribution。
- `random_walk_laplacian(graph)`：回傳 $L_{\mathrm{rw}}$。
- `spectral_gap(laplacian)`：回傳最小的正特徵值。
- `ctqw_trajectory(...)`：回傳每個時間點的量子態。
- `crw_trajectory(...)`：回傳每個時間點的古典分布。
- `target_curve(...)`：取出目標那條曲線。
- `semantic_metrics(...)`：算上面那些 metrics。

`semantic_metrics` 的 `radius` 是：

```python
distances = nx.single_source_shortest_path_length(graph, cue)
radius = sum(distribution[node] * distances.get(node, 0.0)
             for node in range(distribution.size))
```

白話：對每個節點，看它離 cue 多遠，用它的機率當權重，加權平均。

### 6.11 白話總結

CTQW/CRW 是「語意擴散」的兩個版本：
- 古典版本像墨水在紙上擴散，均勻但慢。
- 量子版本像波，會干涉，可能在某些點形成高峰。
- E3 的結果顯示：對遠距離目標，量子版本的峰值明顯較高，但出現得較晚。

---

## 7. 多選項決策：decision graph 與 choice probability

### 7.1 決策圖長什麼樣？

`branched_decision_graph(branch_lengths, coupling_pair, coupling_weight)` 建一個「中心 hub + 多條分支」的圖：

```
             option A terminal
                 ^
                 |
             ... A3
                 |
             ... A2
                 |
             ... A1
                 |
option C <-- hub --> option B
```

- 節點 0 是 hub。
- 每條分支是一條 path，長度由 `branch_lengths` 決定。
- 每條分支的最後一個節點是 option terminal。
- 所有分支都從 hub 出發。

例如 `branch_lengths=[4,4,4]`：
- hub = 0
- A 分支：1 → 2 → 3 → 4，terminal=4
- B 分支：5 → 6 → 7 → 8，terminal=8
- C 分支：9 → 10 → 11 → 12，terminal=12
- 總共 13 個節點。

### 7.2 耦合（coupling）是什麼？

`coupling_pair=(1,2)` 表示「把 B 和 C 兩條分支在相同深度用加權邊連起來」。
`coupling_weight=c` 是那條邊的權重。

白話：B 和 C 越耦合，代表這兩個選項越相似、越容易互相轉移。A 沒有被耦合，所以它是「比較不一樣」的選項。

為什麼用權重而不是直接加邊？因為權重可以連續調整，讓圖的 transition matrix 平滑改變。如果只加一條邊，$c$ 只能 0 或 1，不容易掃描。

### 7.3 Transition matrix 與 weighted graph

`transition_matrix(graph, weight="weight")` 會用邊的 `weight` attribute 當作 adjacency 的數值。也就是：

$$
A_{xy}=\text{edge weight}(x,y).
$$

然後對每一列 normalize：

$$
P_{xy}=\frac{A_{xy}}{\sum_zA_{xz}}.
$$

所以 coupling weight 越大，B 和 C 之間的轉移機率越大。

### 7.4 量子選項曲線

`quantum_option_curve(P, option_sets, initial, s, max_steps)`：

1. marked set = 所有 option terminal 的聯集。
2. 初始狀態 = 在 hub 的 one-hot 分布。
3. 每一步用 interpolated $W(s)$ 演化。
4. 對每個 option，算出它的 terminal 的機率。

為什麼 marked set 是「所有 terminal」？因為在決策模型裡，走到任何一個 terminal 都代表「做出某個選擇」。$W(s)$ 的 ancilla 會記錄「是否已經到達決策邊界」。

### 7.5 古典選項曲線

`absorbing_option_curve(P, option_sets, initial, max_steps)`：

1. 把所有 terminal 設成 absorbing（一旦到達就停住）。
2. 初始分布放在 hub。
3. 每一步用 $P$ 演化。
4. 記錄每個 terminal 的累積吸收機率。

這是古典決策的 baseline：像一個隨機漫步的證據累積器，碰到邊界就決定。

### 7.6 Decision time 與 choice probability

`decision_summary(curve, threshold=0.5)`：

- `curve[t, i]` = 第 $i$ 個選項在時間 $t$ 的機率。
- `total[t] = sum_i curve[t,i]` = 所有選項的總機率。
- `decision_time` = 第一個 `total >= threshold` 的時間；如果都沒有，取 `total` 最大的時間。
- `choice_probabilities` = `curve[decision_time] / total[decision_time]`。
- `choice_entropy` = 選擇分布的熵。
- `max_choice` = 最大的選擇機率。
- `choice_bias` = `max_choice - 1/k`。

白話：
- 決策時間是「證據累積到一定程度」的時間。
- 選擇機率是「在那個時間點，各個選項的相對機率」。
- 熵越低，選擇越集中；bias 越大，越偏向某個選項。

### 7.7 對稱 vs 非對稱

E4 有三個 case：

- **symmetric3**：三條分支等長（4,4,4），B 和 C 耦合。
- **asymmetric3**：三條分支不等長（3,4,5），B 和 C 耦合。
- **symmetric4**：四條分支等長（4,4,4,4），B 和 C 耦合。

在 symmetric3 中，當耦合強度 $c$ 增加：
- B 和 C 變成「一組相似的選項」。
- 量子漫步的機率會往 A 集中。
- 古典漫步則幾乎保持均勻。

先前版本曾在 asymmetric3 中報告非單調的選擇機率（A 的機率依序為
$0.145, 0.782, 0.094, \ldots$，對應 $c=0,0.1,0.25,\ldots$）。此為相位假象，已撤回。
在偵測讀出下，耦合對未耦合選項的影響是單調的（見 `Explain_v2.md` §5.4）。

### 7.8 這是「attraction effect」嗎？

我們在報告裡說它是「model-level analogue of similarity and attraction effects」，而不是說它等於心理學裡的 attraction effect。

為什麼保守？因為：
- 我們沒有真人資料。
- 我們的「選項價值」是對稱的，只有 graph 結構不對稱。
- 真正的 attraction effect 通常涉及一個 asymmetrically dominated decoy。

但這個模型確實展示了：**當兩個選項變得更相似，第三個選項的選擇機率可以不對稱地上升**。這是一個可檢驗的 model-level prediction。

### 7.9 程式碼對照：`src/cognitive.py`

- `vertex_distribution(state)`：把 `(n,n)` 的兩 register state 變成 vertex marginal。
- `activation_curve(...)`：從一組曲線中，對每個 option set 加總。
- `choice_probabilities(...)`：從一個分布算各 option 的機率。
- `response_time(...)`：第一個超過 threshold 的時間。
- `absorbing_option_curve(...)`：古典 absorbing 選項曲線。
- `quantum_option_curve(...)`：量子選項曲線。
- `decision_summary(...)`：把曲線變成 decision time、choice probability、entropy、bias。

`quantum_option_curve` 裡的

```python
curve[step] = [float(np.sum(np.abs(state[:, :, list(option)]) ** 2))
               for option in option_sets]
```

是對每個 option 的所有 terminal（可能不只一個）加總機率。`state[:, :, list(option)]` 的形狀是 `(2, n, len(option))`，平方後加總。

### 7.10 白話總結

- 決策圖把「選項」變成圖上的 terminal。
- 耦合讓兩個選項「越長越像」。
- 量子漫步對耦合非常敏感，會產生很強的 context effect。
- 古典漫步比較「平均」，不容易產生這種效果。
- 這是模型層級的預測，不是生物學主張。

---

## 8. Partial measurement：退相干與「內省」

### 8.1 什麼是 decoherence？

Decoherence（退相干）是量子系統和環境交互作用，導致相位資訊流失的過程。在我們的模型裡，最簡單的版本是：

> 每一步，以機率 $p$ 對 vertex register 做位置量測，然後把狀態重置到 $|\bar0\rangle|x\rangle$；以機率 $1-p$ 正常做么正演化。

- $p=0$：純量子漫步。
- $p=1$：每一步都量測，變成古典 random walk。
- $0<p<1$：介於兩者之間。

### 8.2 為什麼量測會讓它變古典？

量測會把疊加態塌縮到某個位置，破壞不同路徑之間的相位關係。沒有相位，就沒有干涉；沒有干涉，就只剩下古典的機率轉移。

打個比方：
- 純量子漫步像「多條路徑的波」。
- 每次量測就像「偷看一次」，偷看會讓波函數塌縮，路徑之間的干涉就消失了。

### 8.3 Density matrix（密度矩陣）最小版本

如果你只會 state vector，可以把 density matrix 想成「一個機率混合的量子態」。

- 對純態 $|\psi\rangle$，密度矩陣是 $\rho=|\psi\rangle\langle\psi|$。
- 對混合態，$\rho=\sum_i p_i|\psi_i\rangle\langle\psi_i|$。
- 對角線 $\rho_{xx}$ 是「在 $x$ 的機率」。
- 非對角線 $\rho_{xy}$ 是「相干性（coherence）」。量測會把非對角線殺掉。

我們的 channel 是：

$$
\rho_{t+1}
=W(0)\left[(1-p)\rho_t
+p\sum_xR_x\langle R_x|\rho_t|R_x\rangle\langle R_x|\right]W(0)^\dagger,
$$

其中 $R_x=|\bar0\rangle|x\rangle$。

白話：
- 以 $1-p$ 的機率，正常演化。
- 以 $p$ 的機率，量測到 $x$，重置到 $R_x$，再演化。

### 8.4 為什麼 $p=1$ 是古典？

當 $p=1$，每一步都重置到某個 basis state。此時狀態永遠是「某個位置的 classical mixture」，不會有相干性。

更精確地說，從 $|0,x\rangle$ 出發，經過 $W(0)$，量測位置得到 $y$ 的機率是

$$
Q_{xy}=\left\|\Pi_yW(0)|\bar0\rangle|x\rangle\right\|^2.
$$

對於 $s=0$，可以證明 $Q=P$（我們在程式裡用 `test_fully_measured_walk_is_classical` 驗證）。所以 $p=1$ 的 measured walk 就是原本的 classical random walk。

### 8.5 精確平均：為什麼不用 Monte Carlo？

最直接的做法是「跑很多次模擬，每次隨機決定要不要量測，然後平均」。這就是 `success_probability_with_measurement` 做的事。但它很慢，而且有統計誤差。

我們用一個更聰明的方法：**basis-state ensemble**。

觀察：
- 量測一定會把狀態重置到某個 $|\bar0\rangle|x\rangle$。
- 所以「上次量測之後經過 $a$ 步」的狀態，一定是 $W(0)^a|\bar0\rangle|x\rangle$。
- 這個狀態只取決於 $(x,a)$，可以事先算好。

我們預先計算：
- $\mu_{x,a}(y)$：從 $x$ 出發、經過 $a$ 步後，在 $y$ 的機率。
- $s_{x,a}$：從 $x$ 出發、經過 $a$ 步後，在 marked set 的機率。

然後追蹤：
- $q_0(t)$：到時間 $t$ 為止「還沒被量測過」的機率。
- $q_{x,a}(t)$：最後一次量測在 $x$、之後經過 $a$ 步的機率。

遞迴：
- 沒有量測：$q_0$ 乘 $1-p$；$q_{x,a}$ 變成 $q_{x,a+1}$。
- 有量測：從 $(x,a)$ 量到 $y$ 的機率是 $\mu_{x,a}(y)$，重置後 age=1，所以貢獻到 $q_{y,1}$。

成功率：

$$
p_M(t+1)=q_0(t+1)s^{(0)}_{t+1}
+\sum_{x,a}q_{x,a}(t+1)s_{x,a}.
$$

這樣不需要跑 Monte Carlo，結果是精確的平均。

### 8.6 程式碼對照：`src/noise.py`

- `vertex_distribution(state)`：把 `(n,n)` state 變成 vertex marginal。
- `sample_vertex(state, rng)`：根據 marginal 抽一個 vertex。
- `reset_to_vertex(state, vertex)`：把 state 重置到 `state[0,vertex]=1`。
- `partial_measurement_step(...)`：以機率 $p$ 做一次量測重置，否則不動。
- `success_probability_with_measurement(...)`：Monte Carlo 版本（較慢，主要用於早期檢查）。
- `basis_ensembles(...)`：預算 $\mu_{x,a}$ 和 $s_{x,a}$。
- `pure_ensemble(...)`：預算初始純態的 $\mu^{(0)}_t$ 和 $s^{(0)}_t$。
- `measurement_curve(...)`：用上面的遞迴算精確成功率。

`measurement_curve` 的關鍵行：

```python
new_q0 = (1.0 - measurement_probability) * q0
new_q[:, 2:] += (1.0 - measurement_probability) * q[:, 1:-1]
new_q[:, 1] += measurement_probability * np.einsum(
    "xa,xay->y", q[:, 1:], positions[:, 1:, :])
new_q[:, 1] += measurement_probability * q0 * pure_positions[step]
```

逐行：
- `new_q0`：沒有量測的 branch。
- `new_q[:,2:]`：age 增加 1。
- `einsum`：對每個 $(x,a)$，把機率 $q_{x,a}$ 乘上「量到 $y$」的機率 $\mu_{x,a}(y)$，加總到 $q_{y,1}$。
- `pure_positions`：初始純態的量測貢獻。

### 8.7 E5 的設定（已更新）

- 圖：grid $6\times6$、toy semantic graph。
- marked：single、clustered。
- 初始狀態：cue vertex 的 one-hot。
- 統一 lazy walk $\eta=0.1$；$s=0$（plain Szegedy walk），所以 $p=1$ 是精確的古典漫步。
- 步數上限 `max_steps` $=120$；deadline $T$ 掃描（例如 $T=40$、$T=120$）。
- 兩種指標模型：讀出模型（時間平均成功率、振盪指數）與偵測模型（量測落在目標即結束）。
- 指標：$p_{\max}$、$t_{\text{opt}}$、$p_{\text{deadline}}$、振盪指數。

### 8.8 結果的白話版（已更新）

- 若你追求平穩的曲線或全域最大成功率，$p=0$（純量子）通常最好；讀出模型下 4 個案例中有 3 個最好。
- 短 deadline（$T\lesssim15$）：純量子最好。
- 群聚目標、較長 deadline（$T\gtrsim20$）：$p\approx0.2$–$0.3$ 同時勝過純量子與古典（$T=40$，grid 群聚：0.455 對 0.326 對 0.055）。
- 單一目標：最佳 $p$ 隨 deadline 不規則地移向古典。
- 強測量（$p\to1$）就是古典漫步；在長 deadline 下它不一定最差，甚至可能優於純量子。
- 最佳 $p$ 取決於 deadline 與目標函數；見 `Explain_v2.md` §5.5。

---

## 9. Metrics：所有數字的意思

### 9.1 搜尋 metrics

- **$p_{\max}$**：整條 success curve 的最高點。
- **$t_{\text{opt}}$**：最高點出現的時間。
- **$t_{\text{threshold}}$**：第一次超過某個門檻（例如 0.5）的時間。如果沒有超過，回傳 -1。
- **$T_q$**：在 E1/E2 裡，我們用 $t_{\text{opt}}$ 當量子搜尋時間。
- **speedup**：$\mathrm{HT}/T_q$。
- **$t_{\text{half-max}}$**：第一次達到 $0.5p_{\max}$ 的時間。舊版 E5 用它衡量「速度」；新版 E5 的主要指標為偵測成功率與振盪指數，`t_half_max` 仍寫入 `E5_sweep.csv` 並畫在舊版附錄圖 `E5_decoherence.pdf`，但論文正文不再使用。

### 9.2 語意 metrics

- **$p_{\text{peak}}$**：目標活化峰值。
- **$\tau_{\text{peak}}$**：峰值時間，用 $\tau=\lambda_1t$ 表示。
- **AUC**：$\int p_T(t)\,dt$，程式用 `np.trapezoid`。
- **entropy**：$-\sum_i p_i\log_2p_i$。均勻分布熵最大。
- **normalized entropy**：entropy / $\log_2 n$，介於 0 和 1。
- **coverage_half_peak**：有多少比例節點的機率 $\ge 0.5p_{\text{peak}}$。
- **expected_radius_peak**：峰值時離 cue 的期望距離。

### 9.3 決策 metrics

- **decision_time**：總選項機率第一次 $\ge0.5$ 的時間。
- **total_probability**：decision time 的總選項機率。
- **choice_probabilities**：decision time 時各選項的相對機率。
- **choice_entropy**：選擇分布的熵。
- **max_choice**：最大的選擇機率。
- **choice_bias**：$\max_iP_i-1/k$。$k$ 是選項數。

### 9.4 Power-law fit

`power_law_fit(x, y)` 做的是：

$$
\log y=\log a+b\log x.
$$

所以 `exponent=b`，`prefactor=a`。程式用 `np.polyfit` 做線性回歸，然後算 $R^2$：

$$
R^2=1-\frac{\sum(\log y-\text{predicted})^2}{\sum(\log y-\overline{\log y})^2}.
$$

$R^2$ 越接近 1，表示 power law 配得越好。

### 9.5 Bootstrap confidence interval

`bootstrap_confidence_interval(samples, ...)`：

- 從樣本中有放回地抽樣很多次。
- 每次算平均。
- 取平均分布的第 2.5% 和第 97.5% 分位數，就是 95% CI。

E2 的 error band 是用多個 random seeds 的 min–max，不是 bootstrap；bootstrap 函數是備用工具。

### 9.6 程式碼對照：`src/metrics.py`

- `success_metrics`：回傳 $p_{\max}$、$t_{\text{opt}}$、$t_{\text{threshold}}$。
- `power_law_fit`：回傳 exponent、prefactor、$R^2$。
- `entropy`、`normalized_entropy`：熵。
- `choice_probabilities`：從分布算 option 機率。
- `first_passage_time`：第一次超過門檻。
- `area_under_curve`：AUC。
- `bootstrap_confidence_interval`：bootstrap CI。

### 9.7 白話總結

Metrics 的目的不是「讓報告看起來很專業」，而是把「搜尋快不快、準不準、集中不集中」變成可比較的數字。每個數字都要能回答一個問題：
- $p_{\max}$：最好能找到的機率是多少？
- $T_q$：要花多久？
- speedup：比古典快多少？
- entropy：選擇有多集中？
- AUC：整體活化量有多大？

## 10. 實驗 E1–E5（及補充 E6）逐一拆解

這一節把每個實驗當成一個「問題 → 設定 → 程式 → 結果 → 解讀」的故事來講。

### 10.1 E1：Classical vs quantum scaling

#### 問題

> 量子搜尋時間真的比古典 hitting time 的平方根成長嗎？

#### 設定

- 圖：
  - Complete graph $K_N$，$N=8,16,32,64$。
  - Cycle $C_N$，$N=8,16,32,64$。
  - 2D grid $L\times L$，$L=4,6,8,10$，所以 $N=16,36,64,100$。
  - Hypercube $Q_d$，$d=3,4,5,6$，所以 $N=8,16,32,64$。
- Marked set：single。
  - Complete/cycle/hypercube：node 0。
  - Grid：中心點 `(L//2)*L + (L//2)`。
- 初始狀態：$|\bar0\rangle|\sqrt\pi\rangle$（stationary distribution）。
- 量子 walk：interpolated $W(s)$，$s$ 從 `configs/base.yaml` 的 grid 掃描。
- 古典 baseline：$\mathrm{HT}(P,M)$，用線性解。

#### 程式流程

1. `run_e1` 呼叫 `e1_cases` 建出所有 case。
2. 對每個 case：
   - `P = transition_matrix(graph)`。
   - `ht = mean_hitting_time(P, [marked])`。
   - `max_steps = ceil(3*sqrt(ht)) + 5`。
   - 對每個 $s$ 算 `interpolated_lower_bound(P, [marked], s, max_steps)`，選 $q_t$ 最大的 $s$。
   - 用選定的 $s$ 跑 `interpolated_success_curve`，得到真正的 $p_M(t)$。
   - $T_q=\arg\max_{t\ge1}p_M(t)$，$p_{\max}=p_M(T_q)$。
   - 記錄 $\mathrm{HT}$、$T_q$、$p_{\max}$、spectral gap、speedup。
3. `summarize_e1` 對每個 family 做 power-law fit：
   - $\mathrm{HT}\sim N^\alpha$。
   - $T_q\sim N^\beta$。
   - $T_q\sim\mathrm{HT}^\gamma$。
4. `plot_e1_scaling` 畫 2×2 的 log-log 圖。
5. `plot_e1_speedup` 畫 speedup 圖（放在 appendix）。

#### 輸出

- `code/results/raw/E1_scaling.csv`
- `code/results/processed/E1_scaling.json`
- `code/figures/E1_scaling.pdf` / `.png`
- `code/figures/E1_speedup.pdf` / `.png`
- 報告：`report/figures/fig_e1_scaling.pdf`、`fig_e1_speedup.pdf`
- 報告 Figure 2、Table 4。

#### 結果

| Family | $\mathrm{HT}$ exponent | $T_q$ exponent | $T_q\sim\mathrm{HT}^\gamma$ [95% CI] | max speedup |
|---|---:|---:|---:|---:|
| Complete $K_N$ | 1.06 | 0.53 | 0.50 [0.41, 0.59] | 4.7 |
| Cycle $C_N$ | 1.95 | 1.02 | 0.52 [0.51, 0.54] | 11.7 |
| 2D grid | 1.26 | 0.61 | 0.48 [0.39, 0.57] | 7.9 |
| Hypercube | 1.07 | 0.47 | 0.44 [0.32, 0.55] | 5.4 |

$p_{\max}$ 在 0.84–1.00 之間，所以 $T_q$ 不是「低機率下的假象」。

#### 怎麼讀這張圖？

- 橫軸是 $N$，縱軸是 steps，都是 log scale。
- 藍線是古典 $\mathrm{HT}$，橘線是量子 $T_q$。
- 如果 $T_q\sim\sqrt{\mathrm{HT}}$，那在 log-log 圖上，橘線的斜率應該大約是藍線斜率的一半。
- Cycle 最明顯：古典斜率接近 2，量子斜率接近 1。
- Grid 的 $T_q\sim N^{0.61}$，不是完美的 0.5，因為 finite-size 的 $\log N$ 還沒完全分離出來；但 $T_q\sim\mathrm{HT}^{0.48}$ 就很接近 0.5。
- Complete graph 的 speedup 最小，因為它的古典 hitting time 只長得像 $N$，平方根優勢的絕對差距比較小。

#### 常見誤解

- **「$T_q$ 一定是 $\sqrt{\mathrm{HT}}$ 整數倍」**：不是。$\sqrt{\mathrm{HT}}$ 是 scaling，常數可以很大。我們的 $T_q$ 常常是 $1$–$3$ 倍的 $\sqrt{\mathrm{HT}}$。
- **「complete graph 的 exponent 應該是 1」**：有限尺寸下 fit 出來是 1.06，這是 finite-size effect，不是理論錯誤。
- **「$p_{\max}$ 一定要等於 1」**：不一定。AGJK 的演算法保證 constant success probability，不是 1。

### 10.2 E2：Single vs independent vs clustered marked vertices

#### 問題

> 多個目標會讓搜尋變難還是變簡單？`HT⁺` 什麼時候會爆炸？

#### 設定

- 圖：
  - Grid $L=6,8$（$N=36,64$）。
  - Barbell，`n_each=8,16`（$N=24,48$）。
- Marked set：
  - `single`：1 個目標。
  - `independent`：4 個目標，用 farthest-point sampling 分散在圖上。
  - `clustered`：4 個目標，用 BFS 從一個隨機中心長出一個連通塊。
- Seeds：`0–19`；重複的 marked set 已去除，每個設定使用互不相同的 sets（single 只有一組）；報告 distinct sets 的中位數與範圍。
- 量子 walk：interpolated $W(s)$，$s$ 掃描。
- $\mathrm{HT}^+$：用 `ht_extended`，$\epsilon=10^{-6}$。

#### Barbell graph 是什麼？

Barbell graph 是「兩個 clique 用一條 path 連起來」，長得像啞鈴：

```
  K_8  ─── path ───  K_8
```

- 同一個 clique 內，任兩點直接相連，所以很容易走。
- 要到另一個 clique，必須走中間的 path，所以很難。
- 這很適合測試「clustered targets」：如果 4 個目標都在同一個 clique，walker 只要走到那個 clique 就很容易找到其中一個；如果目標分散在兩個 clique，則要跨過 bridge。

#### 程式流程

1. `run_e2` 建 cases。
2. 對每個 case：
   - `P = transition_matrix(graph)`。
   - 對每種 marked kind 和 seed：
     - `marked = marked_set(graph, kind, k=4, seed=seed)`。
     - `ht = mean_hitting_time(P, marked)`。
     - `ht_plus = ht_extended(P, marked, epsilon=1e-6)`。
     - $s$ 掃描，跑 `interpolated_success_curve`。
     - 記錄 $T_q$、$p_{\max}$、$\mathrm{HT}^+/\mathrm{HT}$。
3. `run_e2_adversarial` 另外跑 AGJK 的 torus 構造。
4. `plot_e2_success` 畫 success curves。
5. `plot_e2_ht` 畫 $\mathrm{HT}$ vs $\mathrm{HT}^+$。

#### 輸出

- `code/results/raw/E2_marked.csv`
- `code/results/raw/E2_curves.csv`
- `code/results/raw/E2_adversarial_torus.csv`
- `code/results/processed/E2_marked.json`
- `code/results/processed/E2_adversarial_torus.json`
- `code/figures/E2_success.pdf`、`E2_ht.pdf`
- 報告 Figure 3、Figure 4、Table 5（selected）、Table 7（full）。

#### 結果

Selected rows（distinct sets 的中位數與範圍）：

| Graph | Marked set | # sets | median HT [min, max] | median HT⁺/HT (max) | median Tq |
|---|---|---:|---|---|---:|
| Grid 8×8 | single | 1 | 95.5 | 1.00 | 17 |
| Grid 8×8 | independent | 18 | 34.8 [26.9, 39.7] | 1.02 (1.05) | 10 |
| Grid 8×8 | clustered | 18 | 85.0 [41.5, 131.1] | 1.06 (1.09) | 20 |
| Barbell n=16 | single | 1 | 2558.0 | 1.00 | 134 |
| Barbell n=16 | independent | 18 | 16.8 [16.4, 415.1] | 1.53 (2.94) | 7 |
| Barbell n=16 | clustered | 16 | 2768.0 [1893.1, 2781.3] | 1.00 (1.04) | 133 |

其他：Grid 6×6 independent 14 組、中位數 15.7、clustered 17 組、中位數 40.1（single 46.1）；Barbell n=8 independent 11 組、中位數 7.6、clustered 9 組、中位數 425.3（single 373.6）。Barbell n=16 independent 的最大比值 2.94 來自單一集合 {0,21,25,29}（HT 415），其餘 17 組為 1.35–1.53。

Adversarial torus：

| L | N | m | HT | HT⁺ | HT⁺/HT |
|---:|---:|---:|---:|---:|---:|
| 18 | 324 | 76 | 10.3 | 57.1 | 5.5 |
| 24 | 576 | 108 | 20.5 | 150.9 | 7.35 |
| 30 | 900 | 148 | 34.9 | 295.9 | 8.5 |
| 36 | 1296 | 252 | 50.5 | 443.1 | 8.8 |

L=18 時，$W(s)$ 仍然在 $t=6$ 達到 $p_{\max}=0.978$。

#### 怎麼解讀？

1. **Independent targets 比較容易**：目標分散，walker 從任何方向都可能碰到其中一個，所以 $\mathrm{HT}$ 下降。四張圖上，每一組 independent 都比每一組 clustered 容易。
2. **Clustered targets 相對 single 可易可難**：barbell n=16 的 clustered HT 為 single 的 0.74–1.09 倍；grid 8×8 為 0.43–1.37 倍（中位數 0.89 倍）。
3. **$\mathrm{HT}^+$ 不一定會爆炸**：clustered set 的 $\mathrm{HT}^+/\mathrm{HT}$ 中位數 1.00–1.09（最大 1.10）；barbell independent 較大（1.38／1.53，單一集合達 2.94）。真正的大 gap 需要 AGJK 的 periodic 排列。
4. **Adversarial torus**：`dense` 小方格 + `sparse` 週期格點，會讓 $D(s)$ 出現非常接近 1 的特徵值，所以 $\mathrm{HT}^+$ 很大。
5. **但 Conjecture 3 仍然有效**：L=18 時，$W(s)$ 還是很快找到目標。這說明 $\mathrm{HT}^+$ 大不代表「所有 quantum walk 都慢」；它是 KMOR 那類演算法的 penalty，不是我們數值 protocol 的 penalty。

#### 常見誤解

- **「多個目標一定比較難」**：不一定。Independent targets 反而容易。
- **「Clustered 一定會有很大的 HT⁺」**：不一定。我們的 clustered set 中位數只有 1.00–1.09。大 gap 是 arrangement 的性質。
- **「$\mathrm{HT}^+$ 是量子演算法的實際執行時間」**：不是。$\mathrm{HT}^+$ 是 spectral quantity；我們的 actual $T_q$ 是從 $W(s)$ 的 success curve 量出來的。

### 10.3 E3：Toy semantic graph 的 target activation

#### 問題

> 在語意圖上，cue 到目標的「活化」在量子與古典漫步下有哪裡不同？語意距離有影響嗎？

#### 設定

- 圖：`toy_semantic_graph()`，19 節點。
- Cue：`animal`。
- Targets：
  - `dog`（distance 1，同社群）。
  - `violin`（distance 4，跨社群）。
- CTQW：$e^{-iL_{\mathrm{sym}}t}$。
- CRW：$e^{-L_{\mathrm{rw}}t}$。
- 時間：$\tau=\lambda_1t$，$\lambda_1=0.03335$；窗口 $\tau\le50$，峰值取窗內全域最大值，AUC 取 $\tau\le8$。
- Metrics：$p_{\text{peak}}$、$\tau_{\text{peak}}$、AUC（expected radius 不再回報）。
- CTQW 曲線震盪強烈，峰值依窗口而變；AUC 是較穩定的比較量。

#### 程式流程

1. `run_e3` 建圖，抓 `labels`（concept → integer）。
2. `normalized_laplacian` 得到 $L_{\mathrm{sym}}$、degree、stationary。
3. `spectral_gap` 得到 $\lambda_1$。
4. `times = linspace(0, 8/λ1, 1200)`。
5. `ctqw_trajectory` 和 `crw_trajectory` 算每個時間點的狀態。
6. 對每個 target 和 model，`semantic_metrics` 算 metrics。
7. `plot_e3_semantic` 畫圖。

#### 輸出

- `code/results/raw/E3_semantic_metrics.csv`
- `code/results/raw/E3_semantic_curves.csv`
- `code/results/processed/E3_semantic.json`
- `code/figures/E3_semantic.pdf`
- 報告 Figure 5。

#### 結果

| Cue → target | Model | p_peak | τ_peak | AUC (τ≤8) |
|---|---|---:|---:|---:|
| animal → dog (d=1) | CTQW | 0.337 | 47.5 | 0.481 |
| animal → dog (d=1) | CRW | 0.158 | 0.125 | 0.579 |
| animal → violin (d=4) | CTQW | 0.268 | 19.3 | 0.360 |
| animal → violin (d=4) | CRW | 無內部峰值（單調上升至 stationary π=0.0455） | — | 0.323 |

#### 怎麼解讀？

- **Near target（dog）**：
  - CRW 立刻在 neighbor 上活化（峰值 0.158，τ=0.125），之後衰減到 stationary 值 0.061；AUC 較高（0.579 vs 0.481）。
  - CTQW 的窗內最大值 0.337 出現在 τ=47.5，是單次 recurrence 尖峰，不是穩定的「晚但高」。
- **Far target（violin）**：
  - CRW 沒有內部峰值，單調上升到 stationary 0.0455；AUC 0.323。
  - CTQW 峰值 0.268（τ=19.3），AUC 0.360，高於 CRW。
- **語意距離效應**：
  - 近目標：CRW 的 AUC 較高。
  - 遠目標：CTQW 的 AUC 較高。
  - CTQW 峰值依窗口，結論以 AUC 為準。這是 model-level observation，不是人類資料。

#### 常見誤解

- **「CTQW 一定比 CRW 好」**：不一定。Near target 的 AUC 是 CRW 比較高（0.579 vs 0.481）。
- **「CTQW 的峰值就是它的表現」**：不是。CTQW 曲線震盪強，峰值取決於窗口；AUC 較穩定。
- **「CTQW 和 Szegedy 是同一種 walk」**：不是。CTQW 是 continuous-time，Szegedy 是 discrete-time。我們在報告裡明確分開。

### 10.4 E4：Multi-alternative decision under coupling（已更新）

> 本節已於 2026-10-31 依統一的 lazy walk 與新版讀出模型重寫。舊版「首次越過門檻讀出、對稱三選項 $0.333\to0.966$、不對稱分支非單調」已撤回，屬相位假象。

**問題**：多個選項彼此相似（耦合）時，選擇機率與決策時間如何改變？結論是否依賴讀出方式？

**設定**

- 所有 Szegedy walk 使用 $P_\eta$，$\eta=0.1$。
- 三種讀出：隨機停止、偵測（$p=0.2$）、古典吸收。
- 穩健性：改變 $\eta$ 與 $\pm20\%$ 邊權擾動，計算 spread（變動幅度，越小越穩健）。
- 圖：hub 加每選項一條路徑；symmetric3（4-4-4）、asymmetric3（3-4-5）、symmetric4（4-4-4-4），耦合分支 1 與 2；$c\in\{0,0.1,0.25,0.5,0.75,1,2\}$；步數上限 400；隨機停止為 $t\in\{1,\dots,400\}$ 均勻平均。

**結果檔**

- `code/results/raw/E4_robustness.csv`、`code/results/processed/E4_robustness.json`
- 圖：`code/figures/E4_robustness.pdf`
- 舊版 E4 檔（`E4_metrics.csv`、`E4_choices.csv`、`E4_curves.csv`、`E4_decision.json`）已在 lazy walk 下重新產生，但仍是「首次越過門檻」讀出，只作對照（圖 `E4_decision.pdf`，論文未使用）。

**數字**

穩健性（spread）：

| 讀出 | spread 中位數 | spread 最大值 |
|---|---:|---:|
| 隨機停止 | 0.08 | 0.26 |
| 偵測（$p=0.2$） | 0.035 | 0.045 |
| 古典吸收 | 0.044 | 0.065 |
| 舊版首次越過門檻（已撤回） | 0.44 | 0.78 |

未耦合選項的選擇機率（偵測讀出）：

| 情境 | 耦合前 | 耦合後 |
|---|---:|---:|
| 對稱三選項 | 1/3 | 0.499 |
| 四選項（未耦合選項合計） | 0.500 | 0.653 |
| 不對稱三選項 | 0.342 | 0.470 |
| 對稱三選項，古典 | 1/3 | 1/3（不變） |

決策時間：偵測讀出 31–44 步；古典吸收 17–27 步。

**怎麼讀**

- 偵測讀出下，耦合使量子選擇機率單調偏向未耦合選項。
- 古典漫步在對稱圖上完全不受耦合影響。
- 不同讀出的穩健性差異很大（隨機停止 spread 最大 0.26；偵測 0.045；古典 0.065），因此結論必須附上讀出定義。

**常見誤解**

- 「非單調一定是程式 bug」：此問題已不再適用。先前的非單調結論屬相位假象，已撤回。
- 「耦合會讓 A 得利，所以量子一定比古典好」：不成立。偏向的大小取決於讀出方式，古典在對稱圖上不變。
- 「E4 的結果等同心理學的 attraction effect」：不成立，見 §7.8 的說明。

**代表什麼／不代表什麼**

- 代表：在統一 lazy walk 與偵測讀出下，選項耦合的單調偏向可以重現。
- 不代表：非單調選擇機率已被證實；不代表與 attraction effect 等同。

### 10.4b E6：Small-world 與 scale-free 圖（補充實驗）

- 設定：Watts–Strogatz（β∈{0, 0.05, 0.2, 1}，N∈{32, 64}，k=4）與 Barabási–Albert（m=2，N∈{32, 64}），5 seeds，target 分 hub 與 peripheral。
- 結果：pooled $T_q\sim\mathrm{HT}^{0.52}$（95% CI 0.49–0.54，$R^2=0.94$，100 個 instance）；WS 指數 0.54，BA 指數 0.45。Hub speedup 隨 rewiring 下降（N=64：8.0 → 4.0）；peripheral speedup 4–9。BA 的 hub speedup 1.8–2.4，peripheral 6.8–11.5。
- 來源：`code/results/raw/E6_smallworld.csv`；圖 `code/figures/E6_smallworld.pdf`。

### 10.5 E5：Partial measurement / decoherence sweep（已更新）

> 本節已於 2026-10-31 重寫。舊版「deadline $T=20$ 時 $p\approx0.2$ 最佳、最高 $12\times$」已撤回：該結果來自振盪相位假象；lazy walk 後只剩約 $1.6\times$，平均掉 deadline 後消失。

**問題**：部分量測（測量率 $p$）會侵蝕還是幫助量子搜尋？是否存在最佳 $p$？答案取決於指標與 deadline。

**設定**

- 圖：grid $6\times6$ 與 toy semantic graph；各含 single 與 clustered 目標。
- 初始狀態：cue vertex 的 one-hot；$s=0$，故 $p=1$ 是精確古典漫步。
- Lazy walk $\eta=0.1$；`max_steps` $=120$。
- 兩種指標模型：
  - **讀出模型**：時間平均成功率（欄位 `p_avg_120`）與振盪指數（欄位 `oscillation`，即文中的 CV）。
  - **偵測模型**：量測落在目標即結束。$p=0$ 為純量子；$p=1$ 為古典 $P(\tau\le T)$。
- $p\in\{0,0.05,0.1,0.2,0.3,0.5,0.75,1\}$；時間平均與偵測的 horizon $H\in\{20,40,80,120\}$；`deadline: 20` 只保留給舊版單點比較（附錄圖 `E5_decoherence.pdf`）。

**結果檔**

- `code/results/raw/E5_sweep.csv`、`code/results/raw/E5_curves.csv`
- `code/results/processed/E5_decoherence.json`
- 圖：`code/figures/E5_robustness.pdf`

**數字**

讀出模型（純量子在 4 個案例中有 3 個的時間平均成功率最好）：

| 案例 | 時間平均成功率 $p=0$ | 同 $p=0.2$ | 振盪指數 $p=0$ | 同 $p=0.2$ |
|---|---:|---:|---:|---:|
| grid 單一 | 0.042 | 0.020 | 1.50 | 0.37 |
| grid 群聚 | 0.156 | 0.103 | 0.75 | 0.28 |
| toy 單一 | 0.038 | 0.037 | 0.97 | 0.26 |
| toy 群聚 | 0.178 | 0.200 | 0.41 | 0.24 |

偵測模型（deadline 成功率）：

| 案例 | $T$ | $p=0$ | $p=0.2$ | $p=0.3$ | $p=1$（古典） |
|---|---:|---:|---:|---:|---:|
| grid 單一 | 40 | 0.021 | 0.146 | 0.159 | 0.136 |
| grid 單一 | 120 | 0.098 | 0.373 | 0.447 | 0.516 |
| grid 群聚 | 40 | 0.055 | 0.455 | 0.448 | 0.326 |
| grid 群聚 | 120 | 0.271 | 0.837 | 0.862 | 0.811 |
| toy 單一 | 40 | 0.039 | 0.183 | 0.216 | 0.261 |
| toy 單一 | 120 | 0.004 | 0.503 | 0.582 | 0.621 |
| toy 群聚 | 40 | 0.158 | 0.449 | 0.451 | 0.342 |
| toy 群聚 | 120 | 0.134 | 0.837 | 0.844 | 0.703 |

純量子峰值：grid 單一目標 $p_{\max}=0.449$，出現在 $t=13$。

**怎麼讀**

- $T\lesssim15$：純量子最好。
- 群聚目標、$T\gtrsim20$：$p\approx0.2$–$0.3$ 同時勝過純量子與古典。
- 單一目標：最佳 $p$ 隨 deadline 不規則地移向古典（例如 toy 單一目標在 $T=40$ 時 $p=1$ 最高）。
- 最佳 $p$ 取決於 deadline 與目標函數，沒有單一全域最佳值。

**常見誤解**

- 「$p=1$ 只是近似古典」：對 $s=0$，$p=1$ 是精確的古典漫步（見 `test_fully_measured_walk_is_classical`）。
- 「$p$ 越大越接近古典，所以越差」：不一定。長 deadline 下，古典可以優於純量子（grid 群聚 $T=120$：0.811 對 0.271）。
- 「$p_{\max}$ 和 deadline success 應該同向」：不一定，這是 E5 最重要的洞察之一。

**代表什麼／不代表什麼**

- 代表：弱測量在群聚目標與較長 deadline 下可以提升成功率；最佳 $p$ 依目標函數而定。
- 不代表：不代表 deadline $T=20$ 時 $p\approx0.2$ 是普遍最佳；不代表 $p_{\max}$ 會因測量而提高（$p_{\max}$ 仍以 $p=0$ 為最高）。

---

## 11. 程式碼導覽：每個檔案在做什麼

### 11.1 目錄樹

```
Final/
  Explain.md                  ← 你正在讀的文件
  ROADMAP.md                  ← 專案計畫與進度
  weekly_log.md               ← 每週紀錄
  proposal/                   ← 提案
  report/
    main.tex                  ← 報告主檔
    refs.bib                  ← 參考文獻
    sections/                 ← 各章節 .tex
    figures/                  ← 報告用 figures
    main.pdf                  ← 編譯後的 PDF
    RESULTS_SUMMARY.md
  slides/
    slides.tex                ← 投影片
  code/
    environment.yml           ← Miniforge 環境
    requirements.txt          ← pip fallback
    README.md                 ← 如何跑
    configs/
      base.yaml               ← 全域參數
      experiments.yaml        ← E1–E5 設定
    src/
      __init__.py
      graphs.py               ← 建圖、transition matrix、marked set
      classical.py            ← 古典 hitting time、diffusion
      szegedy.py              ← Szegedy walk
      agjk.py                 ← interpolated walk、HT⁺
      semantic.py             ← CTQW/CRW
      cognitive.py            ← 決策曲線、choice probability
      noise.py                ← partial measurement、ensemble
      metrics.py              ← 統計指標
      experiments.py          ← E1–E5 runner
      plotting.py             ← 所有圖
      schematics.py           ← architecture figure
    tests/                    ← 71 個 pytest
    notebooks/                ← 4 個 Jupyter notebooks
    results/raw/              ← CSV
    results/processed/        ← JSON
    figures/                  ← 實驗圖
```

### 11.2 每個檔案的白話職責

| 檔案 | 職責 | 你什麼時候會改它 |
|---|---|---|
| `graphs.py` | 建 graph、transition matrix、marked set | 加新圖、新 marked set 規則 |
| `classical.py` | 古典 hitting time、diffusion、Monte Carlo | 加古典 baseline |
| `szegedy.py` | $V(P)$、$W(P)$、$D$、spectrum、Chebyshev bound | 改 walk 的定義 |
| `agjk.py` | $P(s)$、$W(s)$、$\mathrm{HT}(s)$、$\mathrm{HT}^+$ | 改 interpolated walk |
| `semantic.py` | CTQW/CRW、semantic metrics | 改語意模型 |
| `cognitive.py` | option curve、decision summary | 改決策模型 |
| `noise.py` | partial measurement、basis ensemble | 改雜訊模型 |
| `metrics.py` | power-law fit、entropy、AUC、bootstrap | 加新指標 |
| `experiments.py` | 讀 config、跑 E1–E5、存 CSV/JSON | 加新實驗 |
| `plotting.py` | 所有 figure 的繪圖 | 改圖的樣式 |
| `schematics.py` | architecture diagram | 改 Fig. 1 |
| `tests/` | 自動檢查程式是否正確 | 加新功能時 |
| `configs/` | 參數 | 想改實驗設定時 |

### 11.3 Experiment runner 的流程

`python -m src.experiments --only E1` 會：

1. `parse_args()` 讀命令列參數。
2. `load_yaml()` 讀 `configs/base.yaml` 和 `configs/experiments.yaml`。
3. `selected = {"E1"}`（或你指定的）。
4. 對每個 selected experiment：
   - 呼叫 `run_e1` / `run_e2` / `run_e3` / `run_e4` / `run_e5`。
   - 得到 DataFrame（表格）。
   - 存 CSV 到 `results/raw/`。
   - 做 summary，存 JSON 到 `results/processed/`。
   - 呼叫 `plot_*`，存 PDF/PNG 到 `figures/`。
5. 印出表格和輸出路徑。

如果你只想跑 E5：

```bash
mamba activate qwalk-cognition
cd Final/code
python -m src.experiments --only E5
```

### 11.4 設定檔怎麼看？

`base.yaml`：

- `seed`：隨機 seed。
- `paths`：輸出位置。
- `agjk.interpolation_grid`：$s$ 的掃描格子。
- `agjk.time_window_sqrt_ht`：$3.0$，也就是 $t\le3\sqrt{\mathrm{HT}}$。
- `agjk.time_window_padding`：$5$，再多跑幾步。
- `agjk.ht_plus_epsilon`：$10^{-6}$，用 $s=1-\epsilon$ 近似 $\mathrm{HT}^+$。

`experiments.yaml`：

- E1：graph families、sizes。
- E2：grid/barbell、marked kinds、seeds、adversarial torus 參數。
- E3：cue、targets、time window、time points。
- E4：decision cases、coupling grid、$s$、threshold、max steps。
- E5：cases、$p$ grid、max steps（120）、horizons、legacy deadline、$s$；lazy 參數 $\eta$ 來自 `base.yaml` 的 `walk.laziness`（全域，非 E5 專用）。

### 11.5 Tests：71 個測試在保護什麼？

- `test_classical.py`：complete graph/cycle 的 hitting time、stationary、diffusion、Monte Carlo。
- `test_quantum.py`：unitarity、$D$ block、$W$ 與 dense matrix 一致、norm、Chebyshev bound、interpolated walk、$\mathrm{HT}^+$。
- `test_metrics.py`：power-law fit、entropy、choice probability、bootstrap。
- `test_semantic.py`：Laplacian spectrum、CTQW norm、CRW 收斂到 stationary、semantic metrics。
- `test_decision.py`：decision graph 結構、classical option curve、quantum option curve、decision summary。
- `test_noise.py`：basis ensemble、$p=1$ 古典極限、$p=0$ 純量子、bounded。

跑測試：

```bash
python -m pytest -q
```

如果測試失敗，先看是哪個 test，再回去看對應的函數。測試是「程式碼的說明書」。

### 11.6 Notebooks

- `01_sanity_checks.ipynb`：classical hitting time、unitarity、$D$ block。
- `02_scaling.ipynb`：E1 的小型版本。
- `03_cognitive_graphs.ipynb`：toy semantic graph 的節點與邊。
- `04_decoherence.ipynb`：partial measurement 的小型版本。

Notebook 適合「互動式探索」，但正式結果以 `src/experiments.py` 為準。

### 11.7 效能與記憶體

- `apply_walk` 每步是 $O(n^3)$，因為要對每個 vertex 做 $n\times n$ 矩陣乘法。
- 對 $n\le100$，NumPy dense 版本已經夠快。
- 更大的圖要用 sparse matrix 或 operator 形式，不能建 dense $n^2\times n^2$ 的 $W$。
- `basis_ensembles` 會對每個 start vertex 預算 $T_{\max}$ 步，複雜度 $O(n\cdot T_{\max}\cdot n^3)$；在 E5 的 $n=36$、$T=120$ 下仍可接受。
- 如果你的圖很大，先從 `random_regular_graph` 或 `grid_graph` 的小尺寸開始，確認邏輯正確再放大。

### 11.8 如何加一個新實驗？

1. 在 `src/` 寫一個 `run_eX` 函數。
2. 在 `configs/experiments.yaml` 加 `EX` 區塊。
3. 在 `experiments.py` 的 `run()` 裡加 `if "EX" in selected:`。
4. 在 `plotting.py` 寫 `plot_eX`。
5. 在 `tests/` 加測試。
6. 在 `README.md` 加指令與輸出。

### 11.9 `experiments.py` 逐函數細節

這一節把 runner 的每個函數拆開。你可以把它當成「程式碼的地圖」。

#### `load_yaml(path)`

```python
with open(path, "r", encoding="utf-8") as handle:
    return yaml.safe_load(handle)
```

- 讀 YAML 檔，回傳 Python dict。
- `safe_load` 比 `load` 安全，不會執行任意 Python 物件。
- 如果 YAML 格式錯誤，這裡會丟出例外；先檢查縮排和冒號。

#### `e1_cases(experiment_config)`

- 從 `experiments["E1"]["graphs"]` 讀取 `complete`、`cycle`、`grid`、`hypercube` 的尺寸。
- 對每個尺寸建一個 dict：`family`、`parameter`、`N`、`graph`、`marked`。
- Grid 的 marked 是中心點：`(length // 2) * length + (length // 2)`。
- 回傳 list of dict。

為什麼要单独建 cases？因為 `run_e1` 只負責「跑」，不負責「決定要跑哪些圖」。這樣你要加新圖，只改 `e1_cases`。

#### `run_e1(base_config, experiment_config)`

流程：

1. 從 `base_config["agjk"]` 讀 `interpolation_grid`、`time_window_sqrt_ht`、`time_window_padding`。
2. 對每個 case：
   - `P = transition_matrix(case["graph"])`。
   - `marked = [case["marked"]]`。
   - `ht = mean_hitting_time(P, marked)`。
   - `max_steps = ceil(3 * sqrt(ht)) + 5`。
   - 對每個 `s` 算 `interpolated_lower_bound`，選 `q_max` 最大的 `s`。
   - `curve = interpolated_success_curve(...)`。
   - `t_q = argmax(curve[1:]) + 1`（跳過 t=0，因為 t=0 可能只是初始的 $\pi_M$）。
   - `p_max = curve[t_q]`。
   - 記錄 `HT`、`spectral_gap`、`s`、`t_q`、`p_max`、`q_max`、`max_steps`、`speedup`。
3. 回傳 `pd.DataFrame`。

`max_steps` 的公式很重要：它保證我們只在 $O(\sqrt{\mathrm{HT}})$ 的窗口內找峰值，不會等到很晚的 recurrence。

#### `summarize_e1(frame)`

- 對每個 `family` 分組。
- 把 `N`、`HT`、`t_q`、`p_max`、`speedup` 存成 list。
- 用 `power_law_fit` 算三個 exponent：
  - `fit_HT_vs_N`
  - `fit_tq_vs_N`
  - `fit_tq_vs_HT`
- 回傳 dict，之後存成 JSON。

#### `e2_cases(experiment_config)`

- Grid：`length` 從 config 讀，`N=length*length`，single marked 是中心。
- Barbell：`n_each` 從 config 讀，`N=3*n_each`，single marked 是 node 0。
- 回傳 list of dict。

#### `_select_interpolation(P, marked, s_grid, max_steps)`

這是 E1/E2 共用的 helper：
- 對每個 `s` 算 `interpolated_lower_bound`。
- 回傳 `(best_s, best_q)`。
- 注意：它只回傳 $q$ 的最大值，不回傳時間；真正的 $t_q$ 是由 `interpolated_success_curve` 決定。

#### `run_e2(base_config, experiment_config)`

流程：

1. 讀 `marked_size`、`seeds`、`ht_plus_epsilon`。
2. 對每個 case：
   - `P = transition_matrix(graph)`。
   - `blocks = walk_operator_blocks(P)`（只算一次，重用）。
   - 對 `single`、`independent`、`clustered`：
     - single 只用 seed 0；其他用 config 的 seeds。
     - `marked = marked_set(graph, kind, k=4, seed=seed)`。
     - `ht = mean_hitting_time`。
     - `ht_plus = ht_extended`。
     - `max_steps = ceil(3*sqrt(ht)) + 5`。
     - 選 $s$，跑 `interpolated_success_curve`。
     - 記錄 metrics，並把整條 curve 存到 `curve_records`。
3. 回傳 `(frame, curves)` 兩個 DataFrame。

為什麼要回傳 curves？因為 `plot_e2_success` 要畫每個 seed 的曲線和 min–max band。

#### `summarize_e2(frame)`

- 對 `(family, parameter, N, kind)` 分組。
- 算 mean/std：`HT`、`HT_plus`、`HT_plus_ratio`、`t_q`、`p_max`、`speedup`。
- 也存 `marked_sets`（每個 seed 的 marked set 字串）。
- 回傳 dict。

#### `run_e2_adversarial(base_config, experiment_config)`

- 從 config 的 `adversarial_torus.cases` 讀 `length`、`d1`、`k1`、`d`。
- 建 `torus_graph(length)`，transition matrix 用 lazy 0.2。
- `marked = adversarial_torus_marked(...)`。
- 算 `HT`、`HT_plus`。
- 如果 `length <= simulate_max_length`（目前是 18），才跑 `W(s)` 的 $t_q$、$p_{\max}$；其他只算 spectral quantities。
- 回傳 DataFrame。

為什麼只模擬 L=18？因為 $W(s)$ 的狀態大小是 $2n^2$，L=36 時 $n=1296$，dense 會太大。L=18 已經足夠展示「$\mathrm{HT}^+$ 很大但 Conjecture 3 仍然有效」。

#### `run_e3(base_config, experiment_config)`

1. 建 toy graph，抓 `labels`。
2. `normalized_laplacian`、`spectral_gap`。
3. `times = linspace(0, 8/λ1, 1200)`。
4. `ctqw_trajectory`、`crw_trajectory`。
5. 對每個 target：
   - 算 graph distance。
   - 對 quantum/classical 算 `semantic_metrics`。
   - 把整條 curve 存到 `curve_records`。
6. 回傳 `(metrics, curves, graph, gap, cue_name, target_names)`。

#### `summarize_e3(metrics, gap)`

- 把 `gap`、`relaxation_time`、`cue`、`targets`、`metrics` 包成 dict。
- `metrics` 是 `metrics.to_dict(orient="records")`，每個 target/model 一筆。

#### `run_e4(base_config, experiment_config)`

1. 讀 `interpolation_s`、`decision_threshold`、`max_steps`、`coupling_grid`。
2. 對每個 case × coupling：
   - `branched_decision_graph(lengths, pair, coupling)`。
   - `P = transition_matrix(graph, weight="weight")`。
   - `option_sets = [[terminal] for terminal in terminals]`。
   - `initial = one-hot hub`。
   - quantum：`quantum_option_curve`。
   - classical：`absorbing_option_curve`。
   - `decision_summary`。
   - 記錄 metrics，並把 choice probabilities 存到 `choices`，整條 curve 存到 `curves`。
3. 回傳 `(frame, choices, curves)`。

#### `summarize_e4(frame, threshold)`

- 把 threshold、cases、coupling grid、metrics 包成 dict。
- `metrics` 是 `frame.to_dict(orient="records")`。

#### `e5_case(case)`

- 如果 `graph == "grid"`：建 grid、cue 是整數、targets 是整數 list。
- 如果 `graph == "toy_semantic"`：建 toy graph，cue/targets 用 concept name 轉成 integer。
- 其他 graph 會丟 `ValueError`。

#### `run_e5(base_config, experiment_config)`

1. 讀 `interpolation_s`、`max_steps`、`deadline`、`measurement_probabilities`，以及 `horizons`；lazy 參數 $\eta$ 由 `walk_transition` 從 `base.yaml` 的 `walk.laziness` 讀取（舊版為 E5 專用的 `self_loop`，已移除）。
2. 對每個 case：
   - `e5_case` 建 graph、cue、targets。
   - `P = lazy_transition_matrix(transition_matrix(graph), 0.1)`（即 $P_\eta$，$\eta=0.1$；見 `code/src/graphs.py`）。
   - `blocks = walk_operator_blocks(P)`。
   - `positions, success = basis_ensembles(P, targets, s=0, max_steps, blocks)`。
   - `pure_positions, pure_success = pure_ensemble(P, targets, 0, max_steps, initial, blocks)`。
   - 對每個 $p$：`measurement_curve`，算 metrics。
   - 把 curve 存到 `curves`。
3. 回傳 `(frame, curves, deadline)`。
4. 最後對每個 case 算 `p_deadline_ratio`：`p_deadline(p) / p_deadline(p=0)`。

#### `summarize_e5(frame, deadline)`

- 對每個 case 找 `p_deadline` 最大的 row，存 `optimal_at_deadline`。
- 回傳 deadline、cases、optimal、metrics。

#### `_json_ready(value)`

- 遞迴地把 NumPy 的 integer/float 轉成 Python 的 int/float。
- `json.dump` 不認識 `np.int64`、`np.float64`，所以需要這個 helper。
- 如果值是 `None`、`str`、`int`、`float`、`bool`，直接回傳。

#### `run(config_path, experiment_path, only)`

1. `load_yaml` 讀兩個 config。
2. `selected = set(only) if only else {"E1","E2","E3","E4","E5"}`。
3. `root = Path(config_path).resolve().parent.parent`，也就是 `code/`。
4. `raw_dir`、`processed_dir`、`figure_dir` 從 `base_config["paths"]` 來。
5. 對每個 selected：
   - 跑 `run_eX`。
   - 存 CSV/JSON。
   - 呼叫 `plot_eX`。
   - `print` 表格和路徑。
6. 如果 `--only E5`，只跑 E5；其他 config 不會被讀取或執行。

#### `parse_args()`、`main()`

- `argparse` 讀 `--config`、`--experiments`、`--only`。
- `main()` 呼叫 `run(args.config, args.experiments, args.only)`。
- 所以 `python -m src.experiments --only E1` 會執行 `main()`。

### 11.10 `plotting.py` 逐函數細節

#### `set_style()`

- 設定 Matplotlib 的 global style：字體大小、線寬、spines、legend、DPI。
- `figure.constrained_layout.use = True` 讓子圖不會重疊。
- 這不是「必要」的，但讓所有圖看起來一致。

#### `save_figure(figure, path)`

```python
path = Path(path)
path.parent.mkdir(parents=True, exist_ok=True)
figure.savefig(path, bbox_inches="tight")
figure.savefig(path.with_suffix(".png"), bbox_inches="tight", dpi=220)
```

- 同時存 PDF 和 PNG。
- PDF 是向量格式，適合放進報告。
- PNG 是點陣格式，方便快速預覽。
- `bbox_inches="tight"` 會把多餘的空白裁掉。

#### `plot_e1_scaling(frame, summary, path)`

- `figure, axes = plt.subplots(2, 2)` 建 2×2 子圖。
- 對每個 family：
  - `axis.loglog(N, HT)` 畫古典。
  - `axis.loglog(N, t_q)` 畫量子。
  - `axis.text(...)` 把 fit 出來的 exponent 寫在圖上。
  - `axis.legend()`。
- `figure.suptitle(...)` 加總標題。
- `save_figure` 存檔。

#### `plot_e1_speedup(frame, path)`

- 對每個 family 畫 `N` vs `HT/T_q`。
- `axis.axhline(1.0)` 畫一條 $y=1$ 的參考線。
- 如果 speedup > 1，量子比古典快。

#### `plot_e2_success(frame, curves, path)`

- 2×2 子圖，每個 case 一個。
- 對每個 kind：
  - 把 curves 按 `t` 分組，算 mean/min/max。
  - `axis.plot` 畫 mean。
  - `axis.fill_between` 畫 min–max band。
- 這樣的 band 代表「不同 random marked set 的變異」。

#### `plot_e2_ht(frame, adversarial, path)`

- 左圖：`HT` vs `HT_plus` 的 scatter，虛線是 $y=x$。
  - 點在虛線上方代表 $\mathrm{HT}^+>\mathrm{HT}$。
  - 標籤 `G6-s` 代表 grid 6 single，`B16-i` 代表 barbell 16 independent。
- 右圖：adversarial torus 的 `N` vs `HT`、`HT_plus`，並標 ratio。

#### `plot_e3_semantic(graph, metrics, curves, cue, targets, path)`

- 2×2：
  - 左上：graph drawing（`nx.kamada_kawai_layout`）。
    - 節點顏色按社群。
    - cue 用星號，targets 用方形框。
  - 右上：cue → target 1 的 activation curves。
  - 左下：cue → target 2。
  - 右下：peak activation bar chart。
- `nx.draw_networkx_edges`、`nodes`、`labels` 畫圖。

#### `plot_e4_decision(frame, choices, path)`

- 2×2：
  - 左上：symmetric3 quantum。
  - 右上：symmetric3 classical。
  - 左下：asymmetric3 quantum。
  - 右下：decision time vs coupling（四條線：symmetric3/asymmetric3 × quantum/classical）。
- `axis.axhline(1/n_options)` 畫均勻參考線。
- 不同 option 用不同線型（solid/dashed/dotted），避免重疊時看不見。

#### `plot_e5_decoherence(frame, curves, deadline, path)`

- 2×2：
  - 左上：grid single 的 success vs t，選幾個 $p$。
  - 右上：toy single 的 success vs t。
  - 左下：deadline success vs $p$（四條 case）。
  - 右下：half-max time vs $p$。
- 左下用星號標出每個 case 的最佳 $p$。
- 右下用 log y，讓時間差異看得清楚。

### 11.11 從零建環境與跑起來

#### 建環境

```bash
cd Final/code
mamba env create -f environment.yml
mamba activate qwalk-cognition
```

`environment.yml` 的內容：

```yaml
name: qwalk-cognition
channels:
  - conda-forge
dependencies:
  - python=3.12
  - numpy>=2.0
  - scipy>=1.13
  - networkx>=3.3
  - matplotlib>=3.9
  - pandas>=2.2
  - pyyaml>=6.0
  - pytest>=8.0
  - jupyterlab>=4.2
  - pip
```

- `name` 是環境名稱。
- `channels: conda-forge` 是套件來源。
- `python=3.12` 是版本。
- 其他是套件。

#### 跑測試

```bash
python -m pytest -q
```

你應該看到 `71 passed`（待確認：本次文件更新未重跑 pytest）。

#### 跑實驗

```bash
python -m src.experiments --only E1
python -m src.experiments --only E2
python -m src.experiments --only E3
python -m src.experiments --only E4
python -m src.experiments --only E5
```

#### 跑 notebook

```bash
jupyter lab
```

然後打開 `notebooks/01_sanity_checks.ipynb`。

#### 編譯報告

```bash
cd ../report
tectonic -X compile main.tex
```

Tectonic 會自動下載需要的 LaTeX 套件。第一次會比較慢，之後會快很多。

#### 常見錯誤

- `ModuleNotFoundError: No module named 'src'`：你不在 `Final/code` 目錄，或沒有 activate 環境。
- `ModuleNotFoundError: No module named 'matplotlib'`：你用了 base Python，不是 `qwalk-cognition`。
- `FileNotFoundError: configs/base.yaml`：你不在 `Final/code`。
- `tectonic: command not found`：Tectonic 不在 PATH；用 `mamba run -n qwalk-cognition tectonic ...`。
- LaTeX `??`：編譯兩次，或 Tectonic 已經自動處理；如果還有，檢查 `\label`/`\cref`。
- `Overfull \hbox`：表格或文字太寬；調整 column width 或改寫句子。

---

## 12. 報告導覽：每一節、每一張圖表

### 12.1 章節結構

| 章節 | 內容 | 重點 |
|---|---|---|
| Abstract | 問題、方法、五個結果 | 不要寫太長 |
| 1 Introduction | 動機、gap、RQ、貢獻 | 為什麼 quantum walk × cognition |
| 2 Background | classical walk、Szegedy、AGJK、quantum cognition | 文獻地圖 Table 1 |
| 3 Theory | $D$、$\mathrm{HT}(s)$、$W(s)$、Chebyshev、measurement channel、CTQW | 公式與定義 |
| 4 Cognitive Model | mapping table、assumptions、RT/choice、context | Table 2 |
| 5 Methods | graphs、protocols、metrics、reproducibility | Table 3 |
| 6 Results | E1–E5 | Figures 2–7、Tables 4–7 |
| 7 Discussion | 解釋、文獻比較、limitations | algorithmic vs biological |
| 8 Conclusion | 總結 | 不要引入新結果 |
| Appendix | 推導、measurement recursion、額外結果、reproducibility | 給想深入的人 |

### 12.2 Figure 對照

| 圖 | 內容 | 在哪一節 |
|---|---|---|
| Figure 1 | 三層架構 | Introduction |
| Figure 2 | E1 scaling | Results 6.1 |
| Figure 3 | E2 success curves | Results 6.2 |
| Figure 4 | E2 HT vs HT⁺ + adversarial torus | Results 6.2 |
| Figure 5 | E3 semantic graph + activation | Results 6.3 |
| Figure 6 | E4 choice probabilities + decision time | Results 6.4 |
| Figure 7 | E5 decoherence sweep | Results 6.5 |

### 12.3 Table 對照

| Table | 內容 | 在哪一節 |
|---|---|---|
| Table 1 | 文獻地圖 | Background |
| Table 2 | 認知映射 | Cognitive Model |
| Table 3 | 實驗矩陣 | Methods |
| Table 4 | E1 scaling exponents | Results 6.1 |
| Table 5 | E2 selected results | Results 6.2 |
| Table 6 | E5 optimal p | Results 6.5 |
| Table 7 | E2 full results | Appendix |

### 12.4 報告中最重要的 claim

1. $T_q\sim\mathrm{HT}^{0.44\text{--}0.52}$：數值支持 AGJK 的 $\sqrt{\mathrm{HT}}$ scaling。
2. Independent targets 比 clustered 容易：這是 marked-set 結構的效應。
3. 大 $\mathrm{HT}^+$ gap 只在 adversarial torus：不要過度推廣。
4. CTQW 對遠目標有較高峰值，但較晚：語意距離效應。
5. Option coupling 造成 context effect：在偵測讀出下，量子選擇機率單調偏向未耦合選項（先前的非單調結論已撤回）。
6. Weak measurement 在群聚目標與較長 deadline 下可以幫助（$p\approx0.2$–$0.3$），但 $p_{\max}$ 仍是 $p=0$ 最好：speed–accuracy tradeoff。

### 12.5 報告的 limitations 一定要看

- 沒有真人資料。
- 圖是合成的、小的。
- $s$ 是 grid search 選的。
- CTQW 與 DTQW 沒有混在同一個 fit。
- Noise 是 projective measurement，不是 Lindblad。
- 尺寸有限，asymptotic exponent 有 finite-size error。

這些不是「缺點」而已，它們是「你的結論適用到哪裡」的邊界。寫報告時要主動說，不要等 reviewer 問。

### 12.6 LaTeX 檔案結構與常用語法

#### `main.tex` 的 preamble

```latex
\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{mathtools}
\usepackage{array}
\usepackage{graphicx}
\graphicspath{{figures/}}
\usepackage{booktabs}
\usepackage{enumitem}
\usepackage[round]{natbib}
\usepackage[hidelinks]{hyperref}
\usepackage{cleveref}
\usepackage{placeins}
```

每個 package 的作用：

- `geometry`：設定邊界。
- `fontenc`、`inputenc`、`lmodern`：字型與編碼。
- `microtype`：微調字距，讓排版更漂亮。
- `amsmath`、`amssymb`、`amsthm`：數學公式與定理環境。
- `mathtools`：數學工具。
- `array`：表格的 `>{\raggedright\arraybackslash}p{}` 語法。
- `graphicx`：插入圖片。
- `graphicspath`：讓 `\includegraphics{figures/...}` 可以簡寫。
- `booktabs`：漂亮的表格線（`\toprule`、`\midrule`、`\bottomrule`）。
- `enumitem`：調整 enumerate/itemize 的間距。
- `natbib`：`\citep{}`、`\citet{}`。
- `hyperref`：超連結。
- `cleveref`：`\cref{}` 會自動寫 "Figure 2"、"Table 3"。
- `placeins`：`\FloatBarrier` 控制浮動圖表的位置。

#### 自訂巨集

```latex
\newcommand{\HT}{\mathrm{HT}}
\newcommand{\HTp}{\mathrm{HT}^{+}}
\newcommand{\Otil}{\widetilde{O}}
\newcommand{\U}{\mathcal{U}}
\newcommand{\Prob}{\mathbb{P}}
\newcommand{\E}{\mathbb{E}}
```

這樣你打 `\HT` 就會變成 $\mathrm{HT}$，打 `\HTp` 就會變成 $\mathrm{HT}^{+}$。好處是：如果以後想改寫法，只改一行。

#### 定理環境

```latex
\newtheorem{theorem}{Theorem}
\newtheorem{lemma}{Lemma}
\newtheorem{proposition}{Proposition}
\newtheorem{definition}{Definition}
\newtheorem{conjecture}{Conjecture}
```

用法：

```latex
\begin{lemma}
  ...
\end{lemma}
```

#### 章節檔案

`main.tex` 用 `\input{sections/01_introduction}` 把各章節檔案接進來。好處是：
- 每個章節一個檔案，容易編輯。
- 不會讓 `main.tex` 變成幾千行。
- 你可以單獨編譯某個 section（需另外設定）。

#### 插入 figure

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{figures/fig_e1_scaling.pdf}
  \caption{...}
  \label{fig:e1}
\end{figure}
```

- `[t]`：放在頁面頂端。
- `\centering`：置中。
- `width=\linewidth`：寬度等於文字寬度。
- `\caption`：圖說。
- `\label`：給 `\cref` 用。

#### 插入 table

```latex
\begin{table}[t]
  \centering
  \small
  \begin{tabular}{@{}lcccc@{}}
    \toprule
    A & B & C & D & E \\
    \midrule
    1 & 2 & 3 & 4 & 5 \\
    \bottomrule
  \end{tabular}
  \caption{...}
  \label{tab:example}
\end{table}
```

- `@{}` 去掉最左和最右的空白。
- `lcccc`：第一欄左對齊，其他置中。
- 如果欄位太窄，用 `p{0.24\linewidth}` 讓它自動換行。
- 如果不想 hyphenation，用 `>{\raggedright\arraybackslash}p{...}`。

#### 引用文獻

```latex
\citep{agjk2019}
\citet{pothos2022}
```

- `\citep`：括號引用，例如 (Ambainis et al., 2019)。
- `\citet`：文字引用，例如 Ambainis et al. (2019)。
- `refs.bib` 裡的 key 必須對應。

`refs.bib` 的格式：

```bibtex
@article{agjk2019,
  author = {Ambainis, Andris and Gily{\'e}n, Andr{\'a}s and Jeffery, Stacey and Kokainis, Martins},
  title = {Quadratic speedup for finding marked vertices by quantum walks},
  journal = {arXiv preprint arXiv:1903.07493},
  year = {2019}
}
```

#### 編譯

```bash
tectonic -X compile main.tex
```

Tectonic 會自動跑 BibTeX 和多次 TeX，直到 references 穩定。如果還有 `??`，檢查：
- `\label` 是否在 `\caption` 之後。
- `\cref` 的 key 是否拼對。
- 是否有 figure 檔案不存在。

#### 常見 LaTeX 警告

- **Overfull hbox**：某一行太寬。通常是長 URL、長 inline math、或表格。解法：改寫句子、加 `\allowbreak`、或調整表格欄寬。
- **Underfull hbox**：某一行太鬆。通常是 `p{}` 欄位對齊造成。可以用 `\raggedright` 或改欄寬。
- **Float too large**：圖太大，放不進頁面。解法：`width=0.9\linewidth` 或 `[t]`/`[p]`。
- **Undefined reference**：編譯次數不夠，或 label 拼錯。

### 12.7 如何修改報告

#### 改作者

打開 `report/main.tex`，找到：

```latex
\author{[Student Name 1] \quad [Student ID 1]\\[0.2em]
[Student Name 2] \quad [Student ID 2]}
```

改成你的名字和學號。如果你是一個人，刪掉第二行。

#### 改 abstract

`main.tex` 的 `\begin{abstract}...\end{abstract}`。abstract 應該包含：
- 問題。
- 方法。
- 主要結果（數字）。
- 貢獻。
- 不要放 citation。

#### 加一個新 section

1. 在 `report/sections/` 建 `09_new_section.tex`。
2. 在 `main.tex` 的 `\input` 區加一行。
3. 用 `\section{}`、`\subsection{}`。
4. 編譯。

#### 換 figure

1. 把新的 PDF 放到 `report/figures/`。
2. 在 section 裡改 `\includegraphics{figures/新檔名.pdf}`。
3. 更新 `\caption` 和 `\label`。
4. 編譯。

#### 改表格數字

1. 確認 `code/results/processed/` 的 JSON 是最新的。
2. 用 `RESULTS_SUMMARY.md` 對照。
3. 手動改 LaTeX 表格，或寫一個小 script 從 JSON 生成表格（進階）。

#### 重新編譯與檢查

```bash
cd report
tectonic -X compile main.tex
```

然後打開 `main.pdf`，檢查：
- figure/table 編號是否正確。
- 有沒有 `??`。
- 有沒有文字溢出。
- 頁數是否可接受。


## 13. 常見誤解與 FAQ

### Q1：量子漫步為什麼會比古典漫步快？

古典漫步是擴散：走 $t$ 步，典型距離 $\sqrt t$。量子漫步是波動：不同路徑的振幅可以建設性干涉，讓機率集中，典型距離 $t$。所以如果古典需要 $T$ 步，量子可能只需要 $\sqrt T$ 步。

但這不是自動的。你需要正確的 walk operator、正確的 initial state、正確的 measurement。Szegedy 的 detection 和 finding 之差就是例子。

### Q2：為什麼 $W(0)$ 從 stationary state 出發不會動？

因為 $|\bar0\rangle|\sqrt\pi\rangle$ 是 $W(0)$ 的特徵向量，特徵值 1。詳細推導在 §3.6。這是初學者最常踩的坑。

### Q3：為什麼要掃 $s$？

因為 AGJK 的 Conjecture 3 只說「存在某個 $s$」，沒有給你公式。我們用 $q_t(s)$ 的下界掃描，選最好的 $s$。這是一個數值 protocol，不是定理。

### Q4：為什麼 clustered targets 的 $\mathrm{HT}^+$ 沒有很大？

因為 $\mathrm{HT}^+$ 大不大，取決於 $D(s)$ 的特徵值是否非常接近 1。一般的 clustered set 沒有這種 spectral resonance。AGJK 的 adversarial torus 有 dense + sparse 的週期結構，才會產生大 gap。

### Q5：為什麼 $p=1$ 是古典？

當 $p=1$，每一步都量測並重置到 basis state，相干性完全消失。位置轉移矩陣是
$$
Q_{xy}=\|\Pi_yW(0)|\bar0\rangle|x\rangle\|^2.
$$
對 $s=0$，可以證明 $Q=P$。所以 $p=1$ 就是原本的 classical random walk。

### Q6：為什麼 $p_{\max}$ 在 $p=0$ 最大，但群聚目標的 deadline success 在 $p\approx0.2$–$0.3$ 最大？

因為這是兩個不同的目標函數：
- $p_{\max}$ 允許你等到最佳時間，所以純量子最好。
- 偵測模型裡，量測一旦落在目標就結束搜尋：中等 $p$ 一方面保留部分相干擴散（比古典快接近目標），一方面給了多次「看見就停」的機會，不必剛好在振盪峰值讀取。群聚目標面積大，被量測命中的機會多，所以中間 $p$ 在 $T\gtrsim20$ 同時勝過兩個極端。
這是「峰值（需要精準計時）」與「穩健偵測」之間的取捨。

### Q7：為什麼 E4 的耦合會單調偏向未耦合選項？

在偵測讀出下，耦合使未耦合選項的機率單調上升；古典漫步在對稱圖上完全不變。先前的非單調結論屬相位假象，已撤回。讀出定義對結論影響很大，因此必須明確寫出讀出方式。

### Q8：CTQW 和 DTQW 差在哪？

- CTQW：continuous time，$e^{-iHt}$，沒有 coin。
- DTQW：discrete time，有 coin、有 register、有 $W(P)$。

我們的 E3 用 CTQW/CRW；E1/E2/E4/E5 用 Szegedy DTQW。報告明確分開，不混用。

### Q9：為什麼 E3 用 normalized Laplacian？

因為 normalized Laplacian 會把 degree 的影響部分消掉，讓不同 degree 的節點比較公平。對語意圖來說，這通常比 combinatorial Laplacian 合理。

### Q10：為什麼 E3 的 near target，古典 AUC 比較高？

因為古典漫步一走到 neighbor 就立刻活化，然後慢慢衰減；AUC（τ≤8）是「整體活化量」，古典的早期高峰讓 AUC 較大（0.579 vs 0.481）。CTQW 窗內最大值（0.337）是 τ=47.5 的 recurrence 尖峰。

### Q11：為什麼 independent targets 反而容易？

因為目標分散，walker 從任何方向都可能碰到其中一個。Clustered targets 則要走到同一個小區域，還要找到其中一個點；四張圖上每一組 independent 都比每一組 clustered 容易，而 clustered 相對 single 可易可難。

### Q12：什麼是 marked set？

Marked set $M\subset V$ 是「目標」的集合。在搜尋問題裡，它是你要找的 vertex；在認知模型裡，它是目標記憶或決策邊界。

### Q13：什麼是 discriminant matrix？

$D_{xy}=\sqrt{P_{xy}P_{yx}}$。它是 Szegedy walk 的「壓縮版」：$W(P)$ 的左上角 $n\times n$ 塊就是 $D$。$D$ 的特徵值控制 $W(P)$ 的振盪頻率。

### Q14：什麼是 Chebyshev 下界？

$q_t(s)=\|\Pi_MT_t(D(s))|\sqrt\pi\rangle\|^2$。它是成功機率的下界，可以用 $O(n^2)$ 每步算，比完整 $W(s)$ 的 $O(n^3)$ 快。我們用它來選 $s$。

### Q15：什麼是 quantum fast-forwarding？

Apers–Sarlette 的技術：用 $O(\sqrt t)$ 次 quantum walk update，模擬 $t$ 步 classical walk 的某些性質。AGJK 用它證明 Theorem 5。我們沒有實作，只引用。

### Q16：為什麼需要 ancilla？

因為 interpolated walk 需要記錄「現在是否 marked」。ancilla 是一個 qubit，`0` 代表繼續走，`1` 代表停住。State 的形狀 `(2,n,n)` 就是 ancilla + 兩個 register。

### Q17：為什麼 $s$ 不能等於 1？

公式裡 $P(s)=(1-s)P+sP'$ 在 $s=1$ 時是完全吸收，$D(1)$ 可能有多個特徵值 1，$\mathrm{HT}(s)$ 的分母會變成 0。所以我們用 $s=1-\epsilon$ 近似 $\mathrm{HT}^+$，並在 $W(s)$ 裡限制 $s<1$。

### Q18：數值出現負機率怎麼辦？

通常是浮點誤差。程式裡會 `clip` 到 0，或 normalize。例如 `crw_trajectory` 最後會 clip 負值再 normalize。如果負值很大，那可能是公式或 indexing 錯誤，不是單純誤差。

### Q19：這些結果可以說「大腦是量子電腦」嗎？

不行。我們從頭到尾都說這是 process-level model，不是生物物理主張。Quantum cognition 用的是量子機率的數學結構，不是說大腦真的在跑量子電路。

### Q20：如果要做真人實驗，要改什麼？

你需要：
- 設計 behavioral task（例如語意搜尋、選擇題）。
- 把 graph 的節點和邊對應到刺激與相似度。
- 用 choice probability 和 RT 去 fit 模型參數。
- 比較 quantum walk、classical random walk、其他 sequential sampling model 的 fit。
- 做 model comparison（AIC/BIC、cross-validation）。

這是 future work，不是這個專案已經做的。

### Q21：報告 26 頁會不會太長？

有可能。ROADMAP 建議主文 10–12 頁，但這是建議不是硬限制。如果老師要求縮短，優先砍：
- Appendix 的重複表格。
- Background 的部分文獻細節。
- Methods 的過度解釋。
- 把部分 figure 移到 appendix。

但不要砍掉：E1–E5 的主要結果、limitations、algorithmic vs biological 的區分。

### Q22：為什麼作者欄位是 placeholder？

因為我們不知道你的真實姓名。`main.tex` 裡是 `[Student Name 1]`、`[Student ID 1]`。送出前要改成你的名字和學號。從 proposal 的檔名看起來學號可能是 `r15k47010`，但請自己確認。

### Q23：為什麼有些 spectral gap 是 0？

因為我們用的是 absolute spectral gap $1-\max_{k\ne1}|\lambda_k|$。對 bipartite graph（例如 even cycle、grid），$D$ 有 eigenvalue $-1$，所以 gap 是 0。這不是 bug，是定義。

### Q24：為什麼 complete graph 的 $\mathrm{HT}$ exponent 不是 1？

有限尺寸下 fit 出來是 1.06，這是 finite-size effect。理論上 $K_N$ 的 $\mathrm{HT}=N-1$，但我們的 $N$ 只有 8–64，log-log fit 會有誤差。

### Q25：為什麼 E2 有些 seeds 的 marked set 一樣？

`_farthest_point_sample` 從隨機起點開始，但對某些圖和 $k$，不同起點可能產生同一組 farthest-point set。這不是 bug，是對稱性造成的。E2 現用 seeds 0–19 並去除重複集合，每個設定使用互不相同的 sets（distinct sets 數量見 §10.2 表）。

### Q26：為什麼 E1/E2 的 $p_M(0)$ 不是 0？

因為 initial state 是 $|\bar0\rangle|\sqrt\pi\rangle$， stationary distribution 在 marked set 上本來就有質量 $\pi_M$。所以 $t=0$ 時已經有 $\pi_M$ 的機率在 marked vertex。這不是「已經找到」，而是「初始注意力剛好在那裡」。

### Q27：為什麼 E3 的 toy single $t_{\text{opt}}$ 有時是 60（$T_{\max}$）？

因為 CRW 的目標機率可能還在慢慢上升，尚未達到峰值；$t_{\text{opt}}=T_{\max}$ 只代表「在我們模擬的窗口內，最大值出現在最後」。這不是真正的無窮時間峰值。報告裡有說明 $T_{\max}=8/\lambda_1$。

### Q28：如果我要跟老師說「這篇的貢獻是什麼」，怎麼說？

三句話：
1. 我們把 AGJK 的 marked-vertex search 當成 cognitive search 的 process model，而不是只做文獻回顧。
2. 我們數值驗證了 $\sqrt{\mathrm{HT}}$ scaling，並釐清 $\mathrm{HT}^+$ 大 gap 的條件（adversarial arrangement，不是 generic clustering）。
3. 我們用 semantic graph、decision graph、partial measurement 展示模型的可檢驗預測，並誠實說明它不是生物物理主張。

---

## 14. 符號與名詞表

### 14.1 常用符號

| 符號 | 意思 |
|---|---|
| $G=(V,E)$ | 圖，$V$ 是頂點，$E$ 是邊 |
| $n$ | 頂點數 |
| $A$ | adjacency matrix |
| $D$ | degree matrix，或 discriminant matrix（看上下文） |
| $P$ | transition matrix |
| $\pi$ | stationary distribution |
| $p_M$ | marked set 的 stationary mass |
| $M$ | marked set |
| $U$ | unmarked set，$U=V\setminus M$ |
| $\mathrm{HT}$ | classical hitting time |
| $\mathrm{HT}^+$ | extended hitting time |
| $P'$ | absorbing transition matrix |
| $P(s)$ | interpolated transition matrix |
| $W(P)$ | Szegedy walk operator |
| $W(s)$ | interpolated walk operator |
| $D(s)$ | discriminant matrix of $P(s)$ |
| $s$ | interpolation parameter |
| $T_t$ | Chebyshev polynomial of the first kind |
| $q_t(s)$ | AGJK lower bound |
| $p$ | measurement probability |
| $\rho$ | density matrix / probability distribution（看上下文） |
| $L_{\mathrm{sym}}$ | symmetric normalized Laplacian |
| $L_{\mathrm{rw}}$ | random-walk Laplacian |
| $\lambda_1$ | spectral gap |
| $\tau$ | normalized time $\lambda_1t$ |
| $T_q$ | quantum search time |
| $p_{\max}$ | peak success probability |
| $P_i$ | choice probability of option $i$ |
| AUC | area under curve |

### 14.2 名詞

| 名詞 | 白話解釋 |
|---|---|
| Amplitude | 振幅；機率的平方根，可以是複數 |
| Ancilla | 輔助 qubit；在 $W(s)$ 裡記錄是否 marked |
| Basis state | 基底狀態，例如 $|x\rangle$ |
| Chebyshev polynomial | 一組多項式，用來算 $T_t(D)$ |
| Coherence | 相干性；非對角 density matrix 元素 |
| CTQW | Continuous-Time Quantum Walk |
| CRW | Continuous-Time Random Walk |
| Decoherence | 退相干；相位資訊流失 |
| Density matrix | 描述混合態的矩陣 |
| Discriminant matrix | $D_{xy}=\sqrt{P_{xy}P_{yx}}$ |
| DTQW | Discrete-Time Quantum Walk |
| Eigenvalue | 特徵值 |
| Eigenvector | 特徵向量 |
| Fast-forwarding | 用量子 walk 模擬多步 classical walk 的技術 |
| Hitting time | 第一次碰到目標的期望時間 |
| Interpolated walk | 在 $P$ 和 $P'$ 之間插值的 walk |
| Marked set | 目標集合 |
| Measurement | 量測；會讓狀態塌縮 |
| Mixing time | 走到接近 stationary 的時間 |
| Normalized Laplacian | $I-D^{-1/2}AD^{-1/2}$ |
| Reversible | 滿足 detailed balance 的 chain |
| Spectral gap | 特徵值間隙；控制 mixing 速度 |
| Stationary distribution | 平穩分布 $\pi P=\pi$ |
| Unitary | 么正；保持 norm 的線性算子 |

---

## 15. 七天讀書計畫與自我測驗

### 15.1 七天計畫

**Day 1：基礎與古典**
- 讀 §0–§2。
- 跑 `python -m pytest tests/test_classical.py -q`。
- 自己算一次 $K_8$ 的 hitting time，確認是 7。
- 自己算一次 $C_8$ 的 hitting time，確認是 $8\cdot9/6=12$。

**Day 2：Szegedy**
- 讀 §3。
- 跑 `notebooks/01_sanity_checks.ipynb`。
- 自己解釋為什麼 $W(0)|\bar0\rangle|\sqrt\pi\rangle=|\bar0\rangle|\sqrt\pi\rangle$。
- 跑 `tests/test_quantum.py`。

**Day 3：AGJK**
- 讀 §4。
- 讀 AGJK 論文 Sec. 1–2、Sec. 3 的 $HT^+$ 例子、Sec. 4 的 Algorithm 1。
- 跑 `tests/test_quantum.py` 裡的 interpolated 測試。
- 自己解釋 $q_t(s)$ 為什麼是 lower bound。

**Day 4：語意**
- 讀 §5–§6。
- 跑 `python -m src.experiments --only E3`。
- 打開 `figures/E3_semantic.png`，指出 cue、targets、CTQW/CRW 曲線。
- 自己解釋為什麼遠目標的 CTQW 峰值較高。

**Day 5：決策與雜訊**
- 讀 §7–§8。
- 跑 E4、E5。
- 自己解釋 $p=1$ 為什麼是古典。
- 自己解釋為什麼群聚目標在較長 deadline 下，$p\approx0.2$ 勝過純量子與古典。

**Day 6：程式與報告**
- 讀 §10–§12。
- 對照 `src/experiments.py` 的 `run_e1`–`run_e5`。
- 打開 `report/main.pdf`，對照 Figure 2–7 和 Table 4–7。
- 跑一次 `tectonic -X compile main.tex`。

**Day 7：口頭報告**
- 讀 §16。
- 用 15 分鐘講一次。
- 錄音，檢查時間。
- 練習 Q1–Q10。

### 15.2 自我測驗（先自己回答，再看下面的答案）

1. $P$ 的每一列為什麼要加起來等於 1？
2. Stationary distribution 的定義是什麼？
3. Reversible 的 detailed balance 條件是什麼？
4. Hitting time 的線性方程怎麼寫？
5. $K_N$ 的 hitting time 是多少？
6. $C_N$ 的 hitting time 是多少？
7. Szegedy walk 的三個基本操作是什麼？
8. $D_{xy}$ 的公式是什麼？
9. 為什麼 $W(0)$ 從 stationary state 出發不會動？
10. Interpolated walk 的 $P(s)$ 公式是什麼？
11. $\mathrm{HT}^+$ 的定義是什麼？
12. 為什麼 $q_t(s)$ 是 lower bound？
13. CTQW 和 CRW 的 generator 分別是什麼？
14. $\tau=\lambda_1t$ 的作用是什麼？
15. 為什麼 $p=1$ 是古典？
16. E5 的 basis ensemble 為什麼是精確的？
17. 為什麼 E2 的 independent targets 比較容易？
18. 為什麼 E4 的耦合在偵測讀出下單調偏向未耦合選項？
19. 這篇論文的主要貢獻是什麼？
20. 這篇論文不能說什麼？

### 15.3 答案（簡短版）

1. 因為從任何點出發，下一步一定要到某個地方。
2. $\pi P=\pi$ 且 $\sum\pi_i=1$。
3. $\pi_xP_{xy}=\pi_yP_{yx}$。
4. $h_x=1+\sum_yP_{xy}h_y$，$h_x=0$ for $x\in M$。
5. $N-1$。
6. $N(N+1)/6$。
7. $V(P)$、Shift、Ref。
8. $\sqrt{P_{xy}P_{yx}}$。
9. 利用 detailed balance，$V^\dagger$ 後會回到 $|\bar0\rangle|\sqrt\pi\rangle$。
10. $P(s)=(1-s)P+sP'$，$P'=\begin{pmatrix}P_{UU}&P_{UM}\\0&I\end{pmatrix}$。
11. $\mathrm{HT}(s)=\frac{1}{1-p_M}\sum_k\frac{|\langle v_k(s)|\sqrt{\pi_U}\rangle|^2}{1-\lambda_k(s)}$，$\mathrm{HT}^+=\lim_{s\to1}\mathrm{HT}(s)$。
12. 因為投影到第一個 register 是 $\bar0$ 的子空間只會讓 norm 變小。
13. CTQW 用 $L_{\mathrm{sym}}$，CRW 用 $L_{\mathrm{rw}}$。
14. 把不同圖的 relaxation time 正規化，讓時間尺度可比。
15. 量測把相干性殺掉，$Q_{xy}=P_{xy}$。
16. 因為量測後狀態一定是某個 basis state，且其後演化只取決於 $(x,a)$，可以預先算好。
17. 目標分散，walker 從任何方向都可能碰到其中一個。
18. 分支長度不對稱 + 量子干涉，讓不同 $c$ 下的相位關係改變。
19. 把 AGJK marked-vertex search 當成 cognitive process model，數值驗證 scaling、釐清 $\mathrm{HT}^+$ 條件、展示 semantic/decision/noise 的 model-level predictions。
20. 不能說大腦是量子電腦，也不能說已經有人類行為資料支持。

---

## 16. 口頭報告與 Q&A 準備

### 16.1 15–18 分鐘 slide plan

| Slide | 內容 | 時間 |
|---|---|---:|
| 1 | Title + 一句話 takeaway | 0.5 min |
| 2 | Motivation：quantum cognition 與 quantum walk 的接點 | 1.5 min |
| 3 | RQ 與 contributions | 1.0 min |
| 4 | Classical walk / hitting time / marked vertices | 2.0 min |
| 5 | Szegedy walk 與 detection vs finding | 2.0 min |
| 6 | AGJK：$\mathrm{HT}^+$、interpolated walk、fast-forwarding | 2.5 min |
| 7 | Cognitive mapping：graph / marked set / RT / choice | 2.0 min |
| 8 | Experimental setup | 1.5 min |
| 9 | Results 1：scaling | 2.0 min |
| 10 | Results 2：multiple marked / clustering | 2.0 min |
| 11 | Results 3：semantic / decoherence | 2.0 min |
| 12 | Discussion：what it explains, what it doesn't | 1.5 min |
| 13 | Limitations 與 future work | 1.0 min |
| 14 | Conclusion | 0.5 min |

### 16.2 給非專家的解釋

如果你只有 30 秒：

> 我們把「量子漫步搜尋」當成一個認知模型。圖上的點是概念或選項，量子漫步是思考時的證據累積。我們發現量子搜尋時間大約是古典的平方根，而且目標的排列、選項的相似度、以及雜訊，都會改變搜尋與選擇的行為。但我們沒有說大腦是量子電腦；這是一個數學模型。

### 16.3 預期 Q&A

**Q：量子認知是不是說大腦是量子電腦？**
A：不是。我們用的是量子機率的數學結構，不是生物物理主張。我們的模型是 process-level model。

**Q：為什麼選 AGJK，而不是一般的 quantum cognition 論文？**
A：因為這是 QIS 課程，核心必須是 quantum algorithm。AGJK 的 marked-vertex search 提供嚴謹的 QIS 骨幹，而且它的多 marked vertices 結構可以映射到多目標認知搜尋與多選項決策。

**Q：這篇的貢獻是什麼？**
A：三點：(1) 數值驗證 $\sqrt{\mathrm{HT}}$ scaling；(2) 釐清 $\mathrm{HT}^+$ 大 gap 的條件是 adversarial arrangement，不是 generic clustering；(3) 用 semantic/decision/decoherence 實驗展示 model-level predictions。

**Q：為什麼沒有真人實驗？**
A：這是 proof-of-concept / numerical study。真人實驗是 future work；我們的重點是建立可檢驗的 model-level predictions。

**Q：量子優勢在認知上有意義嗎？**
A：演算法層面有 $\sqrt{\mathrm{HT}}$ 的優勢；但這不代表大腦能實現。我們的 discussion 明確區分 algorithmic advantage 與 biological plausibility。

**Q：為什麼用 CTQW 又用 DTQW？**
A：AGJK 是 discrete-time Szegedy walk；Pavone–Faro 是 continuous-time walk。我們在 E1/E2/E4/E5 用 DTQW，在 E3 用 CTQW/CRW，並且明確區分，不混用。

**Q：$\mathrm{HT}^+$ 到底是什麼？**
A：它是 AGJK 定義的 extended hitting time，由 interpolated walk 的 discriminant matrix 的特徵值／特徵向量定義。多個 marked vertices 時可能遠大於 $\mathrm{HT}$。

**Q：E4 的耦合效應為什麼是單調的？**
A：在偵測讀出下，耦合使未耦合選項的機率單調上升；古典漫步在對稱圖上不變。先前的非單調結論屬相位假象，已撤回。

**Q：為什麼 E5 的 $p=1$ 是古典？**
A：每一步都量測並重置到 basis state，相干性完全消失；對 $s=0$，transition matrix 剛好等於 $P$。測試 `test_fully_measured_walk_is_classical` 驗證了這一點。

**Q：你用了 AI 嗎？**
A：有，用於 code scaffolding、experiment automation、LaTeX drafting。所有推導、實驗設計、數值結果與解讀都由作者檢查。報告有 AI disclosure section。

### 16.4 口頭報告的禁忌

- 不要說「大腦是量子電腦」。
- 不要說「我們證明了量子認知是對的」。
- 不要說「$\mathrm{HT}^+$ 一定很大」；要說「在 adversarial arrangement 下很大」。
- 不要把 CTQW 和 DTQW 的 time scale 混在一起。
- 不要隱藏 limitations；主動說反而加分。

---

## 17. 最後的檢查清單

### 17.1 送出前

- [ ] `main.tex` 的作者欄位改成你的名字和學號。
- [ ] `main.pdf` 重新編譯，確認沒有 `??`。
- [ ] 所有 figure 在文中都有 `\cref`。
- [ ] 所有 citation 都在 `refs.bib`。
- [ ] `report/figures/` 裡的 PDF 都是最新的。
- [ ] `code/tests/` 71 個測試都通過。
- [ ] `README.md` 的指令可以重現至少一張 main figure。
- [ ] AI disclosure 有寫。
- [ ] 沒有 TODO / placeholder（除了作者欄位）。
- [ ] 報告頁數符合老師要求（如果沒有硬限制，26 頁可接受，但可精簡）。

### 17.2 如果你時間不夠

最低完成標準（ROADMAP §7.4）：

1. AGJK/Szegedy 的理論整理。
2. Complete graph + 2D grid 的 classical vs quantum scaling。
3. 一個 toy semantic graph 的認知映射。
4. 一張 multiple marked vertices 的比較圖。
5. 完整的 discussion/limitations。

你的專案已經超過這個最低標準（E1–E5 都做了）。如果真的要砍，砍 E4/E5 的細節，保留 E1–E3 和 discussion。

### 17.3 最後一句話

這個專案最重要的是「連結」：把一個嚴謹的量子演算法，連到一個有意義的認知問題，並且誠實地說出模型的限制。只要你能在口頭報告中清楚講出：

- 我們用什麼演算法；
- 我們把它映射到什麼認知問題；
- 我們發現了什麼；
- 我們不能說什麼；

你就已經掌握這個專案的核心了。





---

## 附錄 A：指令與輸出速查表

### A.1 環境

```bash
cd Final/code
mamba env create -f environment.yml
mamba activate qwalk-cognition
python -m pytest -q
```

### A.2 實驗、輸出、圖表

| 實驗 | 指令 | 主要輸出 | 圖 |
|---|---|---|---|
| E1 | `python -m src.experiments --only E1` | `results/raw/E1_scaling.csv`、`results/processed/E1_scaling.json` | `figures/E1_scaling.pdf`、`E1_speedup.pdf` |
| E2 | `python -m src.experiments --only E2` | `E2_marked.csv`、`E2_curves.csv`、`E2_adversarial_torus.csv`、`E2_marked.json` | `figures/E2_success.pdf`、`E2_ht.pdf` |
| E3 | `python -m src.experiments --only E3` | `E3_semantic_metrics.csv`、`E3_semantic_curves.csv`、`E3_semantic.json` | `figures/E3_semantic.pdf` |
| E4 | `python -m src.experiments --only E4` | `E4_metrics.csv`、`E4_choices.csv`、`E4_curves.csv`、`E4_decision.json` | `figures/E4_decision.pdf` |
| E5 | `python -m src.experiments --only E5` | `E5_sweep.csv`、`E5_curves.csv`、`E5_decoherence.json` | `figures/E5_robustness.pdf` |

### A.3 報告

```bash
cd Final/report
tectonic -X compile main.tex
open main.pdf
```

報告圖檔在 `report/figures/`，圖的來源與 caption 在 `report/figures/FIGURE_INDEX.md`。數字整理在 `report/RESULTS_SUMMARY.md`。

### A.4 檔案快速定位

| 你想找… | 去哪裡 |
|---|---|
| 專案計畫與進度 | `ROADMAP.md` |
| 每週紀錄 | `weekly_log.md` |
| 提案 | `proposal/proposal.tex` |
| 報告本文 | `report/main.tex` |
| 報告某一節 | `report/sections/*.tex` |
| 參考文獻 | `report/refs.bib` |
| 報告圖檔 | `report/figures/` |
| 程式環境 | `code/environment.yml` |
| 實驗設定 | `code/configs/base.yaml`、`code/configs/experiments.yaml` |
| 建圖 | `code/src/graphs.py` |
| 古典 walk | `code/src/classical.py` |
| Szegedy walk | `code/src/szegedy.py` |
| AGJK / interpolated walk | `code/src/agjk.py` |
| 語意圖 CTQW/CRW | `code/src/semantic.py` |
| 決策模型 | `code/src/cognitive.py` |
| 雜訊模型 | `code/src/noise.py` |
| 統計指標 | `code/src/metrics.py` |
| 實驗 runner | `code/src/experiments.py` |
| 繪圖 | `code/src/plotting.py` |
| 測試 | `code/tests/` |
| 原始數據 | `code/results/raw/` |
| 整理後數據 | `code/results/processed/` |

### A.5 最後的提醒

- 先讓程式跑得動，再追求漂亮。
- 先確認 sanity checks，再相信大圖。
- 先能用自己的話解釋一個公式，再把它放進報告。
- 先承認限制，再說貢獻。

如果你讀到這裡，你已經比「覺得自己很笨」的時候懂得多很多了。慢慢來，重複讀，親手跑一次，你會越來越清楚。
