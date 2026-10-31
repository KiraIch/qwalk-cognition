# MASTER PLAN — 從「初稿完成」到「12/14 報告、12/21 交稿」

> 撰寫日：2026-10-31（距 presentation 44 天、距 final paper 51 天）
> 依據：Haiku 子代理全專案盤點 + 主 session 親自核對關鍵檔案（見 §1.3）。
> 定位：`ROADMAP.md` 是「從零到初稿」的計畫，已大致完成；本文件接手「從初稿到可交付、可經得起提問」的階段。`ROADMAP.md` 不再新增內容，只回勾已完成項目。

---

## 0. 一頁摘要（TL;DR）

**現況**：M0–M6 全部完成且大幅超前。E1–E5 程式、47 個測試全過、9 張圖、26 頁報告初稿、Explain/Result 文件都在。缺的是 **slides（骨架 17 frames、2 個 placeholder）**、**weekly log（只有 Week 0）**、以及**沒有任何 git commit**。

**真正的風險不是「沒做完」，而是「做出來的東西有 4 個會被老師問倒的科學瑕疵」**：

| # | 瑕疵 | 證據 | 嚴重度 |
|---|---|---|---|
| S1 | Methods 寫「除非另述，一律 lazy η=0.1」，但 E1/E2/E4 實際用 **non-lazy** P | `05_methods.tex:22-23` vs `experiments.py:113,220,383` | 高：方法與程式不一致 |
| S2 | 因為 non-lazy，cycle/grid/hypercube 是 bipartite → discriminant 有 −1 特徵值 → `spectral_gap = 1 − max|λᵢ|` = 0。RQ1 卻把 spectral gap 當認知量 | `szegedy.py:173-177`、`E1_scaling.csv` | 高：RQ1 的一個核心量在 3/4 圖上無意義 |
| S3 | E5 摘要寫「up to 12× deadline success」，實際是 0.0025 → 0.0296。p=0 時 grid_single 的 t_opt=12、p_max=0.41，**t=20 剛好落在純量子振盪的谷底**。所以「12×」主要是 deadline 選在谷底的產物，不是退相干本身的效益 | `E5_sweep.csv` 第 2–5 列、`main.tex:58-60` | 最高：headline 結果可被一個問題推翻 |
| S4 | E3 classical violin 的「peak」t=239.9 = 視窗邊界 8/gap，是截斷不是峰值 | `experiments.py:306`、`E3_semantic_metrics.csv` | 中 |

另有 **篇幅問題**：老師指引 10–12 頁正文 + appendix，目前 AI Tool Usage 在第 23 頁 → 正文約 22 頁，需**砍約一半**。

**策略**：Phase A 先修科學（11/1–11/9），Phase B 同步把工程收乾淨，Phase C 依新結果重寫並瘦身論文（11/10–11/23），Phase D 做投影片與排練（11/24–12/13），Phase E 吸收報告回饋後定稿（12/15–12/20）。每個 Phase 都有明確的「完成定義」與凍結點。

---

## 1. 現況盤點

### 1.1 專案一句話
以 AGJK 2019（arXiv:1903.07493）marked-vertex 量子漫步搜尋為 QIS 核心，把 marked set 對應到語意記憶目標 / 決策選項，做 process-level（非生物學宣稱）的認知搜尋模型，用 E1–E5 數值實驗回答 RQ1–RQ3。

### 1.2 資產清單與狀態

