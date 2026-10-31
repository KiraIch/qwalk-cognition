# ROADMAP：量子漫步搜尋 × 量子認知 期末專案

> 課程：EE5105 Special Topics in Quantum Information Science（Fall 2026）
> 題目：**Quantum Walk Search for Marked Vertices as a Model of Cognitive Search: From Semantic Memory Retrieval to Multi-Alternative Decision Making**
> 中文題目：**以量子漫步的標記頂點搜尋模型刻畫認知搜尋：從語意記憶提取到多選項決策**
> 版本：v1.0（2026-10-20）
> 狀態：proposal 截止前衝刺版

**目前進度（2026-10-20）**

- [x] 選定 QIS 核心論文：AGJK 2019
- [x] 下載橋樑與終點文獻：Chen 2022、Huang–Busemeyer 2022、Pavone–Faro 2025
- [x] 保留兩篇量子漫步論文：AGJK 2019、Jeffery–Zur 2025
- [ ] 寄信給老師約 meeting
- [x] 完成並送出 proposal（10/21 17:00）
- [x] 建立程式 repo 與 LaTeX 模板（2026-10-20）
- [x] 完成第一張 classical vs quantum scaling 圖（2026-10-20）
- [x] 完成 E2：single / independent / clustered marked vertices 與 $HT^+$ 實驗（2026-10-20）
- [x] 完成 E3：toy semantic graph 的 CTQW vs CRW target activation（2026-10-20）
- [x] 完成 E4：multi-alternative decision 與 option-coupling 實驗（2026-10-20）
- [x] 完成 E5：partial measurement / decoherence sweep（2026-10-20）
- [x] 凍結 E1–E5 figures 並建立 report figure index（2026-10-20）
- [x] 完成 report full draft（26 頁，含 appendix；2026-10-20）
- [x] 完成 `Explain.md` 教學文件（從零解釋論文、程式、報告；2026-10-20）
- [x] 完成 `Result.md` 實驗結果與討論詳解（2026-10-20）

---

## 0. 一句話總結

以 **AGJK 2019 的「在任意圖上尋找 marked vertices 的量子漫步演算法」** 為量子資訊核心，把它映射成**語意網絡上的認知搜尋／多選項決策模型**，再用 **Chen et al. 2022、Huang–Busemeyer 2022、Pavone–Faro 2025** 這條線連到量子認知，最後用數值實驗回答：

> 圖的拓撲、marked-set 的結構（單一／多個／聚集）、以及退相干，如何改變量子漫步相對古典漫步的搜尋優勢？這個優勢在認知上有什麼可檢驗的意義？

---

## 1. 專案定位與課程要求

### 1.1 課程資訊

| 項目 | 內容 |
|---|---|
| 課程 | EE5105 Special Topics in Quantum Information Science |
| 授課教師 | Shih-Han Hung |
| 學期 | Fall 2026 |
| 專案佔比 | 課程總成績 20% |
| 分組 | 最多 2 人 |
| 報告格式 | LaTeX |
| 課程核心主題 | quantum algorithms、quantum walk、query complexity、Hamiltonian simulation、QSVT、learning quantum states |

### 1.2 評分與截止日

| 項目 | 佔專案成績 | 截止日 | 備註 |
|---|---:|---|---|
| Project proposal | 20% | **10/21（三）17:00**（最新公告） | 網站 Project 區塊寫 10/19，提案前先寄信確認 |
| Presentation | 40% | **12/14（一）** | 最後幾週課堂報告 |
| Final paper | 40% | **12/21（一）** | 與期末考同一週，務必提前完成 |

> 重要：公告說 proposal 10/21 截止，但 Project 區塊寫 10/19。**以最新公告為準，並在寄信給老師時順便確認。** 老師要求每組在 proposal 截止前寄信約時間面談。

### 1.3 本專案如何扣住課程核心

本專案不是單純的「量子認知心得報告」。它的骨幹是：

1. **Quantum walk search**：Szegedy walk、marked vertices、hitting time、spectral gap、interpolated walk、quantum fast-forwarding。
2. **Query/time complexity**：為什麼「偵測」marked vertex 只需要 $O(\sqrt{HT})$，但「找到」它更難；多個 marked vertices 時 $HT^+$ 可能遠大於 $HT$。
3. **Hamiltonian simulation / CTQW**：Pavone–Faro 2025 的 continuous-time quantum walk 直接對應課程的 Hamiltonian simulation 與 continuous-time walk。
4. **Open-system / decoherence**：把 partial measurement、dephasing 加進 walk，對應課程中對 noise 與 open system 的討論。

一句話：**QIS 是主體，量子認知是應用與動機；不能反過來。**

> AGJK 正好在老師的 topic list 裡（Quantum walk → Finding marked items by quantum walk [AGJK]），提案時可以直接說「以課程 topic 為核心，延伸到 quantum cognition」。這比自創一個與課程無關的題目安全得多。

---

## 2. 研究問題、假設與貢獻

### 2.1 背景缺口

- 量子漫步搜尋文獻（AGJK、Szegedy、Jeffery–Zur）關心的是**演算法最壞情況複雜度**：給定圖與 marked set，多快能找到目標。
- 量子認知文獻（Busemeyer、Pothos、Chen、Pavone）關心的是**認知現象的過程模型**：反應時間、選擇機率、順序效應、脈絡效應、洞察。
- 兩邊的交集通常只停留在「quantum walk 可以當 evidence accumulator」的比喻，**很少直接把 marked-vertex search 的 $HT$／$HT^+$ 結構映射到多目標認知搜尋與多選項決策**。

本專案的缺口定位：

> 把 AGJK 的 marked-vertex search 當成一個**認知搜尋的 process model**，並利用它對「多個 marked vertices」的細緻分析，去形式化多選項決策中的困難度與脈絡效應。

### 2.2 研究問題

**RQ1（模型映射）**  
如何把 marked-vertex search 映射到語意網絡／決策圖上的認知搜尋？$HT$、$HT^+$、spectral gap、success probability 分別對應到什麼認知量（反應時間、選擇機率、 deliberation speed、信心）？

**RQ2（結構效應）**  
marked set 的數量與排列（單一、多個獨立、多個聚集）如何改變量子 vs 古典的搜尋時間與成功機率？AGJK 的 $HT^+$ 現象是否能提供**多選項決策困難度／脈絡效應**的形式類比？

**RQ3（雜訊效應）**  
partial measurement／decoherence 如何侵蝕量子優勢？是否存在一個「最佳內省／測量強度」，讓成功機率或決策速度最大化？

### 2.3 假設

