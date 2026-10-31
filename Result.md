# Result.md：實驗結果與討論（鉅細靡遺版）

> **更新說明（2026-10-31）**：本文件的 E1/E2 數字、§5（E4）與 §6（E5）已依統一的 lazy walk（$\eta=0.1$）與新版讀出模型更新。舊版「E5 在 deadline $T=20$ 時 $p\approx0.2$ 最佳、最高 $12\times$」與「E4 非單調選擇機率」兩項結論已撤回。新版完整解說見 `Explain_v2.md`；以論文與 `code/results/` 為準。

> 這份文件只做一件事：把這個專案**所有的實驗結果**講清楚，並且解釋它們代表什麼、不代表什麼。
>
> 如果你還沒讀過 `Explain.md`，建議先讀它的 §0–§4，知道什麼是 Szegedy walk、AGJK、`HT`、`HT⁺`。
> 如果你已經知道那些名詞，這份文件可以獨立閱讀。
>
> 閱讀方式：
> 1. 先看 §1 的總覽與指標字典。
> 2. 再依序看 E1–E5；每個實驗都有「問題 → 設定 → 數字 → 圖怎麼看 → 代表什麼 → 不代表什麼」。
> 3. 最後看 §7–§8 的綜合討論、H1–H4 評估、限制與 future work。
> 4. 附錄有全部數字、重現指令、圖表對照與 FAQ。

---

## 目錄