| 區塊 | 狀態 | 備註 |
|---|---|---|
| `proposal/` | ✅ 已交（`r15k47010_pp.pdf`） | `.tex` 仍有 `[Student Name]`、`[model name]` placeholder；PDF 檔名與 ROADMAP 預期的 `proposal.pdf` 不同（無妨，存檔用）|
| `code/src/` 11 模組 | ✅ 可跑 | `python -m pytest -q` → 47 passed / 1.2 s |
| `code/results/` | ✅ E1–E5 raw CSV + processed JSON | 數字與 `06_results.tex` 抽查一致 |
| `code/figures/` ↔ `report/figures/` | ✅ byte-identical | 但是**手動複製**，沒有自動同步 |
| `code/notebooks/` 4 本 | ⚠️ 未執行、無輸出；`04_decoherence` 用 Monte Carlo 而非 E5 的精確法 | |
| `code/configs/` | ⚠️ drift：`base.yaml` 的 measurement_probabilities 少 0.75；7 個 key 從未被讀 | |
| `report/` | ⚠️ 26 頁初稿；正文 ~22 頁超標；本機無 tectonic/pdflatex 無法重編 | |
| `report/refs.bib` | ⚠️ 3 筆作者錯（Ferro、Pavone、Huang 名字）、Huang 2022 venue 與 proposal 不一致；5 筆未引用 | |
| `slides/slides.tex` | ❌ 骨架；無 E3/E4/E5 結果頁；2 個 figure placeholder；無 PDF | |
| `weekly_log.md` | ❌ 只有 Week 0 | Week 1（10/22–10/28）缺 |
| git | ❌ 0 commits；`.DS_Store`、`__pycache__`、`.pytest_cache` 在樹中 | |
| 師生 meeting | ❓ ROADMAP 仍未勾 | 需確認 |

### 1.3 主 session 親自核對過的事實
- S1：`05_methods.tex:22-23` 原文為 "Unless stated otherwise we use the lazy walk … η=0.1"；`experiments.py` 113/220/383 行呼叫 `transition_matrix(...)` 不帶 self_loop，只有 E5（475 行）用 config 的 0.1、adversarial torus（560 行）用 0.2。
- S3：`E5_sweep.csv` grid_single：p=0 → p_max=0.407、t_opt=12、p_deadline(20)=0.00248；p=0.2 → p_deadline=0.0296（ratio 11.92）。toy_single p=0 時 t_opt=56 > deadline 20。
- 摘要原文確實寫 "up to a 12× improvement in deadline success"。
- slides 共 17 個 `\begin{frame}`，第 19 行 author placeholder、120/128 行 figure placeholder。

---

## 2. 時程總覽

| Phase | 期間 | 主題 | 凍結點 / 交付 |
|---|---|---|---|
| A | 11/01（日）– 11/09（一） | 科學修正 + 新增 E6 | **11/09 Results Freeze v2**：所有 CSV/JSON/圖重生並鎖定 |
| B | 11/01 – 11/12（與 A 平行） | 工程與可重現性 | `make all` 一鍵重生；git 有乾淨歷史 |
| C | 11/10 – 11/23 | 論文重寫 + 瘦身至 12 頁正文 | **11/23 Paper Draft v2**（可給同學/助教看）|
| D | 11/24 – 12/13 | 投影片 + 排練 | 12/07 slides v1；12/10、12/12 兩次計時排練；12/13 凍結 |
| — | **12/14（一）** | **Presentation** | |
| E | 12/15 – 12/20 | 吸收提問、定稿 | **12/20 交稿**（比 12/21 期限提早一天作緩衝）|
| — | 12/21（一） | Final paper 截止 | |

> 期末考週與 12/21 重疊，所以 E 階段只做「回饋修正」，不做新實驗。**12/1 之後不再加任何實驗。**

---

## 3. Phase A — 科學修正（P0，11/01–11/09）

每一項都依「決策 → 程式改動 → 測試 → 重跑 → 論文影響」五段寫明。

### A1. 統一 lazy walk（修 S1 + S2）

**決策**：全部 Szegedy/AGJK 實驗統一使用 lazy walk `P_η = (1−η)P + ηI`，η=0.1；adversarial torus 保留 AGJK 原文設定 η=0.2 並在 Methods 明寫。
理由：(1) 讓 Methods 為真；(2) lazy 消除 bipartite 的 −1 特徵值，spectral gap 在 cycle/grid/hypercube 上才非零、才能拿來對應 RQ1；(3) AGJK 本身的分析就假設 P 可逆且 lazy 化不改變 HT 的數量級（HT 只乘上 1/(1−η)）。