| 編號 | 假設 | 預期檢驗方式 |
|---|---|---|
| H1 | 在 expansion 好的圖與單一目標下，量子搜尋時間約呈 $\sqrt{HT}$ scaling，並優於古典 | 對 complete graph、cycle、2D grid、hypercube 做 scaling fit |
| H2 | 多個聚集的 marked vertices 會讓 naive quantum search 出現明顯的 $HT^+$ penalty；AGJK 的改進演算法可恢復 $\tilde O(\sqrt{HT})$ | 比較 single / independent / clustered marked sets 的 success probability vs $t$ |
| H3 | 多個 marked sets 的選擇機率與反應時間會隨目標相似度／聚集程度非單調變化，可類比 similarity/attraction effect | 在 3–5 選項圖上掃描選項間距與連通性 |
| H4 | 弱 partial measurement 可能透過抑制破壞性干涉而**改善**成功機率；強測量則破壞量子優勢，存在最佳雜訊強度 | 掃描測量機率 $p$，畫 success probability / search time vs $p$ |

> 注意：H1–H4 是「數值/模型層級」的假設，不是生物物理主張。報告中要明確說明這一點。

### 2.4 預期貢獻

1. **重現** AGJK 的 $\tilde O(\sqrt{HT})$ scaling，至少在 small graphs 上數值驗證。
2. **提出** $HT^+$ 與多選項決策困難度的形式對應，並用數值實驗展示 marked-set clustering 的影響。
3. **建立** 一個可重現的 quantum walk × quantum cognition 模擬框架，包含 classical、quantum、open-system 三種 walk。
4. **批判性討論** 量子認知模型的解釋力與限制：什麼時候 quantum walk 只是數學語言，什麼時候它給出古典模型沒有的可檢驗預測。

### 2.5 範圍與非目標

**In scope**

- AGJK 的理論整理與數值重現。
- Classical random walk vs Szegedy/AGJK quantum walk。
- 小型 synthetic graphs + 小型 semantic graph。
- 多 marked vertices、partial measurement/decoherence。
- 認知映射與質性/數值比較。

**Out of scope（除非時間充裕）**

- 證明新的 quantum walk 定理。
- 真人認知實驗。
- 真實量子硬體（可選 stretch）。
- 完整量子認知文獻回顧。
- 宣稱「大腦是量子電腦」或「認知有量子 speedup」。

---

## 3. 文獻地圖

### 3.1 核心論文（必讀）

| 論文 | 角色 | 必讀段落 | 產出 |
|---|---|---|---|
| **AGJK 2019**, *Quadratic speedup for finding marked vertices by quantum walks*（`1903.07493v1.pdf`） | QIS 核心 | Abstract、Sec. 1–2、Sec. 3（HT+ gap）、Sec. 4（兩個演算法） | 理論筆記、演算法 pseudocode、scaling 實驗 |
| **Chen, Ferro & Sornette 2022**, *On the use of discrete-time quantum walks in decision theory*（PLoS ONE） | 橋樑：DTQW → evidence accumulation | Sec. 2–4、partial measurement/decoherence 段 | 認知映射的動機與測量模型 |
| **Huang & Busemeyer 2022**, *A quantum walk framework for multialternative decision making*（ICCM） | 橋樑：多選項量子漫步 | 全部（只有 2 頁） | multi-alternative 的 Hamiltonian / stopping condition |
| **Pavone & Faro 2025**, *Modeling the Emergence of Insight via Quantum Interference on Semantic Graphs*（Mathematics） | 主要終點：CTQW on semantic graphs | Sec. 2–5、Sec. 8 | 語意圖實驗設計、CTQW vs CRW 指標、Colab/code |

### 3.2 背景與延伸（選讀）

| 論文 | 用途 |
|---|---|
| Pothos & Busemeyer 2022, *Quantum Cognition*, Annual Review of Psychology | 量子認知總論；寫 introduction 必引 |
| Pothos & Busemeyer 2025, *An overview of the quantum cognition research program*, Psychonomic Bulletin & Review | 最新 review；批判與 limitation 必引 |
| Busemeyer & Bruza 2024, *Quantum Models of Cognition and Decision* (2nd ed.) | 教科書；數學基礎與模型分類 |
| Zhang & Busemeyer 2021, *A Quantum Walk Model for Idea Propagation in Social Network and Group Decision Making*, Entropy | graph walk → group decision；可當延伸 |
| Epping, Kvam, Pleskac & Busemeyer 2023, *Open system model of choice and response time*, J. Choice Modelling | open-system / decoherence 的認知版本 |
| Widdows, Rani & Pothos 2023, *Quantum Circuit Components for Cognitive Decision-Making*, Entropy | 量子電路實作；stretch goal |
| Huang, Busemeyer, Ebelt & Pothos 2024, *The Quantum Sequential Sampler*, Psychological Review | 量子機率 + sequential sampling；討論用 |
| Jeffery & Zur 2025, *Multidimensional Quantum Walks, with Application to k-Distinctness*（`2208.13492v4.pdf`） | 可選技術延伸；不要當主軸 |
| Tsuchiya et al. 2025, *Quantum-like Qualia hypothesis*, Frontiers in Psychology | 可選；若延伸到 perception/consciousness |

### 3.3 閱讀策略

- **AGJK**：先讀 Abstract + Intro 的 problem statement，再讀 Sec. 3 的 $HT^+$ 反例，最後讀 Sec. 4 的兩個演算法。不要一開始就試圖完全看懂所有 spectral lemma。
- **Chen 2022**：重點是 DTQW 的 formalism、evidence accumulation 的映射、partial measurement 如何造成 decoherence。
- **Huang–Busemeyer 2022**：2 頁而已，直接抓 Hamiltonian、initial state、stopping condition 三個元件。
- **Pavone–Faro 2025**：先看 Fig. 1 與 Sec. 8 的實驗設置，再看 Sec. 4 的 transient amplification 條件。程式碼可直接用來做 semantic graph 實驗。

---

## 4. 理論基礎與必推導內容

### 4.1 Classical random walk 與 hitting time

給定圖 $G=(V,E)$、轉移矩陣 $P$、stationary distribution $\pi$、marked set $M\subset V$。

- Hitting time：
  $$
  HT = \mathbb{E}_{v\sim \pi}\left[\min\{t\ge 0: X_t\in M\}\right].
  $$
- 對 $i\notin M$，令 $h_i$ 為從 $i$ 出發的 expected hitting time，則
  $$
  h_i = 1 + \sum_{j} P_{ij} h_j,\qquad h_i=0\ \text{for } i\in M.
  $$
  可解線性系統 $(I-P_{M^c,M^c})h = \mathbf{1}$。
