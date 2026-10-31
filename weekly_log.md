# Weekly Log

Answer the following questions every Sunday. Keep entries short and link to
figures, commits, and experiment IDs.

## Template

### Week N (YYYY-MM-DD to YYYY-MM-DD)

1. What was proved or derived this week?
2. Which experiments were run, and where are the figures?
3. Which research question do the results address?
4. Is any interpretation overstated? Which limitations are missing?
5. What is next week's milestone? Is descoping needed?
6. Any new papers to read? Do they threaten the main thread?
7. Is the code reproducible? Do the tests pass?
8. Is the report or slide deck behind schedule?

## Week 0 (2026-10-20)

1. Derived: none yet; AGJK definitions collected.
2. Experiments: E1 scaling on complete, cycle, grid, and hypercube graphs (`E1_scaling.pdf`, `E1_speedup.pdf`); E2 single/independent/clustered marked sets on grid and barbell graphs (`E2_success.pdf`, `E2_ht.pdf`), plus the AGJK adversarial-torus `HT+` construction; E3 CTQW vs CRW semantic activation on the toy concept graph (`E3_semantic.pdf`); E4 multi-alternative choice under option coupling (`E4_decision.pdf`); E5 partial-measurement decoherence sweep (`E5_decoherence.pdf`). All figures are frozen in `report/figures/`.
3. RQ addressed: RQ1--RQ3. Quantum time fits $T_q \sim \HT^{0.46\text{--}0.54}$; independent targets lower both HT and t_q, while clustered targets behave like a single target. The large $HT+$ gap appears only in the adversarial torus construction. E3 shows higher CTQW peak activation than CRW for both a near and a far target, with a longer time-to-peak. E4 shows that coupling two options shifts CTQW choice probability toward the uncoupled option, while CRW stays near uniform; asymmetric branches give non-monotonic choice probabilities and decision times. E5 finds an optimal measurement rate $p \approx 0.2$ at a fixed deadline, with up to $12\times$ higher success than the pure quantum walk, and a strong speedup of the half-maximum time at weak decoherence.（2026-10-31 已更正，見 Week 2）
4. Overstatement check: results are numerical and finite-size; no biological claim.
5. Next milestone: revise and trim the full draft, then prepare and rehearse the slides.
6. New papers: none.
7. Code: 47 tests pass in the `qwalk-cognition` Miniforge environment. The report compiles with Tectonic to a 26-page PDF with no unresolved references.
8. Report: full draft written and compiled (`report/main.pdf`); needs revision and trimming.

## Week 2 (2026-10-29 to 2026-11-04)

1. Derived: 無新的定理證明。所有 Szegedy/AGJK 實驗統一改用 lazy walk $P_\eta=(1-\eta)P+\eta I$，$\eta=0.1$（adversarial torus 用 $\eta=0.2$）。
2. Experiments: 依 lazy walk 重跑 E1、E2、E4、E5（A1）。E5 改為「讀出模型」與「偵測模型」兩種定義（A2）。E4 新增讀出與穩健性掃描（隨機停止、偵測 $p=0.2$、古典吸收；`code/results/raw/E4_robustness.csv`，figure `E4_robustness.pdf`）。E5 穩健性圖為 `E5_robustness.pdf`（資料 `code/results/raw/E5_sweep.csv`）。
3. RQ addressed: RQ1--RQ3。撤回兩項先前的強結論：
   - E5：「deadline $T=20$ 時 $p\approx0.2$ 最佳、最高 $12\times$」撤回。該結果來自振盪相位假象；lazy walk 後只剩約 $1.6\times$，平均掉 deadline 後消失。新結論：$T\lesssim15$ 時純量子最好；群聚目標在 $T\gtrsim20$ 時 $p\approx0.2$–$0.3$ 同時勝過純量子與古典（$T=40$，grid 群聚：0.455 vs 古典 0.326 vs 純量子 0.055）；單一目標的最佳 $p$ 隨 deadline 不規則地移向古典。
   - E4：「首次越過門檻讀出」、對稱三選項 $0.333\to0.966$、不對稱分支非單調，撤回。這些屬相位假象（舊讀出在 $\eta$ 與 $\pm20\%$ 邊權擾動下 spread 中位數 0.44、最大 0.78）。在偵測讀出下，耦合使選擇機率單調偏向未耦合選項：對稱三選項 $1/3\to0.499$；四選項未耦合合計 $0.500\to0.653$；不對稱 $0.342\to0.470$；古典在對稱圖上完全不變。
4. Overstatement check: 「12×」與「非單調」兩項強結論已撤回。結果仍為數值、有限尺寸；E5 為簡化的投影量測加重置模型，不是 open system。
5. Next milestone: MASTER_PLAN Phase A 剩餘項目（A3 延長 E3 時間窗、A4 統計強化（E2 增加種子避免重複集合）、A5 E6 小世界/無尺度圖）與 Phase B 工程整理；11/09 Results Freeze v2。
6. New papers: 無。
7. Code: 測試由 47 增為 61，全部通過。新增 `Explain_v2.md`（新版完整解說）與 `MASTER_PLAN.md`。
8. Report: 論文 `report/sections` 已同步 E1、E2、E4、E5 新數字與措辭（摘要、Methods、Results、Discussion、Conclusion、附錄）；PDF 尚未重新編譯（本機無 LaTeX）。