**程式**
- `configs/base.yaml`：新增 `walk.laziness: 0.1`（唯一真相來源）。
- `experiments.py`：E1/E2/E4 改為 `lazy_transition_matrix(transition_matrix(g), cfg.walk.laziness)`；E5 改讀同一 key（刪掉 E5 自己的 `self_loop`）。
- `szegedy.py`：保留 `spectral_gap`（absolute gap δ = 1−max_{i≥1}|λᵢ|），**新增** `phase_gap`（1−λ₂，對應混合時間的單邊 gap），CSV 兩欄都輸出，論文明確定義用哪一個。
- `experiments.py` E1 加一欄 `ht_lazy_over_ht_nonlazy`，作 sanity：理論值應 ≈ 1/(1−η)=1.111。

**測試**（`tests/test_szegedy.py`、`tests/test_classical.py`）
- cycle N=16 lazy 後 `spectral_gap > 0`。
- 任一圖 `HT(P_η) ≈ HT(P)/(1−η)`（rtol 1e-6）。
- `phase_gap ≥ spectral_gap`。

**重跑**：E1、E2、E4（E3 是 CTQW/CRW 不受影響；E5 本來就是 0.1，僅 config 來源改變，數字應不變 → 當回歸測試）。

**預期**：T_q ~ HT^≈0.5 不變（若指數偏離 0.5 超過 0.08 → 進 §9 風險 R2 處理）。

**論文影響**：`05_methods`（walk 定義段）、`06_results` E1 表格數字、`03_theory` gap 定義、RQ1 敘述。

---

### A2. E5 重新設計 metric（修 S3，最重要）

**問題本質**：純量子漫步的成功機率對時間振盪；固定單一 deadline 的比較，結果幾乎由「deadline 落在振盪的哪個相位」決定。

**決策**：保留原 E5 sweep 作 appendix 的「單點示例」，主結果改用三個與相位無關的 metric：

| Metric | 定義 | 認知對應 |
|---|---|---|
| `p_deadline(T, p)` 熱圖 | T ∈ {5,…,80}，p ∈ 原 8 個值 | RT deadline 不確定時的表現地形 |
| `p_avg(T_max, p)` | (1/T_max) Σ_{t≤T_max} p_t（時間平均成功率） | 受試者在隨機時刻被要求作答 |
| `robust_gain(p)` | min_T p_deadline(T,p) / min_T p_deadline(T,0)，或比較 p_deadline 的變異係數 | 對時間不確定性的穩健性 |

並在每個 case 報**絕對值 + 比值**，永不單獨報比值。

**新的可辯護主張（取代「12×」）**：
> 部分量測把振盪的量子成功曲線「熨平」：犧牲峰值成功率（p=0 永遠最高），換取對作答時間不確定性的穩健性。最佳 p 取決於 deadline 分布的寬度。

這是一個真正的 trade-off（peak vs robustness），比「退相干讓搜尋變好 12 倍」誠實且更有意思，也正好對應 H4 的修正版。

**程式**
- `noise.py`：`measurement_curve` 已能給整條曲線 → 新增 `deadline_surface(curve_by_p, T_grid)` 與 `time_averaged_success`。
- `metrics.py`：新增 `coefficient_of_variation`、`robust_gain`。
- `experiments.py` E5：輸出 `E5_surface.csv`（case, p, T, p_success）與 `E5_summary.csv`。
- `plotting.py`：新增 `plot_e5_surface`（4 個 case 的 p×T 熱圖，2×2）、`plot_e5_tradeoff`（x=peak success，y=time-averaged success，每點一個 p，畫成 Pareto 曲線）。

**測試**：p=1 時 `p_avg` 等於 classical 結果（已有 p=1 極限測試可延伸）；`deadline_surface` 在 T=t_opt、p=0 時等於 p_max。