- 簡單圖的 scaling（報告中要推或引用）：
  - complete graph：$HT=\Theta(N)$；
  - cycle：$HT=\Theta(N^2)$；
  - 2D grid（$N=L^2$）：$HT=\Theta(N\log N)$。

### 4.2 Szegedy quantum walk（AGJK 的寫法）

AGJK 使用的 quantum walk operator 如下（register convention 與論文一致）：

- 令 $V(P)$ 滿足
  $$
  V(P)|\bar 0\rangle|x\rangle = \sum_y \sqrt{P_{xy}}\,|y,x\rangle.
  $$
- 令 $\mathrm{Shift}$ 為 $|x,y\rangle\mapsto |y,x\rangle$。
- 令 $\mathrm{Ref} = (2|\bar 0\rangle\langle\bar 0|-I)\otimes I$。
- 定義
  $$
  W(P)=V^\dagger(P)\,\mathrm{Shift}\,V(P)\,\mathrm{Ref}.
  $$

其 discriminant matrix 為
$$
D_{xy}=\sqrt{P_{xy}P^*_{yx}},
$$
且
$$
\langle\bar 0|\langle x|W(P)|\bar 0\rangle|y\rangle = D_{xy}.
$$
對 reversible $P$，有
$$
D=\mathrm{diag}(\pi)^{1/2}\,P\,\mathrm{diag}(\pi)^{-1/2}.
$$

要理解的點：

- $W(P)$ 是 unitary；它的 spectrum 與 $D$（以及 reversible $P$）的 spectrum 有對應。
- Szegedy 的 detection algorithm 可在 $O(1/\sqrt{\delta})$ 或 $O(\sqrt{HT})$ 內**偵測** marked vertex 的存在。
- **Detection ≠ finding**：量測最終狀態不一定會給你 marked vertex，這是 AGJK 的出發點。

### 4.3 AGJK：finding marked vertices 與 $HT^+$

AGJK 的核心問題：

> 給定任意圖、任意 marked set，能不能用量子漫步**找到**一個 marked vertex，且時間是 $\tilde O(\sqrt{HT})$？

關鍵概念：

- **Extended hitting time $HT^+$**：由 $P$ 的特徵值/特徵向量修改而來。若 $D(s)$ 的特徵分解為 $\sum_k \lambda_k(s)|v_k(s)\rangle\langle v_k(s)|$，且 $p_M=\sum_{x\in M}\pi_x$，則
  $$
  HT(s)=\frac{1}{1-p_M}\sum_{k=1}^{n-1}\frac{|\langle v_k(s)|\sqrt{\pi_U}\rangle|^2}{1-\lambda_k(s)},
  \qquad
  HT^+=\lim_{s\to 1}HT(s).
  $$
  若只有一個 marked vertex，$HT^+=HT$；但有多個 marked vertices 時，$HT^+$ 可能遠大於 $HT$。
- 論文 Sec. 3 構造一個 $N\times N$ torus 的例子，使得 $HT^+=\Omega(N^2)$ 但 $HT=O(f(N))$，$f$ 可以任意慢地成長。這說明舊演算法（KMOR）在多 marked vertices 時可能嚴重次優。
- 論文提出兩個演算法：
  1. **較簡單的演算法**：跑 interpolated walk $O(\sqrt{HT})$ 步；作者以數值實驗提出 Conjecture 3，猜測成功機率為 $\Omega(1)$。
  2. **證明的演算法**：結合 interpolated walk 與 quantum fast-forwarding（Apers–Sarlette），證明 $\tilde O(\sqrt{HT})$ 找到 marked vertex（Theorem 5）。
- 你要在報告中清楚區分：
  - 你**數值驗證**的是哪一個版本（建議先做 Conjecture 3 的數值版）。
  - 你**引用**的是 Theorem 5 的理論保證。
  - log factor 與 $HT^+$ 的角色。

### 4.4 Interpolated walk 與 quantum fast-forwarding

- Interpolated walk 在原始 walk $P$ 與 absorbing walk $P'$ 之間插值：
  $$
  P(s)=(1-s)P+sP',
  \qquad
  P'=\begin{pmatrix}P_{UU}&P_{UM}\\0&I\end{pmatrix},
  $$
  參數 $s$ 控制 marked vertex 的「停留／吸收」強度。
- Quantum fast-forwarding 讓 $t$ 步 classical walk 的某些性質，用 $O(\sqrt{t})$ 步 quantum walk 來模擬；但成功機率可能很小，需要調整插值參數。
- 報告中不需要完整重證 Theorem 5，但必須：
  - 寫出 interpolated walk 的定義；
  - 解釋為什麼它比單純跑 Szegedy walk 更容易「找到」；
  - 用數值實驗展示 $s$ 與成功機率的關係。

### 4.5 認知映射

把圖 $G=(V,E)$ 解讀成：

- $V$：概念、證據狀態、或選項；
- $E$：語意關聯、注意力轉移、或證據累積路徑；
- marked set $M$：目標記憶、被選擇的選項、或決策邊界；
- 初始態 $|\psi_0\rangle$：cue／問題／初始注意力分布；
- 演化 $U(t)$： deliberation；
- 量測／吸收：做出決定；
- success probability $p_M(t)=\|\Pi_M U(t)|\psi_0\rangle\|^2$：在時間 $t$ 已找到目標的機率；
- hitting time $T=\min\{t:p_M(t)\ge p^*\}$：反應時間；
- 多個 marked sets $M_1,\dots,M_k$：多選項；選擇機率 $P_i=\|\Pi_{M_i}U(T)|\psi_0\rangle\|^2$。

**必須寫清楚的建模假設：**

1. 這是一個 **process-level / mathematical** 模型，不是生物物理模型。
2. 量子漫步的干涉對應「多條證據路徑的干涉」，不是「大腦真的在跑量子電路」。
3. 古典 baseline 是 Markov random walk；量子模型是它的 unitary 類比。
4. 所有認知量（RT、choice probability）都是從 walk 的統計量**定義**出來的，不是直接 fit 真人資料。

### 4.6 Decoherence / partial measurement

建議先實作最簡單的模型：

- 每一步以機率 $p$ 對 position basis 做 projective measurement（或 partial dephasing），以機率 $1-p$ 做 unitary evolution。
- $p=0$：純量子 walk；$p=1$：每步都量測，行為接近古典 random walk。
- 觀察：
  - success probability vs $p$；
  - search time vs $p$；
  - 是否出現非單調的「decoherence-assisted search」。

若時間允許，再升級成 Lindblad master equation 或 open-system model（Epping et al. 2023）。

### 4.7 必推導／必整理清單

