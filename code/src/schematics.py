"""Schematic figures used in the report."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def draw_architecture(path: str | Path) -> None:
    figure, axis = plt.subplots(figsize=(7.4, 2.3))
    axis.set_xlim(0.0, 1.0)
    axis.set_ylim(0.0, 1.0)
    axis.set_axis_off()
    boxes = (
        (0.02, 0.22, 0.28, 0.58, "#dbe8f5", "QIS core", "AGJK search\n$W(s)$, $\\mathrm{HT}^{+}$"),
        (0.36, 0.22, 0.28, 0.58, "#f6e2d0", "Graph model", "semantic / decision graph\nmarked sets, coupling"),
        (0.70, 0.22, 0.28, 0.58, "#e2f0d9", "Cognition", "response time\nchoice probability"),
    )
    for left, bottom, width, height, color, title, body in boxes:
        patch = FancyBboxPatch(
            (left, bottom),
            width,
            height,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            linewidth=1.0,
            edgecolor="#4d4d4d",
            facecolor=color,
        )
        axis.add_patch(patch)
        axis.text(
            left + width / 2,
            bottom + height - 0.10,
            title,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
        )
        axis.text(
            left + width / 2,
            bottom + height / 2 - 0.04,
            body,
            ha="center",
            va="center",
            fontsize=9,
        )
    for start, end in ((0.30, 0.36), (0.64, 0.70)):
        arrow = FancyArrowPatch(
            (start, 0.51),
            (end, 0.51),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.2,
            color="#4d4d4d",
        )
        axis.add_patch(arrow)
    figure.savefig(path, bbox_inches="tight")
    figure.savefig(Path(path).with_suffix(".png"), bbox_inches="tight", dpi=220)
    plt.close(figure)


if __name__ == "__main__":
    draw_architecture(Path("../report/figures/fig_architecture.pdf"))
