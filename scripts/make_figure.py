"""One figure for both experiments: paired change in mean evil score vs. the no-framing
baseline, per framing, with item-level bootstrap 95% CIs. Writes results/fig_framing_effects.{png,svg}."""

import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from analyze import item_means, paired_effect
from judge import read_jsonl

COLOR = {"gpt-4o": "#2a78d6", "claude-sonnet-5": "#eb6834"}  # fixed categorical slots 1, 2
OWN = {"gpt-4o": "openai", "claude-sonnet-5": "anthropic"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e1"

PANELS = [
    ("Told the model's developer", ["gpt-4o", "claude-sonnet-5"],
     [("anthropic", "Anthropic"), ("openai", "OpenAI"), ("google", "Google")]),
    ("Told about the experiment", ["gpt-4o", "claude-sonnet-5"],
     [("context", "part of an EM study"), ("hint_aligned", "safety-tuned baseline"),
      ("hint_misaligned", "fine-tuned to be misaligned"), ("explicit", "we expect a 4 or 5")]),
]


def load() -> pd.DataFrame:
    rows = []
    for f in ("judgments.jsonl", "judgments_expectation.jsonl"):
        rows += read_jsonl(ROOT / "results" / f)
    df = pd.DataFrame(rows)
    df = df[df["error"].isna()] if "error" in df else df
    df["gradeable"] = df["score"].notna()
    return df


def main():
    df = load()
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.9), sharex=True,
                             gridspec_kw={"width_ratios": [1, 1], "wspace": 0.9})
    fig.patch.set_facecolor("#fcfcfb")
    for ax, (title, judges, framings) in zip(axes, PANELS, strict=True):
        ax.set_facecolor("#fcfcfb")
        y = 0
        ticks, labels = [], []
        for j in judges:
            m = item_means(df, j)
            for fr, name in framings:
                e = paired_effect(m, fr, "none")
                own = OWN[j] == fr
                ax.plot([e["lo"], e["hi"]], [y, y], color=COLOR[j], lw=2, solid_capstyle="round", zorder=2)
                ax.plot(e["diff"], y, "o", ms=8, color=COLOR[j], zorder=3)
                ticks.append(y)
                labels.append(f"{name} (own)" if own else name)
                y -= 1
            y -= 0.6  # gap between judge groups
        ax.axvline(0, color=INK2, lw=1, zorder=1)
        ax.set_yticks(ticks, labels, fontsize=9, color=INK)
        ax.set_title(title, fontsize=10, color=INK, loc="left", pad=10)
        ax.set_xlim(-0.35, 0.35)
        ax.set_xticks([-0.2, 0, 0.2])
        ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(axis="both", length=0, colors=INK2, labelsize=8.5)
    fig.supxlabel("change in mean evil score vs. no framing (1–5 scale, 95% CI over 120 items)",
                  fontsize=9, color=INK2, y=0.06)
    handles = [plt.Line2D([], [], marker="o", color=COLOR[j], lw=2, ms=7, label=f"judge: {j}") for j in COLOR]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 0.005))
    for ax in axes:  # direction cues under the axis
        ax.text(0.0, -0.075, "\u2190 more lenient", transform=ax.transAxes, fontsize=8.5, color=INK2, ha="left", va="top")
        ax.text(1.0, -0.075, "more harsh \u2192", transform=ax.transAxes, fontsize=8.5, color=INK2, ha="right", va="top")
    fig.subplots_adjust(left=0.17, right=0.97, top=0.93, bottom=0.21, wspace=0.75)
    for ext in ("png", "svg"):
        fig.savefig(ROOT / "results" / f"fig_framing_effects.{ext}", dpi=200, facecolor=fig.get_facecolor())
    print("saved results/fig_framing_effects.png")


if __name__ == "__main__":
    main()