**論文影響**：摘要那一句必須改寫（§6 有逐字建議）；`06_results` E5 小節重寫；H4 評估改寫。

---

### A3. E3 classical peak 截斷（修 S4）

- `experiments.py:306`：視窗改成 `max(time_window_relaxation/gap, t_stationary)`，其中 t_stationary 為 classical 機率與 π_target 差 < 1% 的時間；或乾脆把 `time_window_relaxation` 調到 20。
- `semantic.py` metrics：新增 `peak_is_interior: bool`；若 peak 在視窗末端 → 報「單調趨近穩態 π_target」，不叫 peak。
- 論文：E3 改說「CRW 對遠距目標是單調累積到穩態機率；CTQW 有明確的瞬態峰」，這其實讓 CTQW vs CRW 的對比**更清楚**。

---

### A4. 統計強度

| 實驗 | 現況 | 改為 |
|---|---|---|
| E1 | 指數無誤差 | log-log OLS 的 95% CI（`scipy.stats.linregress` 的 stderr × t 值），表格報 `0.49 [0.46, 0.52]` |
| E2 | independent/clustered 各 3 seeds | 20 seeds；HT、HT⁺/HT 報 median + bootstrap 95% CI（已有 `bootstrap_confidence_interval`，終於用上）|
| E4 | 單一權重設定 | 對 branch 權重加 ±20% 擾動 20 次，報 P_A(c) 的 CI 帶 → 驗證「非單調」不是權重微調的巧合 |
| E3 | 單一 toy graph | 保留；在 limitations 明說；E6 補足泛化 |

計算量：E2 grid 8×8、barbell n=16 × 20 seeds，dense 矩陣 ≤ 64·deg 維，數分鐘內可完成。

---

### A5. 新增 E6：認知上真實的拓撲（Should，11/05–11/09；**11/09 未完成即砍**）

**動機**：E1 全是規則格子，但語意網路實證上是 small-world / scale-free（Steyvers & Tenenbaum 2005）。老師或同學最可能問「你的圖跟真的語意網路有什麼關係」。

**設計**
- 圖族：Watts–Strogatz（N∈{32,64,128}，k=4，β∈{0, 0.05, 0.2, 1}）、Barabási–Albert（N 同上，m=2）。每組 10 個隨機實例。
- 量測：與 E1 相同（HT、T_q、p_max、speedup），額外看「目標是 hub vs 邊緣節點」對 HT 與加速比的影響。
- 預期與意義：β 從 0→1 時 HT 大幅下降，量子加速比隨之縮小（因為 √HT 的優勢在 HT 小時不明顯）→ 可導出可檢驗預測：「在高度連通的語意區域，量子模型與古典模型的 RT 預測差異最小」。
- 程式：`graphs.py` 加 `watts_strogatz`、`barabasi_albert`（包 networkx、固定 seed、確保 connected）；`experiments.py` 加 `run_e6`；`plotting.py` 加 `plot_e6`。

**若時間不夠**：E6 只寫進 Future Work，不影響主線。

---

### A6. 假說對齊

| 假說 | Proposal | 現況 | 論文處理 |
|---|---|---|---|
| H1 T_q ~ √HT | ✓ | 支持 | 保留 |
| H2 clustered 更難 / HT⁺ gap | ✓ | **部分被否證**：大 gap 只在 adversarial torus 出現 | 明寫「原假說 → 修正」，這是加分項不是扣分項 |
| H3 CTQW 語意激發 | ✓ | 支持（A3 後敘述更精確）| 保留 |
| H4 退相干最佳點 | ✗（proposal 後新增）| 依 A2 改為 peak-robustness trade-off | 在 Methods 註明「H4 於 proposal 後加入」|

---

### A7. 文獻修正（30 分鐘，不需等任何人）