- [ ] $P$ 的 reversible / detailed balance 條件。
- [ ] Szegedy walk 的定義與 unitarity。
- [ ] Szegedy spectral lemma（至少陳述，不必完整證明）。
- [ ] $HT$ 與 spectral gap 的關係（陳述）。
- [ ] AGJK 的 $HT^+$ 定義與「多 marked vertices 可能很大」的例子。
- [ ] Interpolated walk 的定義。
- [ ] Quantum fast-forwarding 的一句話直覺。
- [ ] 認知映射的變數對照表。
- [ ] Partial measurement 的更新規則。

---

## 5. 實驗設計

### 5.1 圖的家族

**Synthetic graphs（必做）**

| 圖 | 大小 | 用途 |
|---|---|---|
| Complete graph $K_N$ | $N=8,16,32,64$ | sanity check；$HT=\Theta(N)$ |
| Cycle $C_N$ | $N=8,16,32,64$ | 低 expansion；$HT=\Theta(N^2)$ |
| 2D grid $L\times L$ | $L=4,6,8,10$ | 課程標準例子；$HT=\Theta(N\log N)$ |
| Hypercube $Q_d$ | $d=3,4,5,6$ | 高對稱、spectral gap 好 |
| Random regular graph | $N=32,64$，degree 3–4 | 非平凡拓撲 |
| Barbell / clustered graph | $N=32,64$ | 兩個社群，測試 marked-set clustering |

**Semantic graphs（必做一個小型）**

- 手建 toy semantic graph（10–20 節點）：例如動物、交通工具、樂器等概念，邊代表語意關聯。
- 進階：ConceptNet k-hop subgraph（可參考 Pavone–Faro 2025 的 pipeline）。
- 目標概念：選一個 target，或一組 semantically related targets。

**Decision graphs（should）**

- 2AFC：line graph，兩端為 absorbing boundaries。
- 3–5 選項：star-like 或 multi-branch graph，每個 branch 終點是一個 option。
- 用選項間距／branch 連通性來控制 similarity。

### 5.2 Marked-set 設定

| 設定 | 說明 | 對應認知情境 |
|---|---|---|
| Single marked vertex | 只有一個目標 | 單一目標記憶提取 |
| Multiple independent | 多個分散的目標 | 多個無關的候選記憶 |
| Clustered marked vertices | 多個目標集中在同一社群 | 多個相似選項／語意相近的記憶 |
| Absorbing boundary | 一組 boundary states | 決策門檻 |
| Multiple option sets | $M_1,\dots,M_k$ | 多選項決策 |

### 5.3 指標

**Quantum walk 指標**

- $T_q$：達到 success probability $\ge 1/2$ 的最少步數（或最佳步數）。
- $p_{\max}$：時間演化中最大的 success probability。
- $T_{\text{opt}}$：$p_{\max}$ 出現的時間。
- Spectral gap $\delta$。
- $HT^+$ proxy：若完整計算太複雜，至少記錄「多 marked vertices 下的 effective search time」與「success probability 曲線的退化」。
- Scaling exponent $\alpha$：由 $T_q\sim N^\alpha$ 拟合。

**Classical 指標**

- $T_c$：classical expected hitting time（線性解或 Monte Carlo）。
- $p_c(t)$：classical 在 $t$ 步內 hit 的機率。
- Speedup $S=T_c/T_q$。

**Cognitive 指標**

- Choice probability $P_i$。
- Mean RT / RT distribution。
- 順序效應：改變選項呈現順序（若模型允許）。
- 脈絡效應：改變選項相似度／graph 結構。

**Noise 指標**

- $p_{\text{success}}(p)$、$T_q(p)$、$S(p)$。
- 最佳測量強度 $p^*=\arg\max p_{\text{success}}$（若存在）。

### 5.4 實驗矩陣

| ID | 實驗 | 圖 | Marked set | Noise | 優先級 |
|---|---|---|---|---|---|
| E1 | Classical vs quantum scaling | $K_N, C_N, \text{grid}, Q_d$ | single | 無 | Must |
| E2 | Multiple marked vertices | 2D grid, clustered graph | single / independent / clustered | 無 | Must |
| E3 | Toy semantic search | toy semantic graph | single target | 無 | Must |
| E4 | Multi-alternative decision | multi-branch graph | $M_1,\dots,M_k$ | 無 | Should |
| E5 | Decoherence sweep | 2D grid + toy graph | single / multiple | $p\in[0,0.5]$ | Should |
| E6 | ConceptNet / RAT / Candle | ConceptNet subgraph | target concept | 無 | Stretch |
| E7 | Multidimensional walk | 依 Jeffery–Zur | 多維 marked set | 無 | Optional |
| E8 | Circuit simulation / hardware | 小圖 | single | 無 | Optional |

### 5.5 Semantic graph 實驗細節

1. 建圖：節點 = 概念，邊權重 = 語意相似度或共現次數。
2. 正規化：使用 normalized adjacency 或 normalized Laplacian（參考 Pavone–Faro 2025）。
3. 初始態：uniform superposition 或 cue node。
4. 演化：CTQW $U(t)=e^{-iHt}$，$H$ 由 graph Laplacian/adjacency 定義。
5. 比較：CTQW vs classical diffusion（CRW），在相同初始態與 spectral time normalization 下比較。
6. 指標：target AUC、peak probability、time-of-peak、entropy、coverage、expected radius。
7. 若使用 ConceptNet，記錄 k-hop、節點數、邊數、前處理步驟與隨機種子。

### 5.6 Decision 實驗細節

- 2AFC：line graph，左右兩端為 absorbing boundaries；初始態在中間。
- 多選項：每個 option 是一個 marked set；分支長度／連通性控制 similarity。
- 選擇機率：在固定 decision time $T$ 或首次達到門檻時，量測各 $M_i$ 的機率。
- 反應時間：首次達到門檻的時間。
- 預期：當兩個選項的 branch 高度相連（相似）時，會出現類似 attraction/similarity effect 的非單調選擇機率。

### 5.7 驗證與 sanity checks

- [ ] 轉移矩陣每列和為 1。
- [ ] 量子演化保持 norm = 1。
- [ ] $p=1$ 的 partial measurement 極限接近 classical random walk。
- [ ] Complete graph 的 $HT$ 與解析值一致。
- [ ] Cycle 的 $HT$ scaling 接近 $N^2$。
- [ ] 2D grid 的 $HT$ scaling 接近 $N\log N$。
- [ ] 多個 random seeds 的誤差條。
- [ ] 所有圖的 label 固定，避免同構重排造成假差異。

### 5.8 可選：真實量子硬體

