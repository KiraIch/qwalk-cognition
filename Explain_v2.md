# 量子漫步搜尋與認知搜尋：完整解說（Explain v2）

> 讀者：本專題作者本人。目標是讀完後，能像親手設計並寫出這套程式的人一樣，講清楚背景、每個實驗的設計理由、每個函式的作用、每個數字的來源、論文主張的依據與限制，並回答老師的追問。
>
> 寫作依據：`report/main.tex` 與 `report/sections/*.tex`（論文，視為最新敘述）、`code/src/*.py`（實作）、`code/configs/*.yaml`（參數）、`code/results/raw/*.csv` 與 `code/results/processed/*.json`（結果）。舊文件 `Explain.md`、`Result.md`、`report/RESULTS_SUMMARY.md`、`weekly_log.md` 只作背景參考，數字一律以論文與結果檔為準。
>
> 標記約定：「（待確認）」表示本文無法由程式或結果檔直接驗證，或兩份來源互相矛盾；文末會彙整。

> **主 session 核對結果（2026-10-31，覆蓋下文對應的「待確認」）**
> - 測試：實際執行 `python -m pytest -q` → **61 passed**。附錄原寫的 47 已改為 61。
> - E4 穩健性 spread（偵測最大 0.045、古典最大 0.065、隨機停止中位數 0.08／最大 0.26、首次越過門檻中位數 0.44／最大 0.78）已由 code-reviewer 對照 `code/results/processed/E4_robustness.json` 核對無誤。
> - E5 逐 $T$ 敘述（T≲15 純量子最佳、群聚目標 T≳20 中間 p 最佳且 T=35 短暫回到 p=0、grid 單一目標 T=34–36 回到 0 並在 T≥71 為 p=1、語意圖單一目標 13≤T≤85 古典最佳）已由 code-reviewer 以 `E5_curves.csv` 逐點核對，論文已依此改寫。
> - 實測耗時：E5 約 33 秒；E4（含穩健性掃描）超過 10 分鐘（600 秒逾時仍未跑完）。
> - `report/figures/` 的 E1、E2、E4、E5 圖是由 `code/figures/` 直接複製而來，兩邊內容相同。
> - E3：violin 的平穩機率 $\pi=d/2|E|=0.04545$，古典 0.046 確實就是平穩值，論文說法成立；但它在時間窗末端仍在上升，所以不是真正的「峰值」。
> - `base.yaml` 中**只有** `paths.*`、`walk.laziness`、`agjk.*` 會被程式讀取；`seed`、`walk.initial`、`walk.max_steps`、`walk.success_threshold`、`classical.*`、`quantum.*`、`noise.*` 都沒有被讀取（以 grep 確認）。各實驗的 `max_steps`、`seeds`、`measurement_probabilities` 來自 `experiments.yaml`。
> - 以下函式不被 `experiments.py`／`plotting.py` 呼叫，只用於測試或保留：`interpolated_stationary`、`random_regular_graph`、`line_decision_graph`、`multi_branch_decision_graph`、`activation_curve`、`response_time`、`success_probability_with_measurement`、`area_under_curve`、`normalized_entropy`、`success_metrics`、`first_passage_time`、`hit_probability_curve`。
> - 論文第 6 節「complete graph and hypercube have Θ(N log N)-like」已改為「近線性（α≈1.06–1.07）」。

---

## 目錄

- 第 0 章　如何閱讀本文與一頁總覽
- 第 1 章　背景知識（從零講起）
- 第 2 章　認知映射：圖、標記集合與認知量的對應
- 第 3 章　程式架構總覽
- 第 4 章　逐模組逐函式解說（4.1–4.9）
- 第 5 章　五個實驗 E1–E5
- 第 6 章　測試
- 第 7 章　如何重現
- 第 8 章　論文逐節導讀
- 第 9 章　已知限制、開放問題與未來工作
- 第 10 章　名詞對照表與符號表
- 第 11 章　自我檢測題與參考答案
- 附錄 A　程式、論文與結果之間的不一致（只回報，未修改）

---

## 第 0 章　如何閱讀本文與一頁總覽

### 0.1 本文怎麼用

全文分三層。第一層（第 1–2 章）是背景與概念，只需要線性代數與機率的基礎。第二層（第 3–7 章）是程式與實驗，逐函式講解並連到實際檔案。第三層（第 8–11 章）是論文導讀、限制、名詞與自我測驗。

建議順序：先讀第 0 章的總覽，再讀第 1 章；遇到程式細節時再跳到第 4 章。每個實驗的圖怎麼看，放在第 5 章對應的小節。

### 0.2 專題在做什麼

這個專題把 **Ambainis–Gilyén–Jeffery–Kokainis（AGJK, 2019）** 的量子漫步找標記點演算法，當成一個「認知搜尋」的過程模型的數學核心。直觀地說：

- 圖（graph）代表語意網路或決策網路。
- 標記點集合 $M$ 代表「目標記憶」或「決策邊界」。
- 量子漫步的振幅與機率隨時間變化，可以對應到「啟動程度」或「選擇傾向」。

整個專題是 **process-level（過程層級）** 的數學模型。它不主張大腦是量子電腦，也不主張生物學上的量子效應；它只檢驗：在這樣的模型下，會得到哪些可測試的預測，而且這些預測是否與古典隨機漫步不同。

### 0.3 研究問題（RQ）與假說

論文 `report/sections/01_introduction.tex` 提出三個問題：

| 編號 | 問題 | 對應實驗 |
|---|---|---|
| RQ1 Mapping | $\HT$、$\HT^+$、譜隙、成功機率如何對應到反應時間、選擇機率與思考速度？ | E1、E3、E4 |
| RQ2 Structure | 標記點的數量與排列（單一、獨立、群聚）如何改變量子與古典搜尋的時間與成功率？$\HT^+$ 能否刻畫多選項決策的難度與情境效應？ | E2、E4 |
| RQ3 Noise | 部分量測（或退相干）如何侵蝕量子優勢？是否存在使成功機率或決策速度最大的「內省」程度？ | E5 |

論文的可測試預測（`report/sections/04_cognitive_model.tex` 中的 Testable predictions）有四條：

1. 連通性良好的圖與單一目標，量子搜尋時間隨 $\sqrt{\HT}$ 成長，並優於古典基準。
2. 獨立目標比群聚目標容易；$\HT^+$ 的大幅懲罰需要「結構化」而非僅僅群聚的標記集合。
3. 語意距離改變活化時序：量子漫步對遠目標有較高峰值，古典漫步對近目標有較高的早期 AUC。
4. 相干與量測互相權衡：純量子漫步有最高的「定時峰值」；能在偵測到目標時停止的部分量測漫步，在中等截止時間下找群聚目標的機率高於純量子與古典。

### 0.4 五個實驗各一句話結論

下列結論均來自論文 `report/main.tex` 摘要與 `report/sections/06_results.tex`，數字已對照結果檔（見各章）。

| 實驗 | 一句話結論 | 主要數字（來源） |
|---|---|---|
| E1 古典 vs 量子縮放 | 量子搜尋時間 $T_q$ 大致隨 $\HT^{\gamma}$ 成長，$\gamma\approx0.44$–$0.52$。 | 指數表來自論文；單點數值見 `code/results/raw/E1_scaling.csv` |
| E2 單一／獨立／群聚標記 | 獨立標記最容易；群聚標記行為接近單一目標；大的 $\HT^+/\HT$ 只出現在 AGJK 對抗式環面（adversarial torus）。 | 8×8 格點 $\HT$：單一 95.5、獨立 34.7、群聚 79.5（`E2_marked.csv` 平均） |
| E3 語意活化 | 在玩具語意圖上，CTQW 對遠目標有較高且較晚的峰值；CRW 對近目標有較高的早期 AUC。 | `code/results/raw/E3_semantic_metrics.csv` |
| E4 多選項決策與耦合 | 耦合兩個選項，量子選擇機率會移向未耦合選項（對稱三選項從 $1/3$ 到約 $0.50$）；古典在對稱圖上保持均勻；但只有「無相位」讀出才成立。 | `code/results/raw/E4_robustness.csv` |
| E5 部分量測退相干 | 純量子的定時峰值最高，但需要對準時機；在偵測模型中，中等量測率（$p\approx0.2$–$0.3$）對群聚目標在中等截止時間下優於純量子與古典。 | `code/results/raw/E5_sweep.csv` |

### 0.5 本次修正的重點（舊文件沒有，必須理解）

舊版 `Explain.md` 與 `Result.md` 的部分結論已經過時。以下四點是目前程式與論文的正確狀態，每一點都會在後續章節詳述。

1. **統一的 lazy walk**：所有 Szegedy／AGJK 實驗（E1、E2、E4、E5）都使用 $P_\eta=(1-\eta)P+\eta I$，$\eta=0.1$（`code/configs/base.yaml` 的 `walk.laziness`）；對抗式環面用 $\eta=0.2$（`experiments.yaml` 的 `adversarial_torus.laziness`）。理由：二分圖（cycle、grid、hypercube）的 discriminant 矩陣有特徵值 $-1$，使「絕對譜隙」為 0；lazy 之後 $-1$ 變成 $2\eta-1$。
2. **E5 重新設計**：舊版只在截止時間 $T=20$ 比較量測率，宣稱「12 倍增益」。檢查後發現 $T=20$ 剛好落在純量子振盪的谷底，那是相位假象。新版提供「讀出模型」與「偵測模型」兩種無相位依賴的讀法。
3. **E4 重新設計**：舊版「首次越過 0.5 門檻」的讀出對 $\eta$ 與邊權擾動極度敏感，舊文件的「非單調」結論是假象。新版增加隨機停止（random stopping）、偵測（detection，$p=0.2$）與古典吸收三種讀出，並做穩健性掃描。
4. **共同的方法論教訓**：凡是讀出時間固定在某個相位上的量子振盪量，結論都可能只反映相位。E4 與 E5 都必須採用與相位無關的讀出。這是本文最核心的方法論點，之後會多次回到它。

---

## 第 1 章　背景知識（從零講起）

本章的目標是讓讀者不需要查資料，也能理解後面所有的數學與程式。每一節都附一個小例子。

### 1.1 量子力學的最低需求

#### 1.1.1 狀態向量與 Dirac 記號

一個有限維量子系統的狀態是複數向量 $\lvert\psi\rangle\in\mathbb{C}^n$，並且歸一化 $\langle\psi\vert\psi\rangle=\sum_x\lvert\psi_x\rvert^2=1$。

- $\lvert x\rangle$ 是第 $x$ 個標準基底向量。
- $\langle\phi\vert\psi\rangle$ 是內積，$\langle\phi\vert$ 是 $\lvert\phi\rangle$ 的共軛轉置。
- 向量的每個分量 $\psi_x$ 叫做「振幅」（amplitude），$\lvert\psi_x\rvert^2$ 是在 $x$ 測到的機率。

**小例子**：$\lvert\psi\rangle=\frac{1}{\sqrt2}(\lvert0\rangle+\lvert1\rangle)$。測量得 $0$ 的機率是 $\lvert1/\sqrt2\rvert^2=1/2$。

#### 1.1.2 么正矩陣（unitary）

矩陣 $U$ 是么正的，若 $U^\dagger U=I$。么正變換保持範數，因此保持總機率為 1。這是量子演化的基本要求。

在本專題中，`code/src/szegedy.py` 的 `check_unitarity` 函式（第 188 行）就是在檢查 $W^\dagger W=I$（容許誤差 $10^{-9}$）。`tests/test_quantum.py` 的 `test_walk_matrix_is_unitary` 與 `test_interpolated_walk_is_unitary` 會對多個 $s$ 值檢查它。

#### 1.1.3 測量與坍縮

投影測量把狀態投影到某個子空間。對於基底測量，測得 $x$ 的機率是 $\lvert\psi_x\rvert^2$，測量後狀態變成 $\lvert x\rangle$（坍縮）。這個「坍縮」在本專題的部分量測（第 5 章 E5）中扮演核心角色：測量會把漫步者重設到某個頂點。

#### 1.1.4 密度矩陣與退相干

若系統有不確定性或與環境交互作用，要用密度矩陣 $\rho$（半正定、跡為 1）描述。純態 $\rho=\lvert\psi\rangle\langle\psi\rvert$。退相干（decoherence）指非對角項（振幅之間的干涉項）因環境而衰減。

本專題的 E5 不做一般的 Lindblad 演化，而是用「以機率 $p$ 做位置測量並重設」的離散模型（`code/src/noise.py`）。論文 `report/sections/03_theory.tex` Partial measurement 小節（子節 3.4，即 `\subsection{Partial measurement}`）給出這個通道的定義，式 `eq:measurement-channel`。

### 1.2 Markov chain（馬可夫鏈）

#### 1.2.1 轉移矩陣與平穩分布

設 $P$ 是 $n\times n$ 的列隨機矩陣（非負、每列和為 1）。$P_{xy}$ 是從 $x$ 走到 $y$ 的機率。機率列向量 $\pi$ 是平穩分布，若 $\pi P=\pi$。

**小例子**：三個點的圈 $0\to1\to2\to0$ 每步以 1/2 機率往左或往右（在圈上）。對稱性給出 $\pi=(1/3,1/3,1/3)$。

本專題的程式以**列向量**為慣例（README 的 Conventions）：機率分布寫成 `distribution @ P`。`code/src/classical.py` 的 `stationary_distribution`（第 21 行）是解線性系統 $(P^\top-I)\pi=0$，並加上 $\sum\pi=1$ 的約束，用最小平方法求解，然後把負的數截掉。

#### 1.2.2 可逆性（reversibility）

若 $\pi_x P_{xy}=\pi_y P_{yx}$ 對所有 $x,y$ 成立，則稱為可逆（detailed balance）。可逆鏈的重要性質是：

$$
D_{xy}=\sqrt{P_{xy}P_{yx}}=\sqrt{\pi_x/\pi_y}\,P_{xy}\quad\Longrightarrow\quad D=\mathrm{diag}(\pi)^{1/2}\,P\,\mathrm{diag}(\pi)^{-1/2}.
$$

所以 $D$ 是對稱矩陣，且與 $P$ 相似、特徵值相同。這正是第 1.4 節 Szegedy 漫步的關鍵。

注意：本專題的 `discriminant_matrix`（`code/src/szegedy.py` 第 22 行）直接計算 $\sqrt{P\circ P^\top}$，不需要先算 $\pi$，因此對非可逆鏈也會給出一個對稱矩陣，但其譜不一定等於 $P$ 的譜。本專題的所有圖都是無向圖加上權重，因此都是可逆的。

#### 1.2.3 Hitting time（擊中時間）與線性方程

Hitting time 是從某個起點走到標記集合 $M$ 的期望步數。論文 `report/sections/02_background.tex` 的定義是「從平穩分布出發」的平均：

$$
\HT(P,M)=\mathbb{E}_{X_0\sim\pi}\left[\min\{t\ge0:X_t\in M\}\right].
$$

計算方法是解線性系統。令 $h_x$ 為從 $x\notin M$ 出發的期望擊中時間，則

$$
h_x=1+\sum_y P_{xy}h_y\quad(x\notin M),\qquad h_x=0\quad(x\in M).
$$

然後取條件平均：

$$
\HT(P,M)=\frac{1}{1-p_M}\sum_{x\notin M}\pi_x h_x,\qquad p_M=\sum_{x\in M}\pi_x.
$$

**小例子（完全圖 $K_N$，$M=\{0\}$）**：所有非標記點對稱，$h=1+\frac{N-2}{N-1}h$，所以 $h=N-1$，且 $\HT=N-1$。這在 `tests/test_classical.py` 的 `test_complete_graph_hitting_time` 中被檢查。

**小例子（圈 $C_N$，$M=\{0\}$）**：從距離 $i$ 出發的期望擊中時間是 $h_i=i(N-i)$，平均後 $\HT=N(N+1)/6$。`test_cycle_hitting_time_formula` 檢查了這一點。

程式對應：`code/src/classical.py` 的 `hitting_times`（第 35 行）建立 $(I-P_{UU})h=\mathbf{1}$ 並求解；`mean_hitting_time`（第 50 行）做條件平均。

#### 1.2.4 Lazy walk（惰性漫步）

惰性版本 $P_\eta=(1-\eta)P+\eta I$：每一步以機率 $\eta$ 原地不動。它對擊中時間的影響是精確的倍數：

$$
\HT(P_\eta,M)=\frac{\HT(P,M)}{1-\eta}.
$$

這個恆等式被 `tests/test_quantum.py` 的 `test_laziness_rescales_hitting_time` 檢查，$\eta\in\{0.1,0.2\}$ 都通過。它的用途是消除二分圖的負特徵值（見第 1.4 節）。

**從 E1 CSV 直接驗證**：`code/results/raw/E1_scaling.csv` 的 `HT_lazy_ratio` 欄位全部為 $1.1111=1/(1-0.1)$，與上式一致。

### 1.3 Grover 搜尋與二次加速

Grover 演算法在 $N$ 個項目中找一個標記項，只需 $O(\sqrt N)$ 次查詢，而古典需要 $\Theta(N)$。

對於量子漫步，Szegedy（2004）證明：若古典漫步的擊中時間為 $\HT$，量子版本可以在 $O(\sqrt{\HT})$ 步內偵測到標記點（detection）。這是量子漫步搜尋的「二次加速」。

直觀上，這與 Grover 類似：古典漫步要「等待」$\HT$ 步才碰到標記點；量子漫步像 Grover 的振幅放大，把振幅集中到標記點。

### 1.4 Szegedy 量子漫步

#### 1.4.1 兩個暫存器與 $V(P)$

Szegedy 把馬可夫鏈提升到兩個頂點暫存器上的么正算符。論文與程式採用 AGJK 的慣例：

$$
V(P)\lvert\bar0\rangle\lvert x\rangle=\sum_y\sqrt{P_{xy}}\,\lvert y,x\rangle,\qquad
\mathrm{Shift}\lvert x,y\rangle=\lvert y,x\rangle,\qquad
\mathrm{Ref}=(2\lvert\bar0\rangle\langle\bar0\rvert-I)\otimes I,
$$

$$
W(P)=V(P)^\dagger\,\mathrm{Shift}\,V(P)\,\mathrm{Ref}.
$$

直觀理解：$V(P)$ 把「位於 $x$」的狀態展開成「下一步可能去 $y$」的疊加態；$\mathrm{Shift}$ 交換兩個暫存器，讓「從 $x$ 到 $y$」變成「從 $y$ 到 $x$」的鏡像；$\mathrm{Ref}$ 是對 $\lvert\bar0\rangle$ 子空間的反射。

#### 1.4.2 Discriminant matrix（判別矩陣）與譜

$W(P)$ 的左上區塊是 $D_{xy}=\sqrt{P_{xy}P_{yx}}$，即 discriminant matrix。$W(P)$ 的非平凡特徵值是 $e^{\pm i\theta_k}$，其中 $\lambda_k=\cos\theta_k$ 是 $D$ 的特徵值（Szegedy 譜引理，論文 `03_theory.tex` 中以陳述方式使用，不再證明）。