- `refs.bib`：`chen2022` → Giuseppe M. Ferro；`pavone2025` → Arianna Pavone；`huang2022` → Jiaqi Huang。
- Huang–Busemeyer 2022 venue：以 `Tentative/2022_Huang_Busemeyer_multialternative_quantum_walk.pdf` 首頁為準，proposal 與 bib 統一。
- AGJK：釘選版本（`eprint = {1903.07493}`，註明 v1 或最新版；若有期刊版則引期刊版）。
- 5 筆未引用（pothos2025、zhang2021、huang2024、jeffery2025、tsuchiya2025）：Jeffery–Zur 在 Related Work 引一句（multidimensional QW 是 AGJK 之後的推廣），其餘若無處可引就刪。

---

## 4. Phase B — 工程與可重現性（11/01–11/12，與 A 平行）

### B1. git 基線（需你同意，見 §10）
1. `.gitignore` 加 `.DS_Store`、`code/results/**/*.png`（若決定只追 PDF）、`*.synctex.gz`。
2. 刪除工作樹中的 `.DS_Store`、`code/.pytest_cache/`、`code/src/__pycache__/`。
3. 第一個 commit = 「v1 draft as of 2026-10-20」，打 tag `draft-v1`。之後每個 Phase A 子項各一個 commit，方便回溯舊數字。
4. `Tentative/` 的 PDF（6.5 MB）建議**不進 git**（版權 + 體積），改在 `Tentative/README.md` 列出書目與 arXiv 連結。

### B2. 設定檔收斂
- `base.yaml` 是預設、`experiments.yaml` 只放每實驗的覆寫；寫一個 `load_config(exp)` 做 deep-merge。
- 刪除 7 個未使用 key，或接上：`walk.success_threshold`（E1 已需要）、`classical.monte_carlo_samples`（測試用）。其他刪。
- 新增 `tests/test_config.py`：所有 key 都被讀取（以 sentinel 檢查），避免再 drift。

### B3. 一鍵重生
`code/Makefile`（或 `run_all.sh`）：
```
make test       # pytest
make results    # python -m src.experiments --all
make figures    # 由 processed/ 重畫所有圖
make sync       # 複製 figures/*.pdf → ../report/figures/
make report     # cd ../report && tectonic -X compile main.tex
make all        # 以上全部
```
- 每次 `make results` 寫 `results/MANIFEST.json`：git hash、config hash、時間、各 CSV 的 sha256、Python/numpy 版本。論文 Reproducibility appendix 直接引用它。
- `schematics.py` 納入 `make figures`，`FIGURE_INDEX.md` 補上生成者。

### B4. Notebook 處置
- 4 本 notebook 改為「純展示」：只讀 `results/processed/`，不重算；執行後保存輸出。
- `04_decoherence.ipynb` 改用 E5 的精確法；Monte Carlo 版本保留為交叉驗證 cell（兩者應在 MC 誤差內一致 → 本身就是一個好的 sanity check）。

### B5. LaTeX 建置
- `environment.yml` 加 `tectonic`（conda-forge 有）；或在 `report/README.md` 寫 `brew install tectonic`。
- 建置驗證：無 `??`、無 overfull > 10pt、bib 無 warning。

### B6. 測試補強
- 新增 A1–A5 的測試（上文已列）。
- `tests/test_experiments_smoke.py`：每個 E 以極小 config 跑 < 5 s，確認輸出欄位齊全。
- ROADMAP §411–418 那 5 個 sanity check 已被測試覆蓋 → 回勾。

---

## 5. Phase C — 論文重寫與瘦身（11/10–11/23）

### C1. 篇幅預算（正文 12 頁上限）