- 只在時間充裕時做。
- 使用 Qiskit / Cirq / IonQ 模擬小圖（N ≤ 8）。
- 參考 Widdows et al. 2023 的 quantum circuit components。
- 重點不是跑大電路，而是展示「認知模型 → 電路」的可行性。

---

## 6. 程式實作計畫

### 6.1 建議 repo 結構

```text
Final/
  ROADMAP.md
  proposal/
    proposal.tex
    proposal.pdf
  report/
    main.tex
    refs.bib
    sections/
    figures/
  slides/
    slides.tex
    slides.pdf
  code/
    README.md
    requirements.txt
    configs/
      base.yaml
      experiments.yaml
    src/
      graphs.py
      classical.py
      szegedy.py
      agjk.py
      cognitive.py
      noise.py
      metrics.py
      experiments.py
      plotting.py
    tests/
      test_classical.py
      test_quantum.py
      test_metrics.py
    notebooks/
      01_sanity_checks.ipynb
      02_scaling.ipynb
      03_cognitive_graphs.ipynb
      04_decoherence.ipynb
    results/
      raw/
      processed/
    figures/
```

### 6.2 模組職責

| 模組 | 職責 |
|---|---|
| `graphs.py` | 生成 synthetic graphs、semantic graphs、decision graphs；回傳 adjacency/transition matrix、marked set |
| `classical.py` | stationary distribution、hitting time（線性解 + Monte Carlo）、classical diffusion |
| `szegedy.py` | Szegedy walk 的 $W$、spectral gap、success probability |
| `agjk.py` | interpolated walk、AGJK 搜尋流程、$HT^+$ proxy |
| `cognitive.py` | 認知映射、choice probability、RT、multi-alternative |
| `noise.py` | partial measurement、dephasing、open-system 簡化模型 |
| `metrics.py` | scaling fit、confidence interval、AUC、entropy、coverage |
| `experiments.py` | 讀 config、跑 experiment matrix、存 CSV |
| `plotting.py` | 統一的 figure style、輸出 PDF/PNG |

### 6.3 關鍵 pseudocode

**Classical hitting time（線性解）**

```python
# h_i = 0 for i in M
# h_i = 1 + sum_j P_ij h_j for i not in M
A = I - P[free, free]
b = ones(len(free))
h_free = solve(A, b)
```

**Quantum search（數值版）**

```python
psi = initial_state
best_p = 0
best_t = 0
for t in range(T_max):
    p = norm(projector_M @ psi)**2
    if p > best_p:
        best_p = p
        best_t = t
    psi = W @ psi
```

**Partial measurement**

```python
for t in range(T_max):
    if rng.random() < p:
        outcome = sample(position_basis, prob=abs(psi)**2)
        psi = basis_state(outcome)
    psi = W @ psi
```

**AGJK interpolated walk**

```python
# 依論文 Sec. 4 定義 W(s)
# 先實作 Conjecture 3 的數值版本：
for s in s_grid:
    W_s = interpolated_walk(P, M, s)
    p_max, t_opt = run_search(W_s, initial_state)
    record(s, p_max, t_opt)
```

> 注意：不要憑記憶硬寫 AGJK 的公式；以論文 Sec. 4 的定義為準，並在程式註解標明 equation number。

### 6.4 效能與可重現性

- 使用 `numpy` dense matrix 即可處理 $N\le 128$ 的 Szegedy walk（維度 $2N$）。
- 更大的圖用 `scipy.sparse`；CTQW 用 `scipy.sparse.linalg.expm_multiply`。
- 所有實驗固定 random seed；config 寫入 YAML。
- 每次實驗輸出：
  - `results/raw/<experiment_id>.csv`
  - `results/processed/<experiment_id>.json`
  - `figures/<experiment_id>.pdf`
- 在 `README.md` 寫清楚「如何重現每一張圖」。

### 6.5 測試

- `test_classical.py`：完整圖 hitting time、cycle scaling、stationary distribution。
- `test_quantum.py`：unitarity、norm preservation、$p=1$ 極限。
- `test_metrics.py`：AUC、entropy、scaling fit 的 small-case 驗證。
- 每個測試都要能在 1 分鐘內跑完。

---

## 7. 時程規劃

### 7.1 總覽

| 週次 | 日期 | 主要任務 | 里程碑 | 若落後怎麼辦 |
|---|---|---|---|---|
| Week 0 | 10/20–10/21 | 定題、寄信約老師、寫 proposal、建 repo | **10/21 proposal 送出** | 先送最小版：題目 + RQ + 方法 + 時程 |
| Week 1 | 10/22–10/28 | 讀 AGJK Sec. 1–2；實作 classical walk + Szegedy walk；sanity checks | M1：classical/quantum 基礎 code 可跑 | 只做 complete graph + cycle |
| Week 2 | 10/29–11/04 | 實作 AGJK interpolated walk；重現 scaling；讀 Chen 2022 | M2：$\sqrt{HT}$ scaling 圖 | 用 Szegedy + 數值 interpolation，不追 Theorem 5 |
| Week 3 | 11/05–11/11 | 建 toy semantic graph；實作認知映射；讀 Huang 2022 | M3：semantic search 實驗 | 先用手建 10 節點圖，不碰 ConceptNet |
| Week 4 | 11/12–11/18 | 多 marked vertices / clustering；$HT^+$ 實驗；讀 Pavone–Faro | M4：multiple marked 結果 | 只做 single vs clustered 兩組 |
| Week 5 | 11/19–11/25 | partial measurement/decoherence；open-system 比較 | M5：decoherence sweep | 只做 $p=0,0.1,0.5,1$ 四點 |
| Week 6 | 11/26–12/02 | 完成所有實驗；敏感度分析；產 figures | M6：figures freeze | 砍 E6–E8，保 E1–E5 |
| Week 7 | 12/03–12/09 | 寫 theory/model/results/discussion；完成 full draft | M7：full draft | 先寫 results，再補 intro |
| Week 8 | 12/10–12/13 | 修稿、做 slides、排練 | M8：slides 完成 | 只練 2 次也要練 |
| Week 9 | 12/14 | **Presentation** | — | — |
| Week 10 | 12/15–12/20 | 吸收回饋、修 final paper、檢查 references/格式 | M9：final paper 完成 | 12/20 前務必上傳 |
| Week 11 | 12/21 | **Final paper 截止** | — | 與期末考同週，提前交 |

### 7.2 前七天每日計畫（10/20–10/26）

**10/20（二）**