所以：
- $D$ 的特徵值接近 1，對應 $W$ 的特徵值接近 1（相位接近 0），振幅緩慢轉移。
- $D$ 的特徵值接近 $-1$，對應相位接近 $\pi$。

#### 1.4.3 為何要用「譜隙」與「相位隙」

設 $\lambda_1\ge\lambda_2\ge\cdots$ 為 $D$ 的特徵值。定義：

- 絕對譜隙：$\text{spectral\_gap}=1-\max_{i\ge2}\lvert\lambda_i\rvert$。
- 相位隙：$\text{phase\_gap}=1-\lambda_2$。

在二分圖（例如 cycle 偶數點、grid、hypercube）上，$D$ 有特徵值 $-1$，絕對譜隙為 0。這使得量子搜尋速度的估計失效。

**Lazy walk 的修正**：$\lambda\mapsto(1-\eta)\lambda+\eta$，所以 $-1\mapsto 2\eta-1$，絕對譜隙變為 $1-(1-2\eta)=2\eta$。以 $\eta=0.1$ 為例，絕對譜隙最多是 $0.2$。

**從 E1 CSV 驗證**：hypercube 的 `spectral_gap` 全部為 $0.2=2\eta$，與上述一致。`phase_gap` 為 $0.6,0.45,0.36,0.30$（$d=3,4,5,6$），等於 $1.8/d$（lazy 後 $\lambda_2=1-1.8/d$），也一致。

程式：`code/src/szegedy.py` 的 `spectral_gap`（第 173 行）與 `phase_gap`（第 180 行）。`test_laziness_removes_bipartite_zero_gap` 對 $C_{16}$、$4\times4$ grid、$Q_4$ 檢查這個現象。

#### 1.4.4 為何是 $\sqrt{\HT}$

直觀說法：量子漫步在譜隙的時間尺度上做相干旋轉，把振幅從「古典需要 $\HT$ 步的擴散」轉成「約 $\sqrt{\HT}$ 步的旋轉」。Szegedy 的界與 Grover 的 $\sqrt N$ 是同一類現象。精確的界在 AGJK（2019）中給出，本專題不重新證明。

#### 1.4.5 初始態

本專題的初始態是 $\lvert\bar0\rangle\lvert\sqrt\pi\rangle=\sum_x\sqrt{\pi_x}\lvert\bar0\rangle\lvert x\rangle$（`code/src/szegedy.py` 的 `initial_state`，第 100 行）。它的第一暫存器全在 $\lvert\bar0\rangle$，第二暫存器是平穩分布的平方根振幅。

E5 與 E4 的初始態不同：E5 從指定的 cue 頂點出發（$\lvert\bar0\rangle\lvert\text{cue}\rangle$），E4 從樞紐（hub）出發。這些在第 5 章說明。

### 1.5 AGJK（2019）：內插漫步與擴充擊中時間

#### 1.5.1 吸收漫步與內插漫步

給定標記集合 $M$，令 $U=V\setminus M$。吸收漫步 $P'$ 在 $M$ 上停留：

$$
P'=\begin{pmatrix}P_{UU}&P_{UM}\\0&I\end{pmatrix}.
$$

內插漫步：

$$
P(s)=(1-s)P+sP',\qquad s\in[0,1).
$$

$s=0$ 是原本的漫步；$s\to1$ 時越來越像吸收漫步。直觀上，$s$ 控制「碰到標記點後要不要停留」，這是 AGJK 放大標記點振幅的關鍵。

程式：`code/src/agjk.py` 的 `absorbing_transition`（第 21 行）與 `interpolated_transition`（第 32 行）。

#### 1.5.2 內插量子漫步 $W(s)$

$W(s)$ 多了一個量子位元（qubit）記錄「目前位置是否為標記點」。對 $x\in U$，它的作用與 $W(P)$ 相同；對 $x\in M$，它把狀態以係數 $\sqrt{1-s}$ 與 $\sqrt{s}$ 分配到「繼續走」與「停留」兩個分支。這個 qubit 的硬幣矩陣在程式中是 `_coin(s)`（`code/src/agjk.py` 第 90 行）：

$$
C(s)=\begin{pmatrix}\sqrt{1-s}&-\sqrt{s}\\ \sqrt s&\sqrt{1-s}\end{pmatrix}.
$$

這是么正的（行列式與正交性都成立）。

#### 1.5.3 Extended hitting time $\HT^+$

AGJK 定義：

$$
\HT(s)=\frac{1}{1-p_M}\sum_{k}\frac{\lvert\langle v_k(s)\vert\sqrt{\pi_U}\rangle\rvert^2}{1-\lambda_k(s)},\qquad \HT^+=\lim_{s\to1}\HT(s),
$$

其中 $\lambda_k(s),v_k(s)$ 是內插判別矩陣 $D(s)$ 的特徵值與特徵向量，$\sqrt{\pi_U}$ 是 $U$ 上的次正規化向量。

- 單一標記點時，$\HT^+=\HT$。
- 多個標記點時，$\HT^+$ 可能遠大於 $\HT$。AGJK 的對抗式構造（第 1.5.5 節）就是要製造這種差距。

程式：`code/src/agjk.py` 的 `ht_spectral`（第 58 行）與 `ht_extended`（第 81 行）。`ht_extended` 用 $s=1-\varepsilon$（$\varepsilon=10^{-6}$）近似極限。

#### 1.5.4 多個標記點的困難

直觀理解：若標記點很多，古典擊中時間變小，但「找到其中任何一個」的量子演化可能受到「被標記點吸收的分支」與「未被吸收的分支」之間的干涉限制，使得 $\HT^+$ 不一定小。這就是為何 AGJK 要定義 $\HT^+$ 而不是直接用 $\HT$。

#### 1.5.5 對抗式環面（adversarial torus）

AGJK 的反例是 $N\times N$ 環面（週期邊界的格點），標記集合為兩個子集合的聯集：

- $M_1=\{(j_1d_1,j_2d_1):0\le j_1,j_2<k_1\}$：稠密叢集。
- $M_2=\{(j_1d,j_2d):0\le j_1,j_2<N/d\}$：稀疏週期格點。

其中 $d_1\mid d\mid N$。論文 `03_theory.tex` 陳述 $\HT=\widetilde O(d^2)$、$\HT^+=\Omega(N^2)$（待確認：此漸近式在本專題只在 $L\le36$ 的範圍內檢查，見第 5 章 E2）。

程式：`code/src/graphs.py` 的 `adversarial_torus_marked`（第 39 行）。它要求 $d\mid L$ 且 $d_1\mid d$，否則丟出 `ValueError`。

#### 1.5.6 Detection 與 finding 的差別

- Detection（偵測）：判斷「有沒有」標記點存在。
- Finding（尋找）：真的得到一個標記點的位置。

Szegedy 的量子漫步可以 detection 在 $O(\sqrt{\HT})$ 步。但直接量測最後的狀態，不保證會得到標記點。AGJK 的 Algorithm 1 準備 $\lvert\bar0\rangle\lvert\sqrt\pi\rangle$，跑 $W(s)$ 共 $t$ 步，然後量測 qubit；若 qubit 為 1，再量測位置得到候選點。

本專題實作的是這個「簡單版本」（論文稱為 Conjecture 3 的數值檢驗），而不是 AGJK 證明的 $\widetilde O(\sqrt{\HT})$ 版本（後者需要快速前饋 fast-forwarding，本專題只引用不重做）。

### 1.6 CTQW 與 CRW（連續時間漫步）

與前面的離散時間漫步不同，語意實驗（E3）使用連續時間。

- 對稱正規化 Laplacian：$L_{\mathrm{sym}}=I-D^{-1/2}AD^{-1/2}$。
- 隨機漫步產生元：$L_{\mathrm{rw}}=I-D^{-1}A$。
- CTQW：$\lvert\psi(t)\rangle=e^{-iL_{\mathrm{sym}}t}\lvert c\rangle$，$p_T(t)=\lvert\langle T\vert\psi(t)\rangle\rvert^2$。
- CRW：$\rho(t)=\rho(0)e^{-L_{\mathrm{rw}}t}$，$p_T(t)=\rho_T(t)$。

兩者的特徵值相同（都是 $L$ 的譜），因此可以用同一個時間尺度比較。論文用 $\tau=\lambda_1 t$ 作為無因次時間，$\lambda_1$ 是 $L_{\mathrm{sym}}$ 的最小正特徵值（代數連通度）。

程式：`code/src/semantic.py` 的 `normalized_laplacian`（第 13 行）、`ctqw_trajectory`（第 41 行）、`crw_trajectory`（第 53 行）、`spectral_gap`（第 33 行）。

**注意一個細節**：`crw_trajectory` 的實作是 $\sqrt{d}\,V e^{-\Lambda t}V^\top(p_0/\sqrt d)$，最後對每個時間點做欄歸一化（`trajectory / trajectory.sum(axis=0)`）。它實際上是 $p_0 e^{-tL_{\mathrm{rw}}}$ 的等價實作（矩陣相似變換）。欄歸一化在數值上保證總機率為 1，但也會掩蓋微小的負值（先 `np.clip` 到 0）。這一點在第 4 章再詳述。

### 1.7 Grover 與量子漫步的「時間選擇」問題

這是 E5 的重要背景。量子振盪的 $p_M(t)$ 不會單調增加，而是在某些時間出現峰值、之後回落。所以「截止時間 $T$」的選擇會決定結果：

- 若 $T$ 剛好落在峰值，成功機率高。
- 若 $T$ 落在谷底，成功機率低。

因此比較兩種方法時，只看單一 $T$ 會引入相位假象。量子搜尋文獻的標準解法是「隨機停止時間」（randomized stopping）：在 $\{1,\dots,H\}$ 上均勻抽一個停止時間，計算平均成功機率。本專題的 `metrics.time_averaged_success` 就是這個量。

### 1.8 量子認知（quantum cognition）背景

量子認知用量子機率的數學模型來描述判斷與決策，主要處理情境效應、次序效應與連接謬誤等古典機率難以處理的現象（論文引用 Pothos & Busemeyer 2022；Busemeyer & Bruza 2024）。

與本專題相關的文獻：

| 文獻 | 模型 | 在本專題的角色 |
|---|---|---|
| AGJK 2019 | 量子漫步找標記點 | 量子核心 |
| Chen, Ferro, Sornette 2022（DTQW） | 離散時間量子漫步作為證據累積，部分量測引起退相干 | E5 的量測模型動機 |
| Huang & Busemeyer 2022 | 多選項決策的量子漫步框架 | E4 的決策映射動機 |
| Pavone & Faro 2025 | 語意圖上的連續時間量子漫步，洞察與干涉 | E3 的語意實驗動機 |
| Epping et al. 2023 | 開放系統的選擇與反應時間模型 | E5 的噪聲解釋（論文承認本專題是其簡化版） |

**定位原則**：本專題是「過程層級」的數學模型（process-level）。它不宣稱神經元或大腦實現了量子漫步，也不宣稱生物學上的量子效應。所有的「認知量」都是從漫步統計量直接定義的，不是對人類資料擬合的結果（論文 `04_cognitive_model.tex` 的假設 2 與 4）。

> 注意：論文 `02_background.tex` 中 `\cite{zhang2021}`、`huang2024`、`jeffery2025`、`tsuchiya2025` 等條目存在於 `refs.bib`，但正文未必都引用（待確認：需用 grep 檢查 `\cite` 清單）。

---

## 第 2 章　認知映射：圖、標記集合與認知量的對應

### 2.1 對應表

論文 `report/sections/04_cognitive_model.tex` 的 Table `tab:mapping` 把漫步物件對應到認知量。本節逐項檢查每個對應的合理性與限制。

| 漫步物件 | 認知解釋 | 合理性 | 主要限制 |
|---|---|---|---|
| 頂點 $x\in V$ | 概念、證據狀態或選項 | 語意網路中節點即概念 | 概念之間的關係是人為設計 |
| 邊 $(x,y)\in E$ | 語意聯想或證據轉移 | 邊權可解釋為聯想強度 | 無向對稱假設；未擬合人類聯想數據 |
| 標記集合 $M$ | 目標記憶或決策邊界 | 搜尋的目標就是標記點 | 標記集合本身由實驗者指定 |
| 初始態 $\lvert\psi_0\rangle$ | 提示（cue）或初始注意力 | E3、E5 直接從 cue 頂點出發 | E4、E1 的初始態是平穩分布或樞紐，語意不同 |
| 么正 $W(s)$ 或 $e^{-iLt}$ | 思考／證據累積 | 只是一種數學動力學 | 「證據累積」是比喻，不是測得的神經過程 |
| 測量 | 承諾一個答案或決定 | E5 的測量重設位置 | 測量的頻率 $p$ 是人為參數 |
| $p_M(t)$ | 目標的活化或成功機率 | 數學上是某個機率 | 不是實測的活化程度 |
| $T_q=\arg\max_t p_M(t)$ | 「峰值證據」的反應時間 | 只是數學定義 | 峰值不等於人的反應時間；E5 顯示峰值對截止時間敏感 |
| 首次越過門檻 | 截止時間下的反應時間 | 直觀合理 | **E4 證明此讀出受相位影響，不應用** |
| 選項集合 $M_i$ 的機率 | 選擇機率 | 直接對應 | 需要無相位的停止規則 |
| $\HT$、$\HT^+$ | 搜尋難度、情境難度 | 數學上的困難度量 | 「情境難度」是新詞，論文只給數學定義 |
| 譜隙 $\lambda_1$ | 思考／弛緩速度 | 與收斂速度相關 | 「思考速度」是比喻 |
| 內插 $s$ | 承諾或吸收強度 | 對應「碰到目標就停留」的程度 | 純數學參數，無獨立心理依據 |
| 測量率 $p$ | 內省或噪聲程度 | 對應「中途檢查」的頻率 | 「內省」是比喻，論文以引號標示 |

### 2.2 五條基本假設（論文 04 節）

1. **過程層級**：描述搜尋或決策過程的統計量，不描述大腦實現。
2. **干涉即多路徑**：量子干涉代表多條證據路徑或語意聯想的交互作用；相位結構只是建模工具。
3. **古典基準**：相同圖、相同初始分布、相同標記集合上的馬可夫隨機漫步。這樣就把「干涉效應」與「圖結構效應」分開。
4. **定義而非擬合**：反應時間、選擇機率、目標活化、熵、半徑都由漫步統計定義，沒有對行為資料擬合。
5. **圖作為先驗**：圖編碼語意或決策先驗；改變邊或權重就改變預測的情境效應。

**檢查**：假設 3 的「古典基準」是否真的使用相同初始分布？E1 與 E2 的量子初始態是 $\sqrt\pi$，古典擊中時間用的也是 $\pi$ 的條件平均，兩者一致。E5 的量子與古典都從同一 cue 出發，一致。E3 的 CTQW 與 CRW 都從 cue 出發，一致。E4 的量子與古典都從樞紐出發，一致。所以假設 3 在程式中成立。

### 2.3 反應時間與選擇機率的兩種定義

論文 `04_cognitive_model.tex` 第 4.4 節定義：

- **峰值時間**：$T_q=\arg\max_{t\ge1}p_M(t)$。它是「證據最強」的時刻，接近無截止時間的搜尋。
- **門檻時間**：第一個 $t$ 使 $p_M(t)\ge\theta$。它較接近截止時間實驗。

論文的重點是：**門檻時間對相位敏感**。若選擇機率在首次越過門檻的時刻取值，則同一個圖只要稍微改動 $\eta$，就會跳到另一個相位，給出完全不同的選擇。這是 E4 的重要發現，第 5 章會以數字展示。

### 2.4 相似性效應與情境效應

論文 `04_cognitive_model.tex` 把相似性效應（similarity effect）對應到耦合權重 $c$：

- 古典隨機漫步在對稱圖上，耦合只會在兩個耦合分支之間重新分配機率，第三個（未耦合）選項的機率保持不變。因此古典選擇在對稱圖上恆為均勻分布。
- 量子漫步的干涉會改變這個分布，未耦合選項獲得較多機率。

這是一個**模型層級的類比**，不是對人類相似性效應的解釋。論文 `07_discussion.tex` 明確寫道：「它沒有說明人類相似性效應是否來自量子干涉。」

### 2.5 本章的限制與注意事項

- 所有認知量都是漫步統計的定義，沒有行為資料支持。
- 「內省」「證據累積」「思考速度」等詞是比喻，論文以引號或限定語標示。寫報告或回答老師時，應該說「在本模型中對應的是」，不要說「大腦做的是」。
- 語意圖只有 19 個頂點（`code/src/graphs.py` 的 `TOY_SEMANTIC_NODES`），是手工建立的玩具圖。它說明機制，不代表真實語意記憶的規模或雜訊。

---

## 第 3 章　程式架構總覽

### 3.1 資料流

```text
configs/base.yaml ──┐
configs/experiments.yaml ──┤
                          ▼
 experiments.run()  ── 讀取設定，依 --only 選擇實驗（code/src/experiments.py:812）
        │
        ├─ graphs.py          建圖、標記集合、option sets、lazy 轉移矩陣 P_η
        │      │
        ├─ classical.py       平穩分布 π、擊中時間 HT（線性系統）
        ├─ szegedy.py         判別矩陣 D、Szegedy 漫步 W(P)、譜隙
        ├─ agjk.py            內插漫步 P(s)、W(s)、HT^+、內插 Chebyshev 下界
        ├─ semantic.py        CTQW / CRW（E3）
        ├─ noise.py           basis ensembles、測量遞迴、偵測遞迴（E5, E4-detect）
        ├─ cognitive.py       選項曲線、決策摘要、隨機停止、first passage（E4）
        └─ metrics.py         成功指標、冪律擬合、時間平均、振盪指數
                 │
                 ▼
 results/raw/*.csv（逐筆紀錄與逐時間曲線）
 results/processed/*.json（摘要：指數、最佳參數、spread 等）
                 │
                 ▼
 plotting.py（PDF 與 PNG）→ figures/
                 │
                 ▼
 report/（論文 .tex 以 figures/ 的檔案引用；report/figures/ 內的圖另行整理）
```

`schematics.py` 獨立產生論文的三層架構圖（`draw_architecture`，`code/src/schematics.py:15`），與資料流無關。

### 3.2 每個模組的責任