| 節 | 目前（估）| 目標 | 處理 |
|---|---|---|---|
| Abstract | 0.3 | 0.3 | 依 §6 改寫 |
| 1 Introduction | 1.5 | 1.0 | 砍文獻敘事，保留 RQ + contributions 條列 |
| 2 Background | 2.0 | 1.5 | Markov chain / HT 定義保留；量子認知文獻壓成一段 |
| 3 Theory (Szegedy + AGJK) | 2.5 | 2.5 | **QIS 課程的核心，不砍**；推導細節移 appendix |
| 4 Cognitive model | 2.0 | 1.0 | mapping 表格化 |
| 5 Methods | 3.0 | 1.0 | experiment matrix 一張表 + 參數表；細節移 appendix |
| 6 Results | 4.0 | 3.5 | E1–E6 各 ≈0.5 頁，一圖一段；E5 用新圖 |
| 7 Discussion | 2.5 | 1.0 | 保留「解釋了什麼 / 沒解釋什麼」+ limitations |
| 8 Conclusion | 0.3 | 0.3 | |
| **合計** | **~18–22** | **≤12** | |
| Appendix | ~4 | 不限（合理即可）| 推導、measurement recursion、E2/E4 全表、reproducibility、原 E5 單點 deadline 結果 |

### C2. 寫作順序（依賴關係）
1. Methods（A1 後定義才固定）→ 2. Results（Results Freeze v2 後）→ 3. Theory 定義對齊（gap 定義）→ 4. Discussion（依新 H2/H4）→ 5. Intro/Abstract 最後寫。

### C3. 每個結果小節的固定格式
`主張一句（粗體）→ 圖 → 關鍵數字（含 CI 與絕對值）→ 對應哪個 RQ/H → 一句限制`。

### C4. 圖表規劃（正文 ≤ 7 張）

| Fig | 內容 | 來源 |
|---|---|---|
| 1 | 架構圖：graph → walk → marked set → cognitive readout | `schematics.py` |
| 2 | E1：T_q vs HT log-log，四圖族 + 斜率 0.5 參考線 | 既有，重跑 |
| 3 | E2：HT⁺/HT by marked type + adversarial torus 插圖 | 既有，加 CI |
| 4 | E3：CTQW vs CRW 激發曲線（dog/violin）| 既有，延長視窗 |
| 5 | E4：P_A(c) 三種 branch 結構 + CI 帶 | 既有，加擾動 |
| 6 | E5：peak vs time-averaged Pareto（主）；熱圖放 appendix | **新** |
| 7 | E6：speedup vs β（WS）與 hub/邊緣 | **新**（若 A5 被砍則無）|

E2 success curves、E1 speedup 圖移 appendix。

### C5. 必改的具體文字
- `main.tex:37-38` 作者、`main.tex:74-78` AI 使用聲明補上實際工具名稱與用途（依課程規定）。
- `05_methods.tex:22-23` lazy walk 句：A1 後即為真，補「adversarial torus 用 η=0.2 依 AGJK」。
- `03_theory`：明確定義 δ（absolute gap）與 1−λ₂，並說明 lazy 化的作用。
- `06_results` E3：「peak」措辭依 A3。
- `06_results` E5、摘要：依 §6。
- Discussion 加一段「Proposal 之後的修正」：H2 修正、H4 新增與重構 —— 展現科學誠實。

### C6. 外部審閱
11/23 把 Draft v2 給一位同學（或隊友）讀，請對方只回答三件事：哪一段看不懂、哪個數字不信、哪張圖看不出重點。

---

## 6. 摘要改寫建議（取代 `main.tex:58-60`）

> A partial-measurement sweep reveals a peak–robustness trade-off: the pure quantum walk attains the highest peak success, while intermediate measurement rates (p ≈ 0.1–0.3) flatten its oscillations and raise time-averaged success when the response deadline is uncertain.

（數值以 A2 重跑後為準；若 time-averaged 結果不支持此說法，就照實寫「沒有發現穩健性優勢」，並把 H4 列為未支持。）

---

## 7. Phase D — 投影片與口頭報告（11/24–12/13）

### D1. 規格
- 15–18 分鐘 + Q&A；beamer 16:9；主投影片 16 張 + backup 6 張。
- 原則：每張一個主張、一張圖、≤ 3 行字；數學只出現在 Theory 兩張。
- 所有圖直接 `\includegraphics` 自 `../report/figures/`（不另存副本，避免不同步）。

### D2. 逐張架構