- [ ] 確認題目與兩位組員分工（若 solo，確認範圍）。
- [ ] 寄信給老師約 meeting（見 §13 範本）。
- [ ] 建立 `Final/proposal`、`Final/code`、`Final/report` 資料夾。
- [ ] 讀 AGJK Abstract + Sec. 1，寫 1 頁 problem statement。
- [ ] 寫 proposal 初稿（1–2 頁）。

**10/21（三）**

- [ ] 早上和老師/組員確認 scope。
- [ ] 完稿 proposal，檢查 references。
- [ ] **17:00 前送出。**

**10/22（四）**

- [ ] 讀 AGJK Sec. 2；整理 Markov chain / hitting time 定義。
- [ ] 實作 `graphs.py` + `classical.py`。
- [ ] 在 complete graph 上驗證 $HT$。

**10/23（五）**

- [ ] 實作 `szegedy.py` 的 $W$。
- [ ] 驗證 unitarity 與 norm preservation。
- [ ] 在 cycle 上跑 detection probability。

**10/24（六）**

- [ ] 讀 AGJK Sec. 3；整理 $HT^+$ 反例。
- [ ] 在 2D grid 上跑 classical vs Szegedy。
- [ ] 畫第一張 scaling 圖。

**10/25（日）**

- [ ] 讀 AGJK Sec. 4；寫 interpolated walk 筆記。
- [ ] 開始實作 `agjk.py` 的簡化版。
- [ ] 記錄所有假設與未解問題。

**10/26（一）**

- [ ] 週檢討：M1 是否達成？
- [ ] 若未達成，砍範圍（只保留 E1）。
- [ ] 更新 ROADMAP 的進度。

### 7.3 里程碑定義

| 里程碑 | 完成標準 |
|---|---|
| M0 | proposal 送出，老師確認 scope |
| M1 | classical + Szegedy code 可跑，通過 sanity checks |
| M2 | 至少兩個 graph family 的 scaling 圖 |
| M3 | toy semantic graph 的 classical vs quantum 結果 |
| M4 | single / multiple / clustered marked sets 的比較圖 |
| M5 | decoherence sweep 圖 |
| M6 | 所有 main figures 凍結 |
| M7 | full draft 完成（含 references） |
| M8 | slides 完成並排練 |
| M9 | final paper 上傳 |

### 7.4 最低完成標準（fallback）

如果時間不夠，**一定要有**：

1. AGJK/Szegedy 的理論整理。
2. Complete graph + 2D grid 的 classical vs quantum scaling。
3. 一個 toy semantic graph 的認知映射。
4. 一張 multiple marked vertices 的比較圖。
5. 完整的 discussion/limitations。

**可以砍**：ConceptNet、multi-alternative、decoherence、硬體、Jeffery–Zur。

---

## 8. 書面報告大綱

### 8.1 結構與頁數預算

> 課程沒有明定頁數；建議主文 10–12 頁，附錄 2–4 頁。以老師公告為準。

| 章節 | 頁數 | 內容 |
|---|---:|---|
| Abstract | 0.3 | 問題、方法、主要結果、貢獻 |
| 1 Introduction | 1.0–1.5 | 量子認知動機、quantum walk、research questions |
| 2 Background | 1.5–2.0 | classical/quantum walk、hitting time、quantum cognition |
| 3 Theory | 2.0–3.0 | Szegedy、AGJK、$HT^+$、interpolated walk、fast-forwarding |
| 4 Cognitive Model | 1.5–2.0 | graph mapping、choice/RT 定義、multi-alternative |
| 5 Methods | 1.0–1.5 | graphs、metrics、noise model、implementation |
| 6 Results | 2.0–3.0 | scaling、multiple marked、semantic graph、decoherence |
| 7 Discussion | 1.0–1.5 | 解釋、與文獻比較、限制、可檢驗預測 |
| 8 Conclusion | 0.3–0.5 | 總結與 future work |
| References | 1.0–2.0 | 10–20 篇 |
| Appendix | 2.0–4.0 | 推導、額外圖、程式細節 |

### 8.2 圖表規劃

| 圖/表 | 內容 | 章節 |
|---|---|---|
| Fig. 1 | 三層架構圖：quantum walk search → cognitive graph → quantum cognition | Introduction |
| Fig. 2 | Szegedy walk / marked vertices 示意圖 | Background |
| Fig. 3 | Classical vs quantum scaling（complete/cycle/grid） | Results |
| Fig. 4 | Single vs multiple vs clustered marked vertices 的 success probability | Results |
| Fig. 5 | Toy semantic graph 與 target activation | Results |
| Fig. 6 | Decoherence sweep：success probability / search time vs $p$ | Results |
| Fig. 7 | Multi-alternative choice probability / RT | Results（若有） |
| Table 1 | 文獻對照：paper / model / cognitive phenomenon | Background |
| Table 2 | 實驗參數與 graph families | Methods |
| Table 3 | Scaling exponents 與 speedup | Results |
| Table 4 | 與 quantum cognition 文獻的 qualitative comparison | Discussion |

### 8.3 寫作順序

1. **Methods + Results**：先把做過的事寫清楚，附上 figures。
2. **Theory**：把 Szegedy/AGJK 的定義與定理整理好。
3. **Introduction + Discussion**：最後寫，確保前後呼應。
4. **Abstract + Conclusion**：最後最後寫。
5. **References + Appendix**：用 BibTeX，檢查 DOI。

### 8.4 LaTeX / repo 檢查清單

- [ ] `main.tex` 可編譯，無 overfull hbox 嚴重問題。
- [ ] `refs.bib` 所有引用都有對應條目。
- [ ] Figure 使用向量格式（PDF），不要貼 screenshot。
- [ ] 每個 figure 在文中都有引用與解釋。
- [ ] 數字與表格的誤差條/單位清楚。
- [ ] 程式碼與數據有 README。
- [ ] 若有使用 AI，於 AI disclosure section 說明。

### 8.5 AI disclosure

課程規定：若使用 AI 工具，必須揭露模型與使用方式，且所有內容必須基於自己的理解。建議在 final paper 加一節：

> **AI Tool Usage**  
> We used [model name] for [coding assistance / LaTeX formatting / literature search]. All technical derivations, experiment design, and interpretation were verified by the authors. The AI tool was not used to generate research results or citations without verification.

---

## 9. 口頭報告大綱

### 9.1 Slide plan（15–18 分鐘）