| 模組 | 責任 | 主要輸入 → 輸出 |
|---|---|---|
| `graphs.py` | 建立圖族、語意圖、決策圖；轉移矩陣；標記集合 | 參數 → `nx.Graph` 或 $n\times n$ 矩陣 |
| `classical.py` | 平穩分布、擊中時間、蒙地卡羅驗證、機率演化 | $P$, 標記集合 → $\pi$, $h$, 曲線 |
| `szegedy.py` | Szegedy 漫步：判別矩陣、區塊、作用、稠密矩陣、譜 | $P$ → 區塊 $U_x$、狀態 $n\times n$、譜隙 |
| `agjk.py` | 內插漫步 $P(s)$、$W(s)$、$\HT(s)$、$\HT^+$、Chebyshev 下界 | $P$, $M$, $s$ → 曲線、HT |
| `semantic.py` | 正規化 Laplacian、CTQW、CRW、語意指標 | 圖, 起點, 時間 → 軌跡 |
| `noise.py` | 位置測量與重設、basis ensembles、測量與偵測遞迴 | $P$, $M$, $p$, $T$ → 曲線 |
| `cognitive.py` | 選項曲線（量子與古典）、決策摘要、時間平均選擇、first passage | 選項集合 → 機率曲線與摘要 |
| `metrics.py` | 指標（峰值、門檻、AUC、熵、冪律擬合、時間平均、振盪指數） | 曲線 → 純量 |
| `experiments.py` | 實驗矩陣、呼叫以上模組、寫 CSV／JSON、呼叫繪圖 | YAML → CSV／JSON／圖 |
| `plotting.py` | 共用樣式與各實驗的圖（PDF＋PNG） | DataFrame → 圖檔 |
| `schematics.py` | 論文的架構示意圖 | 無 → PDF／PNG |

依賴方向（由上而下，沒有循環）：`experiments` → `{cognitive, noise, agjk, szegedy, semantic, classical, graphs, metrics}` → `{szegedy, classical}` → `numpy`。`agjk` 會呼叫 `szegedy` 與 `classical`；`noise` 會呼叫 `agjk` 與 `szegedy`；`cognitive` 會呼叫 `agjk` 與 `szegedy`（以及 `metrics.entropy`）。

### 3.3 慣例（README 與程式共同遵守）

- 機率分布是**列向量**，演化寫成 `distribution @ P`。
- 量子狀態在離散時間漫步中是 $n\times n$ 陣列，索引為 `[第一暫存器, 第二暫存器]`；頂點暫存器是第二個。
- 內插漫步的狀態是 $2\times n\times n$ 陣列，第一維是 qubit（標記旗標）。
- 所有隨機實驗都有明確的 seed（`base.yaml` 的 `seed: 20261020`；`experiments.yaml` 中各 E 的 seeds）。注意：`base.yaml` 的 `seed` 欄位目前是否被任何程式讀取（待確認，需 grep `\["seed"\]`）。
- 圖一律以 `networkx` 建立後轉為 `0..N-1` 的整數標籤（`convert_node_labels_to_integers`）。

### 3.4 設定檔中的每個欄位

`code/configs/base.yaml`：

| 欄位 | 值 | 用在哪裡 |
|---|---|---|
| `seed` | 20261020 | 隨機實驗的預設種子（實際使用見上一節的待確認） |
| `paths.raw / processed / figures` | `results/raw`、`results/processed`、`figures` | `experiments.run` 決定輸出位置（相對於 `code/`） |
| `walk.initial` | `stationary` | 語意上的初始態說明；程式中 E1、E2 直接使用 $\sqrt\pi$（待確認：程式未讀取此欄位，只是文件用途） |
| `walk.laziness` | 0.1 | `walk_transition` 的 $\eta$（E1、E2、E3 不用、E4、E5） |
| `walk.max_steps` | 2000 | 程式中未見使用（待確認） |
| `walk.success_threshold` | 0.5 | 程式中未見使用（門檻在各函式預設為 0.5） |
| `classical.hitting_time_solver` | `linear` | 文件用途；程式直接使用線性解（`hitting_times`） |
| `classical.monte_carlo_samples` | 20000 | 只在 `monte_carlo_hitting_time` 的測試中使用（待確認） |
| `quantum.backend` / `dtype` / `dense_max_vertices` | dense / complex128 / 32 | 文件用途；程式總是用稠密陣列 |
| `agjk.interpolation_grid` | `[0.3,…,0.999]`（13 個值） | E1、E2、E2 對抗式的 $s$ 網格（`_select_interpolation`） |
| `agjk.time_window_sqrt_ht` | 3.0 | 最大步數 $\lceil 3\sqrt{\HT}\rceil+5$ |
| `agjk.time_window_padding` | 5 | 同上的 $+5$ |
| `agjk.ht_plus_epsilon` | $10^{-6}$ | $\HT^+$ 的 $\varepsilon$（$s=1-\varepsilon$） |
| `noise.measurement_probabilities` | `[0,0.05,0.1,0.2,0.3,0.5,1.0]` | 程式中 E5 實際使用 `experiments.yaml` 的版本（見下），此欄位未被讀取（待確認） |
| `noise.trials` | 2000 | 程式使用精確遞迴，不做蒙地卡羅；此欄位未被讀取（待確認） |

**重要**：`base.yaml` 的 `noise.*`、`walk.max_steps`、`walk.success_threshold` 等欄位在程式中似乎沒有被讀取（待確認，需以 grep 完整驗證）。實際參數來源是 `experiments.yaml` 與各函式的預設值。這是修改參數時容易踩的坑：改了 `base.yaml` 的某個欄位，結果不一定改變。

`code/configs/experiments.yaml` 的 E1–E5 欄位已在第 5 章逐一列出。

---

## 第 4 章　逐模組逐函式解說

本章的每一節都依模組列出函式，寫法如下：**輸入／輸出的形狀、演算法步驟、數學對應、為何這樣寫、陷阱**。行號指向 `code/src/` 下的檔案。

### 4.1 `szegedy.py`：Szegedy 量子漫步

檔頭的慣例（第 1–11 行）說明：$V(P)\lvert\bar0\rangle\lvert x\rangle=\sum_y\sqrt{P_{xy}}\lvert y,x\rangle$、$\mathrm{Shift}$、$\mathrm{Ref}$、$W(P)=V^\dagger\,\mathrm{Shift}\,V\,\mathrm{Ref}$。頂點暫存器是第二個。

#### `discriminant_matrix(P)`（第 22 行）

- 輸入：$P\in\mathbb{R}^{n\times n}$（方陣，否則 `ValueError`）。
- 輸出：$D=\sqrt{P\circ P^\top}$，形狀 $n\times n$，對稱。
- 程式：`np.sqrt(P * P.T)`，`*` 是逐元素乘法。

陷阱：若 $P_{xy}P_{yx}<0$ 會產生 NaN；但 $P$ 是非負的，所以不會發生。

#### `is_reversible(P, stationary=None, atol=1e-10)`（第 29 行）

- 檢查 $\pi_x P_{xy}=\pi_y P_{yx}$（`flow` 與轉置相等）。
- 若沒有給 $\pi$，會呼叫 `stationary_distribution`。
- 主要用途是測試；E1–E5 的圖都是無向加權圖，應該都可逆。

#### `_householder_completion(p)`（第 37 行）

這是最關鍵但最容易看不懂的函式。

- 輸入：單位長度的實向量 $p$（即 $\sqrt{P_{x\cdot}}$，一個頂點的轉移機率的平方根）。
- 目標：找一個么正矩陣 $U$，使 $Ue_0=p$，也就是 $U$ 的第一行是 $p$。這樣 $V(P)\lvert\bar0\rangle\lvert x\rangle$ 的第一暫存器振幅就是 $\sqrt{P_{x\cdot}}$。
- 做法：Householder 反射 $U=I-2\frac{dd^\dagger}{d^\dagger d}$，$d=e_0-p$。當 $\lvert e_0\rvert=\lvert p\rvert=1$ 時，這個反射把 $e_0$ 映到 $p$。
- 特例：若 $\langle e_0\vert p\rangle\approx1$（即 $p=e_0$），直接回傳 $I$（避免除以零）。`1e-14` 是容許誤差。

陷阱：程式假設 $p$ 已歸一化。`np.sqrt(P[vertex])` 的平方和是 $\sum_y P_{xy}=1$，所以成立；若 $P$ 不是列隨機，這裡會錯。

#### `walk_operator_blocks(P)`（第 51 行）

- 輸入：$P$。輸出：形狀 `(n, n, n)` 的複數陣列 `blocks`，其中 `blocks[:, :, x]` 是 $U_x$。
- 步驟：對每個 $x$，呼叫 `_householder_completion(np.sqrt(P[x]))`。
- 作用：把 $V(P)$ 寫成 $\sum_x U_x\otimes\lvert x\rangle\langle x\rvert$ 的區塊形式，因為 $V$ 在頂點暫存器 $x$ 上作用 $U_x$（只作用第一暫存器）。

這個函式的時間與空間都是 $O(n^3)$，在 $n=64$ 時約為 26 萬個複數，可接受；$n=100$（grid $10\times10$）約為 100 萬個複數，仍可接受（16 bytes × $10^6$ ≈ 16 MB）。

#### `apply_v(state, blocks, adjoint=False)`（第 60 行）

- 輸入：`state` 形狀 `(n, n)`，`[第一暫存器, 第二暫存器]`。
- 步驟：`np.einsum("ijx,jx->ix", blocks, state)`，即 $\text{out}[i,x]=\sum_j U_x[i,j]\,\text{state}[j,x]$。
- `adjoint=True` 時先把 `blocks` 換成 $U_x^\dagger$：`blocks.conj().transpose(1,0,2)`。

解讀：這個 einsum 只作用在第一暫存器上，且每個第二暫存器的索引 $x$ 各自乘以自己的 $U_x$。這就是 $V$ 的區塊結構。

#### `apply_reflection(state)`（第 66 行）

- 把第一暫存器索引 $\ge1$ 的列乘以 $-1$，即 $\mathrm{Ref}=2\lvert\bar0\rangle\langle\bar0\rvert-I$（第一暫存器的 $\bar0=0$）。
- 注意：這是 `reflected = state.copy()` 後的原地修改。複製避免修改輸入（保持純函式）。

#### `apply_walk(state, P, blocks=None)`（第 72 行）

這是一步 Szegedy 漫步的核心：

1. `reflected = apply_reflection(state)`：$\mathrm{Ref}$。
2. `stepped = apply_v(reflected, blocks)`：$V$。
3. `shifted = stepped.T`：$\mathrm{Shift}$（交換兩個暫存器，轉置）。
4. `apply_v(shifted, blocks, adjoint=True)`：$V^\dagger$。

合起來是 $W=V^\dagger\,\mathrm{Shift}\,V\,\mathrm{Ref}$，與 AGJK 慣例一致。若 `blocks` 為 `None` 會每次重算（慢），實驗中都會傳入預先算好的 `blocks`。

陷阱：`stepped.T` 只在 `(n,n)` 方陣上成立；這裡的狀態總是方陣，所以沒問題。

#### `walk_matrix(P)`（第 81 行）

- 建立 $n^2\times n^2$ 稠密矩陣，用於測試（`test_apply_walk_matches_dense_matrix`）。
- 用 `np.kron(blocks[:,:,v], projector_v)` 組出 $V$，`shift` 是一個置換矩陣，`reflection` 是對角矩陣。
- 回傳 `v_matrix.conj().T @ shift @ v_matrix @ reflection`。

目的：獨立驗證 `apply_walk` 的正確性。這是本專題的重要測試之一。

#### `initial_state(P, distribution=None)`（第 100 行）

- 輸出：`state[0, :] = sqrt(distribution)`，其餘為 0。即 $\lvert\bar0\rangle\sum_x\sqrt{\pi_x}\lvert x\rangle$。
- 檢查：長度、非負（容許 $-10^{-12}$）；截掉小的負數；歸一化。

#### `success_probability_curve(P, marked, max_steps, distribution=None, blocks=None)`（第 117 行）

- 輸出：長度 `max_steps+1` 的陣列，`curve[t]` $=\sum_{x\in M}\sum_y\lvert\text{state}_t[y,x]\rvert^2$。
- 這是**標準 Szegedy 漫步**的成功曲線，不含內插。注意：在本專題的實驗中，這個函式只在測試中使用；實驗的成功曲線由 `agjk.interpolated_success_curve` 計算，因為 E1、E2 使用內插的 $s$。

#### `chebyshev_lower_bound(P, marked, max_steps, distribution=None)`（第 139 行）

- 演算法：令 $x_0=\sqrt\pi$，$x_1=Dx_0$，$x_{k+1}=2Dx_k-x_{k-1}$（第二類 Chebyshev 遞迴的第一類版本，論文稱為 $T_t(D)$）。
- 輸出：`curve[t]` $=\sum_{x\in M}\lvert(x_t)_x\rvert^2$。這就是論文式 `eq:chebyshev` 的 $q_t$（只取向量的標記分量）。
- 注意：這裡的 `root` 不把標記點歸零（對比 `agjk.ht_spectral` 會歸零）。

測試 `test_success_curve_is_bounded_by_chebyshev_bound` 檢查 `bound <= curve`（對非內插的標準漫步），是論文 Lemma 形式的數值版本。

#### `discriminant_spectrum(P)`（第 164 行）

- 若 $D$ 對稱（幾乎總是），用 `eigvalsh`；否則 `eigvals`。
- 回傳降冪排序的實部。

#### `spectral_gap(P)` 與 `phase_gap(P)`（第 173、180 行）

- `spectral_gap` $=1-\max_{i\ge2}\lvert\lambda_i\rvert$：絕對譜隙。二分圖上為 0（未 lazy 時）。
- `phase_gap` $=1-\lambda_2$：單邊隙，不受 $-1$ 影響。
- 若只有一個特徵值，回傳 1.0（退化情況）。

**注意**：E1 的 `spectral_gap` 欄位用的是絕對譜隙；`phase_gap` 才是論文在 lazy 後推薦的量。論文 `05_methods.tex` 說明「當 $\lambda_2<0$（如小完全圖）時，相位隙超過 1」，這在 `E1_scaling.csv` 的 $K_8$ 列可見（`phase_gap = 1.0286`）。

#### `check_unitarity(matrix, atol=1e-9)`（第 188 行）

- 檢查 $M^\dagger M=I$。

### 4.2 `classical.py`：古典隨機漫步

#### `_validate_transition(P)`（第 10 行）

- 檢查方陣、列和為 1（`np.allclose`）、非負（容許 $-10^{-12}$）。所有公開函式都先呼叫它。
- 陷阱：`allclose` 的預設容許是 $10^{-5}$ 與 $10^{-8}$，所以輕微的數值誤差會被接受。

#### `stationary_distribution(P)`（第 21 行）

- 方法：建立 $(n+1)\times n$ 的系統 $[P^\top-I;\,\mathbf 1^\top]\pi=[0;\,1]$，用 `np.linalg.lstsq` 求解。
- 之後把負的解截為 0（`clip`）並歸一化。
- 為何用最小平方而非直接解：系統是超定的（$n+1$ 個方程、$n$ 個未知數），且 $P^\top-I$ 是奇異的；最小平方可以穩定地找到解。
- 陷阱：若圖不連通，$\pi$ 不唯一，`lstsq` 會給出某個解。本專題的圖都是連通的（`test_toy_semantic_graph_is_connected...` 檢查語意圖）。

#### `hitting_times(P, marked)`（第 35 行）

- 輸出：長度 $n$ 的向量 $h$，$h_x=0$（$x\in M$），其餘由 `np.linalg.solve(I - P[free,free], 1)` 求得。
- 這是式 `eq:hitting-linear` 的直接解。若 $M$ 是空集，丟出 `ValueError`；若 $M$ 等於全體，回傳全 0。

#### `mean_hitting_time(P, marked, stationary=None)`（第 50 行）

- 公式：$\HT=\frac{\sum_{x\notin M}\pi_x h_x}{\sum_{x\notin M}\pi_x}$。
- 若 $1-p_M\le0$（$M$ 佔所有 $\pi$），回傳 0。

這是 E1、E2、E2 對抗式 HT 的實作。`ht_lazy_ratio` 的正確性由 $\HT(P_\eta)=\HT(P)/(1-\eta)$ 保證。

#### `monte_carlo_hitting_time(P, marked, n_samples, max_steps, seed)`（第 67 行）

- 用累積分布（`cumsum`）與均勻抽樣模擬，回傳 `mean`、`fraction_found`、`censored`。
- 只在 `test_monte_carlo_hitting_time_matches_exact` 中使用（以完全圖 $K_8$ 驗證，容許 10%）。主要實驗不使用蒙地卡羅（待確認：以 grep 確認）。

#### `hit_probability_curve(P, marked, initial, max_steps)`（第 100 行）

- 吸收漫步的累積擊中機率：`curve[t]`$=1-\sum_{x\notin M}(\text{survival}_t)_x$。
- 只在測試中使用（待確認）。E3 之外的古典吸收曲線由 `cognitive.absorbing_option_curve` 計算。

#### `diffusion(P, initial, steps)` 與 `diffusion_trajectory(P, initial, steps)`（第 122、130 行）

- 機率向量的連續演化 $p_{t+1}=p_tP$。前者只回傳終點，後者回傳全部軌跡（形狀 `(steps+1, n)`）。
- 測試 `test_diffusion_preserves_total_probability` 檢查總機率守恆。

### 4.3 `graphs.py`：圖、標記集合與轉移矩陣

#### 圖族（第 11–36 行）

- `complete_graph(n)`：$K_n$。
- `cycle_graph(n)`：$C_n$。
- `grid_graph(length)`：$L\times L$ 格點，用 `grid_2d_graph` 後轉整數標籤（列優先：標籤 $= \text{row}\cdot L+\text{col}$）。
- `hypercube_graph(dim)`：$Q_d$，$2^d$ 個頂點。
- `random_regular_graph(n, degree, seed)`：只在 `graphs.py` 中定義，實驗未使用（待確認）。
- `barbell_graph(n_each)`：`nx.barbell_graph(n_each, n_each)`，兩個 $K_{n_{\text{each}}}$ 由長度 $n_{\text{each}}$ 的路徑相連。總頂點數 $3n_{\text{each}}$（與 CSV 的 N=24, 48 一致）。
- `torus_graph(length)`：$L\times L$ 週期格點（`periodic=True`），4-正則。

#### `adversarial_torus_marked(length, d1, k1, d)`（第 39 行）

- 規則：`length % d == 0` 且 `d % d1 == 0`，否則丟出錯誤。
- 稠密部分：$\{(\text{row}\cdot d_1,\ \text{col}\cdot d_1):\text{row},\text{col}<k_1\}$。
- 稀疏部分：$\{(\text{row}\cdot d,\ \text{col}\cdot d):\text{row},\text{col}<L/d\}$。
- 回傳兩者聯集（排序、去重）。
- 數值驗證：$L=18$、$d_1=1$、$k_1=7$、$d=3$ 得到 $|M|=76$（`test_torus_and_adversarial_marked_set` 檢查）。與 `E2_adversarial_torus.csv` 的 $k=76$ 一致。

#### 語意圖（第 58–121 行）

- `TOY_SEMANTIC_NODES`：19 個概念，分為三群：動物（animal、dog、cat、wolf、horse、cow、bird）、交通工具（vehicle、car、bus、train、bicycle、airplane）、樂器（instrument、piano、guitar、violin、drum、flute）。
- `TOY_SEMANTIC_EDGES`：33 條無向邊（`code/src/graphs.py` 第 81–113 行逐行計數得出；以 `len(TOY_SEMANTIC_EDGES)` 再次確認較佳）。
- 橋接概念：`bird`（連到 `airplane` 與 `flute`），`airplane`（連到 `train`、`bird`、`vehicle`）。
- `toy_semantic_graph()`：建立圖，節點以字串加上 `concept` 屬性，再 `convert_node_labels_to_integers(label_attribute="concept")`。整數標籤是 `TOY_SEMANTIC_NODES` 的順序：`animal=0`、`dog=1`、`cat=2`、…、`violin=16`、`flute=18`。