| # | 標題（即主張）| 視覺 | 秒數 |
|---|---|---|---:|
| 1 | Title + 一句 takeaway | — | 20 |
| 2 | 找東西是認知的核心操作：記憶提取、多選項決策 | 語意網路示意 | 60 |
| 3 | 問題：圖拓撲與目標結構如何決定「找到」的速度？ | RQ1–3 | 50 |
| 4 | 古典答案：hitting time HT | 隨機漫步動畫截圖 | 70 |
| 5 | Szegedy walk：二次加速 √HT | 公式 + 示意 | 80 |
| 6 | AGJK：多目標時要用 HT⁺，interpolated walk W(s) | HT vs HT⁺ 對比圖 | 90 |
| 7 | 認知對應：marked set = 目標記憶 / 選項 | mapping 表 | 60 |
| 8 | 實驗矩陣 E1–E6 | 一張表 | 50 |
| 9 | E1：T_q ∝ HT^0.5 在四種圖上都成立 | Fig 2 | 70 |
| 10 | E2：分散目標比聚集目標容易；大 HT⁺ gap 只在對抗構造 | Fig 3 | 80 |
| 11 | E3：量子激發有瞬態峰，古典是單調累積 | Fig 4 | 70 |
| 12 | E4：耦合兩選項會把選擇推向第三者；不對稱時非單調 | Fig 5 | 70 |
| 13 | E5：峰值 vs 穩健性的取捨 | Fig 6 | 80 |
| 14 | E6（若有）：small-world 越強，量子優勢越小 | Fig 7 | 50 |
| 15 | 它解釋了什麼、沒有宣稱什麼（非生物學主張）| 兩欄 | 60 |
| 16 | 結論 + 3 個可檢驗預測 | — | 40 |
| | **合計** | | **~16.5 min** |

Backup：B1 lazy walk 與 spectral gap 定義、B2 HT⁺ 的精確定義與 AGJK 定理、B3 E5 熱圖、B4 E2 全表與 CI、B5 原 E5 單點 deadline 結果與為何不採用、B6 reproducibility（MANIFEST、測試數）。

### D3. 預想提問與準備答案（寫進 speaker notes）
1. 「這跟大腦真的是量子的有關嗎？」→ 否，process-level；引 Discussion「algorithmic vs biological」。
2. 「為什麼是 √HT 不是 √N？」→ Grover 是完全圖特例；AGJK 對任意圖的推廣。
3. 「HT⁺ 什麼時候真的比 HT 大很多？」→ adversarial torus，E2 數字。
4. 「退相干怎麼會有幫助？」→ 不是提高峰值，是穩健性；B3/B5。
5. 「E3 只有一張 19 節點的圖？」→ 承認；E6 + future work（真實語意網路，如 free-association norms）。
6. 「量子漫步要怎麼跟 RT 資料比？」→ 時間步 ↔ RT 的單調映射假設；future work 擬合實驗資料。

### D4. 排練時程
- 12/07 slides v1 完成。
- 12/08 單人通讀，逐張計時，砍超時頁。
- 12/10 第一次完整計時排練（目標 16–17 min），錄音回聽。
- 12/12 第二次排練（找人聽、模擬提問）。
- 12/13 凍結；輸出 PDF + 備份到雲端與隨身碟。

---

## 8. Phase E — 定稿（12/15–12/20）
1. 12/14 報告當天記下所有提問 → 12/15 分類：論文需補一句 / 需補一段 / 只需口頭回答。
2. 12/16–12/18 修改論文（不加新實驗）。
3. 12/19 全文校對：數字與 CSV 一致（寫一個小 script 從 `processed/*.json` 抽數字 grep 進 `.tex` 比對）、圖號引用、bib、頁數 ≤ 12。
4. 12/20 編譯最終 PDF、`make all` 從乾淨 clone 重跑一次確認可重現、提交、git tag `final`。

---

## 9. 風險登記