| Slide | 內容 | 時間 |
|---|---|---:|
| 1 | Title + group + one-sentence takeaway | 0.5 min |
| 2 | Motivation：quantum cognition 與 quantum walk 的接點 | 1.5 min |
| 3 | Research questions 與 contributions | 1.0 min |
| 4 | Classical walk / hitting time / marked vertices | 2.0 min |
| 5 | Szegedy walk 與 detection vs finding | 2.0 min |
| 6 | AGJK：$HT^+$、interpolated walk、fast-forwarding | 2.5 min |
| 7 | Cognitive mapping：graph / marked set / RT / choice | 2.0 min |
| 8 | Experimental setup：graphs、metrics、noise | 1.5 min |
| 9 | Results 1：scaling | 2.0 min |
| 10 | Results 2：multiple marked / clustering | 2.0 min |
| 11 | Results 3：semantic graph / decoherence | 2.0 min |
| 12 | Discussion：what it explains, what it doesn't | 1.5 min |
| 13 | Limitations 與 future work | 1.0 min |
| 14 | Conclusion + references | 0.5 min |

### 9.2 報告時間控制

- 15 分鐘版：砍掉 slide 7 的細節、slide 11 只留一張圖。
- 18 分鐘版：完整。
- 問答準備 5 分鐘。

### 9.3 預期問答

**Q1：量子認知是不是說大腦是量子電腦？**  
A：不是。quantum cognition 用的是量子機率/Hilbert space 的數學結構，不是生物物理主張。我們的模型是 process-level model。

**Q2：為什麼選 AGJK，而不是一般的 quantum cognition 論文？**  
A：因為這是 QIS 課程，核心必須是 quantum algorithm。AGJK 的 marked-vertex search 正好提供一個嚴謹的 QIS 骨幹，而它的多 marked vertices 結構可以映射到多選項決策。

**Q3：這篇論文的貢獻是什麼？**  
A：重現 AGJK 的 scaling；把 $HT^+$ 映射到多目標認知搜尋的困難度；用 semantic graph 與 decoherence 實驗展示量子認知模型的解釋力與限制。

**Q4：為什麼沒有真人實驗？**  
A：這是 proof-of-concept / numerical study；真人實驗是 future work。我們的重點是建立可檢驗的 model-level predictions。

**Q5：量子優勢在認知上有意義嗎？**  
A：演算法層面上有 $\sqrt{HT}$ 的優勢；但是否能在大腦中實現是另一個問題。我們的討論會區分 algorithmic advantage 與 biological plausibility。

**Q6：為什麼用 CTQW 又用 DTQW？**  
A：AGJK 是 discrete-time Szegedy walk；Pavone–Faro 是 continuous-time walk。我們會明確區分兩者，並在相同時間正規化下比較，不混用。

**Q7：$HT^+$ 到底是什麼？**  
A：它是 AGJK 定義的 extended hitting time，由 Markov chain 的特徵值/特徵向量修改而來；多個 marked vertices 時可能遠大於 $HT$。我們會用數值 proxy 與 success probability 曲線來呈現它的影響。

### 9.4 排練檢查清單

- [ ] 15 分鐘內講完（不含 Q&A）。
- [ ] 每張圖都有一句話結論。
- [ ] 不看稿也能講出 RQ、方法、主要結果。
- [ ] 準備好 Q1–Q7 的答案。
- [ ] 檢查字體大小（投影機可讀）。
- [ ] 準備 backup slides：$HT^+$ 定義、額外 scaling、程式架構。

---

## 10. 風險管理

| 風險 | 機率 | 影響 | 緩解策略 |
|---|---|---|---|
| AGJK 的 Theorem 5 太難實作 | 高 | 高 | 只數值驗證 Conjecture 3；Theorem 5 用引用與直覺解釋 |
| 多 marked vertices 的 $HT^+$ 計算複雜 | 中 | 中 | 用 success probability vs $t$ 與 effective search time 代替完整 $HT^+$ |
| Semantic graph 資料太髒 | 中 | 中 | 先用手建 toy graph；ConceptNet 只當 stretch |
| 沒有真人資料，被質疑不夠「認知」 | 中 | 中 | 強調 process-level model 與 qualitative predictions；引用 quantum cognition 文獻支撐 |
| 專案範圍太大 | 高 | 高 | 以 E1–E3 為 must，E4–E8 為 should/stretch |
| 時間不足 | 高 | 高 | 依 §7.4 fallback，優先保 theory + scaling + one cognitive experiment |
| 組員協作問題 | 低 | 中 | 一週兩次 sync；用 GitHub/Notion 分工 |
| 引用錯誤或幻覺 | 中 | 高 | 每篇引用都開 PDF 確認；用 DOI；不要憑記憶寫 bibliographic data |
| 過度宣稱量子優勢 | 中 | 高 | 在 discussion 明確區分 algorithmic vs biological；加 limitation section |

### 10.1 Scope creep 控制

每當想加新實驗，先問：

1. 它是否直接回答 RQ1–RQ3？
2. 它是否能在 3 天內完成？
3. 它是否會影響 main figures 的 deadline？

如果答案是否，放進 future work，不要做。

### 10.2 技術風險的 fallback

- **Interpolated walk 實作卡住**：先用 Szegedy walk + 手動調整 measurement time，展示 scaling；把 AGJK 的演算法當理論背景。
- **CTQW 太大**：限制 $N\le 64$；用 sparse matrix。
- **ConceptNet pipeline 卡住**：改用手建 15 節點 semantic graph。
- **Decoherence 模型太複雜**：只做 projective measurement with probability $p$，不做 Lindblad。

---

## 11. 交付物清單

### 11.1 課程要求

- [ ] Proposal（10/21 17:00 前）
- [ ] Presentation slides（12/14）
- [ ] Final paper PDF（12/21）
- [ ] LaTeX source
- [ ] 所有 figures 的原始檔

### 11.2 專案內部

- [ ] `ROADMAP.md`（本文件）
- [ ] `proposal/proposal.pdf`
- [ ] `report/main.pdf`
- [ ] `slides/slides.pdf`
- [ ] `code/README.md`
- [ ] `code/requirements.txt`
- [ ] `code/src/` 全部模組
- [ ] `code/tests/` 全部測試
- [ ] `results/raw/` 實驗數據
- [ ] `figures/` 最終圖檔
- [ ] `refs.bib`
- [ ] AI disclosure（若有使用）

### 11.3 送出前 check

- [ ] PDF 可以打開，頁碼正確。
- [ ] 所有圖表在文中被引用。
- [ ] 所有引用在 reference list 中。
- [ ] 沒有未定義的縮寫。
- [ ] 沒有 “TODO” 或 placeholder。
- [ ] 程式碼可在乾淨環境重現至少一張 main figure。
- [ ] 檔案命名一致，沒有空格或奇怪字元。

---

## 12. 參考文獻

### 12.1 核心