E3 的 cue 是 `animal`（0），target 是 `dog`（1，距離 1）與 `violin`（16，距離 4）。這與 `E3_semantic_metrics.csv` 的 `target_distance` 欄位一致（1 與 4）。

#### `branched_decision_graph(branch_lengths, coupling_pair, coupling_weight, weight_jitter, seed)`（第 124 行）

這是 E4 的決策圖，請仔細看：

- 節點 0 是樞紐（hub）。
- 對每個分支 $i$，從樞紐延伸一條長度為 `lengths[i]` 的路徑；路徑最後一個節點是 terminal（選項終端）。
- 耦合：若 `coupling_pair=(a,b)` 且 `coupling_weight>0`，對深度 $d\le\min(\text{len}_a,\text{len}_b)$，在分支 $a$ 的第 $d$ 個節點與分支 $b$ 的第 $d$ 個節點之間加一條權重為 $c$ 的邊。
- 抖動：若 `weight_jitter>0`，每條邊的權重乘上獨立的 $U[1-\delta,1+\delta]$（`sorted(graph.edges())` 保證跨平台的順序穩定）。
- 回傳：圖、terminal 的元組、分支節點的元組。

**注意**：耦合邊的權重是 $c$，但路徑邊的權重是 1.0。因此 $c$ 的意義是「相對於路徑邊的強度」。

`test_branched_decision_graph_structure` 檢查 `[4,4,4]` 的圖有 13 個節點（$1+12$）、terminal 為 $(4,8,12)$。

#### `line_decision_graph`、`multi_branch_decision_graph`（第 178、185 行）

- 早期版本的決策圖。實驗主流程不使用（待確認：grep 確認）。`multi_branch_decision_graph` 的 `rung_probability` 會以亂數加梯子邊。

#### `transition_matrix(graph, self_loop=0.0, weight=None)`（第 219 行）

- `nx.to_numpy_array(graph, weight=weight)` 得到鄰接矩陣 $A$，加上 `self_loop·I`，再除以列和。
- 孤立點（列和為 0）會被設為自環，以免除以零。
- 這就是論文式 $P_{xy}=A_{xy}/\sum_zA_{xz}$（加權時是權重之和）。

#### `lazy_transition_matrix(P, stay_probability)`（第 237 行）

- $(1-\eta)P+\eta I$。$\eta\notin[0,1]$ 會丟出錯誤。
- 這是全部 Szegedy 實驗的惰性化入口（經由 `experiments.walk_transition` 或直接呼叫）。

#### 標記集合（第 244–300 行）

- `_farthest_point_sample(graph, k, seed)`：隨機起點，之後每次選距離已選集合最遠的點（以 BFS 距離的最小值）。這產生「獨立」（彼此遠離）的標記集合。
- `single_marked(graph, node, seed)`：單一點；若沒給 `node` 就隨機選。
- `independent_marked(graph, k, seed)`：呼叫 `_farthest_point_sample`。
- `clustered_marked(graph, k, seed, center)`：從隨機中心做 BFS，取前 $k$ 個節點。這產生「群聚」（連通）的集合。
- `marked_set(graph, kind, k, seed)`：分派。

**已知問題（重要）**：`_farthest_point_sample` 的隨機起點由 `seed` 決定。在 E2 的 seeds 0、1、2 中，grid $6\times6$ 的 seed 0 與 seed 2 產生**完全相同**的集合（`E2_marked.csv`：兩者都是 `30 5 0 21`）。barbell $n=8$ 的 seed 0 與 seed 2 也相同。因此「三個隨機標記集合的平均」實際上只有兩個不同的集合。論文 `06_results.tex` 的表格說明「means are over three random marked sets」，這在統計上是誤導的（待確認：應改寫為「三個種子、兩個不同集合」，或增加種子）。

#### `option_sets(terminals, extra=None)`（第 303 行）

- 把每個 terminal 包成單元素的集合。`extra` 可以加入額外節點（目前實驗不使用）。

### 4.4 `agjk.py`：內插漫步、$\HT^+$ 與 Chebyshev 下界

檔頭（第 1–9 行）給出 AGJK 的定義：$P'=\begin{pmatrix}P_{UU}&P_{UM}\\0&I\end{pmatrix}$、$P(s)=(1-s)P+sP'$、$\HT(s)$、$\HT^+$。

#### `absorbing_transition(P, marked)`（第 21 行）

- 複製 $P$，把標記列清零，再把 $(x,x)$ 設為 1，得到 $P'$。
- 注意：這裡的 `absorbing[marked, :] = 0.0` 之後再設 `absorbing[marked, marked] = 1.0`。`marked` 是陣列，`absorbing[marked, marked]` 取的是對角元素（因為兩個索引陣列一一配對），正確。

#### `interpolated_transition(P, marked, s)`（第 32 行）

- $(1-s)P+sP'$，$s\in[0,1)$（$s=1$ 會丟錯，因為那時 $\HT(s)$ 的分母為 0；極限用 `ht_extended`）。

#### `interpolated_stationary(P, marked, s, stationary=None)`（第 39 行）

- 內插後的平穩分布的解析式。主流程未呼叫（待確認）。

#### `interpolated_discriminant(P, marked, s)`（第 54 行）

- $D(s)=\sqrt{P(s)\circ P(s)^\top}$（直接用 `discriminant_matrix`）。

#### `ht_spectral(P, marked, s, stationary=None)`（第 58 行）

- 步驟：
  1. 求 $\pi$ 與 $p_M$。
  2. `matrix = interpolated_discriminant(P, marked, s)`，`eigh` 得特徵值與特徵向量（$D(s)$ 對稱）。
  3. `root = sqrt(π)`，把標記分量歸零（得到 $\sqrt{\pi_U}$）。
  4. 對每個 $k$，若 $1-\lambda_k<10^{-12}$ 則跳過（這是特徵值 1 的分量），否則加上 $\langle v_k,\sqrt{\pi_U}\rangle^2/(1-\lambda_k)$。
  5. 除以 $1-p_M$。
- 陷阱：步驟 4 的門檻 $10^{-12}$ 很嚴格。若數值誤差讓特徵值略小於 1（例如 $1-10^{-11}$），會產生極大的項。論文的實驗用的是 $s=1-10^{-6}$（`ht_extended`），特徵值接近 1 的分量需要被仔細處理。目前的結果（E2 的 $\HT^+$）與 $\HT$ 合理，表示此處未出錯（待確認：以單獨測試確認跳過的分量個數）。
- 與 `classical.mean_hitting_time` 的關係：`test_extended_hitting_time_matches_classical_for_single_marked` 檢查單一標記時 $\HT^+\approx\HT$（相對誤差 2%）。

#### `ht_extended(P, marked, epsilon=1e-6, stationary=None)`（第 81 行）

- 就是 `ht_spectral(P, marked, 1-epsilon)`。是 $\HT^+$ 的數值近似。
- 論文 `05_methods.tex` 明說這只用於診斷，搜尋曲線用的是真正的 $W(s)$。

#### `_coin(s)`（第 90 行）

- 回傳 $C(s)=\begin{pmatrix}\sqrt{1-s}&-\sqrt s\\\sqrt s&\sqrt{1-s}\end{pmatrix}$（實矩陣）。
- 當 $s=0$ 時是單位矩陣，所以 $W(0)$ 與 Szegedy 漫步一致（這是 E5 與多個測試的基礎）。

#### `interpolated_initial_state(P, distribution=None)`（第 94 行）

- 回傳形狀 `(2, n, n)` 的複數陣列，`state[0, 0, :] = sqrt(distribution)`。第一維 0 是 qubit 為 0（未標記）的分支，第一個 $0$ 是第一暫存器的 $\bar0$，最後一維是頂點。
- `distribution=None` 時使用 $\pi$；E5、E4 會傳入指定的初始分布（E5 是 cue 的 one-hot；E4 是樞紐的 one-hot）。

#### `apply_interpolated_reflection(state)`（第 107 行）

- 先整體乘以 $-1$，再把 `[0,0,:]` 乘回 $-1$，所以只有 `[0,0,:]` 保持正號，其餘分量變號。這就是 $2\lvert\bar0,0\rangle\langle\bar0,0\rvert-I$。
- 與 `szegedy.apply_reflection` 的差異：這裡的「標記旗標」也參與反射。

#### `apply_interpolated_shift(state)`（第 113 行）

- 只對 qubit 為 0 的分支（`shifted[0]`）做轉置，即「受控的 Shift」（controlled shift）。qubit 為 1 的分支不交換，對應於標記點上的停留。

#### `apply_interpolated_v(state, blocks, marked, s, adjoint=False)`（第 119 行）

這是最複雜的函式。

- 非伴隨（forward）：
  1. 對所有 qubit 分支套用 $U_x$：`transformed = einsum("ijx,ajx->aix", blocks, state)`。
  2. 若有標記點：對每個標記頂點 $x\in M$，把 qubit 分支用硬幣 $C(s)$ 混合，得到 `mixed`。
  3. `transformed[1][:, x] = mixed[1]`（qubit 為 1 的分支只取混合後的值，不再乘 $U_x$，即停留）。
  4. `transformed[0][:, x] = U_x · mixed[0]`（qubit 為 0 的分支仍走 $U_x$）。
- 伴隨（adjoint）：先對所有分支套用 $U_x^\dagger$；再對標記頂點用 $C(s)^\dagger$ 逆混合（`coin.conj()` 的轉置，即 $C^\dagger$）。

解讀：論文的公式（`03_theory.tex`）寫成 $\lvert0\rangle\lvert\bar0\rangle\lvert x\rangle\mapsto\sqrt{1-s}\lvert0\rangle V\lvert\bar0\rangle\lvert x\rangle+\sqrt s\lvert1\rangle\lvert\bar0\rangle\lvert x\rangle$。程式在標記頂點的實作與之一致，但細節（尤其「`mixed[1]` 不乘 $U_x$」）是程式的實作選擇，需要用 `interpolated_walk_matrix` 的么正性測試來保證（測試存在：`test_interpolated_walk_is_unitary`）。

#### `apply_interpolated_walk(state, P, marked, s, blocks=None)`（第 147 行）

- 步驟：`Ref'` → `V'` → `Shift'` → `V'^†`。與 `szegedy.apply_walk` 對應，只是多了 qubit 與標記處理。
- 在 $s=0$ 時必須與 `szegedy.apply_walk` 一致（因為 `_coin(0)=I`，標記處理退化）。測試 `test_interpolated_walk_is_stationary_at_zero_interpolation` 只檢查曲線為 $1/n$（對完全均勻的初始分布），並不直接比較兩者（待確認：可補一個 $s=0$ 與 `apply_walk` 比較的測試）。

#### `interpolated_walk_matrix(P, marked, s)`（第 163 行）

- 建立 $2n^2\times 2n^2$ 稠密矩陣，用於測試么正性（`test_interpolated_walk_is_unitary`，$s\in\{0,0.3,0.9\}$）。
- 對每個基底向量呼叫 `apply_interpolated_walk`，成本 $O((2n^2)^2)$ 次作用，只適合小圖。

#### `interpolated_success_curve(P, marked, s, max_steps, distribution=None, blocks=None)`（第 178 行）

- `curve[t]` $=\sum_{a,i}\lvert\text{state}_t[a,i,x]\rvert^2$ 對 $x\in M$ 求和。也就是「位於標記點上的機率」（不論 qubit 為何）。
- 這是 E1、E2 與對抗式環面的實際搜尋曲線 $p_M(t)$。

#### `interpolated_lower_bound(P, marked, s, max_steps, distribution=None)`（第 199 行）

- 內插版的 Chebyshev 下界：令 $x_0=\sqrt\pi$（**不歸零**），用 $D(s)$ 做 Chebyshev 遞迴，取標記分量平方和。
- 這是論文式 `eq:chebyshev` 的 $q_t(s)$。
- 在 E1、E2 中用來選擇 $s$：對每個 $s$ 取 $\max_t q_t(s)$，選最大者（`_select_interpolation`）。

**注意**：`ht_spectral` 把標記分量歸零，但 `interpolated_lower_bound` 沒有歸零。這是兩個不同的量（HT 用的是 $\pi_U$，下界用的是完整的 $\sqrt\pi$），設計上合理，但讀者容易混淆。

### 4.5 `noise.py`：部分量測、基底系綜與偵測遞迴（E5 與 E4 偵測讀出）

本模組的設計目標是**精確**計算平均成功機率，而不是用蒙地卡羅抽樣。核心想法是：量測只會把狀態重設到某個頂點，所以整個演化可以寫成「自上次重設後經過了幾步（年齡 $a$）、重設在哪個頂點 $x$」的線性遞迴。

#### 時間慣例（這一節必讀）

- `curve[t]` 是在「經過 $t$ 個漫步步驟之後」的成功機率。
- 每一步 $s\to s+1$ 的順序是：**先**以機率 $p$ 做位置量測並重設，**再**做一步漫步（`measurement_curve` 第 133 行的迴圈；`success_probability_with_measurement` 第 62–64 行的順序也是如此）。
- 因此，在步 $s$ 的量測「落點」的分布，是**在時刻 $s$ 的狀態**的位置分布。
- 被重設的漫步者在時刻 $s+1$ 的年齡是 1（已經走了一步）。

#### `vertex_distribution(state)`（第 13 行）

- 輸入 `(n,n)`，輸出 $\sum_i\lvert\text{state}[i,x]\rvert^2$：對第一暫存器求和，得到頂點機率。
- 注意：這與 `cognitive.vertex_distribution` 的實作相同。

#### `sample_vertex(state, rng)`（第 18 行）與 `reset_to_vertex(state, vertex)`（第 24 行）

- `sample_vertex`：依 `vertex_distribution` 抽一個頂點。
- `reset_to_vertex`：回傳 $\lvert\bar0\rangle\lvert v\rangle$，即 `collapsed[0, vertex] = 1`。

#### `partial_measurement_step(state, p, rng)`（第 31 行）與 `success_probability_with_measurement`（第 43 行）

- 以機率 $p$ 抽樣量測並重設，否則不動。這是**軌跡層級**的模擬（Monte Carlo）。
- `success_probability_with_measurement` 用 `n_trials` 條軌跡平均。它的初始態是**均勻**的 $\sqrt{1/n}$（第 57 行），不是 cue 或平穩分布。實驗主流程不呼叫它（待確認：以 grep 確認）；它的用途是在小例子上與精確遞迴交叉檢查。使用時請注意初始態不同。

#### `basis_ensembles(P, marked, s, max_steps, blocks)`（第 69 行）

- 對每個起點 $x$，從 $\lvert\bar0,0\rangle\lvert x\rangle$ 出發（`state[0,0,start]=1`），做 `max_steps` 步內插漫步（E5 中 $s=0$），記錄：
  - `positions[x, a, :]`：走了 $a$ 步後的頂點機率分布 $\mu_{x,a}(y)$。
  - `success[x, a]`：走了 $a$ 步後在 $M$ 上的機率 $s_{x,a}$。
- 這是 E5 與 E4 偵測讀出的「基底系綜」。它只需計算一次（每個圖與標記集合），之後掃描 $p$ 幾乎免費。
- 成本：$n$ 個起點 × $T_{\max}$ 步 × 一次作用，即 $O(n\cdot T\cdot n^2)$。E5 的 grid $6\times6$（$n=36$）與語意圖（$n=19$）都很小。

#### `pure_ensemble(P, marked, s, max_steps, distribution, blocks)`（第 94 行）

- 從指定的初始分布（不是基底）出發的無量測演化：`positions[t]` 與 `success[t]`。
- 用途：算「尚未發生任何量測」的那條路徑（遞迴中的 $q_0$ 項）。E5 的初始分布是 cue 的 one-hot。

#### `measurement_curve(p, max_steps, positions, success, pure_positions, pure_success)`（第 118 行）

這是「**讀出模型**」（readout model）：量測只重設，不停止搜尋；`curve[t]` 是時刻 $t$ 在標記點上的機率。

狀態變數：

- `q0`：到目前為止從未量測過的機率（純量）。
- `q[x, a]`：最近一次重設在頂點 $x$、之後已經走了 $a$ 步的機率權重（$a\ge1$）。

遞迴（對應論文附錄 `app:measurement` 的式子）：

$$
q_0(t+1)=(1-p)\,q_0(t),\qquad
q_{x,a+1}(t+1)=(1-p)\,q_{x,a}(t),
$$

$$
q_{y,1}(t+1)=p\Big[q_0(t)\,\mu^{(0)}_t(y)+\sum_{x,a}q_{x,a}(t)\,\mu_{x,a}(y)\Big],
$$

$$
p_M(t+1)=q_0(t+1)\,s^{(0)}_{t+1}+\sum_{x,a}q_{x,a}(t+1)\,s_{x,a}.
$$

程式對應（第 133–148 行，節錄核心）：

```python
new_q0 = (1.0 - measurement_probability) * q0
new_q[:, 2:] += (1.0 - measurement_probability) * q[:, 1:-1]      # 年齡 +1，無量測
new_q[:, 1] += measurement_probability * np.einsum(
    "xa,xay->y", q[:, 1:], positions[:, 1:, :]                    # 有量測：落點 = Σ q·μ
)
new_q[:, 1] += measurement_probability * q0 * pure_positions[step] # 從未量測過的路徑
```

陷阱與要點：

- `q[:, 0]` 永遠是 0（年齡 0 不使用）。
- 只有 `q[:, 1:]` 的年齡需要 `positions[:, 1:, :]`，所以切片從 1 開始。
- `if max_steps >= 2` 與 `if q[:, 1:].any()` 只是效率保護，不改變結果。
- 年齡超過 `max_steps` 的權重會被截掉，但因為 $T\le \texttt{max\_steps}$，不影響 $t\le T$ 的值。

測試保證（`code/tests/test_noise.py`）：

- `test_zero_measurement_is_pure_quantum_walk`：$p=0$ 時恰好是 `pure_success`。
- `test_fully_measured_walk_is_classical`：$p=1$ 時，`positions[:,1,:]` 等於 $P$（即 $W(0)$ 的一步位置分布就是 $P$），曲線等於古典的（非吸收）佔據機率。
- `test_measurement_curve_is_bounded`：$p\in\{0.1,0.3,0.5,0.9\}$ 時 $0\le p_M\le1$。

#### `detection_curve(p, max_steps, positions, success, pure_positions, pure_success, marked)`（第 152 行）

這是「**偵測模型**」：若量測落在標記點上，搜尋就**結束**（被吸收到 `found`），不再重設。

與讀出模型的差異（第 185–191 行）：

- `landing` 是量測落點的分布（同前）。
- `found += p * landing[marked].sum()`：落在標記點的質量被移到 `found`。
- `new_q[:,1] += p * where(unmarked, landing, 0)`：只有非標記的落點會被重設。

最後的讀數（forced readout）：`curve[T] = found(T) + q0(T)·pure_success[T] + Σ q·success`。也就是說，在截止時間 $T$ 一定做一次位置讀取；已被偵測的機率保留在 `found`。