- [1. 實驗總覽與指標字典](#1-實驗總覽與指標字典)
- [2. E1：Classical vs quantum scaling](#2-e1classical-vs-quantum-scaling)
- [3. E2：Single vs independent vs clustered marked vertices](#3-e2single-vs-independent-vs-clustered-marked-vertices)
- [4. E3：Toy semantic graph 的 target activation](#4-e3toy-semantic-graph-的-target-activation)
- [5. E4：Multi-alternative decision under coupling](#5-e4multi-alternative-decision-under-coupling)
- [6. E5：Partial measurement / decoherence sweep](#6-e5partial-measurement--decoherence-sweep)
- [7. 跨實驗綜合：RQ1–RQ3 與 H1–H4](#7-跨實驗綜合rq1rq3-與-h1h4)
- [8. Discussion：這些結果到底說明了什麼](#8-discussion這些結果到底說明了什麼)
- [9. 結論](#9-結論)
- [附錄 A：全部數字](#附錄-a全部數字)
- [附錄 B：重現指令與檔案對照](#附錄-b重現指令與檔案對照)
- [附錄 C：圖表對照與 caption](#附錄-c圖表對照與-caption)
- [附錄 D：結果相關 FAQ](#附錄-d結果相關-faq)

---

## 1. 實驗總覽與指標字典

### 1.1 五個實驗一句話

| ID | 一句話 | 主要問題 |
|---|---|---|
| E1 | 在四種合成圖上比較 classical hitting time 與 quantum search time | 量子搜尋時間是否 scaling 成 $\sqrt{\mathrm{HT}}$？ |
| E2 | 比較 single / independent / clustered marked sets，並計算 $\mathrm{HT}^+$ | 多個目標會變難還是變簡單？$\mathrm{HT}^+$ 何時會爆炸？ |
| E3 | 在 toy semantic graph 上比較 CTQW 與 CRW 的目標活化 | 語意距離如何改變活化時間與峰值？ |
| E4 | 在 multi-branch decision graph 上掃描選項耦合強度 | 選項相似度如何改變選擇機率與決策時間？ |
| E5 | 在 grid 與 toy graph 上掃描 partial measurement rate $p$ | 雜訊會侵蝕還是幫助量子優勢？是否存在最佳 $p$？ |

### 1.2 五個實驗的共同邏輯

每個實驗都遵循同一個模板：

1. **建一個圖**：圖的頂點是概念、狀態或選項。
2. **指定 marked set**：目標記憶、決策邊界、或 option terminal。
3. **選一個 initial state**：stationary distribution、cue vertex、或 hub。
4. **跑古典與量子兩個版本**：
   - 古典：Markov random walk、absorbing walk、或 CRW。
   - 量子：Szegedy walk、interpolated walk、或 CTQW。
5. **定義一個「成功」或「活化」的曲線**：
   - E1/E2：$p_M(t)$，marked 的機率。
   - E3：$p_T(t)$，target 的活化。
   - E4：$p_i(t)$，各 option 的機率。
   - E5：$p_M(t)$，在測量雜訊下的 marked 機率。
6. **從曲線抽出指標**：$p_{\max}$、$T_q$、$t_{\text{opt}}$、AUC、decision time、choice probability。
7. **比較、畫圖、放進報告**。

### 1.3 指標字典（先看這裡，後面才不會迷路）

| 指標 | 定義 | 白話 |
|---|---|---|
| $\mathrm{HT}$ | classical hitting time | 古典平均要走幾步才找到目標 |
| $\mathrm{HT}^+$ | AGJK extended hitting time | interpolated walk 的 effective hitting time；多目標時可能變大 |
| $p_M(t)$ | marked probability at time $t$ | 在時間 $t$，walker 在 marked set 的機率 |
| $p_{\max}$ | $\max_t p_M(t)$ | 整條曲線的最高點 |
| $T_q$ | $\arg\max_t p_M(t)$ | 量子搜尋時間；用峰值時間定義 |
| $t_{\text{opt}}$ | 同上，E1/E2 的欄位名稱 | 峰值時間 |
| $t_{\text{threshold}}$ | 第一次 $p_M(t)\ge0.5$ 的時間 | 達到門檻的時間 |
| speedup | $\mathrm{HT}/T_q$ | 量子比古典快幾倍 |
| $p_{\text{deadline}}$ | 固定 deadline $T$ 的 success probability | deadline 下的成功率 |
| $t_{\text{half-max}}$ | 第一次 $p_M(t)\ge0.5p_{\max}$ 的時間 | 達到半高峯的時間 |
| AUC | $\int p_T(t)\,dt$ | 整體活化量 |
| entropy | $-\sum_i p_i\log_2p_i$ | 分布有多分散 |
| coverage | 峰值時 $p_i\ge0.5p_{\text{peak}}$ 的節點比例 | 活化範圍 |
| expected radius | 峰值時離 cue 的期望距離 | 活化跑得多遠 |
| choice probability $P_i$ | decision time 時 option $i$ 的相對機率 | 選項被選中的機率 |
| decision time | 總選項機率第一次 $\ge0.5$ 的時間 | 做出決定的時間 |
| choice entropy | 選擇分布的熵 | 選擇有多集中 |
| choice bias | $\max_iP_i-1/k$ | 偏離均勻的程度 |

### 1.4 資料與圖表在哪裡

- 原始數據：`code/results/raw/`（CSV）。
- 整理後數據：`code/results/processed/`（JSON）。
- 實驗圖：`code/figures/`（PDF/PNG）。
- 報告用圖：`report/figures/`（PDF）。
- 數字摘要：`report/RESULTS_SUMMARY.md`。

---

## 2. E1：Classical vs quantum scaling

### 2.1 問題

> 量子搜尋時間 $T_q$ 是否隨著古典 hitting time $\mathrm{HT}$ 的平方根成長？

如果 AGJK 的 $\widetilde O(\sqrt{\mathrm{HT}})$ 在數值上成立，我們應該看到

$$
T_q \sim \mathrm{HT}^{1/2}
$$

也就是在 log-log 圖上，$T_q$ 對 $\mathrm{HT}$ 的斜率接近 $0.5$。

### 2.2 設定

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
- 時間窗口：$t\le3\sqrt{\mathrm{HT}}+5$。

### 2.3 數字

| Family | $\mathrm{HT}\sim N^\alpha$ | $T_q\sim N^\beta$ | $T_q\sim\mathrm{HT}^\gamma$ | max speedup |
|---|---:|---:|---:|---:|
| Complete $K_N$ | 1.06 | 0.53 | 0.50 | 4.7 |
| Cycle $C_N$ | 1.95 | 1.02 | 0.52 | 11.7 |
| 2D grid $L\times L$ | 1.26 | 0.61 | 0.48 | 7.9 |
| Hypercube $Q_d$ | 1.07 | 0.47 | 0.44 | 5.4 |

$p_{\max}$ 在所有 16 個 instance 中介於 $0.84$ 和 $0.99$。

### 2.4 圖怎麼看

Figure 2（`fig_e1_scaling.pdf`）是 2×2 的 log-log 圖：

- 橫軸：$N$。
- 縱軸：steps。
- 藍線：classical $\mathrm{HT}$。
- 橘線：quantum $T_q$。
- 每個 panel 的左上角有 fit 出來的 exponent。

如果你只記一件事：

> 橘線的斜率大約是藍線斜率的一半。

這就是 $\sqrt{\mathrm{HT}}$ scaling 的視覺版本。

### 2.5 逐個 family 解讀

#### Complete graph $K_N$

- 理論：$\mathrm{HT}=N-1$，所以 $\alpha\approx1$。
- 數值：$\alpha=1.06$，非常接近 1。
- 量子：$T_q\sim N^{0.53}$，接近 $\sqrt N$。
- Speedup：$4.7\times$ at $N=64$。
- 為什麼 speedup 不是很大？因為 $\mathrm{HT}$ 本身只長得像 $N$，平方根優勢的絕對差距比較小。

#### Cycle $C_N$

- 理論：$\mathrm{HT}=N(N+1)/6$，所以 $\alpha\approx2$。
- 數值：$\alpha=1.95$，非常接近 2。
- 量子：$T_q\sim N^{1.02}$，幾乎是線性。
- Speedup：$11.7\times$ at $N=64$，是四個 family 中最大的。
- 為什麼？因為古典在 cycle 上要走很遠，量子卻可以保持振幅、快速傳播。

#### 2D grid $L\times L$

- 理論：$\mathrm{HT}=\Theta(N\log N)$，所以 $\alpha$ 應該略大於 1。
- 數值：$\alpha=1.26$，符合 $N\log N$ 在有限尺寸下的行為。
- 量子：$T_q\sim N^{0.61}$，比 0.5 大一點，因為 $\log N$ 還沒完全分離。
- 但如果直接 fit $T_q$ vs $\mathrm{HT}$，$\gamma=0.48$，接近 0.5。
- 這說明：**看 $T_q$ vs $\mathrm{HT}$ 比看 $T_q$ vs $N$ 更接近理論**。

#### Hypercube $Q_d$

- 理論：$N=2^d$，$\mathrm{HT}\sim N\log N$。
- 數值：$\alpha=1.07$，接近 $N\log N$ 的有限尺寸行為。
- 量子：$T_q\sim N^{0.47}$，$\gamma=0.44$，略低於 0.5。
- Speedup：$5.4\times$ at $N=64$。

### 2.6 這個實驗證明了什麼？

- **支持 H1**：在 well-connected graphs 與 single target 下，量子搜尋時間約呈 $\sqrt{\mathrm{HT}}$ scaling，且優於古典。
- **支持 AGJK 的數值內容**：我們用的是 Conjecture 3 的 Algorithm 1，不是 Theorem 5 的 fast-forwarding；但 scaling 仍然符合預期。
- **提供 baseline**：後面的 E2–E5 都建立在這個 baseline 上。

### 2.7 這個實驗沒有證明什麼？

- 沒有證明 Theorem 5；我們只有引用它。
- 沒有證明 asymptotic exponent 一定是 0.5；我們只有有限尺寸的 fit。
- 沒有證明所有圖都一定有 quantum advantage；我們只測了四個 family。
- 沒有處理 noise；noise 在 E5。

### 2.8 常見誤解

- **「complete graph 的 exponent 應該是 1」**：有限尺寸 fit 出來是 1.06，這是 finite-size effect。
- **「$p_{\max}$ 一定要等於 1」**：AGJK 保證 constant success probability，不是 1。
- **「$T_q$ 一定要小於 $\sqrt{\mathrm{HT}}$」**：常數可以大於 1；我們看的是 scaling，不是絕對值。

## 3. E2：Single vs independent vs clustered marked vertices

### 3.1 問題

> 如果目標不只一個，搜尋會變快還是變慢？目標的「排列方式」有差嗎？AGJK 的 $\mathrm{HT}^+$ 什麼時候會爆炸？

### 3.2 設定

- 圖：
  - Grid $L=6,8$（$N=36,64$）。
  - Barbell，`n_each=8,16`（$N=24,48$）。
- Marked set：
  - `single`：1 個目標。
  - `independent`：4 個目標，用 farthest-point sampling 分散在圖上。
  - `clustered`：4 個目標，用 BFS 從一個隨機中心長出一個連通塊。
- Seeds：independent/clustered 用 `[0,1,2]` 三個 seeds，取 mean 和 min–max band。
- 量子 walk：interpolated $W(s)$，$s$ 掃描。
- $\mathrm{HT}^+$：用 `ht_extended`，$\epsilon=10^{-6}$。
- 時間窗口：$t\le3\sqrt{\mathrm{HT}}+5$。

### 3.3 Barbell graph 為什麼重要？

Barbell graph 是「兩個 clique 用一條 path 連起來」：

```
  K_8  ─── path ───  K_8
```

- 同一個 clique 內，任兩點直接相連，所以很容易走。
- 要到另一個 clique，必須走中間的 path，所以很難。
- 這很適合測試「clustered targets」：
  - 如果 4 個目標都在同一個 clique，walker 只要走到那個 clique，就很容易找到其中一個。
  - 如果目標分散在兩個 clique，則要跨過 bridge。

### 3.4 完整數字

| Graph | Marked set | mean HT | mean HT⁺ | HT⁺/HT | mean Tq | mean p_max |
|---|---|---:|---:|---:|---:|---:|
| Grid 6×6 | single | 46.1 | 46.1 | 1.00 | 12.0 | 0.904 |
| Grid 6×6 | independent | 14.4 | 14.6 | 1.01 | 6.7 | 0.938 |
| Grid 6×6 | clustered | 50.0 | 54.7 | 1.09 | 14.7 | 0.907 |
| Grid 8×8 | single | 95.5 | 95.5 | 1.00 | 17.0 | 0.914 |
| Grid 8×8 | independent | 34.7 | 35.3 | 1.02 | 10.7 | 0.886 |
| Grid 8×8 | clustered | 79.5 | 85.3 | 1.07 | 20.3 | 0.845 |
| Barbell n=8 | single | 373.6 | 373.6 | 1.00 | 51.0 | 0.959 |
| Barbell n=8 | independent | 7.6 | 10.5 | 1.38 | 5.0 | 0.966 |
| Barbell n=8 | clustered | 349.8 | 358.8 | 1.03 | 41.3 | 0.972 |
| Barbell n=16 | single | 2558.0 | 2557.9 | 1.00 | 134.0 | 0.958 |
| Barbell n=16 | independent | 16.8 | 25.4 | 1.52 | 7.0 | 0.968 |
| Barbell n=16 | clustered | 2478.6 | 2507.4 | 1.01 | 115.3 | 0.970 |

### 3.5 Figure 3：success probability curves

Figure 3（`fig_e2_success.pdf`）有 2×2 子圖：

- 左上：grid 6×6。
- 右上：grid 8×8。
- 左下：barbell n=8。
- 右下：barbell n=16。

每個子圖有三條線：

- 藍線：single。
- 橘線：independent。
- 綠線：clustered。

陰影 band 是三個 seeds 的 min–max。

#### 怎麼看？

- **Independent（橘線）通常最早達到高峰**：因為目標分散，walker 從任何方向都可能碰到其中一個。
- **Single（藍線）與 clustered（綠線）通常比較晚**：因為目標集中在一個小區域，walker 要先走到那裡。
- **Clustered 的曲線和 single 很像**：這是 E2 的核心觀察。多個目標集中在同一區，並沒有讓「找到第一個」變得多容易。
- **Barbell 的曲線震盪很大**：因為 barbell 的 graph 很小、對稱性高，量子漫步會有明顯的 recurrence。這是正常的，不是 bug。

### 3.6 Figure 4：HT vs HT⁺ 與 adversarial torus

Figure 4（`fig_e2_ht.pdf`）有兩個 panel：

#### 左 panel：grid 與 barbell 的 $\mathrm{HT}$ vs $\mathrm{HT}^+$

- 橫軸：classical $\mathrm{HT}$。
- 縱軸：extended $\mathrm{HT}^+$。
- 虛線：$y=x$。
- 點在虛線上方代表 $\mathrm{HT}^+>\mathrm{HT}$。
- 標籤：
  - `G6-s` = grid 6 single；`G6-i` = independent；`G6-c` = clustered。
  - `B16-s` = barbell 16 single；其他類推。

觀察：
- 大部分點非常靠近 $y=x$。
- 最大的偏離是 barbell 的 independent（$\mathrm{HT}^+/\mathrm{HT}=1.38$ 和 $1.52$）。
- 一般的 clustered set 只有 $1.07$–$1.09$。

#### 右 panel：AGJK adversarial torus

- 橫軸：$N$。
- 縱軸：steps。
- 藍線：classical $\mathrm{HT}$。
- 橘線：extended $\mathrm{HT}^+$。
- 點旁邊的數字是 $\mathrm{HT}^+/\mathrm{HT}$。

數字：

| $L$ | $N$ | $m$ | $p_M$ | $\mathrm{HT}$ | $\mathrm{HT}^+$ | ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 18 | 324 | 76 | 0.235 | 10.3 | 57.1 | 5.5 |
| 24 | 576 | 108 | 0.188 | 20.5 | 150.9 | 7.3 |
| 30 | 900 | 148 | 0.164 | 34.9 | 295.9 | 8.5 |
| 36 | 1296 | 252 | 0.194 | 50.5 | 443.1 | 8.8 |

- $\mathrm{HT}^+$ 的成長速度遠快於 $\mathrm{HT}$。
- 這個 gap 是 AGJK paper 的 Lemma 2 構造：dense 小方格 + sparse 週期格點。
- 對 $L=18$，我們也跑了 $W(s)$：$p_{\max}=0.978$ at $t=6$。也就是說，$\mathrm{HT}^+$ 很大，但 Conjecture 3 的數值 protocol 仍然很快找到目標。

### 3.7 這個實驗證明了什麼？

- **Independent targets 比較容易**：目標分散，$\mathrm{HT}$ 和 $T_q$ 都下降。
- **Clustered targets 像 single target**：$\mathrm{HT}$、$T_q$、success curve 都和 single 很接近。
- **$\mathrm{HT}^+$ 的大 gap 不是 generic clustering**：它需要 adversarial periodic arrangement。
- **$\mathrm{HT}^+$ 大不代表 actual search 一定慢**：L=18 的 $W(s)$ 仍然在 $t=6$ 達到高成功率。

### 3.8 H2 的評估

原本的 H2 說：

> 多個聚集的 marked vertices 會讓 naive quantum search 出現明顯的 $\mathrm{HT}^+$ penalty；AGJK 的改進演算法可恢復 $\tilde O(\sqrt{\mathrm{HT}})$。

結果：
- **前半不成立（作為一般敘述）**：一般的 clustered set 沒有明顯 penalty。
- **後半成立**：AGJK 的 adversarial torus 有明顯 penalty；但 Algorithm 1 的數值 protocol 仍然很快。
- 所以 H2 需要修正為：
  > $\mathrm{HT}^+$ 的大 penalty 是 marked-set arrangement 的性質，不是「多目標」本身的性質；在 adversarial arrangement 下，$\mathrm{HT}^+$ 可以遠大於 $\mathrm{HT}$，但 Conjecture 3 的 interpolated walk 仍可能在 $O(\sqrt{\mathrm{HT}})$ 內找到目標。

這是一個很重要的「negative result + refinement」，不是失敗。

### 3.9 這個實驗沒有證明什麼？

- 沒有證明所有 clustered set 都不會有 penalty；我們只測了 grid 和 barbell 的 BFS cluster。
- 沒有證明 independent targets 在所有圖上都比較容易；這是這兩個 graph family 的結果。
- 沒有跑 Theorem 5 的 fast-forwarding；我們只有 Conjecture 3 的數值 protocol。
- 沒有處理 noise；noise 在 E5。

### 3.10 常見誤解

- **「多個目標一定比較難」**：不一定。Independent targets 反而容易。
- **「Clustered 一定會有很大的 $\mathrm{HT}^+$」**：不一定。大 gap 是 arrangement 的性質。
- **「$\mathrm{HT}^+$ 是 actual runtime」**：不是。它是 spectral quantity；我們的 actual $T_q$ 是從 success curve 量出來的。
- **「Seeds 0 和 2 一樣是 bug」**：不是。Farthest-point sampling 在對稱圖上可能產生同一組點。

---

## 4. E3：Toy semantic graph 的 target activation

### 4.1 問題

> 在語意圖上，cue 到目標的「活化」在量子與古典漫步下有哪裡不同？語意距離有影響嗎？

### 4.2 設定

- 圖：`toy_semantic_graph()`，19 節點。
  - animal 社群：animal, dog, cat, wolf, horse, cow, bird。
  - vehicle 社群：vehicle, car, bus, train, bicycle, airplane。
  - instrument 社群：instrument, piano, guitar, violin, drum, flute。
  - bridge：bird 連到 airplane 和 flute。
- Cue：`animal`。
- Targets：
  - `dog`（distance 1，同社群）。
  - `violin`（distance 4，跨社群）。
- CTQW：$e^{-iL_{\mathrm{sym}}t}$。
- CRW：$e^{-L_{\mathrm{rw}}t}$。
- 時間：$\tau=\lambda_1t$，$\lambda_1=0.03335$，$T_{\max}=8/\lambda_1$。
- 取樣 1200 個時間點。
- Metrics：$p_{\text{peak}}$、$\tau_{\text{peak}}$、AUC、entropy、coverage、expected radius。

### 4.3 數字

| Cue → target | Model | $p_{\text{peak}}$ | $\tau_{\text{peak}}$ | AUC | Entropy | Coverage | Radius |
|---|---|---:|---:|---:|---:|---:|---:|
| animal → dog (d=1) | CTQW | 0.2367 | 4.75 | 0.4807 | 3.4128 | 0.1053 | 1.7978 |
| animal → dog (d=1) | CRW | 0.1581 | 0.1268 | 0.5796 | 3.2369 | 0.3158 | 0.9675 |
| animal → violin (d=4) | CTQW | 0.2470 | 6.859 | 0.3604 | 3.2822 | 0.1053 | 2.9949 |
| animal → violin (d=4) | CRW | 0.0455 | 8.000 | 0.3235 | 4.1768 | 1.0000 | 2.3635 |

### 4.4 Figure 5 怎麼看

Figure 5（`fig_e3_semantic.pdf`）有四個 panel：

- 左上：toy semantic graph。
  - 紅色星號是 cue（animal）。
  - 紅色方框是 targets（dog、violin）。
  - 節點顏色按社群。
- 右上：cue → dog 的 activation curves。
  - 橘線：CTQW。
  - 藍線：CRW。
  - 圓點：peak。
- 左下：cue → violin 的 activation curves。
- 右下：peak activation bar chart。

### 4.5 逐個 target 解讀

#### Near target：animal → dog（distance 1）

- CRW 立刻在 neighbor 上活化：
  - $p_{\text{peak}}=0.158$。
  - $\tau_{\text{peak}}=0.127$（非常早）。
  - AUC $=0.580$（比 CTQW 高）。
- CTQW：
  - $p_{\text{peak}}=0.237$（比 CRW 高）。
  - $\tau_{\text{peak}}=4.75$（比 CRW 晚很多）。
  - AUC $=0.481$（比 CRW 低）。
- 解讀：
  - 古典漫步「快但低」：它一走到 neighbor 就活化，然後慢慢衰減。
  - 量子漫步「晚但高」：它需要時間累積振幅，但峰值較高。

#### Far target：animal → violin（distance 4）

- CRW：
  - $p_{\text{peak}}=0.0455$，幾乎就是 stationary value。
  - $\tau_{\text{peak}}=8.0$（在我們的窗口邊界）。
  - AUC $=0.324$。
  - entropy $=4.18$（非常分散）。
  - coverage $=1.0$（幾乎所有節點都超過半峰值，因為峰值很低）。
- CTQW：
  - $p_{\text{peak}}=0.247$，是 CRW 的 5 倍多。
  - $\tau_{\text{peak}}=6.86$。
  - AUC $=0.360$（比 CRW 高）。
  - entropy $=3.28$（比 CRW 集中）。
  - radius $=2.99$（比 CRW 的 2.36 大）。
- 解讀：
  - 古典漫步對遠目標幾乎「均勻化」，沒有明顯的峰值。
  - 量子漫步可以跨社群建立較高的峰值，但需要時間。
  - 這就是「語意距離效應」：近目標古典快，遠目標量子峰值高。

### 4.6 這個實驗證明了什麼？

- **語意距離會改變活化時間**：near target 的 CRW 很早達到峰值；far target 的 CTQW 較晚但峰值高。
- **CTQW 與 CRW 的差異不是單調的優勢**：near target 的 AUC 是 CRW 高；far target 的峰值是 CTQW 高。
- **模型產生可檢驗的 prediction**：如果你做一個跨社群的語意搜尋實驗，量子模型預測「較晚但較強的活化」，古典模型預測「較早但較弱、較均勻的活化」。

### 4.7 這個實驗沒有證明什麼？

- 沒有真人資料；這是 model-level。
- Toy graph 只有 19 節點，不能代表真實語意網絡。
- CTQW 和 DTQW 的 time scale 沒有混在一起；不要把這裡的 $\tau$ 和 E1/E2 的步數直接比較。
- Coverage 和 radius 的定義是我們選的；換一個定義，數字會不同。

### 4.8 常見誤解

- **「CTQW 一定比 CRW 好」**：不一定。Near target 的 AUC 是 CRW 比較高。
- **「AUC 高就是比較好」**：取決於你的問題。如果你在意早期反應，AUC 或 early activation 重要；如果你在意峰值，$p_{\text{peak}}$ 重要。
- **「CTQW 和 Szegedy 是同一種 walk」**：不是。CTQW 是 continuous-time，Szegedy 是 discrete-time。我們在報告裡明確分開。

## 5. E4：Multi-alternative decision under coupling

> **2026-10-31 更新**：本節已依統一的 lazy walk（$\eta=0.1$）與新版讀出模型重寫。舊版「首次越過門檻讀出、對稱三選項 $0.333\to0.966$、不對稱分支非單調」已撤回，該現象屬相位假象。

### 5.1 問題

多個選項彼此相似（耦合）時，選擇機率與決策時間如何改變？這個結論是否依賴「怎麼讀出」？

### 5.2 設定

- 所有 Szegedy walk 統一使用 lazy walk $P_\eta=(1-\eta)P+\eta I$，$\eta=0.1$。
- 三種讀出（另保留舊的「首次越過門檻」作對照；定義見 `code/src/experiments.py` 的 `e4_readouts`）：

  | 讀出 | 說明 |
  |---|---|
  | 隨機停止 | 停止時間在 $\{1,\dots,400\}$ 均勻分布：$P_i\propto\frac{1}{400}\sum_{t=1}^{400}p_i(t)$ |
  | 偵測（$p=0.2$） | 以 $p=0.2$ 的部分量測判定，量測落在某選項即決定 |
  | 古典吸收 | 古典隨機漫步，首次到達選項即吸收 |

- 穩健性：改變 $\eta$ 與 $\pm20\%$ 邊權擾動，計算各讀出的 spread（變動幅度，越小越穩健）。
- 圖：中心 hub 加每選項一條路徑；cases symmetric3（4-4-4）、asymmetric3（3-4-5）、symmetric4（4-4-4-4），耦合分支 1 與 2；耦合網格 $c\in\{0,0.1,0.25,0.5,0.75,1,2\}$；步數上限 400；$\eta\in\{0,0.05,0.1,0.2\}$ 與 10 組 $\pm20\%$ 邊權擾動。

### 5.3 數字

穩健性（spread）：

| 讀出 | spread 中位數 | spread 最大值 |
|---|---:|---:|
| 隨機停止 | 0.08 | 0.26 |
| 偵測（$p=0.2$） | 0.035 | 0.045 |
| 古典吸收 | 0.044 | 0.065 |
| 舊版首次越過門檻讀出（已撤回） | 0.44 | 0.78 |

未耦合選項的選擇機率（偵測讀出）：

| 情境 | 耦合前 | 耦合後 |
|---|---:|---:|
| 對稱三選項 | 1/3 | 0.499 |
| 四選項（未耦合選項合計） | 0.500 | 0.653 |
| 不對稱三選項 | 0.342 | 0.470 |
| 對稱三選項，古典 | 1/3 | 1/3（不變） |

決策時間：偵測讀出 31–44 步；古典吸收 17–27 步。

### 5.4 怎麼讀

- 偵測讀出下，耦合使量子選擇機率**單調**偏向未耦合選項。
- 古典漫步在對稱圖上完全不受耦合影響。
- 圖檔為 `E4_robustness.pdf`：前三格為三個 case 的 P(未耦合選項) 對 $c$（四種讀出，帶狀為 $\eta$ 與擾動範圍），右下為各讀出的 spread 長條圖。

### 5.5 代表什麼／不代表什麼

- **代表**：在統一 lazy walk 與偵測讀出下，耦合造成的單調偏向可以重現；結論強烈依賴讀出定義，因此必須附上讀出定義。
- **不代表**：非單調的選擇機率已被證實（舊結論已撤回）；不代表與認知中的 attraction effect 等同。

### 5.6 H3 的評估

H3 原本主張：多個 marked sets 的選擇機率與反應時間會隨相似度非單調變化。

**結論：需修正。** 單調偏向未耦合選項在偵測讀出下可重現；非單調部分因屬相位假象而撤回。

---

## 6. E5：Partial measurement / decoherence sweep

> **2026-10-31 更新**：本節已重寫。舊版「deadline $T=20$ 時 $p\approx0.2$ 最佳、最高 $12\times$」已撤回：該結果來自振盪相位假象；lazy walk 後只剩約 $1.6\times$，平均掉 deadline 後消失。

### 6.1 問題

部分量測（測量率 $p$）會侵蝕還是幫助量子搜尋？是否存在最佳 $p$？答案取決於指標與 deadline。

### 6.2 設定

- 圖：grid $6\times6$ 與 toy semantic graph；各含 single 與 clustered 目標。
- 初始狀態：cue vertex 的 one-hot；$s=0$，因此 $p=1$ 是精確的古典漫步。
- Lazy walk $\eta=0.1$，步數上限 `max_steps` $=120$。
- 兩種指標模型：
  - **讀出模型**：時間平均成功率（欄位 `p_avg_120`）與振盪指數（欄位 `oscillation`，即文中的 CV）。
  - **偵測模型**：每一步以量測判定，量測落在目標即結束。$p=0$ 為純量子；$p=1$ 為古典 $P(\tau\le T)$。
- Deadline $T$ 的完整掃描見 `code/results/raw/E5_sweep.csv`。

### 6.3 讀出模型的結果

| 案例 | 時間平均成功率 $p=0$ | 同 $p=0.2$ | 振盪指數 $p=0$ | 同 $p=0.2$ |
|---|---:|---:|---:|---:|
| grid 單一 | 0.042 | 0.020 | 1.50 | 0.37 |
| grid 群聚 | 0.156 | 0.103 | 0.75 | 0.28 |
| toy 單一 | 0.038 | 0.037 | 0.97 | 0.26 |
| toy 群聚 | 0.178 | 0.200 | 0.41 | 0.24 |

- 純量子在 4 個案例中有 3 個的時間平均成功率最好。
- 量測的主要作用是讓曲線平穩（例如 grid 單一目標的振盪指數由 1.50 降至 0.37）。
- 純量子峰值：grid 單一目標 $p_{\max}=0.449$，出現在 $t=13$。

### 6.4 偵測模型的結果（deadline 成功率）

| 案例 | $T$ | $p=0$（純量子） | $p=0.2$ | $p=0.3$ | $p=1$（古典） |
|---|---:|---:|---:|---:|---:|
| grid 單一 | 40 | 0.021 | 0.146 | 0.159 | 0.136 |
| grid 單一 | 120 | 0.098 | 0.373 | 0.447 | 0.516 |
| grid 群聚 | 40 | 0.055 | 0.455 | 0.448 | 0.326 |
| grid 群聚 | 120 | 0.271 | 0.837 | 0.862 | 0.811 |
| toy 單一 | 40 | 0.039 | 0.183 | 0.216 | 0.261 |
| toy 單一 | 120 | 0.004 | 0.503 | 0.582 | 0.621 |
| toy 群聚 | 40 | 0.158 | 0.449 | 0.451 | 0.342 |
| toy 群聚 | 120 | 0.134 | 0.837 | 0.844 | 0.703 |

### 6.5 怎麼讀

- **短 deadline（$T\lesssim15$）**：純量子最好。
- **群聚目標、長 deadline（$T\gtrsim20$）**：$p\approx0.2$–$0.3$ 同時勝過純量子與古典。例如 $T=40$ 時，grid 群聚為 0.455（$p=0.2$）對 0.326（古典）對 0.055（純量子）。
- **單一目標**：最佳 $p$ 隨 deadline 不規則地移向古典。例如 toy 單一目標在 $T=40$ 時，$p=1$ 反而最高。
- 最佳 $p$ 取決於 deadline 與目標函數，沒有單一的全域最佳值。

### 6.6 撤回的舊結論

- 「deadline $T=20$ 時 $p\approx0.2$ 最佳、最高 $12\times$」：撤回。此為振盪相位假象；lazy walk 後只剩約 $1.6\times$，平均掉 deadline 後消失。

### 6.7 H4 的評估

H4 原本主張：弱測量可能改善成功率；強測量破壞優勢；存在最佳 $p$。

- 「弱測量改善成功率」：在群聚目標與 $T\gtrsim20$ 時成立。
- 「強測量破壞優勢」：在 $T=120$ 時，古典（$p=1$）遠優於純量子（例如 grid 群聚 0.811 對 0.271），與直覺相反，因此在此指標下不成立。
- 「存在最佳 $p$」：存在，但取決於 deadline 與目標函數。

**結論：部分支持，需區分目標函數與 deadline。**

### 6.8 檔案

- `code/results/raw/E5_sweep.csv`、`code/results/raw/E5_curves.csv`
- `code/results/processed/E5_decoherence.json`
- 圖：`E5_robustness.pdf`

---

## 7. 跨實驗綜合：RQ1–RQ3 與 H1–H4

### 7.1 RQ1：映射

> $\mathrm{HT}$、$\mathrm{HT}^+$、spectral gap、success probability 分別對應到什麼認知量？

| Walk 量 | 認知量 | 我們的證據 |
|---|---|---|
| $\mathrm{HT}$ | 古典搜尋困難度 / 反應時間 baseline | E1/E2 |
| $\mathrm{HT}^+$ | 多目標 / 脈絡困難度的 spectral proxy | E2 |
| spectral gap $\lambda_1$ | 思考 / 鬆弛速度 | E3 |
| $p_M(t)$ | 目標活化 / 證據累積 | E3/E5 |
| $T_q$ | 峰值反應時間 | E1/E2 |
| $t_{\text{deadline}}$ | deadline 下的反應時間 | E5 |
| choice probability $P_i$ | 選項被選中的機率 | E4 |
| decision time | 做出決定的時間 | E4 |
| measurement rate $p$ | 內省 / 雜訊強度 | E5 |

這個 mapping 是**定義出來的**，不是 fit 出來的。這是優點也是限制：優點是模型可解釋、可重現；限制是它還沒有和真人資料對照。

### 7.2 RQ2：結構

> 多個 marked vertices 的數量與排列如何改變量子優勢？

- **數量**：independent targets（4 個分散）比 single target 容易；$\mathrm{HT}$ 和 $T_q$ 都下降。
- **排列**：clustered targets（4 個集中）和 single target 差不多；沒有明顯的 $\mathrm{HT}^+$ penalty。
- **adversarial arrangement**：AGJK 的 periodic torus 構造讓 $\mathrm{HT}^+/\mathrm{HT}$ 達到 5.5–8.8。
- **actual search**：L=18 的 $W(s)$ 仍然在 $t=6$ 達到 $p_{\max}=0.978$。
- **認知意義**：多個「相似」的目標不一定讓搜尋變難；真正困難的是 spectral structure，而不是目標數量本身。

### 7.3 RQ3：雜訊

> Partial measurement / decoherence 如何侵蝕量子優勢？是否存在最佳內省強度？

- $T\lesssim15$ 時純量子最好；群聚目標在 $T\gtrsim20$ 時 $p\approx0.2$–$0.3$ 同時勝過純量子與古典；單一目標的最佳 $p$ 不規則。
- 但 unrestricted $p_{\max}$ 仍然是 $p=0$ 最好。
- 弱測量可以加速 toy graph 的 half-max time（53→8 步）。
- 強測量（$p\to1$）把系統變成古典，通常最差。
- 所以「最佳 $p$」是目標函數的函數：deadline success、peak success、speed 會給出不同的最佳值。

### 7.4 H1–H4 評估表

| 假設 | 內容 | 結果 | 評價 |
|---|---|---|---|
| H1 | well-connected graph + single target，$T_q\sim\sqrt{\mathrm{HT}}$ 且優於古典 | E1 支持：$\gamma=0.44$–$0.52$ | **支持** |
| H2 | clustered multiple targets 會有明顯 $\mathrm{HT}^+$ penalty；AGJK 改進演算法恢復 $\tilde O(\sqrt{\mathrm{HT}})$ | 一般 clustered 沒有大 penalty；adversarial torus 有 5.5–8.8×；L=18 的 $W(s)$ 仍快 | **部分支持，需修正** |
| H3 | 多 marked sets 的 choice probability / RT 隨 similarity 單調或非單調變化 | 偵測讀出下單調偏向未耦合選項；舊非單調結論撤回 | **需修正** |
| H4 | 弱測量可能改善 success；強測量破壞優勢；存在最佳 p | $T\gtrsim20$、群聚目標下 $p\approx0.2$–$0.3$ 勝過純量子與古典；$T=120$ 時古典勝過純量子 | **部分支持，需區分目標函數與 deadline** |

### 7.5 一句話總結每個 RQ

- **RQ1**：walk 的統計量可以自然地映射到反應時間、選擇機率、活化；但這是 model-level 定義，不是 behavioral fit。
- **RQ2**：目標的「排列」比「數量」更重要；independent 容易，clustered 像 single，adversarial 才會爆炸。
- **RQ3**：弱雜訊可以是助力，也可以是阻力；最佳 $p$ 取決於你想要 peak accuracy 還是 deadline speed。

## 8. Discussion：這些結果到底說明了什麼

### 8.1 五個主要發現

把 E1–E5 的結果壓縮成五句話：

1. **Scaling**：在四種合成圖上，量子搜尋時間大致滿足 $T_q\sim\mathrm{HT}^{0.44\text{--}0.52}$，接近 $\sqrt{\mathrm{HT}}$。
2. **Structure**：independent targets 比 clustered targets 容易；clustered targets 的行為像 single target；大 $\mathrm{HT}^+$ penalty 只在 adversarial periodic arrangement 出現。
3. **Semantics**：在 toy semantic graph 上，近目標的古典漫步較早活化、AUC 較高；遠目標的量子漫步峰值較高、半徑較大。
4. **Decision**：選項耦合會讓量子選擇機率強烈偏向未耦合的選項；在偵測讀出下，耦合單調偏向未耦合選項；先前的非單調結論已撤回（見 §5）。
5. **Noise**：在群聚目標與較長 deadline（$T\gtrsim20$）下，弱測量（$p\approx0.2$–$0.3$）可以提升成功率；但 unrestricted peak success 仍然是 $p=0$ 最好。

### 8.2 這些結果的內在邏輯

#### E1：為什麼 scaling 重要？

因為它把「量子漫步比較快」從一句口號變成一個可測量的關係：

$$
T_q \sim \sqrt{\mathrm{HT}}.
$$

這不是說量子一定比古典快，而是說：當古典的 hitting time 變大時，量子的搜尋時間只以平方根成長。這個關係是 AGJK 的理論核心，也是整個專案的 QIS 骨幹。

#### E2：為什麼 independent 比 clustered 容易？

因為搜尋問題問的是「找到**任何一個** marked vertex」。如果目標分散，walker 從任何方向都可能碰到其中一個；如果目標集中在一個小區域，walker 必須先走到那個區域，再找到其中一個點。Clustered targets 並沒有讓「第一個目標」變得更近，所以 $\mathrm{HT}$ 和 single target 差不多。

這個結果對認知搜尋有意義：多個「相似的記憶」不一定讓提取變容易；如果它們集中在同一個語意社群，你可能還是要先把注意力移到那個社群。相反地，分散的線索可能讓你從多個方向接觸到目標。

#### E2：為什麼 $\mathrm{HT}^+$ 大不等於搜尋一定慢？

$\mathrm{HT}^+$ 是 spectral quantity，描述的是 KMOR 那類演算法的 effective hitting time。它對 $D(s)$ 的特徵值非常敏感；當 $s\to1$，某些特徵值接近 1，分母 $1-\lambda_k$ 變小，$\mathrm{HT}^+$ 就變大。

但我們的數值 protocol 不是 KMOR；我們用 Conjecture 3 的 interpolated walk，直接掃 $s$ 和 $t$。在 L=18 的 adversarial torus 上，$W(s)$ 仍然在 $t=6$ 達到 $p_{\max}=0.978$。所以：

> $\mathrm{HT}^+$ 大是一個 warning，但不是死刑。

這也是為什麼我們在報告裡把 $\mathrm{HT}^+$ 當作「結構診斷」，而不是「actual runtime」。

#### E3：為什麼 near target 的古典 AUC 比較高？

因為 AUC 是「整體活化量」，不是「峰值」。古典漫步一走到 neighbor 就立刻活化，然後慢慢衰減；它的早期高峰讓 AUC 變大。量子漫步的峰值較高，但出現得較晚，所以 AUC 不一定比較大。

這告訴我們：**不同的認知指標會給不同的結論**。如果你關心「多快注意到」，古典可能更好；如果你關心「峰值注意力」，量子可能更好。

#### E4：為什麼耦合會讓 A 得利？

在 symmetric3 中，B 和 C 被耦合，變成一個「聯合選項」。量子漫步的振幅在 B/C 之間來回，對 A 的振幅造成建設性干涉。古典漫步只是在 B/C 之間重新分配機率，對 A 的影響很小。

在偵測讀出下，耦合單調地偏向未耦合選項；先前關於 asymmetric3 非單調的結論已撤回（見 §5.6）。這不是說「量子一定比較好」，而是說「量子對 context 的讀出方式很敏感」。

#### E5：為什麼弱測量可以幫助？

量子漫步的破壞性干涉會讓某些時間點的目標機率很低。弱測量打斷一部分相干性，抑制破壞性干涉，讓機率較快累積到目標。但測量太強會把整個系統變成古典，失去量子優勢。

所以「最佳 $p$」不是一個固定的物理常數，而是**目標函數的函數**：
- 如果你要群聚目標在 $T\gtrsim20$ 的成功率，$p\approx0.2$–$0.3$ 是目前數值上最好的選擇（見 §6）。
- 如果你要 unrestricted peak，$p=0$。
- 如果你要 half-max speed，弱 $p$ 可能最好，但要看圖。

### 8.3 與文獻的關係

#### AGJK 2019

- 我們實作 Szegedy walk、interpolated walk、$\mathrm{HT}^+$。
- 我們數值驗證 $\sqrt{\mathrm{HT}}$ scaling（E1）。
- 我們重現 adversarial torus 的 $\mathrm{HT}^+\gg\mathrm{HT}$（E2）。
- 我們沒有重證 Theorem 5；我們用 Conjecture 3 的數值 protocol。

#### Chen et al. 2022

- 他們用 DTQW 當 evidence accumulator，討論 partial measurement。
- 我們的 E5 是簡化版：projective measurement + reset，不是完整 open-system。
- 我們的結果和他們的 qualitative message 一致：弱雜訊可以幫助，強雜訊會破壞。

#### Huang–Busemeyer 2022

- 他們提出 multi-alternative quantum walk framework。
- 我們的 E4 是一個簡化的 multi-branch decision graph，使用 Szegedy/interpolated walk，而不是他們的 Hamiltonian 形式。
- 我們的重點是 option coupling 的 context effect，不是完整 fit 他們的多選項模型。

#### Pavone–Faro 2025

- 他們用 CTQW on semantic graphs 模型 insight。
- 我們的 E3 用 CTQW/CRW 在同一個 toy semantic graph 上比較 target activation。
- 我們沒有用他們的 ConceptNet pipeline；這是 future work。

#### Epping et al. 2023

- 他們用 open-system model 描述 choice and response time。
- 我們的 E5 是 simplified projective measurement，不是 Lindblad。
- 我們的結果提供一個「弱雜訊可能幫助」的 toy demonstration，但不能取代他們的完整模型。

### 8.4 Algorithmic advantage vs biological plausibility

這是整份報告最重要的區分。

**Algorithmic advantage**：
- 在給定的 graph、marked set、walk operator 下，量子 walk 需要多少步？
- 這是我們 E1/E2 測量的東西。
- 它是數學/計算複雜度的陳述。

**Biological plausibility**：
- 大腦是否真的能實現這種 walk？
- 這需要神經科學證據，不是我們的數值實驗能回答的。
- 我們的模型是 process-level，不是生物物理。

所以我們不能說：
- 「大腦是量子電腦。」
- 「人類的語意搜尋有量子加速。」
- 「Quantum cognition 被我們的實驗證實了。」

我們可以說：
- 「量子 walk 提供一個 process model，產生和古典 walk 不同的可檢驗預測。」
- 「在某些 graph 和 marked-set 結構下，量子搜尋時間的 scaling 比古典好。」
- 「弱測量在群聚目標與較長 deadline（$T\gtrsim20$）下可以改善成功率。」

### 8.5 限制（Limitations）

#### 8.5.1 沒有真人資料

所有的 response time、choice probability 都是從 walk 統計量**定義**出來的，不是 fit 真人資料。我們不能說「人類就是這樣」。我們只能說「這個模型會產生這樣的預測」。

#### 8.5.2 圖是合成的、小的

- Grid 最大 $10\times10$（$N=100$）。
- Toy semantic graph 只有 19 節點。
- Barbell 最大 $N=48$。
- Adversarial torus 最大 $N=1296$，但只算 spectral quantities，沒有跑完整 $W(s)$。

這些尺寸足以展示 mechanism，但不足以推廣到真實語意網絡或大型 decision problem。

#### 8.5.3 $s$ 是 grid search 選的

E1/E2/E4 用固定 grid 掃 $s$，選 $q_t$ 最大的值。不同的 $s$ 選擇規則會改變常數，甚至可能改變某些曲線的形狀。我們沒有證明這個 grid search 是最佳的。

#### 8.5.4 CTQW 與 DTQW 沒有混在同一個 fit

E3 用 CTQW/CRW；E1/E2/E4/E5 用 Szegedy DTQW。我們沒有把兩者的 time scale 放在同一張圖上比較。這是故意的，但也限制了「統一的量子優勢」敘述。

#### 8.5.5 Noise model 是簡化的

E5 用 projective measurement + reset，不是 Lindblad master equation，也不是 continuous dephasing。真實的 open-system 可能會有不同的行為。

#### 8.5.6 統計不確定性

- E2 用 3 個 seeds；E1/E3/E4 是 deterministic（或單一配置），沒有 error bars。
- 我們沒有做正式的 hypothesis test 或 confidence interval（雖然 `metrics.py` 有 bootstrap 函數）。
- E4 的讀出結論對讀出定義、$\eta$ 與邊權擾動敏感（見 §5.3）；換一個配置可能不一樣。

#### 8.5.7 參數選擇

- Lazy 參數 $\eta=0.1$（adversarial torus 為 0.2）。
- Deadline：$T$ 掃描，見 §6.2。
- Decision threshold $0.5$。
- E4 的 $s=0.9$。
- E5 的 `max_steps` $=120$。

這些都是我們選的，不是從資料 fit 出來的。改變它們會改變數字，但不一定改變 qualitative conclusion。

### 8.6 Threats to validity

#### Construct validity

- 我們用 graph distance 代表語意距離，用 edge weight 代表相似度。這是不是有效的 operationalization？可能不是；真實語意相似度更複雜。
- 我們用 success probability 代表「找到目標」，用 decision time 代表「反應時間」。這些是 model-level constructs，不是直接觀察。

#### Internal validity

- E4 的讀出結論是否真的來自 quantum interference，還是 graph 結構造成的 classical effect？古典基線在偵測讀出下幾乎不變，但我們沒有做 mediation analysis。
- E5 的 $p=0.2$ 最佳是否只是因為 deadline 選在 20？如果 deadline 改成 10 或 30，最佳 $p$ 可能不同。

#### External validity

- 合成圖和 toy graph 不能代表真實世界。
- 我們的結果不能直接推廣到人類認知或大型語意網絡。

#### Statistical conclusion validity

- 3 個 seeds 不足以做正式統計推論。
- 我們沒有 multiple comparison correction。
- 我們沒有報告 effect size 的 confidence interval。

### 8.7 Future work

1. **ConceptNet / 真實語意圖**：用 Pavone–Faro 的 pipeline 建 k-hop subgraph，測試 semantic distance effect 是否仍然存在。
2. **真人行為實驗**：設計語意搜尋或選擇任務，fit choice probability 和 RT，比較 quantum walk vs classical sequential sampling。
3. **Open-system 模型**：用 Lindblad 或 continuous dephasing 取代 projective measurement，看最佳 $p$ 是否改變。
4. **更大的圖**：用 sparse matrix、operator form、或 quantum fast-forwarding，測試 $N=10^3$–$10^4$。
5. **Quantum hardware**：在小圖上用 Qiskit/Cirq 實作 decision graph，看 context effect 是否能在真實雜訊下存活。
6. **更好的 $s$ 選擇**：用 spectral optimization 或 machine learning 選 $s$，而不是 grid search。
7. **Multi-dimensional walks**：用 Jeffery–Zur 的多維 walk 處理 multi-feature decision。
8. **Statistical rigor**：更多 seeds、bootstrap CI、formal model comparison（AIC/BIC）。

### 8.8 什麼結果會推翻我們的結論？

- 如果 ConceptNet 實驗顯示 semantic distance effect 完全不見，E3 的 external validity 就受質疑。
- 如果更多 seeds 或其他讀出定義讓 E4 的單調偏向消失，E4 的 context effect 就不穩。
- 如果 Lindblad 模型讓最佳 $p$ 變成 0 或 1，E5 的「最佳內省」就不成立。
- 如果更大的圖讓 $T_q$ 的 exponent 遠離 0.5，E1 的 scaling claim 就有限制。
- 如果真人資料更支持 classical sequential sampling，quantum walk 的 cognitive interpretation 就需要重新評估。

這些都是未來可以做的實驗，也是這份專案誠實的地方：我們沒有把 model-level 結果當成最終答案。

---

## 9. 結論

這個專案的核心貢獻不是「證明量子認知是對的」，而是：

> 把 AGJK 的 marked-vertex search 當成一個嚴謹的 process model，連到語意搜尋、多選項決策、與雜訊，並用數值實驗展示它的可檢驗預測與限制。

具體來說：

1. 我們數值驗證了 $T_q\sim\mathrm{HT}^{0.44\text{--}0.52}$ 的 scaling。
2. 我們釐清 independent vs clustered targets 的差異，以及 $\mathrm{HT}^+$ 大 gap 的結構條件。
3. 我們展示 semantic distance、option coupling、partial measurement 如何改變活化、選擇與速度。
4. 我們明確區分 algorithmic advantage 與 biological plausibility，並列出 limitations。

如果要用一句話總結：

> 量子漫步不是認知萬靈丹，但它提供了一個有結構、可比較、可反駁的 process model；這正是這個專案最有價值的地方。

---

## 附錄 A：全部數字

### A.1 E1 scaling exponents

| Family | $\mathrm{HT}$ exponent | $T_q$ exponent | $T_q\sim\mathrm{HT}$ exponent | max speedup |
|---|---:|---:|---:|---:|
| Complete | 1.06 | 0.53 | 0.50 | 4.7 |
| Cycle | 1.95 | 1.02 | 0.52 | 11.7 |
| Grid | 1.26 | 0.61 | 0.48 | 7.9 |
| Hypercube | 1.07 | 0.47 | 0.44 | 5.4 |

### A.2 E2 full table

| Graph | Marked set | mean HT | mean HT⁺ | HT⁺/HT | mean Tq | mean p_max |
|---|---|---:|---:|---:|---:|---:|
| Grid 6×6 | single | 46.1 | 46.1 | 1.00 | 12.0 | 0.904 |
| Grid 6×6 | independent | 14.4 | 14.6 | 1.01 | 6.7 | 0.938 |
| Grid 6×6 | clustered | 50.0 | 54.7 | 1.09 | 14.7 | 0.907 |
| Grid 8×8 | single | 95.5 | 95.5 | 1.00 | 17.0 | 0.914 |
| Grid 8×8 | independent | 34.7 | 35.3 | 1.02 | 10.7 | 0.886 |
| Grid 8×8 | clustered | 79.5 | 85.3 | 1.07 | 20.3 | 0.845 |
| Barbell n=8 | single | 373.6 | 373.6 | 1.00 | 51.0 | 0.959 |
| Barbell n=8 | independent | 7.6 | 10.5 | 1.38 | 5.0 | 0.966 |
| Barbell n=8 | clustered | 349.8 | 358.8 | 1.03 | 41.3 | 0.972 |
| Barbell n=16 | single | 2558.0 | 2557.9 | 1.00 | 134.0 | 0.958 |
| Barbell n=16 | independent | 16.8 | 25.4 | 1.52 | 7.0 | 0.968 |
| Barbell n=16 | clustered | 2478.6 | 2507.4 | 1.01 | 115.3 | 0.970 |

### A.3 E2 adversarial torus

| L | N | m | p_M | HT | HT⁺ | ratio | W(s) p_max | W(s) t |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 18 | 324 | 76 | 0.235 | 10.3 | 57.1 | 5.5 | 0.978 | 6 |
| 24 | 576 | 108 | 0.188 | 20.5 | 150.9 | 7.3 | — | — |
| 30 | 900 | 148 | 0.164 | 34.9 | 295.9 | 8.5 | — | — |
| 36 | 1296 | 252 | 0.194 | 50.5 | 443.1 | 8.8 | — | — |

### A.4 E3 semantic metrics

| Target | Model | p_peak | tau_peak | AUC | Entropy | Coverage | Radius |
|---|---|---:|---:|---:|---:|---:|---:|
| dog | CTQW | 0.2367 | 4.75 | 0.4807 | 3.4128 | 0.1053 | 1.7978 |
| dog | CRW | 0.1581 | 0.1268 | 0.5796 | 3.2369 | 0.3158 | 0.9675 |
| violin | CTQW | 0.2470 | 6.859 | 0.3604 | 3.2822 | 0.1053 | 2.9949 |
| violin | CRW | 0.0455 | 8.000 | 0.3235 | 4.1768 | 1.0000 | 2.3635 |

### A.5 E4 key numbers

> **已撤回（歷史紀錄）**：本小節是舊版非 lazy、首次越過門檻讀出的 E4 數字，屬相位假象，不代表目前結論；新版見 §5 與 `code/results/raw/E4_robustness.csv`。

At $c=1$：

| Case | Model | P_A | P_B | P_C | Decision time |
|---|---|---:|---:|---:|---:|
| symmetric3 | CTQW | 0.852 | 0.074 | 0.074 | 126 |
| symmetric3 | CRW | 0.369 | 0.316 | 0.316 | 15 |
| asymmetric3 | CTQW | 0.779 | 0.189 | 0.032 | 34 |
| asymmetric3 | CRW | 0.507 | 0.395 | 0.098 | 14 |

Asymmetric3 CTQW sequences：

- $P_A=(0.145,0.782,0.094,0.430,0.955,0.779,0.902)$.
- $P_C=(0.629,0.149,0.394,0.043,0.038,0.032,0.033)$.
- decision time $=(5,212,186,214,89,34,17)$.

### A.6 E5 optimal p

> **已撤回（歷史紀錄）**：下表是舊版單一 deadline $T=20$、非 lazy 的 E5 結果（含 11.9× 假象），不代表目前結論；新版見 §6 與 `code/results/raw/E5_sweep.csv`。

| Case | p* | deadline success | ratio to p=0 | half-max p=0 | half-max p* |
|---|---:|---:|---:|---:|---:|
| grid_single | 0.2 | 0.0296 | 11.9 | 10 | 10 |
| grid_clustered | 0.2 | 0.1140 | 1.68 | 9 | 9 |
| toy_single | 0.2 | 0.0322 | 1.31 | 53 | 8 |
| toy_clustered | 0.2 | 0.1767 | 1.21 | 9 | 7 |

---

## 附錄 B：重現指令與檔案對照

### B.1 環境

```bash
cd Final/code
mamba env create -f environment.yml
mamba activate qwalk-cognition
python -m pytest -q
```

### B.2 跑實驗

```bash
python -m src.experiments --only E1
python -m src.experiments --only E2
python -m src.experiments --only E3
python -m src.experiments --only E4
python -m src.experiments --only E5
```

### B.3 輸出檔案

| 實驗 | raw CSV | processed JSON | figure |
|---|---|---|---|
| E1 | `E1_scaling.csv` | `E1_scaling.json` | `E1_scaling.pdf`、`E1_speedup.pdf` |
| E2 | `E2_marked.csv`、`E2_curves.csv`、`E2_adversarial_torus.csv` | `E2_marked.json`、`E2_adversarial_torus.json` | `E2_success.pdf`、`E2_ht.pdf` |
| E3 | `E3_semantic_metrics.csv`、`E3_semantic_curves.csv` | `E3_semantic.json` | `E3_semantic.pdf` |
| E4 | `E4_metrics.csv`、`E4_choices.csv`、`E4_curves.csv`、`E4_robustness.csv` | `E4_decision.json`、`E4_robustness.json` | `E4_decision.pdf`、`E4_robustness.pdf` |
| E5 | `E5_sweep.csv`、`E5_curves.csv` | `E5_decoherence.json` | `E5_robustness.pdf` |

### B.4 報告

```bash
cd Final/report
tectonic -X compile main.tex
```

---

## 附錄 C：圖表對照與 caption

| 圖/表 | 內容 | 在哪一節 |
|---|---|---|
| Figure 1 | 三層架構 | Introduction |
| Figure 2 | E1 scaling | Results 6.1 |
| Figure 3 | E2 success curves | Results 6.2 |
| Figure 4 | E2 HT vs HT⁺ + adversarial torus | Results 6.2 |
| Figure 5 | E3 semantic graph + activation | Results 6.3 |
| Figure 6 | E4 choice probabilities + decision time | Results 6.4 |
| Figure 7 | E5 decoherence sweep | Results 6.5 |
| Table 1 | 文獻地圖 | Background |
| Table 2 | 認知映射 | Cognitive Model |
| Table 3 | 實驗矩陣 | Methods |
| Table 4 | E1 scaling exponents | Results 6.1 |
| Table 5 | E2 selected results | Results 6.2 |
| Table 6 | E5 optimal p | Results 6.5 |
| Table 7 | E2 full results | Appendix |

---

## 附錄 D：結果相關 FAQ

### D1：為什麼 E1 的 complete graph speedup 只有 4.7×？

因為 $\mathrm{HT}=N-1$ 只長得像 $N$，平方根優勢的絕對差距比較小。Cycle 的 $\mathrm{HT}$ 長得像 $N^2$，所以 speedup 可以到 11×。

### D2：為什麼 E2 的 independent targets 反而容易？

因為搜尋問題是「找到任何一個」。目標分散，walker 從任何方向都可能碰到其中一個。Clustered targets 則要先把注意力移到同一個小區域。

### D3：為什麼 E2 的 clustered 沒有大 $\mathrm{HT}^+$ penalty？

因為 $\mathrm{HT}^+$ 對 spectral resonance 很敏感。一般的 BFS cluster 沒有 adversarial periodic structure，所以 $\mathrm{HT}^+$ 只比 $\mathrm{HT}$ 大一點。AGJK 的 dense+sparse torus 才有大 gap。

### D4：為什麼 E2 的 L=18 可以跑 $W(s)$，L=24 以上不行？

因為 $W(s)$ 的 state 大小是 $2n^2$。L=18 時 $n=324$，state 約 210k；L=36 時 $n=1296$，state 約 3.4M，dense 操作會太慢/太大。所以我們只對 L=18 跑完整 $W(s)$，其他只算 spectral quantities。

### D5：為什麼 E3 的 near target 古典 AUC 比較高？

因為 AUC 是整體活化量。古典漫步立刻在 neighbor 上活化，早期高峰讓 AUC 變大；量子峰值較高，但出現得晚。

### D6：為什麼 E3 的 far target CTQW 峰值較高？

因為量子振幅可以跨社群建設性干涉，而古典漫步會均勻化。這是 semantic distance effect 的 model-level prediction。

### D7：為什麼 E4 的耦合偏向是單調的？

Symmetric3 有三條等長分支，對稱性讓未耦合選項的機率隨耦合強度單調上升。先前認為 asymmetric3 會非單調，該結論屬相位假象，已撤回（見 §5.6）。

### D8：為什麼 E4 的 decision time 會跳到 126、212 這種大數字？

因為當耦合讓總選項機率遲遲達不到 0.5 時，decision time 會跳到很晚的時間。這是 threshold 定義的結果，不是 bug。

### D9：為什麼 E5 的 $p_{\max}$ 在 $p=0$ 最大，但 deadline success 在 $p=0.2$ 最大？

因為 $p_{\max}$ 允許你等到最佳時間；deadline success 固定在給定的 $T$。在群聚目標與長 deadline 下，弱測量可以較快累積機率，但 $p_{\max}$ 仍是純量子最高。這是 speed–accuracy tradeoff。

### D10：為什麼 E5 的 $p=1$ 是古典？

因為每一步都量測並重置到 basis state，相干性完全消失；對 $s=0$，$Q=P$。測試 `test_fully_measured_walk_is_classical` 驗證了這一點。

### D11：這些結果有統計顯著性嗎？

E2 有 3 個 seeds，但我們沒有做 formal hypothesis test。E1/E3/E4 是 deterministic 或單一配置。所以我們應該把結果當成**numerical evidence**，不是 statistical proof。

### D12：哪個結果最強？哪個最弱？

- 最強：E1 的 scaling（四個 family、16 個 instance、$p_{\max}$ 高）。
- 次強：E2 的 independent vs clustered 對比（多個 seeds、兩個 graph families）。
- 較弱：E4 的 non-monotonicity（單一 graph 配置、對 $c$ 敏感）。
- 最弱：E5 的 optimal $p$（deadline 依賴、簡化 noise model）。

### D13：如果 reviewer 攻擊「這不是真的認知」，怎麼回答？

我們同意。這是 process-level model，不是 behavioral data。我們的貢獻是建立可檢驗的 model-level predictions，並區分 algorithmic advantage 與 biological plausibility。真人實驗是 future work。

### D14：如果 reviewer 攻擊「$\mathrm{HT}^+$ 沒有很大」，怎麼回答？

我們沒有說它一定很大。我們說：一般的 clustered set 沒有大 penalty；大 penalty 需要 adversarial periodic arrangement。這是 E2 的主要 finding，也是對 AGJK 的 numerical clarification。

### D15：如果 reviewer 攻擊「E4 的耦合結論是 cherry-picking」，怎麼回答？

我們承認 E4 對讀出定義、branch lengths 和 coupling grid 敏感；舊的非單調結論已撤回，目前主張限於偵測讀出下的單調偏向。我們沒有做 exhaustive scan；這是 limitation。未來可以用更多 seeds、更多 branch lengths、formal sensitivity analysis。

### D16：如果 reviewer 問「為什麼不用 ConceptNet」，怎麼回答？

因為時間和 scope。Toy graph 足以展示 mechanism；ConceptNet 是 future work。我們在 limitations 有寫。

### D17：如果 reviewer 問「為什麼不用真實量子硬體」，怎麼回答？

因為我們的圖和 state 太大，而且重點是 model-level predictions。小圖硬體實作是 future work，可以參考 Widdows et al. 2023。

### D18：如果 reviewer 問「這篇的 novelty 是什麼」，怎麼回答？

Novelty 不是新定理，而是：
1. 把 AGJK 的 marked-vertex search 當成 cognitive process model。
2. 用 $\mathrm{HT}^+$ 的結構分析多目標搜尋。
3. 用 semantic/decision/noise 三個實驗展示 model-level predictions。
4. 誠實區分 algorithmic vs biological。

---

## 最後的總結

如果你只記得三件事：

1. **量子搜尋時間大約是古典 hitting time 的平方根**，但常數和 finite-size 會影響實際數字。
2. **目標的排列比數量重要**：independent 容易，clustered 像 single，adversarial 才會讓 $\mathrm{HT}^+$ 爆炸。
3. **弱雜訊可以是助力，也可以是阻力**：deadline 下 $p\approx0.2$ 最好，但 unrestricted peak 仍是 $p=0$。

這就是這個專案從 E1 到 E5 的故事。