| ID | 風險 | 機率 | 影響 | 對策 |
|---|---|---|---|---|
| R1 | A2 重跑後 E5 沒有任何穩健性優勢 | 中 | 中 | 照實寫 H4 未支持；負結果配清楚解釋（振盪相位）依然是好結果 |
| R2 | lazy 化後 E1 指數偏離 0.5 | 低 | 高 | 先檢查 time window 是否需乘 1/√(1−η)；仍偏離則報告並分析有限尺寸效應 |
| R3 | E6 時間不夠 | 中 | 低 | 11/09 硬性截止，砍到 Future Work |
| R4 | 本機無 LaTeX → 無法驗證排版 | 高 | 中 | 11/01 先裝 tectonic；備案 Overleaf |
| R5 | 期末考與交稿撞期 | 高 | 高 | 12/20 提前交；E 階段禁止新實驗 |
| R6 | 正文砍到 12 頁時遺失關鍵內容 | 中 | 中 | 先把要砍的段落移到 appendix 而非刪除 |
| R7 | 老師期待更多 QIS 理論深度（不只數值）| 中 | 高 | Theory 節保持 2.5 頁不砍；加一個小定理/命題：lazy 化對 HT 與 gap 的精確影響（自己推、放 appendix 證明）|

---

## 10. 需要你決定的事

1. **團隊**：單人（ChiaAn Lin, R15K47010）還是有隊友？影響作者欄與 Phase 分工。
2. **老師 meeting**：proposal 前的約談有沒有發生？若沒有，建議本週寄信約 11 月中討論 Draft v2 方向（尤其 E5 重構與 E6）。
3. **E6**：要做（建議）還是直接列 Future Work？
4. **git**：可否建立第一個 commit 並清掉 `.DS_Store` / cache？`Tentative/` PDF 是否排除在 git 外？
5. **E5 摘要改寫**：是否同意以「peak–robustness trade-off」取代「12×」框架？

---

## 11. 第一週行動清單（11/01–11/07）

| 日 | 任務 | 完成定義 |
|---|---|---|
| 11/01 日 | B1 git 基線（經同意）、B5 裝 tectonic、補 weekly_log Week 1–2 | `tectonic main.tex` 成功；log 有兩週 |
| 11/01 日 | A7 文獻修正 | bib 3 處改正、未引用處理完 |
| 11/02 一 | A1 lazy walk：config + 程式 + 測試 | 新測試過、全測試過 |
| 11/03 二 | A1 重跑 E1/E2/E4，比對新舊數字 | 新 CSV；指數 diff 記錄於 weekly_log |
| 11/04 三 | A2 E5 新 metric 程式 + 測試 | `E5_surface.csv` 產出 |
| 11/05 四 | A2 新圖 + 判讀；A3 E3 視窗 | Fig 6 草圖；E3 `peak_is_interior` 欄 |
| 11/06 五 | A4 統計強化（E1 CI、E2 20 seeds、E4 擾動）| CSV 含 CI 欄 |
| 11/07 六 | A5 E6 開工；B2/B3 Makefile | `make all` 可跑 |
| 11/09 一 | **Results Freeze v2**、`git tag results-v2` | 所有圖重生、MANIFEST 寫入 |

---

## 12. 分工建議（若使用 Claude Code 代理）

| 工作 | 代理 / 模型 | effort |
|---|---|---|
| A7 bib、B1 清理、weekly_log | 主 session（Haiku）| low |
| A1、A3、B2、B3 程式修改 | `implementer`（Haiku → 跨檔時 Sonnet）| medium |
| A2 E5 metric 設計與實作 | `implementer`（Sonnet）| high |
| A4、A5 實驗與測試 | `implementer` + `qa-tester` | medium |
| 每個 Phase A 子項完成後 | `code-reviewer` | medium |
| R7 lazy 化命題的推導檢查 | Opus | high |
| C 論文重寫 | `doc-writer`（Sonnet），主 session 審 | medium |
| D 投影片 | `doc-writer`（Sonnet）| medium |
| 12/19 數字一致性比對 script | `qa-tester` | low |