語意：

- $p=0$：`found` 恆為 0，曲線 = `pure_success`（純量子、只在 $T$ 讀一次）。
- $p=1$：每一步都量測；第一次落在標記點就被吸收。曲線 = 古典的 $\Pr[\tau_M\le T]$（first passage）。測試 `test_fully_measured_detection_is_classical_first_passage` 驗證這點（以吸收矩陣計算）。
- 測試 `test_detection_is_bounded_and_dominates_readout`：偵測曲線 $\ge$ 讀出曲線（因為偵測不會丟失已找到的機率）。

**為何偵測模型不會超過 1**：每個步驟的量測質量只被分配一次（要嘛被吸收，要嘛被重設），所以總質量守恆。測試檢查 $\le1$。

#### `detection_option_curve(p, max_steps, positions, pure_positions, option_sets, final_readout=True)`（第 200 行）

- 與 `detection_curve` 相同，但對每個選項集合分開計數。回傳形狀 `(max_steps+1, n_options)`。
- 選項集合必須**互斥**（否則丟出 `ValueError`）。
- `final_readout=False`（E4 偵測讀出使用）：只計入中途量測的機率，所以每一欄是**非遞減**的「首次偵測分布」（第一次到達），在 `first_passage_summary` 中解讀為決策時間分布。
- `final_readout=True`：與 `detection_curve` 一致，加上截止時間的讀取，因此 `p=0` 時等於 `quantum_option_curve`（測試 `test_detection_option_curve_limits` 驗證）。

**注意**：`detection_option_curve` 的選項是用 `positions` 中的頂點分布做加總，而 `positions` 是以 `option_nodes`（所有終端的聯集）為標記集合計算的（`e4_readouts` 第 493 行）。這表示基底系綜中的 `success` 與 `pure_positions` 的標記是終端集合，與選項分組無關（分組只在 `per_option` 階段發生）。

### 4.6 `cognitive.py`：選項曲線、決策摘要與時間平均

#### `vertex_distribution(state)`（第 19 行）

- 同 `noise.vertex_distribution`，但多一個檢查：`state.ndim != 2` 時丟出錯誤。

#### `activation_curve(curves, option_sets)`（第 26 行）

- 把多條頂點曲線加總為選項曲線。主流程未呼叫（待確認）。

#### `choice_probabilities(state, option_sets)`（第 34 行）與 `response_time(curve, threshold)`（第 39 行）

- 前者由單一狀態算選項機率；後者回傳首次越過門檻的索引（否則 −1）。主流程使用 `decision_summary` 與 `first_passage_summary` 取代它們（待確認：以 grep 確認未被呼叫）。

#### `absorbing_option_curve(P, option_sets, initial, max_steps)`（第 44 行）

- 古典基準：把所有選項終端變成吸收態（`absorbing[option_nodes,:]=0`，對角設 1），然後做 `distribution @ absorbing`。
- `curve[t, i]` $=$ 時刻 $t$ 的分布在選項 $i$ 上的質量。因為吸收，每一欄非遞減。
- 初始分布會先正規化。

#### `quantum_option_curve(P, option_sets, initial, s, max_steps, blocks)`（第 64 行）

- 量子版本：`marked = option_nodes`（所有選項終端的聯集）。注意：**所有選項一起**作為內插漫步的標記集合，所以內插只發生在選項終端上。
- 初始態 `interpolated_initial_state(P, distribution)`，即 $\lvert\bar0,0\rangle\sum\sqrt{\text{init}_x}\lvert x\rangle$。
- `curve[t, i] = Σ_{a,x∈option_i} |state[a, :, x]|²`。

#### `decision_summary(curve, threshold=0.5)`（第 91 行）

這是 **E4 的舊讀出（first crossing）** 所用的函式：

1. `total[t] = Σ_i curve[t,i]`。
2. `decision_time` = 第一個 `total ≥ threshold` 的時刻；若從未越過，取 `argmax(total)`。
3. `choice_probabilities = curve[decision_time] / total[decision_time]`（若 total 為 0，則均勻）。
4. 回傳 `choice_entropy`、`max_choice`、`choice_bias = max − 1/k` 等。

**為何不可靠（重要）**：`decision_time` 的選取依賴 `total` 第一次越過門檻的時刻，而 `total(t)` 是振盪的。`choice_probabilities` 因此取決於振盪相位。E4 的穩健性掃描證明這點（見第 5 章 E4）。

#### `time_averaged_choice(curve, horizon)`（第 116 行）

- 隨機停止讀出（E4 `quantum_average`）：`mean = curve[1:H+1].mean(axis=0)`，再歸一化。
- 注意：這是**對時間平均後**的選項機率再歸一化，不是對每個時刻的選擇再平均。兩者不同；這裡取的是前者，論文也是如此（`05_methods.tex` 寫「$P_i\propto T_{\max}^{-1}\sum_t p_i(t)$」）。
- `horizon` 必須在 $[1, \text{len}-1]$ 之間。

#### `first_passage_summary(curve, horizon)`（第 132 行）

- 用於「決定於 $T$ 之前」的單調曲線（古典吸收，或偵測讀出）。
- `decided = total[-1]`（到 $T$ 為止已經決定的機率）。
- `probabilities = curve[-1] / decided`：條件於已決定，各選項的比例。
- `density = diff(total)`：每步的首次決定增量。`mean_time` = 這個密度的條件期望（時間索引加權平均）。
- `median_time`：第一個 `total ≥ 0.5` 的索引（若從未達到，為 −1）。

**注意**：`mean_time` 與 `median_time` 的定義與 `decision_summary` 的 `decision_time` 不同。`mean_time` 是條件平均，只有在 `decided > 0` 時有定義（否則 NaN）。

### 4.7 `semantic.py`：連續時間漫步與語意指標（E3）

#### `normalized_laplacian(graph)`（第 13 行）

- 回傳三個量：$L_{\mathrm{sym}}=I-D^{-1/2}AD^{-1/2}$、度數向量 $d$、平穩分布 $\pi=d/\sum d$。
- 若有孤立點（度數為 0）丟出錯誤。

#### `random_walk_laplacian(graph)`（第 24 行）

- $L_{\mathrm{rw}}=I-D^{-1}A$。E3 的主流程沒有直接使用它（CRW 用的是對稱版本的 eigen 分解，見下），此函式只在概念上對應論文式 `eq:ctqw-crw`（待確認：以 grep 確認是否被呼叫）。

#### `spectral_gap(laplacian)`（第 33 行）

- 回傳最小的正特徵值 $\lambda_1$（門檻 $10^{-12}$）。這是代數連通度，不是 $1-\lambda$ 的那種隙。

#### `ctqw_trajectory(laplacian, initial, times)`（第 41 行）

- 用 `eigh` 做 $L=V\Lambda V^\top$，係數 $c=V^\top\psi_0$，相位 $e^{-i\lambda_k t}$，回傳複數振幅矩陣，形狀 `(n, len(times))`。
- 注意：$L$ 是實對稱的，所以 $e^{-iLt}=Ve^{-i\Lambda t}V^\top$，這裡的實作正確。

#### `crw_trajectory(laplacian, degree, initial, times)`（第 53 行）

- 步驟：`coefficients = V^T (initial / sqrt(d))`；`decay = exp(-λ t)`；`trajectory = sqrt(d) · V (decay · coefficients)`；然後 `clip(0)`，並對每個時間點歸一化。
- 數學：$p(t)=p_0 e^{-tL_{\mathrm{rw}}}$ 的等價實作（$D^{1/2}$ 相似變換），但 **`clip` 會把數值上的負值截為 0，之後再歸一化**，這在 E3 的數字上影響很小，但理論上不是精確的 $p_0e^{-tL_{\mathrm{rw}}}$（待確認：可用 `test_crw_preserves_probability_and_relaxes_to_stationary` 的結果判斷，該測試只驗證總和為 1 與終點為平穩分布）。

#### `target_curve(trajectory, target)`（第 69 行）

- 就是 `trajectory[target]`。

#### `semantic_metrics(trajectory, times, target, graph, cue, gap)`（第 73 行）

輸入的 `trajectory` 是**機率**（E3 傳入的是 $\lvert\psi\rvert^2$，見 `experiments.run_e3` 第 341 行）。

- `curve = trajectory[target]`；`peak = argmax(curve)`；`p_peak`、`t_peak`、`tau_peak = gap * t_peak`。
- `auc = trapz(curve, times) * gap`：對 $\tau$ 積分。注意：積分範圍是整個時間窗（$\tau\le8$），因此 AUC 依賴時間窗的選擇（見第 5 章 E3）。
- `distribution = |trajectory[:, peak]|` 歸一化：峰值時刻的頂點分布。`np.abs` 在這裡是冗餘的（輸入已經是機率），但不會造成錯誤。
- `entropy_peak = entropy(distribution)`（以 2 為底）。
- `coverage_half_peak`：頂點中機率 $\ge 0.5\,p_{\text{peak}}$ 的比例（注意：這是頂點分布 `distribution` 與 `0.5*p_peak` 的比較，`p_peak` 來自目標曲線）。
- `expected_radius_peak`：以圖上的最短路徑距離（從 cue）加權的期望距離。

### 4.8 `metrics.py`：指標與冪律擬合

| 函式 | 行號 | 用途（在主流程中） |
|---|---|---|
| `success_metrics` | 10 | 測試用（`test_success_metrics`）；主流程未直接呼叫（待確認） |
| `power_law_fit(x, y)` | 25 | E1：$\log y=\gamma\log x+b$，回傳指數、前因子、$R^2$（對數尺度） |
| `entropy(p, base=2)` | 44 | 語意與決策的熵 |
| `normalized_entropy` | 52 | 測試用（待確認） |
| `choice_probabilities` | 59 | 測試用（`cognitive.choice_probabilities` 才是主流程的版本） |
| `first_passage_time(curve, θ)` | 67 | 測試用（待確認） |
| `area_under_curve` | 72 | 主流程未呼叫（待確認） |
| `bootstrap_confidence_interval` | 76 | 測試用；論文未報告 bootstrap CI（待確認） |
| `time_averaged_success(curve, H)` | 93 | E5：$\bar p(H)=H^{-1}\sum_{t=1}^H p_t$ |
| `oscillation_index(curve, H)` | 101 | E5：$\text{std}/\text{mean}$（母體標準差，ddof=0），$t\in[1,H]$ |
| `deadline_win_rate(curve, baseline, H)` | 111 | E5：$t\in[1,H]$ 中 curve 超過 baseline 的比例 |

重點細節：

- `power_law_fit` 要求 $x,y>0$，否則丟出錯誤（測試 `test_power_law_rejects_non_positive_values`）。E1 的 $T_q$ 全部為正，沒問題。
- `oscillation_index` 用 `values.std()`（ddof=0）。若 `mean ≤ 0` 回傳 NaN。
- `time_averaged_success` 與 `oscillation_index` 都只看 $t\in[1,H]$，不含 $t=0$。
- `deadline_win_rate` 的比較是嚴格大於（`>`）。

### 4.9 `experiments.py`：實驗矩陣與輸出

這是總指揮模組。它讀取 YAML、呼叫各模組、寫 CSV 與 JSON、呼叫繪圖。

| 函式 | 行號 | 作用 |
|---|---|---|
| `load_yaml(path)` | 75 | 用 `yaml.safe_load` 讀設定 |
| `walk_transition(graph, base_config, weight=None)` | 80 | **統一的 lazy 入口**：`lazy_transition_matrix(transition_matrix(graph, weight), η)`，$\eta$ 來自 `base.yaml` 的 `walk.laziness` |
| `e1_cases(experiment_config)` | 86 | 產生 E1 的圖與標記點（complete、cycle、hypercube 標記 0；grid 標記中心 $(L/2)L+L/2$） |
| `run_e1` / `summarize_e1` | 132 / 176 | E1 主流程與冪律擬合（HT vs N、$T_q$ vs N、$T_q$ vs HT） |
| `e2_cases` | 193 | E2 的 grid（$L=6,8$，中心單一標記）與 barbell（$n_{\text{each}}=8,16$，節點 0 為單一標記） |
| `_select_interpolation` | 219 | 對 $s$ 網格取 `interpolated_lower_bound` 的最大峰值，回傳 $(s^\ast,q^\ast)$ |
| `run_e2` / `summarize_e2` | 236 / 299 | E2 主流程：single（seed 0）、independent（seeds 0,1,2）、clustered（seeds 0,1,2） |
| `run_e3` / `summarize_e3` | 325 / 385 | E3：CTQW 與 CRW 軌跡、語意指標、曲線 |
| `run_e4` | 395 | E4 舊讀出（首次越過門檻）＋古典吸收（`E4_metrics.csv`） |
| `e4_readouts(P, option_sets, s, max_steps, threshold, p_detect)` | 471 | **E4 新讀出的核心**：回傳四種讀出的選擇、時間、已決定質量 |
| `run_e4_robustness` / `summarize_e4_robustness` | 533 / 586 | 穩健性掃描（變體：nominal、laziness、jitter）與 spread |
| `e5_case` | 618 | 建立 E5 的圖、cue、targets |
| `run_e5` / `summarize_e5` | 633 / 720 | E5 主流程：讀出與偵測曲線、時間平均、CV、最佳 $p$ |
| `run_e2_adversarial` | 753 | 對抗式環面的 HT、HT^+，並只對 $L\le18$ 模擬 $W(s)$ |
| `_json_ready` | 798 | 把 numpy 型別轉成 JSON 可接受的 Python 型別 |
| `run(config, experiments, only)` | 812 | 依 `--only` 執行，寫入 `results/` 與 `figures/` |
| `parse_args` / `main` | 936 / 944 | 命令列入口。預設 `--config configs/base.yaml --experiments configs/experiments.yaml` |

**相對路徑的陷阱**：`parse_args` 的預設值是相對路徑（`Path("configs/base.yaml")`），因此必須在 `code/` 目錄下執行 `python -m src.experiments`。在其他目錄執行會找不到設定檔。`run()` 內部用 `Path(config_path).resolve().parent.parent` 推算根目錄，所以輸出位置相對於 `code/`。

**`--only` 的語意**：`selected = set(only) if only else {"E1",...,"E5"}`。`--only E4` 會同時跑 E4 主流程與穩健性掃描（後者最耗時）。

**輸出格式**：CSV 用 `float_format="%.8g"`；JSON 用 `indent=2`。E4 主流程寫的是 `E4_metrics.csv`，穩健性寫的是 `E4_robustness.csv`；前者只含舊讀出與古典，後者含全部四種讀出（詳見第 5 章 E4）。

## 第 5 章　五個實驗 E1–E5

每個實驗依序列出：動機 → 對應 RQ／假說 → 設定（來自 `experiments.yaml`）→ 程式路徑 → 輸出檔與欄位 → 結果數字 → 圖怎麼看 → 結論與限制 → 老師可能的追問。

數字來源標示：**[CSV]** 表示我直接從 `code/results/raw/*.csv` 核對過；**[論文]** 表示取自論文表格或文字，本次寫作未重新計算（待確認）。

### 5.1 E1：古典 vs 量子縮放

**動機與假說**：RQ1 與預測 1。若量子搜尋時間隨 $\sqrt{\HT}$ 成長，那麼在 $\log$-$\log$ 圖上，$T_q$ 對 $\HT$ 的斜率應約為 $1/2$。

**設定**（`experiments.yaml` 的 E1）：complete $N\in\{8,16,32,64\}$、cycle $N\in\{8,16,32,64\}$、grid $L\in\{4,6,8,10\}$、hypercube $d\in\{3,4,5,6\}$；單一標記；無噪聲。全部使用 `walk.laziness=0.1`。

**程式路徑**：`experiments.run_e1`（第 132 行）→ 對每個 case：

1. `P = walk_transition(graph)`（lazy）。
2. `HT = mean_hitting_time(P, [marked])`；`ht_nonlazy` 用未 lazy 的矩陣算，檢查比值為 $1/(1-\eta)$。
3. `gap = spectral_gap(P)`；`phase_gap(P)`。
4. `max_steps = ceil(3·sqrt(HT)) + 5`。
5. 對 $s\in$ 網格，`interpolated_lower_bound` 取峰值，選 $s^\ast$ 使峰值最大。
6. `curve = interpolated_success_curve(P, [marked], s*, max_steps)`；`t_q = argmax(curve[1:]) + 1`；`speedup = HT / t_q`。

**輸出**：`results/raw/E1_scaling.csv`（16 列，欄位含 `family, parameter, N, marked, HT, spectral_gap, phase_gap, HT_lazy_ratio, s, t_q, p_max, q_max, max_steps, speedup`）；`results/processed/E1_scaling.json`（各族的 $N$、HT、$T_q$、$p_{\max}$、speedup 與三個擬合）；`figures/E1_scaling.pdf/.png`、`figures/E1_speedup.pdf/.png`。

**結果**：

- [CSV] `HT_lazy_ratio` 全為 1.1111 $=1/(1-0.1)$。
- [CSV] $p_{\max}$ 範圍 0.8417（grid $L=4$）到 0.99985（$K_8$）。論文寫「0.84 到 1.00」，一致。
- [CSV] hypercube 的 $T_q\in\{6,8,11,16\}$，與論文一致。
- [CSV] hypercube 的 `spectral_gap` 全為 0.2（$=2\eta$），`phase_gap` 為 0.6、0.45、0.36、0.30，等於 $1.8/d$。
- [CSV] 最大 speedup：$K_N$ 4.67、cycle 11.67、grid 7.93、hypercube 5.35。論文表格 4.7、11.7、7.9、5.4，一致。
- [論文] 指數表：$\HT\sim N^\alpha$ 的 $\alpha$ 為 1.06、1.95、1.26、1.07；$T_q\sim\HT^\gamma$ 的 $\gamma$ 為 0.50、0.52、0.48、0.44。本次沒有重新做 OLS 擬合（待確認：可由 `E1_scaling.json` 的 `fit_tq_vs_HT` 核對）。

**圖怎麼看**（`plotting.plot_e1_scaling`，2×2）：四格分別是 complete、cycle、grid、hypercube。每格以雙對數座標畫兩條線：藍色圓點是古典 $\HT$（`classical HT`），橘色方點是量子 $T_q$（`quantum T_q`），並加上冪律擬合；縱軸單位是 steps。右上角或附註會顯示擬合的指數（待確認：未實際目視確認附註位置）。`plot_e1_speedup` 則是一張圖，縱軸 $\HT/T_q$，灰色虛線在 1。

**結論與限制**：

- 量子 $T_q$ 與 $\sqrt{\HT}$ 的關係在四族上都成立（指數約 0.44–0.52），這支持預測 1。
- **需要修正的論文說法**：論文 `06_results.tex` 第 48 行寫「complete graph and hypercube have $\HT=\Theta(N\log N)$-like behavior」。但完全圖的 $\HT=N-1$（非 lazy）是精確的線性（附錄 `app:hitting` 與測試 `test_complete_graph_hitting_time`）；[CSV] 的 $K_N$ 也只隨 $N$ 線性（$\alpha=1.06$）。hypercube 的 [CSV] $\HT/N$ 為 1.15、1.27、1.32、1.34，接近線性，與 `02_background.tex` 寫的「$N\log N$」不完全一致（待確認：需要更大的 $d$ 才能區分 $N$ 與 $N\log N$）。
- 有限尺寸：每族只有四個點，指數的不確定性很大。hypercube 只有四個整數的 $T_q$ 值，論文自己承認此擬合最不精確。