1. A. Ambainis, A. Gilyén, S. Jeffery, M. Kokainis, “Quadratic speedup for finding marked vertices by quantum walks,” arXiv:1903.07493 (2019).
2. M. Chen, G. M. Ferro, D. Sornette, “On the use of discrete-time quantum walks in decision theory,” *PLoS ONE* 17(8), e0273551 (2022). DOI: 10.1371/journal.pone.0273551.
3. J. Huang, J. R. Busemeyer, “A quantum walk framework for multialternative decision making,” ICCM 2022. DOI: 10.31234/osf.io/hmv4a.
4. A. Pavone, S. Faro, “Modeling the Emergence of Insight via Quantum Interference on Semantic Graphs,” *Mathematics* 13(19), 3171 (2025). DOI: 10.3390/math13193171.

### 12.2 背景與延伸

5. E. M. Pothos, J. R. Busemeyer, “Quantum Cognition,” *Annual Review of Psychology* 73, 749–778 (2022). DOI: 10.1146/annurev-psych-033020-123501.
6. E. M. Pothos, J. R. Busemeyer, “An overview of the quantum cognition research program,” *Psychonomic Bulletin & Review* 32, 2507–2556 (2025). DOI: 10.3758/s13423-025-02675-9.
7. J. R. Busemeyer, P. D. Bruza, *Quantum Models of Cognition and Decision*, 2nd ed., Cambridge University Press (2024). DOI: 10.1017/9781009205351.
8. Q. Zhang, J. R. Busemeyer, “A Quantum Walk Model for Idea Propagation in Social Network and Group Decision Making,” *Entropy* 23(5), 622 (2021). DOI: 10.3390/e23050622.
9. G. P. Epping, P. D. Kvam, T. J. Pleskac, J. R. Busemeyer, “Open system model of choice and response time,” *Journal of Choice Modelling* 49, 100453 (2023). DOI: 10.1016/j.jocm.2023.100453.
10. D. Widdows, J. Rani, E. M. Pothos, “Quantum Circuit Components for Cognitive Decision-Making,” *Entropy* 25(4), 548 (2023). DOI: 10.3390/e25040548.
11. J. A. Huang, J. R. Busemeyer, Z. Ebelt, E. M. Pothos, “Bridging the gap between subjective probability and probability judgments: The quantum sequential sampler,” *Psychological Review* (2024). DOI: 10.1037/rev0000489.
12. S. Jeffery, S. Zur, “Multidimensional Quantum Walks, with Application to k-Distinctness,” *TheoretiCS* 4, Article 7 (2025). DOI: 10.46298/theoretics.25.7.
13. N. Tsuchiya, P. Bruza, M. Yamada, H. Saigo, E. M. Pothos, “Quantum-like Qualia hypothesis: from quantum cognition to quantum perception,” *Frontiers in Psychology* (2025). DOI: 10.3389/fpsyg.2024.1406459.

---

## 13. Proposal 與寄信範本

### 13.1 寄給老師的 meeting request

```text
Subject: EE5105 final project meeting request — [Name] / [Student ID]

Dear Prof. Hung,

We are [Name 1] and [Name 2] from EE5105. We would like to propose a final project
on quantum walk search and quantum cognition, centered on the paper
"Quadratic speedup for finding marked vertices by quantum walks" (AGJK 2019),
and connecting it to quantum cognition models of semantic memory retrieval and
multi-alternative decision making.

Before submitting our proposal, we would like to confirm the scope with you.
Would it be possible to meet for 15–20 minutes on [date/time]? We are also
available on [alternative times].

Best regards,
[Name]
[Student ID]
```

### 13.2 Proposal 一句話版

> 本專案以 AGJK 的「任意圖上尋找 marked vertices 的量子漫步演算法」為核心，將其 marked-set 與 $HT^+$ 結構映射到語意網絡中的多目標記憶提取與多選項決策，並比較 classical、quantum 與 open-system walk 的 hitting time、選擇機率與退相干效應。

### 13.3 Proposal 結構（1–2 頁）

1. **Title / group members**
2. **Motivation**（3–5 句）：quantum walk 與 quantum cognition 的接點。
3. **Research questions**（RQ1–RQ3）。
4. **Core papers**（AGJK + Chen 2022 + Huang–Busemeyer 2022 + Pavone–Faro 2025）。
5. **Method**：theory + numerical simulation + cognitive mapping。
6. **Expected results**：scaling、multiple marked vertices、semantic graph、decoherence。
7. **Timeline**：10/21–12/21 的 milestones。
8. **References**：5–8 篇。
9. **AI disclosure**（若有）。

### 13.4 Proposal 英文摘要草稿

> This project bridges quantum walk search algorithms and quantum cognition. The core technical paper is Ambainis–Gilyén–Jeffery–Kokainis (2019), which gives a quantum walk algorithm for finding marked vertices in an arbitrary graph with a quadratic speedup over the classical hitting time, up to logarithmic factors. We interpret marked vertices as target memories or decision alternatives on a semantic/decision graph, and compare classical random walks, Szegedy/AGJK quantum walks, and open-system walks with partial measurement. We study how graph topology, the number and arrangement of marked vertices, and decoherence affect hitting time, success probability, and choice probability. The project aims to (i) reproduce the $\tilde O(\sqrt{HT})$ scaling numerically, (ii) relate the extended hitting time $HT^+$ for multiple marked vertices to multi-alternative decision difficulty, and (iii) use the semantic-graph experiments of Pavone–Faro (2025) as an endpoint for a critical discussion of quantum cognition models.

---

## 14. 每週自我檢查問題

每週日回答以下問題，寫在 `Final/weekly_log.md`：

1. 這週我證明了什麼？推導了什麼？
2. 這週我跑了哪些實驗？圖在哪裡？
3. 這些結果回答了哪一個 RQ？
4. 有沒有過度解讀？有沒有限制沒寫？
5. 下週的 milestone 是什麼？會不會需要砍範圍？
6. 有沒有新的論文需要讀？是否會影響主軸？
7. 程式碼是否可重現？測試是否通過？
8. 報告/投影片進度是否落後？

---

## 15. 最後的建議

這個專案最容易失敗的方式，是把它做成「量子認知文獻回顧」或「量子漫步介紹」。這兩者都不夠。**成功的關鍵是：用 AGJK 的技術核心（marked vertices、$HT^+$、interpolated walk、$\sqrt{HT}$ scaling）去支撐一個具體的認知映射與數值實驗。** 只要你能在結果章節展示：

- 一張 classical vs quantum 的 scaling 圖；
- 一張 single vs multiple/clustered marked vertices 的比較圖；
- 一張 semantic graph 的 target activation 圖；
- 一段誠實的 limitation/discussion；

這個專案就會是一個紮實、扣住課程、又有個人特色的期末專案。