**老師可能的追問**：

- 「為什麼用 $\HT$ 而不是 $N$？」答：$\HT$ 是古典搜尋難度的直接量度，AGJK 的界以 $\sqrt{\HT}$ 表示；$N$ 只是頂點數，對 cycle 這類圖會誤導。
- 「為什麼 $s$ 要用下界選？」答：下界 $q_t(s)$ 是論文指定的數值協定（Conjecture 3 的檢驗），避免用真實 $p_M$ 做選擇，這樣實際成功曲線仍是獨立的檢驗。但這也代表 $s$ 的選擇有偏差（見第 9 章）。
- 「lazy 會不會改變結論？」答：不會改變指數，只改變常數（HT 乘以 $1/(1-\eta)$；$T_q$ 也會受影響，但 E1 的比值 HT/T_q 仍由 η 的 $s$ 選擇決定，論文未單獨報告 η 的敏感度（待確認））。

### 5.2 E2：單一、獨立與群聚標記；對抗式環面

**動機與假說**：RQ2 與預測 2。獨立目標應比群聚目標容易；$\HT^+\gg\HT$ 只出現在結構化的標記集合上。

**設定**（`experiments.yaml` 的 E2）：

- grid $L\in\{6,8\}$（單一標記在中心）；barbell $n_{\text{each}}\in\{8,16\}$（單一標記在節點 0）。
- 標記型態 single、independent（最遠點取樣，$k=4$）、clustered（BFS，$k=4$），種子 $\{0,1,2\}$。
- 對抗式環面：$L\in\{18,24,30,36\}$，$\eta=0.2$，只模擬 $L\le18$。

**程式路徑**：`run_e2`（第 236 行）→ 每個 (graph, kind, seed) 計算 HT、$\HT^+$（`ht_extended`，$\varepsilon=10^{-6}$）、`_select_interpolation`、`interpolated_success_curve`、$T_q$、speedup。對抗式部分由 `run_e2_adversarial`（第 753 行）處理。

**輸出**：`results/raw/E2_marked.csv`（28 列：四個 case，每個 case 為 single 1 列、independent 3 列、clustered 3 列）、`E2_curves.csv`（每條曲線每個 $t$ 一列）、`E2_adversarial_torus.csv`（4 列）；`processed/E2_marked.json`（依 `family_parameter_kind` 分組的平均）、`processed/E2_adversarial_torus.json`；`figures/E2_success.pdf`、`figures/E2_ht.pdf`。

**結果（[CSV] 核對）**：

| 圖 | 標記 | HT（平均） | $\HT^+$（平均） | 比值 | $T_q$（平均） |
|---|---|---|---|---|---|
| grid $8\times8$ | single | 95.5 | 95.5 | 1.00 | 17.0 |
| grid $8\times8$ | independent | 34.7 | 35.3 | 1.02 | 10.7 |
| grid $8\times8$ | clustered | 79.5 | 85.3 | 1.07 | 20.3 |
| barbell $n=16$ | single | 2558.0 | 2557.9 | 1.00 | 134.0 |
| barbell $n=16$ | independent | 16.8 | 25.4 | 1.52 | 7.0 |
| barbell $n=16$ | clustered | 2478.6 | 2507.4 | 1.01 | 115.3 |

以上都與論文表格一致（我把三個種子的平均重新算過）。

- [CSV] 對抗式環面：$L=18$ 的 HT $=10.33$、$\HT^+=57.13$、比值 5.53，$p_{\max}=0.978$ 於 $t_q=6$；$L=36$ 的比值 8.78。論文寫「5.5 到 8.8」，一致。
- [CSV] 論文的 $N$ 是環面的邊長，程式中的 `length` 即為 $N$（頂點數為 $N^2$）。以邊長平方 $L^2$ 計算，$\HT^+/L^2$ 在 $L=18,24,30,36$ 分別為 0.18、0.26、0.33、0.34。論文 `03_theory.tex` 寫「$\HT^+=\Omega(N^2)$」是漸近陳述。這些數字與它相容，但**只有 $L\le36$ 的數據，無法驗證漸近性**（待確認）。

**重要的實驗設計問題（必須在答辯時說明）**：

1. 「三個隨機標記集合」其實只有兩個不同的集合。grid $6\times6$ 的 seed 0 與 seed 2 完全相同（`30 5 0 21`）；barbell $n=8$ 的 seed 0 與 seed 2 也相同（`20 0 11 14`）。這是 `_farthest_point_sample` 隨機起點的結果（第 4.3 節）。論文的 "mean over three random marked sets" 應改為更精確的描述，或增加種子（待確認：是否要修正論文）。
2. 獨立集合的 HT 差異，部分來自對稱性：barbell $n=8$ 的 seed 0 與 seed 1 得到相同的 HT（7.5887），因為兩個集合在兩個團之間的結構等價。

**圖怎麼看**：

- `E2_success.pdf`（`plot_e2_success`，2×2）：四格是四個 case（grid 6、grid 8、barbell 8、barbell 16）。每格的橫軸是步數 $t$，縱軸是成功機率 $p_M(t)$；三種標記型態各一條線，陰影帶是三個種子的最小到最大範圍（論文 caption 如此描述；待確認陰影實作細節）。
- `E2_ht.pdf`（`plot_e2_ht`，1×2）：左圖是古典 HT（橫軸）對 $\HT^+$（縱軸）的散點，灰色虛線是 $\HT=\HT^+$；右圖是對抗式環面的 HT 與 $\HT^+$ 對 $N$ 的曲線，標籤是比值。

**結論與限制**：

- 獨立標記最容易（8×8 grid 上 HT 從 95.5 降到 34.7）。
- 群聚標記的 HT 介於單一與獨立之間（8×8 grid 上 79.5），並非「與單一幾乎一樣」。論文說「群聚標記行為接近單一目標」，但在 8×8 grid 上 79.5 相對 95.5 差 17%；在 barbell 上則幾乎相同（2478.6 對 2558.0）。這應表述為「在 barbell 上接近；在 grid 上較接近但仍有差別」（待確認論文的措辭是否需要調整）。
- 大的 $\HT^+/\HT$ 只出現在 barbell 獨立集合（1.52）與對抗式環面。論文的 "structural" 結論依賴於對抗式環面，而該環面只模擬到 $L=18$。

**老師可能的追問**：

- 「為什麼 $\HT^+$ 在 barbell 獨立集合上是 1.52？」答：標記點分布在兩個團中，而 $\HT^+$ 考慮的是內插漫步的譜，兩個團之間的瓶頸使得 $\HT^+$ 比 HT 大。這是數值觀察，本文沒有給出解析解（待確認）。
- 「為什麼對抗式環面只模擬 $L=18$？」答：$W(s)$ 是稠密矩陣，$n=324$ 時狀態為 $2n^2\approx2\times10^5$ 維的運算仍可做，但 $L=24$ 以上的 $N$ 在本專題的稠密實作中成本較高（待確認：未量測實際時間）。

### 5.3 E3：語意活化（玩具語意圖）

**動機與假說**：RQ1 與預測 3。語意距離改變活化時序：CTQW 對遠目標有較高峰值，CRW 對近目標有較高早期 AUC。

**設定**：`toy_semantic` 圖（19 頂點，33 邊）；cue `animal`；目標 `dog`（距離 1）與 `violin`（距離 4）；時間窗 $\tau\in[0,8]$（即 $t\in[0,8/\lambda_1]$），1200 個點。

**程式路徑**：`experiments.run_e3`（第 325 行）：

1. `laplacian, degree, _ = normalized_laplacian(graph)`；`gap = spectral_gap(laplacian)`。
2. `max_time = 8.0 / gap`；`times = linspace(0, max_time, 1200)`。
3. 量子：`ctqw_trajectory` 得到振幅，取 $\lvert\cdot\rvert^2$。古典：`crw_trajectory`。
4. 對每個目標與模型，呼叫 `semantic_metrics`，並寫出曲線（`tau = gap * t`）。

**輸出**：`results/raw/E3_semantic_metrics.csv`（4 列）、`E3_semantic_curves.csv`（4800 列 + 表頭）、`processed/E3_semantic.json`（含 `spectral_gap`、`relaxation_time`、所有指標）、`figures/E3_semantic.pdf/.png`。

**結果（[CSV] 核對）**：

- 譜隙 $\lambda_1=1/29.9879\approx0.03335$，四捨五入為 0.0333，與論文一致。（`relaxation_time` 欄位即 $1/\lambda_1$。）弛緩時間 $1/\lambda_1=29.99\approx30.0$。
- 近目標 `dog`：量子 $p_{\text{peak}}=0.2367$（$\tau=4.75$）；古典 $p_{\text{peak}}=0.1581$（$\tau=0.127$）。論文 0.237、4.75、0.158、0.13，一致。
- 近目標 AUC：古典 0.5796、量子 0.4807。論文 0.580 與 0.481，一致。
- 遠目標 `violin`：量子 $p_{\text{peak}}=0.2470$（$\tau=6.86$），AUC 0.3604，峰值處的期望半徑 2.99；古典 $p_{\text{peak}}=0.0455$，AUC 0.3235，半徑 2.36。論文數字一致。

**需要注意的兩件事**：

1. **古典遠目標的「峰值」位於時間窗的右端點**。[CSV] 古典 `violin` 的 `tau_peak = 8.0`，正好是 $\tau_{\max}$。這表示 CRW 在窗內仍單調上升，所謂「峰值 0.046」只是窗內最大值，不是真正的峰。論文說「CRW 只到 0.046，基本上是其平穩值」，平穩值為 $\pi_{\text{violin}}=d_{\text{violin}}/\sum d$（violin 的度數與總度數需由 JSON 或程式核對，待確認），因此「基本上是平穩值」的說法需要以此檢查。
2. **AUC 與半徑依賴時間窗**。AUC 只積分到 $\tau=8$；若改用更長窗，數字會變。論文沒有說明時間窗對 AUC 的敏感度（待確認）。

**圖怎麼看**（`plot_e3_semantic`，2×2 加一張圖）：左上是玩具語意圖（節點依群組上色，`_semantic_group`），其餘格是兩個目標的活化曲線（橫軸 $\tau=\lambda_1 t$，縱軸 $p_T$），藍線與橘線分別是 CRW 與 CTQW（依程式中的 `label` 與顏色）；最後一格（metric 軸）是各模型的峰值活化長條圖。（待確認：未目視確認面板的確切排列。）

**結論與限制**：

- 語意距離效應在本玩具圖上存在，方向與預測 3 一致。
- 遠目標的量子優勢在 $p_{\text{peak}}$ 上（0.247 對 0.046），但古典的「峰」在窗外或窗邊，比較不乾淨。
- 19 個頂點、手工建立的圖；沒有真實語意網路資料（見第 9 章）。

**老師可能的追問**：

- 「為什麼 $\tau$ 要除以 $\lambda_1$？」答：CTQW 與 CRW 的特徵值相同，但時間尺度仍需要對齊。以 $\lambda_1$ 為單位，兩者在同一個弛緩尺度上比較。這是一個規範化選擇，不是唯一選擇。
- 「為什麼用 $1200$ 個時間點？」答：是 `experiments.yaml` 的設定。它決定峰值位置的解析度，約為 $8/(1200\lambda_1)$ 的時間步長（待確認：未測試對解析度的敏感度）。

### 5.4 E4：多選項決策與選項耦合

**動機與假說**：RQ2 的決策部分與預測 2 的情境效應。耦合兩個選項（相似性）後，量子選擇應偏向未耦合選項，古典則不應如此（在對稱圖上）。

**設定**（`experiments.yaml` 的 E4）：

- 三個案例：`symmetric3`（分支長 $(4,4,4)$）、`asymmetric3`（$(3,4,5)$）、`symmetric4`（$(4,4,4,4)$）。耦合對都是 `[1,2]`（分支 1 與 2）。
- 耦合網格 $c\in\{0,0.1,0.25,0.5,0.75,1,2\}$。
- $s=0.9$，決策門檻 0.5，最大步數 400，全部使用 lazy $\eta=0.1$。
- 穩健性：`detection_probability=0.2`；`laziness_grid=[0,0.05,0.1,0.2]`；`weight_jitter=0.2`；`jitter_seeds=10`。

**四種讀出（`cognitive.py` 與 `experiments.e4_readouts`）**：

| 名稱（程式） | 論文名稱 | 做法 | 時間 |
|---|---|---|---|
| `quantum_threshold` | First crossing | 在 $\sum_i p_i(t)$ 第一次 $\ge0.5$ 的時刻取歸一化的 $p_i$（`decision_summary`） | 該時刻索引 |
| `quantum_average` | Random stopping | $P_i\propto\sum_{t=1}^{400}p_i(t)$（`time_averaged_choice`） | 無（NaN） |
| `quantum_detect` | Detection | 偵測模型，$p=0.2$：量測落在終端即決定；`final_readout=False` 的首次偵測分布 | 條件平均首次偵測時間 |
| `classical` | Absorption | 吸收隨機漫步的最終吸收機率（`first_passage_summary`） | 條件平均吸收時間 |

**程式路徑**：`run_e4`（第 395 行）產生舊讀出與古典（寫 `E4_metrics.csv`）；`run_e4_robustness`（第 533 行）對每個 (case, c) 跑 15 個變體（nominal 1 個、laziness 4 個，其中 $\eta=0.1$ 與 nominal 重複，jitter 10 個），每個變體用 `e4_readouts` 計算四種讀出，最後寫 `E4_robustness.csv`（1260 列）。`summarize_e4_robustness` 計算每 (readout, case, c) 在非 nominal 變體上的 $P(\text{uncoupled})$ 的 spread（max − min），再對 c 取中位數與最大值。

**輸出**：`E4_metrics.csv`（42 列：3 案例 × 7 耦合 × 2 模型）、`E4_choices.csv`、`E4_curves.csv`（56140 列）、`E4_robustness.csv`（1260 列）、`E4_decision.json`、`E4_robustness.json`、`figures/E4_decision.pdf`、`figures/E4_robustness.pdf`。

**結果（[CSV] 核對 nominal 變體）**：

- **古典、對稱圖**：`symmetric3` 在所有 $c$ 下，三個選項都是 $1/3$（`E4_robustness.csv` 中 `readout=classical`）。`symmetric4` 的古典 $p_{\text{uncoupled}}$ 恆為 0.5（兩個未耦合選項合計）。論文「古典在對稱圖上完全均勻」成立（在吸收讀出下）。
- **量子偵測讀出，`symmetric3`**：$c=0\to2$ 時，未耦合選項 $p_0$ 從 0.3333 升到 0.4993；耦合的兩個選項各降到 0.2503。論文寫「$1/3\to0.499$」「耦合對 0.250 each」，一致。決策時間從 31.1 增至 44.0，論文「31–44」一致。
- **量子隨機停止，`symmetric3`**：$p_0$ 在 $c=2$ 為 0.5798，論文「0.580」一致。
- **量子偵測，`symmetric4`**：未耦合兩選項合計從 0.5000 到 0.6531，論文「0.500 到 0.653」一致。
- **量子偵測，`asymmetric3`**：未耦合短分支從 0.3417 到 0.4705，論文「0.342 到 0.470」一致，且單調。
- **古典，`asymmetric3`**：選項 B（$p_1$）從 0.3191 到 0.5047（論文 0.32 到 0.51，一致）；選項 C（$p_2$）從 0.2553 到 0.0866（論文 0.26 到 0.09，一致）；未耦合 $p_0$ 從 0.4255 到 0.4087（論文 0.426 到 0.409，一致）。
- **量子隨機停止，`asymmetric3`**：未耦合的 $p_{\text{uncoupled}}$ 序列為 0.3331, 0.3426, 0.3395, 0.3769, 0.3758, 0.3860, 0.5061，有一處下降 0.0031（論文說「dips below 0.004」，一致）。
- **舊讀出（first crossing）的不穩定性**：`quantum_threshold` 在 `symmetric3` 的 $p_{\text{uncoupled}}$ 依 $c$ 跳動：$c=0.75$ 時 0.8333（決策時間 351），$c=1$ 時 0.5185（時間 6），$c=2$ 時 0.9898（時間 39）。這正是「相位假象」的例子。
- [論文、待確認] 穩健性 spread：偵測讀出的最大 spread 0.045、古典 0.065（論文以「最大」或「中位數」描述此數字，本次未重新計算，待以 `E4_robustness.json` 的 `spread_by_readout` 核對）；隨機停止的中位數 0.08、最大 0.26；舊讀出的中位數 0.44、最大 0.78。

**代價（時間）**：偵測讀出的決策時間為 31–44 步，古典為 17–27 步（[CSV] nominal 核對：古典 17.0–26.7）。論文解釋：因為每步只有五分之一的機會被量測（$p=0.2$）。

**圖怎麼看**：

- `E4_decision.pdf`（`plot_e4_decision`，2×2 加上決策時間圖）：三個案例各一格，橫軸是耦合 $c$，縱軸是選擇機率（每個選項一條線，灰色虛線是 $1/n$ 的均勻基準）；右下格是決策時間對 $c$（每個 case×模型一條線）。這張圖使用的是**舊讀出與古典**（`run_e4` 的輸出），不是穩健性版本。
- `E4_robustness.pdf`（`plot_e4_robustness`，2×2 加上長條圖）：前三格分別是三個案例，縱軸為 $P(\text{uncoupled})$ 對 $c$，四種讀出各一條線（nominal 是實線，帶狀區域是 laziness 與 jitter 的範圍，灰色虛線是 $(n-2)/n$ 的基準）。右下長條圖是每種讀出的 spread，每種讀出有 median 與 max 兩根長條（待確認：未目視確認圖的外觀）。

**結論與限制**：

- 偵測與隨機停止兩個無相位讀出都顯示「耦合把機率推向未耦合選項」，且在三個案例中單調（偵測讀出在 nominal 上單調，已核對）。
- 古典在對稱圖上不變；在不對稱圖上，耦合主要在耦合對內部重新分配（已核對）。
- **限制**：(1) 只有三個小圖，分支長度 3 至 5；(2) 穩健性只改變 $\eta$ 與邊權，沒有改變圖的拓撲；(3) 「類比相似性效應」是模型層級的類比，不是對人類資料的解釋；(4) 偵測讀出的 $p=0.2$ 是人為選定的，論文沒有掃描它（待確認）。
- 計算成本：穩健性掃描需要 315 次圖的建構與四種讀出的計算。論文說「超過 10 分鐘」，本次未計時（待確認）。

**老師可能的追問**：

- 「為什麼古典不需要 $s$？」答：古典吸收漫步就是 $s=1$ 的極限；$s=0.9$ 只是量子內插參數。古典基準使用的是吸收矩陣，而非內插矩陣（`absorbing_option_curve`）。
- 「偵測讀出是不是只是把古典加上一個量測？」答：不完全是。偵測讀出的未吸收部分仍在量子干涉下演化，只是在 $p$ 機率下被「抽樣」結束。其與古典的差異正是 E4 要測的量。
- 「為什麼要 10 個 jitter 種子？」答：是 `experiments.yaml` 的設定；10 個樣本對 spread 的估計很粗糙，論文沒有給出 spread 的信賴區間（待確認）。

### 5.5 E5：部分量測退相干（偵測與讀出模型）

**動機與假說**：RQ3。是否存在使成功機率最大的部分量測率？在只看單一截止時間時，純量子的結果會受振盪相位影響，因此需要無相位的讀出。

**設定**（`experiments.yaml` 的 E5）：

- 四個案例：`grid_single`（$6\times6$，cue 0 為左上角，target 35 為右下角）、`grid_clustered`（targets 28、29、34、35，即右下角的 $2\times2$ 區塊）、`toy_single`（cue `animal`，target `violin`）、`toy_clustered`（`instrument`、`piano`、`guitar`、`violin`）。
- 測量率 $p\in\{0,0.05,0.1,0.2,0.3,0.5,0.75,1\}$。
- `max_steps=120`；`deadline=20`（舊的單一截止時間，僅供附錄）；`horizons=[20,40,80,120]`；`interpolation_s=0.0`（即 $W(0)$）。
- 注意：`walk_transition` 仍套用 $\eta=0.1$ 的 lazy（`run_e5` 第 649 行），因此「plain Szegedy walk」應讀作「$s=0$、但 $\eta=0.1$ 的 lazy 版本」。README 的說法不完整（見附錄 A）。

**程式路徑**：`run_e5`（第 633 行）：

1. `basis_ensembles(P, targets, s=0, …)` 計算每個起點的位置分布與標記質量。
2. `pure_ensemble(P, targets, s, …, initial=cue)` 計算純路徑。
3. 對每個 $p$：`measurement_curve`（讀出模型）與 `detection_curve`（偵測模型）。
4. 記錄 `p_max`、`t_opt`、`p_deadline`（$T=20$）、`oscillation_index`（$H=120$）、`win_rate`（相對於 $p=0$）、`p_avg_H`（$H\in\{20,40,80,120\}$）、`detect_H`（偵測讀出在 $T=H$ 的值）。

`summarize_e5` 另外給出：(a) 每個案例在 $T=20$ 的最佳 $p$；(b) 每個指標的最佳 $p$（`optimal_by_metric`）。

**輸出**：`E5_sweep.csv`（32 列：4 案例 × 8 個 $p$）、`E5_curves.csv`（3872 列：4 × 8 × 121 個時間點）、`E5_decoherence.json`、`figures/E5_decoherence.pdf`、`figures/E5_robustness.pdf`。

**結果（[CSV] 核對）**：

- **振盪**：`grid_single` 在 $p=0$ 的 `p_max=0.449`，出現在 $t=13$；`p_deadline`（$T=20$）只有 0.0134。論文「0.449 at $T=13$、$T=20$ 時 0.013」，一致。
- **舊的 12 倍結論是相位假象**：`p_deadline_ratio`（$T=20$，相對 $p=0$）在 `grid_single` 上的最大值為 1.63（$p=0.2$）；論文寫「1.6 倍」，一致。舊版的 12 倍來自舊的設定（論文附錄與 `Explain.md` 有描述，本次未重跑舊版）。
- **讀出模型的時間平均（$H=120$）**：`grid_single` 的 $\bar p$ 在 $p=0$ 為 0.0420，為最大；`grid_clustered` 在 $p=0$ 為 0.1562，為最大；`toy_single` 在 $p=0$ 為 0.0376，為最大（與 $p=0.1$ 的 0.0372 接近）；`toy_clustered` 在 $p=0.2$ 為 0.2001，高於 $p=0$ 的 0.1782。論文的表述一致。
- **振盪指數**：`grid_single` 的 `oscillation` 從 $p=0$ 的 1.501 降到 $p=0.2$ 的 0.373。論文 1.50 到 0.37，一致。
- **偵測模型，$T=40$**：`grid_clustered` 在 $p=0$ 為 0.0549，$p=0.2$ 為 0.4548（最佳），$p=1$ 為 0.3256；`toy_clustered` 在 $p=0$ 為 0.1583，$p=0.3$ 為 0.4511（最佳），$p=1$ 為 0.3421。論文的 0.055、0.455、0.326、0.158、0.451、0.342 全部一致。
- **偵測模型，$T=120$**：`grid_clustered` 的最佳 $p=0.3$ 為 0.8619，$p=1$ 為 0.8110；`toy_clustered` 的最佳 $p=0.3$ 為 0.8444，$p=1$ 為 0.7025。論文「0.862 對 0.811」「0.844 對 0.703」一致。
- **單一目標，$T=40$**：`grid_single` 的 $p=0$ 為 0.0205、$p=1$ 為 0.1356、最佳 $p=0.3$ 為 0.1587；`toy_single` 的 $p=0$ 為 0.0388、$p=1$ 為 0.2612（最佳，但 $p=0.75$ 的 0.2506 很接近）。論文表格 E5 的數字一致。
- **峰值表**（論文表 `tab:e5` 的 peak 欄）：`grid_clustered` 0.583 於 $t=12$，`toy_single` 0.198 於 $t=107$，`toy_clustered` 0.394 於 $t=58$，與 `E5_sweep.csv` 的 `p_max` 與 `t_opt` 一致。

[待確認] 以下論文敘述需要曲線資料（`E5_curves.csv` 的 `detect` 欄位）才能完全核對，本次未逐 $T$ 檢查：

- 「偵測模型中，$T\lesssim15$ 時純量子在每個案例都勝出」。
- 「群聚目標在 $T\gtrsim20$ 時 $p^\ast=0.2$–$0.3$，但在 $T=35$ 左右有單步回跳」。
- 「單一目標的 $p^\ast(T)$ 在 grid 上從 0 經 0.2–0.5，於 $T=34$–$36$ 回到 0，$T\ge71$ 為 1」。
- 「語意單一目標在 $13\le T\le85$ 古典最佳，之後與 $p=0.5$ 相差 0.01 以內」。

**圖怎麼看**：

- `E5_decoherence.pdf`（`plot_e5_decoherence`，2×2）：前三格分別是四個案例中的一部分（依 `plot_e5_decoherence` 的迴圈，共四格的成功曲線，每條線是一個 $p$，灰色虛線標示 $T=20$）；第四格（或附圖）為 $T=20$ 的成功機率對 $p$，以及「半最大時間」`t_half_max` 對 $p$。（待確認：確切的格子分配未目視確認。）
- `E5_robustness.pdf`（`plot_e5_robustness`，2×2）：左上是 `grid_single` 的讀出成功率熱圖（縱軸 $p$，橫軸 $T$，白色虛線 $T=20$）；右上是偵測讀出的 $F_p(T)$ 對 $T$（每案例一條線）；左下是最佳 $p^\ast(T)$ 對 $T$（階梯線）；右下是 $T=40$ 的偵測機率對 $p$。（待確認：未目視確認。）

**結論與限制**：

- 讀出模型：量測主要讓曲線變平（振盪指數下降），並不提高峰值。在此模型中，「量測買到的是可預測性，不是成功率」（論文的說法，與數字一致）。
- 偵測模型：純量子的峰值最高，但需要對準時機；中等量測率對群聚目標在 $T\ge20$ 左右較有利；單一目標上，最佳 $p$ 隨 $T$ 往古典方向移動，但不單調。
- 限制：(1) 只有四個案例，兩個是玩具語意圖；(2) 量測模型是投影重設，不是 Lindblad 演化；(3) $p$ 的網格不夠密（0.05、0.1、0.2、0.3、0.5、0.75、1），最佳 $p$ 的數值解析度有限；(4) $\eta=0.1$ 的 lazy 改變了振盪的位置，因此「舊 $T=20$ 結果」與「新結果」的數值不能直接比較。

**老師可能的追問**：

- 「為什麼 $T=20$ 的結果不可靠？」答：純量子的 $p_T$ 是振盪的。若 $T=20$ 落在谷底，所有 $p>0$ 的「增益」只是把谷底抬高，不代表量測有效。讀出模型在 $H=120$ 上取平均，就是為了消除這個相位。
- 「偵測模型的 $F_p(T)$ 為什麼是單調的？」答：偵測後被吸收，`found` 只增不減，因此在 `final_readout=False` 的版本中單調（測試 `test_detection_option_curve_limits` 檢查）。含截止讀取的版本 `detection_curve` 則可能因讀取而非單調。
- 「這與量子搜尋的隨機停止有何關係？」答：讀出模型的 $\bar p(H)$ 正是在 $\{1,\dots,H\}$ 上均勻抽停止時間，與 Grover／量子搜尋在未知最佳時間時的隨機化技巧同構。

---

## 第 6 章　測試

測試位於 `code/tests/`。`conftest.py` 只把 `code/` 加入 `sys.path`，讓 `from src...` 可以匯入。

### 6.1 每個測試檔在保證什麼

| 檔案 | 測試數（依原始碼計數） | 保證的性質 | 為何重要 |
|---|---|---|---|
| `test_quantum.py` | 25 | 么正性（$W$、$W(s)$）、範數守恆、稠密矩陣與 `apply_walk` 一致、判別矩陣為左上區塊、譜隙與 lazy 去除二分圖零隙、lazy 的 $1/(1-\eta)$ 恆等式、內插漫步在 $s=0$ 時的均勻性、標記點放大、Chebyshev 下界 $\le$ 成功曲線、$\HT^+\approx\HT$（單一標記）、對抗式環面的標記數 76 | 整個量子核心的正確性基礎 |
| `test_classical.py` | 8 | 完全圖與圈的 HT 解析式、正則圖的平穩分布、語意圖連通且 $\pi P=\pi$、擊中機率單調、擴散守恆、蒙地卡羅與精確解一致（10%）、獨立集合的大小 | 古典基準的正確性（所有比較的分母） |
| `test_metrics.py` | 7 | 成功指標、冪律擬合（精確恢復指數 2）、熵的均勻上界、選擇機率與 first passage、bootstrap 區間包含樣本平均、負值拒絕、時間平均、振盪指數、勝率 | E1 擬合與 E5 指標 |
| `test_semantic.py` | 5 | 正規化 Laplacian 的譜、CTQW 機率守恆、CRW 機率守恆與收斂到平穩分布、語意指標良定義、語意圖的社群連通 | E3 的物理與數值正確性 |
| `test_decision.py` | 8 | 決策圖結構（13 個節點、terminal 為 $(4,8,12)$）、古典選項曲線單調且最終為 1、量子選項曲線有界、`decision_summary` 的首次越過、偵測極限（$p=0$ 等於量子、偵測和等於 `detection_curve`、非遞減）、重疊選項拒絕、`time_averaged_choice` 與 `first_passage_summary` 的數值、抖動的種子與範圍 | E4 的全部讀出 |
| `test_noise.py` | 7 | 基底系綜是機率分布、$p=1$ 讀出等於古典、$p=0$ 讀出等於純量子、有界、偵測 $p=0$ 等於純量子讀出、$p=1$ 偵測等於古典 first passage、偵測 $\ge$ 讀出 | E5 的遞迴正確性（最重要的測試之一） |
| `test_experiments.py` | 1 | `walk_transition` 使用設定的 $\eta$ 且對角為 $\eta$ | 確保 lazy 入口正確 |

合計 61 個測試（依原始碼計數）。**論文 `05_methods.tex` 的 61 與此相符；附錄 `appendix.tex` 寫的 47 與原始碼不符**（見附錄 A）。以 `python -m pytest --collect-only -q` 確認（待確認：本次沒有執行測試）。

### 6.2 三個最關鍵的「交叉驗證」測試

1. `test_walk_matrix_is_unitary` 與 `test_apply_walk_matches_dense_matrix`：用獨立的稠密矩陣實作檢查 `apply_walk` 的區塊實作。若區塊的索引順序寫錯，這兩個會失敗。
2. `test_fully_measured_detection_is_classical_first_passage`：用吸收矩陣計算古典 first passage，與偵測遞迴在 $p=1$ 的輸出比較。這同時檢查了遞迴的時間慣例與 `found` 的累加。
3. `test_zero_measurement_is_pure_quantum_walk` 與 `test_detection_without_measurement_is_pure_readout`：檢查 $p=0$ 時遞迴退化成純量子。

### 6.3 測試未覆蓋的部分

- `experiments.py` 的主流程（`run_e1`、`run_e2`、…、`run_e5`）幾乎沒有測試（只有 `walk_transition`）。實驗輸出的正確性是靠 CSV 與論文數字的交叉核對，而非單元測試。
- `interpolated_lower_bound` 與 `ht_spectral` 的跳過門檻（`1e-12`）沒有直接測試。
- `interpolated_walk` 在 $s=0$ 與 `szegedy.apply_walk` 一致性的測試缺失（待確認；可補）。
- 語意圖的平穩分布與 `semantic_metrics` 的數值（如 `expected_radius_peak`）只檢查「非負」等弱性質。

---

## 第 7 章　如何重現

### 7.1 環境

```bash
cd Final/code
mamba env create -f environment.yml     # Python 3.12 與 numpy>=2、networkx>=3.3 等
mamba activate qwalk-cognition
# 或：pip install -r requirements.txt
```

本次寫作時檢查到的本機套件版本為 numpy 2.5.4、pandas 3.0.6、networkx 3.7、matplotlib 3.11.2、pytest 9.1.1（Python 直譯器版本未記錄），與 `environment.yml` 的下限不完全相同（待確認：版本差異是否影響輸出的 `%.8g` 精度；論文表格的數字與 CSV 一致，因此目前看不出影響）。

### 7.2 測試

```bash
cd Final/code
python -m pytest -q
```

預期：61 個測試（依原始碼計數，待確認）。本次撰寫時未執行，故未驗證通過與否。

### 7.3 實驗（必須在 `code/` 下執行）

```bash
python -m src.experiments --only E1
python -m src.experiments --only E2
python -m src.experiments --only E3
python -m src.experiments --only E4     # 含穩健性掃描，最耗時
python -m src.experiments --only E5
python -m src.experiments                # 全部 E1–E5
python -m src.experiments --only E1 E3   # 多個實驗可以同時列出
```

各實驗的大致耗時：

| 實驗 | 估計 | 來源 |
|---|---|---|
| E1 | 數秒到數十秒 | 對 16 個 case 各做 $s$ 網格（13 個值）的下界掃描與一次 $W(s)$ |
| E2 | 數十秒 | 27 個 (graph, kind, seed) × $s$ 網格；對抗式環面只模擬 $L=18$ |
| E3 | 小於 1 秒 | $n=19$，1200 時間點 |
| E4 主流程 | 數秒 | 42 條曲線，$T=400$ |
| E4 穩健性 | 論文說超過 10 分鐘（待確認：本次未計時） | 315 次圖建構 × 四種讀出；每次含 `basis_ensembles` |
| E5 | 數十秒（待確認） | 4 案例 × 8 個 $p$；`basis_ensembles` 只算一次 |

（時間估計為依演算法複雜度推估，不是實測。）

### 7.4 如何改參數

- **改實驗範圍**：編輯 `code/configs/experiments.yaml`，例如把 E1 的 `complete.n` 改為 `[8,16,32,64,128]`。注意 `walk_operator_blocks` 的成本為 $O(n^3)$，$n=128$ 時約 $2\times10^6$ 個複數，仍可接受，但 `interpolated_success_curve` 每步是 $O(n^3)$（待確認）。
- **改 lazy**：編輯 `base.yaml` 的 `walk.laziness`。它影響 E1、E2（grid、barbell）、E4、E5；E2 對抗式環面**不使用**此值，而用 `experiments.yaml` 的 `adversarial_torus.laziness`。
- **改隨機種子**：編輯 `experiments.yaml` 的 `seeds`（E2）或 `robustness.jitter_seeds`（E4）。注意 `base.yaml` 的 `seed` 目前是否被讀取需確認（見第 3.4 節）。
- **改 $s$ 網格**：`base.yaml` 的 `agjk.interpolation_grid`。這會影響 E1、E2 的 $s^\ast$ 與 $T_q$。
- **改 E5 的測量率**：`experiments.yaml` 的 `measurement_probabilities`。注意此處的值與 `base.yaml` 的 `noise.measurement_probabilities` 不同，程式只讀前者。

---

## 第 8 章　論文逐節導讀

論文位於 `report/main.tex`，章節檔在 `report/sections/`。

| 節 | 檔案 | 主要主張 | 依據 | 措辭注意 |
|---|---|---|---|---|
| 摘要 | `main.tex` 第 46–68 行 | $T_q\sim\HT^{0.44\text{–}0.52}$；獨立目標較易；大的 $\HT^+$ 只在對抗式環面；E3、E4、E5 三項結論 | 第 5 章各實驗 | 「process-level」與「不主張生物量子優勢」的限定有明確寫出，這是正確的 |
| 1 Introduction | `01_introduction.tex` | 三個 RQ、四項貢獻、論文結構 | 無 | 貢獻 2 寫「clustered targets behave like a single target」，與 E2 數字（8×8 grid 79.5 vs 95.5）有差距，建議改寫（見第 5.2 節） |
| 2 Background | `02_background.tex` | 古典擊中時間、Szegedy、AGJK、量子認知文獻表（表 `tab:literature`） | 文獻 | 「hypercube behaves like $N\log N$」與 E1 數據（近線性）不完全一致（待確認） |
| 3 Theory | `03_theory.tex` | 判別矩陣的譜、HT 與 $\HT^+$ 的定義、對抗式環面、內插漫步、部分量測通道、CTQW/CRW | 數學推導與 AGJK | 「$\HT=\widetilde O(d^2)$，$\HT^+=\Omega(N^2)$」是漸近陳述，數值只到 $L=36$（見第 5.2 節） |
| 4 Cognitive model | `04_cognitive_model.tex` | 對應表、五條假設、反應時間與選擇機率定義、相似性與語意距離、四個可測試預測 | 定義 | 預測 3 寫「古典有較高的早期 AUC」，數字 0.580 對 0.481 一致 |
| 5 Methods | `05_methods.tex` | 圖族、lazy 協定、HT 計算、AGJK 協定、語意協定、決策四讀出、部分量測協定、61 個測試 | 程式 | 「E2b 的 $\HT^+/\HT$」與 E2 表的標示一致；「61 tests」與原始碼一致 |
| 6 Results | `06_results.tex` | E1 指數表、E2 表與對抗式結果、E3 數字、E4 讀出比較、E5 讀出與偵測、總結 | `results/` | 第 48 行「complete graph ... $\Theta(N\log N)$-like」與完全圖 $\HT=N-1$ 矛盾（需修正）；「three random marked sets」只有兩個不同集合（需修正） |
| 7 Discussion | `07_discussion.tex` | 發現、文獻關係、生物學不宣稱、限制、未來工作 | 前述 | 「noise can help at intermediate levels」與文獻比較：措辭合理但「consistent with the broader literature」是寬鬆的說法（待確認） |
| 8 Conclusion | `08_conclusion.tex` | 三點總結 | 前述 | 第 13 行的一句過長，格式可調整 |
| 附錄 | `appendix.tex` | HT 解析式（完全圖、圈）、判別矩陣恆等式、測量系綜遞迴、偵測遞迴、額外 E1 speedup、完整 E2 表、重現指令 | 程式與推導 | 「47 passing tests」與原始碼的 61 不符（需修正） |

另外：`main.tex` 的作者欄位仍是 `[Student Name 1] [Student ID 1]`（佔位符），提交前需要填寫（待確認）。`report/figures/` 內的圖（`fig_e1_scaling.pdf` 等）與 `code/figures/`（`E1_scaling.pdf` 等）是兩組檔案，本次未比對兩組是否內容相同（待確認）。

---

## 第 9 章　已知限制、開放問題與未來工作

### 9.1 技術限制

1. **Conjecture 3 而非證明的 AGJK 演算法**：實驗只驗證 Algorithm 1（簡單版本）的數值行為，不是 $\widetilde O(\sqrt{\HT})$ 的完整版本（快速前饋）。論文明確寫出這點。
2. **$s$ 的選擇依賴下界**：`_select_interpolation` 用 `interpolated_lower_bound` 的峰值選 $s$，而非真實的 $p_M$。這會影響 $T_q$ 的常數（論文說指數穩定，但未量化）。
3. **有限尺寸**：最大的圖約 $10^2$ 個頂點（grid $10\times10$）、對抗式環面 $L\le18$ 模擬。指數估計來自 4 個點，不確定性大。
4. **獨立標記的種子問題**：三個種子只產生兩個不同集合（第 4.3 節、第 5.2 節）。
5. **E3 的時間窗**：古典遠目標的峰值在窗邊（$\tau=8$），AUC 依窗而定。
6. **E4 的 $p=0.2$**：偵測讀出的量測率是人為設定，未掃描。
7. **E5 的 $\eta$**：$\eta=0.1$ 改變了振盪位置，使早期的 $T=20$ 結果不能直接比較。
8. **投影量測而非 Lindblad**：E5 的噪聲模型是離散重設，不是開放系統的主方程。

### 9.2 開放問題（與論文呼應）

- $\HT^+=\Omega(N^2)$ 在更大的 $L$ 上是否成立？需要更高效的 $\HT^+$ 計算（目前是稠密的譜分解）。
- 獨立標記的 $\HT^+/\HT$ 在 barbell 上為何達 1.52？是否有解析解？
- 偵測讀出的最佳 $p$ 是否與圖的譜隙有可解釋的關係？
- 相似性效應的量子模型是否能擬合真實的選擇資料？（需要行為資料，論文未做。）

### 9.3 未來工作（論文 `07_discussion.tex` 第 130–140 行）

1. 以 ConceptNet 子圖取代玩具語意圖。
2. 以耦合參數作為自由的相似性參數，擬合行為資料。
3. 以 Lindblad 方程或連續退相干模型取代投影量測。
4. 在小型量子電路模擬器上實作決策圖，測試情境效應在雜訊下是否存活。
5. 更大的決策圖研究：分支長度、耦合模式、偵測讀出的量測率。

---

## 第 10 章　名詞對照表與符號表

### 10.1 名詞對照

| 中文 | 英文 | 本文用法 |
|---|---|---|
| 量子漫步 | quantum walk | 離散時間（Szegedy）與連續時間（CTQW） |
| 連續時間隨機漫步 | continuous-time random walk, CRW | E3 的古典基準 |
| 擊中時間 | hitting time, $\HT$ | 從平穩分布到標記集合的條件期望 |
| 擴充擊中時間 | extended hitting time, $\HT^+$ | AGJK 的內插極限 |
| 判別矩陣 | discriminant matrix, $D$ | $\sqrt{P\circ P^\top}$ |
| 譜隙 | spectral gap | $1-\max_{i\ge2}\lvert\lambda_i\rvert$ |
| 相位隙 | phase gap | $1-\lambda_2$ |
| 惰性漫步 | lazy walk | $P_\eta=(1-\eta)P+\eta I$ |
| 內插漫步 | interpolated walk | $P(s)=(1-s)P+sP'$ |
| 吸收漫步 | absorbing walk | 標記點為吸收態 |
| 偵測 | detection | 判斷有無標記點 |
| 尋找 | finding | 取得標記點的位置 |
| 對抗式環面 | adversarial torus | AGJK 的反例構造 |
| 部分量測 | partial measurement | E5 的重設模型 |
| 退相干 | decoherence | 振幅干涉的衰減 |
| 讀出模型 | readout model | E5：只重設，在 $T$ 讀一次 |
| 偵測模型 | detection model | E5：量測落在標記即結束 |
| 隨機停止 | random stopping | 在 $\{1,\dots,H\}$ 上均勻抽時間 |
| 首次越過 | first crossing | E4 舊讀出 |
| 首次通過時間 | first passage time | 古典吸收的 $\Pr[\tau\le T]$ |
| 相似性效應 | similarity effect | 認知科學中的決策現象（模型中以耦合類比） |
| 情境效應 | context effect | 選項集合改變的選擇偏移 |
| 過程層級 | process-level | 模型只描述統計過程，不描述實現 |
| 量子認知 | quantum cognition | 以量子機率描述判斷與決策的研究綱領 |

### 10.2 符號表

| 符號 | 意義 | 程式對應 |
|---|---|---|
| $P$ | 轉移矩陣（列隨機） | `transition_matrix` |
| $P_\eta$ | lazy 轉移矩陣 | `lazy_transition_matrix`、`walk_transition` |
| $\pi$ | 平穩分布 | `stationary_distribution` |
| $M$ | 標記集合 | `marked` |
| $U=V\setminus M$ | 非標記頂點 | `free`（在 `hitting_times` 中） |
| $p_M$ | $\sum_{x\in M}\pi_x$ | `stationary[marked].sum()` |
| $h_x$ | 從 $x$ 出發的期望擊中時間 | `hitting_times` 的回傳值 |
| $\HT$ | 古典擊中時間 | `mean_hitting_time` |
| $D$ | 判別矩陣 | `discriminant_matrix` |
| $W(P)$、$W(s)$ | Szegedy 漫步、內插漫步 | `apply_walk`、`apply_interpolated_walk` |
| $V(P)$ | 準備態么正 | `apply_v`、`walk_operator_blocks` |
| $\mathrm{Ref}$、$\mathrm{Shift}$ | 反射、交換 | `apply_reflection`、`apply_interpolated_shift` |
| $C(s)$ | qubit 硬幣 | `_coin` |
| $s$ | 內插參數 | `interpolated_*` 的 `s` |
| $\HT(s)$、$\HT^+$ | 內插的擊中時間與極限 | `ht_spectral`、`ht_extended` |
| $q_t(s)$ | Chebyshev 下界 | `interpolated_lower_bound` |
| $p_M(t)$ | 時刻 $t$ 在 $M$ 上的成功機率 | `interpolated_success_curve` |
| $T_q$ | 峰值時間 $\arg\max_t p_M(t)$ | `t_q` |
| $\eta$ | lazy 參數 | `walk.laziness` |
| $p$（E5） | 量測機率 | `measurement_probability` |
| $q_0$、$q_{x,a}$ | 未量測權重、最近重設在 $x$ 且年齡 $a$ 的權重 | `measurement_curve` 的 `q0`、`q` |
| $\mu_{x,a}$、$s_{x,a}$ | 基底系綜的位置分布與標記質量 | `positions`、`success` |
| $F_p(T)$ | 偵測模型在 $T$ 的找到機率 | `detection_curve` |
| $\tau=\lambda_1t$ | 無因次時間（E3） | `gap * times` |
| $L_{\mathrm{sym}}$、$L_{\mathrm{rw}}$ | 對稱與隨機漫步 Laplacian | `normalized_laplacian`、`random_walk_laplacian` |
| $c$（E4） | 耦合權重 | `coupling` |
| $\delta$（E4） | 權重抖動幅度（0.2） | `weight_jitter` |

---

## 第 11 章　自我檢測題（附參考答案）

以下 15 題。答案依本文與程式、結果檔可以回答。

1. **為什麼要用 lazy walk？** 答：二分圖（cycle 偶數、grid、hypercube）的判別矩陣有特徵值 $-1$，絕對譜隙為 0。lazy 後 $-1\mapsto2\eta-1$，絕對譜隙變為 $2\eta$（$\eta=0.1$ 時為 0.2，E1 CSV 的 hypercube 欄位為 0.2）。同時 $\HT$ 精確乘以 $1/(1-\eta)$。
2. **$D=\sqrt{P\circ P^\top}$ 與 $P$ 的譜有何關係？** 答：可逆鏈中 $D=\mathrm{diag}(\pi)^{1/2}P\,\mathrm{diag}(\pi)^{-1/2}$，兩者相似，譜相同，且 $D$ 對稱。
3. **完全圖 $K_N$ 的 $\HT$ 是多少？為什麼論文說它是 $\Theta(N\log N)$-like 有問題？** 答：$\HT=N-1$（非 lazy），是線性的。論文 `06_results.tex` 第 48 行的說法與附錄與測試不一致，應修正。
4. **偵測讀出的 $p=0$ 與 $p=1$ 分別等於什麼？** 答：$p=0$ 等於純量子漫步在截止時間 $T$ 的讀取（`detection_curve` 回傳 `pure_success`）；$p=1$ 等於古典的 first passage $\Pr[\tau_M\le T]$（`test_fully_measured_detection...`）。
5. **為什麼 E5 在 $T=20$ 比較會有假象？** 答：純量子的 $p_T$ 是振盪的，$T=20$ 落在 $p=0$ 的谷底（$p_{20}=0.013$），而 $p=0$ 的峰在 $T=13$（0.449）。任何 $p>0$ 的「增益」在谷底都會很大。舊版的 12 倍即由此而來。
6. **E4 的 first crossing 讀出為何不可靠？** 答：它在 $\sum_ip_i(t)$ 第一次越過 0.5 的時刻讀取選擇，而該時刻受振盪相位影響。E4 的 `symmetric3` 在 $c=0.75$ 時 $p_{\text{uncoupled}}=0.833$（時間 351），在 $c=1$ 時為 0.519（時間 6），顯示對 $c$ 極度敏感。
7. **古典模型在對稱三選項圖上為何在任何 $c$ 下都均勻？** 答：耦合只在分支 1、2 之間加邊，兩者對稱；選項 0 與 1、2 的吸收機率在古典吸收漫步中保持 $1/3$（[CSV] `E4_robustness.csv` 的 classical 讀出為 0.3333）。
8. **$\HT(s)$ 中為什麼要把標記分量歸零得到 $\sqrt{\pi_U}$？** 答：HT 的定義是從 $U=V\setminus M$ 出發的條件平均，因此只取 $U$ 上的分量。`ht_spectral` 第 72 行。注意 `interpolated_lower_bound` 不歸零，兩者用途不同。
9. **E2 的 `independent` 三個種子為何只有兩個不同的集合？** 答：`_farthest_point_sample` 的隨機起點由種子決定，種子 0 與 2 在 grid $6\times6$ 與 barbell $n=8$ 上給出相同的起點，因而相同的集合（[CSV] 可見 `30 5 0 21` 重複）。
10. **論文 $\HT^+/\HT$ 最大的實驗數字是多少？** 答：對抗式環面 $L=36$ 的 8.78；有限集合中 barbell $n=16$ 獨立集合為 1.52（[CSV]）。
11. **CTQW 與 CRW 為何用同一個時間尺度 $\tau=\lambda_1t$ 比較？** 答：兩者的生成元 $L_{\mathrm{sym}}$ 與 $L_{\mathrm{rw}}$ 有相同的特徵值，因此以 $\lambda_1$ 為單位的時間對齊弛緩尺度（論文 `03_theory.tex` 的陳述）。這是規範化選擇，不是唯一可能的選擇。
12. **E3 中古典遠目標的「峰值」有什麼問題？** 答：[CSV] 顯示其 `tau_peak=8.0`，恰為時間窗右端點。它是窗內最大值而非真正的峰，因此「0.046 基本上是平穩值」的說法需要以平穩分布核對（待確認）。
13. **`measurement_curve` 的時間慣例是什麼？** 答：每一步 $s\to s+1$ 先以機率 $p$ 量測並重設，再做一步漫步。落點分布用的是時刻 $s$ 的狀態；被重設者在 $s+1$ 的年齡為 1。
14. **為什麼偵測模型的質量守恆？** 答：每次量測的質量要嘛被吸收到 `found`，要嘛被重設（`new_q[:,1]` 只取非標記）；讀取時剩下的質量在 $q_0$ 與 $q_{x,a}$ 中。總和為 1（`test_detection_is_bounded_and_dominates_readout` 檢查 $\le1$）。
15. **論文宣稱的「61 個測試」與附錄的「47 個」哪個正確？** 答：依原始碼逐一計數為 61（每個 parametrize 展開計算），與 `05_methods.tex` 一致；附錄的 47 是舊數字。正式確認需以 `pytest --collect-only -q` 執行（待確認）。

---

## 附錄 A　程式、論文與結果之間的不一致（只回報，未修改）

依本次閱讀與核對得到的清單。依嚴重程度排序。

| # | 位置 | 內容 | 依據 | 建議 |
|---|---|---|---|---|
| 1 | `report/sections/06_results.tex` 第 48–49 行 | 「complete graph and hypercube have $\HT=\Theta(N\log N)$-like behavior」 | 完全圖 $\HT=N-1$（附錄、測試）；[CSV] $K_N$ 的 $\alpha=1.06$ | 改為「完全圖線性，hypercube 近線性（$\alpha\approx1.07$）」 **[已修正（先前版本已改）]** |
| 2 | `report/sections/appendix.tex` 第 145 行 | 「currently contains 47 passing tests」 | 原始碼計數 61；`05_methods.tex` 寫 61 | 改為 61 並以實際 pytest 結果為準 **[已修正（appendix.tex 已為 61，pytest 61 passed）]** |
| 3 | `report/sections/06_results.tex` 第 62–63、78–98 行（表與文字） | 「means are over three random marked sets」 | [CSV] 三個種子只有兩個不同集合（grid 6 的 seed 0、2 相同；barbell 8 的 seed 0、2 相同） | 改寫為「三個種子（兩個不同集合）」或增加種子 **[已修正：caption 改為三個種子、部分情況僅兩個不同集合（grid 6、barbell 8、16）]** |
| 4 | `report/sections/02_background.tex` 第 26–27 行 | 「hypercube behaves like $N\log N$」 | [CSV] hypercube 的 $\HT/N$ 為 1.15–1.34，接近線性 | 待確認後改寫 **[已修正：改為 Θ(N)，並引用 HT/N≈1.15–1.34]** |
| 5 | `report/sections/01_introduction.tex` 第 64–65 行（貢獻 2） | 「clustered targets behave like a single target」 | 8×8 grid：群聚 79.5 對單一 95.5（差 17%）；barbell：幾乎相同 | 改為「在 barbell 上接近，在 grid 上較接近」 **[已修正：改為「僅小幅降低（barbell ≈3%、8×8 grid ≈17%）」]** |
| 6 | `report/sections/06_results.tex` 第 142–143（E3）與 `E3_semantic_metrics.csv` | 古典遠目標峰值在窗邊（$\tau=8.0$） | [CSV] `tau_peak=8.0` | 加註「窗內最大值，峰值位於右端點」；AUC 亦依窗而定 |
| 7 | `report/sections/06_results.tex` 第 129–130 行 | 「CRW only reaches 0.046, essentially its stationary value」 | 平穩值需以 violin 的度數核對（待確認） | 核對後保留或修改 |
| 8 | `report/sections/03_theory.tex` 「$\HT^+=\Omega(N^2)$」 | 漸近陳述 | 數值只到 $L=36$，$\HT^+/L^2$ 為 0.18–0.34 | 註明僅為漸近陳述，數值支持有限 **[已修正：註明為 AGJK 漸近陳述，數值 L=18–36 不能確立速率]** |
| 9 | `code/README.md` E5 段落 | 「E5 uses a plain Szegedy walk (s = 0)」 | 程式 `walk_transition` 仍套用 $\eta=0.1$（`experiments.py` 第 649 行） | 補充「並使用 lazy $\eta=0.1$」 **[已修正：README 與 methods 改為 lazy chain P_η(η=0.1) 的 W(0)，即 s=0]** |
| 10 | `code/configs/experiments.yaml` E5 的註解 | 「plain Szegedy walk」 | 同上 | 同上 **[已修正：yaml 加註解]** |
| 11 | `code/configs/base.yaml` 的 `noise.*`、`walk.max_steps`、`walk.success_threshold`、`classical.monte_carlo_samples`、`seed`（待確認） | 欄位是否被讀取 | 本次只確認 `walk.laziness` 與 `paths` 被讀取；其餘未在 `experiments.py` 中看到讀取（待 grep 確認） | 若未使用，應標註為文件用途或刪除，以免誤導 |
| 12 | `code/src/agjk.py` `interpolated_stationary`、`code/src/graphs.py` `random_regular_graph`、`line_decision_graph`、`multi_branch_decision_graph`、`code/src/cognitive.py` `activation_curve`、`choice_probabilities`、`response_time` | 主流程未呼叫（待確認） | 目前只有測試或文件用途 | 標註或移除（不屬於本次修改範圍） |
| 13 | `code/src/semantic.py` `crw_trajectory` | 使用 `clip` 後歸一化，不是嚴格的 $p_0e^{-tL_{\mathrm{rw}}}$ | 程式第 65–66 行 | 在論文 methods 或程式註解中說明 |
| 14 | `report/main.tex` 作者欄位 | `[Student Name 1]` 等佔位符 | 原始檔 | 提交前填寫 **[保留：作者名單未定，佔位符不填]** |
| 15 | `report/figures/` 與 `code/figures/` | 兩組檔案 | 本次未比對內容 | 確認論文引用的版本是最新的（待確認） |
| 16 | `report/RESULTS_SUMMARY.md`、`Explain.md`、`Result.md`、`weekly_log.md` | 舊數字（E4、E5 的舊結論、12 倍） | 依任務說明已過時 | 不要引用，或加上「已過時」標記 |
| 17 | `report/sections/06_results.tex` 第 155–156 行的 E4 spread（0.045、0.065、0.08、0.26、0.44、0.78） | 未在本次逐一核對 | 應以 `results/processed/E4_robustness.json` 與舊讀出的 spread 核對 | 核對後保留 |

---

**未完成項目**（誠實標示）：

- 未執行 `pytest`，測試數 61 為原始碼計數，非實際執行結果。
- 未逐一核對 E5 的 $T$ 相關敘述（第 5.5 節的待確認清單）。
- 未核對 E4 的 spread 統計（第 5.4 節的待確認項）。
- 未目視檢查任何圖（所有圖的描述來自 `plotting.py` 的標籤與結構，標為待確認）。
- 未計時實驗耗時（第 7.3 節為依演算法推估）。
