"""
figstyle.py - Figure house style for matplotlib/seaborn.

Copy this file next to the analysis script (or add its folder to sys.path) and:

    import figstyle as fs
    fs.apply("paper")                       # or "thesis", "slide"
    fig, ax = plt.subplots(figsize=fs.size("single"))
    fs.dot_plot(ax, df, x="group", y="value", order=["Control", "Treated"],
                colors={"Control": fs.BLUE, "Treated": fs.RED}, rep="replicate")
    fs.sig_bracket(ax, 0, 1, p=0.009)       # only call for significant results
    fs.finish(ax, title="Modulus", ylabel="Modulus (kPa)")
    fs.save(fig, "fig1a_modulus")       # PNG + SVG (+ PDF), white background

Conventions are documented in ../SKILL.md and ../references/palettes.md.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb

# --------------------------------------------------------------------------- colours
# Colour by role (see ../references/palettes.md).
BLUE, RED, GREEN = "#0000FF", "#FF0000", "#008000"     # Prism primaries: contrasting pair + third
SOFT_BLUE, SOFT_RED = "#1F77B4", "#D62728"             # softer pair
TEAL, GREY, INK = "#0E7C7B", "#9AA0A6", "#2B2B2B"       # slide accent / control / text
PAIR = (BLUE, RED)                                      # baseline-like vs changed-like
REF_GREY = "#808080"                                    # reference lines and bands
OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#D55E00",
             "#CC79A7", "#56B4E9", "#F0E442", "#000000"]

# --------------------------------------------------------------------------- targets
# Font sizes are at FINAL printed/projected size. Never scale a figure after export.
_TARGETS = {
    "paper":  dict(base=8,  title=8.5, tick=7,  lw=0.8, marker=4.5, letter=10),
    "thesis": dict(base=10, title=11,  tick=9,  lw=1.0, marker=6,   letter=12),
    "slide":  dict(base=14, title=16,  tick=12, lw=1.5, marker=8,   letter=18),
}
_SIZES_MM = {"single": (85, 70), "onehalf": (120, 85), "double": (175, 110),
             "springer": (117, 85), "slide_half": (150, 110), "slide_full": (300, 150)}
_state = {"target": "paper"}
ANNOT = "annotation"   # gid tag on significance brackets, stripped by save(clean_axes=...)


def apply(target: str = "paper") -> None:
    """Set rcParams for 'paper', 'thesis' or 'slide'."""
    t = _TARGETS[target]
    _state["target"] = target
    mpl.rcParams.update({
        # a family LIST enables per-glyph fallback (Arial lacks ⁻ superscript minus)
        "font.family": ["Arial", "DejaVu Sans"],
        "font.size": t["base"], "axes.labelsize": t["base"],
        "axes.titlesize": t["title"], "axes.titleweight": "bold",
        "xtick.labelsize": t["tick"], "ytick.labelsize": t["tick"],
        "legend.fontsize": t["tick"], "legend.frameon": False,
        "axes.linewidth": t["lw"], "xtick.major.width": t["lw"], "ytick.major.width": t["lw"],
        "xtick.major.size": 3.5, "ytick.major.size": 3.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "axes.edgecolor": "black", "axes.labelcolor": "black",
        "text.color": "black", "xtick.color": "black", "ytick.color": "black",
        "lines.linewidth": t["lw"] * 1.5, "lines.markersize": t["marker"],
        "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white", "savefig.dpi": 600 if target != "slide" else 300,
        "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "mathtext.default": "regular",
    })


def size(name: str = "single", h_mm: float | None = None) -> tuple[float, float]:
    """Figure size in inches from a named width (mm based)."""
    w, h = _SIZES_MM[name]
    return (w / 25.4, (h_mm or h) / 25.4)


# --------------------------------------------------------------------------- tones
def rep_tones(base: str, n: int, lo: float = 0.45, hi: float = 1.0) -> list:
    """n tones of one hue, dark -> light, for biological replicates.

    Replicate identity is shown by colour TONE within the group colour,
    so n is visible without extra labels.
    """
    name = base.lower()
    if name in ("#0000ff", "blue"):
        cmap = plt.cm.Blues
    elif name in ("#ff0000", "red", "#d62728"):
        cmap = plt.cm.Reds
    elif name in ("#008000", "green"):
        cmap = plt.cm.Greens
    else:
        cmap = LinearSegmentedColormap.from_list("t", ["white", base, "black"])
        return [cmap(v) for v in np.linspace(0.35, 0.75, n)][::-1]
    return [cmap(v) for v in np.linspace(hi, lo, n)]


# --------------------------------------------------------------------------- marks
def dot_plot(ax, df, x, y, order=None, colors=None, rep=None, jitter=0.15,
             summary="sd", marker="o", open_markers=False, edge=False, seed=0):
    """Scatter-dot plot with every point shown and a black mean +/- SD bar.

    Default: solid points, no outline (Prism look). edge=True adds a thin black outline.

    rep: column with biological-replicate IDs -> points coloured by tone per replicate.
    summary: 'sd' (default), 'sem' (dose/time curves only) or None.
    Returns {group: (mean, err, n)} computed on replicate means if rep given.
    """
    rng = np.random.default_rng(seed)
    order = order or list(dict.fromkeys(df[x]))
    t = _TARGETS[_state["target"]]
    out = {}
    for i, g in enumerate(order):
        sub = df[df[x] == g]
        base = (colors or {}).get(g, OKABE_ITO[i % 8])
        if rep:
            reps = list(dict.fromkeys(sub[rep]))
            tones = dict(zip(reps, rep_tones(base, len(reps))))
            cols = [tones[r] for r in sub[rep]]
        else:
            cols = [base] * len(sub)
        xs = i + rng.uniform(-jitter, jitter, len(sub))
        ax.scatter(xs, sub[y], s=t["marker"] ** 2, c="none" if open_markers else cols,
                   edgecolors=cols if open_markers else ("black" if edge else "none"),
                   linewidths=t["lw"] * (1.2 if open_markers else 0.4),
                   marker=marker, zorder=3)
        vals = sub.groupby(rep)[y].mean().values if rep else sub[y].values
        m = float(np.mean(vals))
        e = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
        if summary == "sem":
            e /= np.sqrt(len(vals))
        if summary:  # centred over the points, drawn on top (Prism layout)
            ax.errorbar(i, m, yerr=e, fmt="none", ecolor="black",
                        elinewidth=t["lw"] * 1.5, capsize=t["marker"] * 0.9,
                        capthick=t["lw"] * 1.5, zorder=4)
            ax.hlines(m, i - 0.26, i + 0.26, colors="black", lw=t["lw"] * 1.6, zorder=4)
        out[g] = (m, e, len(vals))
    ax.set_xticks(range(len(order)), order)
    ax.set_xlim(-0.6, len(order) - 0.4)
    return out


def bar_with_points(ax, groups, values, colors=None, n_inside=True, value_labels=None):
    """Slide-style bar: mean bar, SD whisker, open points, 'n = k' inside the base.

    groups: list of names; values: list of 1-D arrays.
    value_labels: optional list of strings printed bold above each bar (e.g. '91%').
    Use Unicode for units ('S cm⁻¹', 'µg mL⁻¹', 'N/mm²'), not mathtext.
    Call ax.set_ylim(0, top) BEFORE this so 'n = k' sits on the baseline.
    """
    t = _TARGETS[_state["target"]]
    for i, (g, v) in enumerate(zip(groups, values)):
        v = np.asarray(v, float)
        c = (colors or {}).get(g, [TEAL, GREY][i % 2])
        m, sd = v.mean(), v.std(ddof=1) if len(v) > 1 else 0
        ax.bar(i, m, width=0.62, color=c, edgecolor="none", zorder=2)
        ax.errorbar(i, m, yerr=sd, fmt="none", ecolor=INK, capsize=4,
                    elinewidth=t["lw"], zorder=3)
        ax.scatter(i + np.random.default_rng(i).uniform(-0.12, 0.12, len(v)), v,
                   s=(t["marker"] * 0.8) ** 2, facecolors="white", edgecolors=INK,
                   linewidths=t["lw"] * 0.7, zorder=4)
        if n_inside:
            ax.text(i, ax.get_ylim()[0], f"n = {len(v)}", ha="center", va="bottom",
                    color="white", fontsize=t["tick"] * 0.85, fontweight="bold", zorder=5)
        if value_labels:
            top = max(m + sd, v.max())
            ax.annotate(value_labels[i], (i, top), xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom",
                    fontweight="bold", fontsize=t["base"], color=INK)
    ax.set_xticks(range(len(groups)), groups)


def open_violin(ax, data, positions, colors, width=0.7):
    """Prism-style violin: outline only, dashed median, dotted quartiles."""
    t = _TARGETS[_state["target"]]
    parts = ax.violinplot(data, positions=positions, widths=width,
                          showextrema=False, showmedians=False)
    for body, c in zip(parts["bodies"], colors):
        body.set_facecolor("none"); body.set_edgecolor(c)
        body.set_linewidth(t["lw"] * 2); body.set_alpha(1)
    for p, d, c in zip(positions, data, colors):
        q1, med, q3 = np.percentile(d, [25, 50, 75])
        for q, ls in ((q1, ":"), (med, "--"), (q3, ":")):
            ax.hlines(q, p - width * 0.22, p + width * 0.22, colors=c, linestyles=ls,
                      lw=t["lw"])


def mean_band(ax, x, Y, color, label=None, ls="-"):
    """Mean line with shaded +/- SD band (spectra, sweeps, time courses). Y: (n, len(x))."""
    Y = np.asarray(Y, float)
    m, sd = Y.mean(0), Y.std(0, ddof=1) if len(Y) > 1 else np.zeros(Y.shape[1])
    ax.fill_between(x, m - sd, m + sd, color=color, alpha=0.25, lw=0)
    ax.plot(x, m, color=color, ls=ls, label=label)


# --------------------------------------------------------------------------- annotation
def fmt_p(p: float) -> str:
    """Exact p, 2 significant figures; 'p < 0.001' below that."""
    return "p < 0.001" if p < 0.001 else f"p = {p:.2g}" if p < 0.01 else f"p = {p:.3f}".rstrip("0")


def sig_bracket(ax, x1, x2, p, y=None, style="p", h=0.03, gap=0.02):
    """Bracket between two x positions. Call ONLY for significant comparisons.

    style='p'     -> label is the exact p value only (paper default)
    style='stars' -> *, **, ***, **** (thesis / Prism-matched figures)
    Brackets stack upward if you pass increasing y.
    """
    if p >= 0.05:
        return  # never draw 'ns' brackets
    t = _TARGETS[_state["target"]]
    lo, hi = ax.get_ylim()
    log = ax.get_yscale() == "log"
    span = (np.log10(hi) - np.log10(lo)) if log else (hi - lo)
    if y is None:
        ys = [l.get_offsets()[:, 1].max() for l in ax.collections if len(l.get_offsets())]
        y = max(ys) if ys else hi
    ty = lambda v, k: v * 10 ** (k * span) if log else v + k * span
    y0 = ty(y, gap); y1 = ty(y0, h)
    ax.plot([x1, x1, x2, x2], [y0, y1, y1, y0], color="black", lw=t["lw"], clip_on=False,
            gid=ANNOT)
    label = fmt_p(p) if style == "p" else "*" * (1 + (p < .01) + (p < .001) + (p < .0001))
    ax.text((x1 + x2) / 2, ty(y1, 0.005), label, ha="center", va="bottom",
            fontsize=t["tick"] if style == "p" else t["title"] * 1.2, gid=ANNOT)
    top = ty(y1, 0.12)
    if top > hi:
        ax.set_ylim(lo, top)


def ref_line(ax, y, label, color=REF_GREY, ls=":", side="right", band=None):
    """Horizontal reference (control, baseline, threshold, target) with a direct label.

    band: optional (low, high) shaded target range.
    """
    t = _TARGETS[_state["target"]]
    if band:
        ax.axhspan(*band, color=color, alpha=0.25, lw=0, zorder=0)
    ax.axhline(y, color=color, ls=ls, lw=t["lw"] * 1.3, zorder=1)
    x = 1.01 if side == "right" else 0.01
    ax.text(x, y, label, transform=ax.get_yaxis_transform(), ha="left", va="center",
            fontsize=t["tick"], fontweight="bold" if band else "normal", color=color)


def panel_label(ax, letter: str, x=-0.18, y=1.06):
    """Bold panel letter top-left (A, B, C or A-1, A-2)."""
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=_TARGETS[_state["target"]]["letter"],
            fontweight="bold", va="bottom", ha="left")


def finish(ax, title=None, xlabel=None, ylabel=None, rotate=False, logy=False, zero=True):
    """Short bold title, labels with units, optional 45 deg ticks and log y."""
    if title:
        ax.set_title(title, pad=6)
    ax.set_xlabel(xlabel or "")
    if ylabel:
        ax.set_ylabel(ylabel)
    if logy:
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(
            lambda v, _: f"{v:g}" if 1e-3 <= v <= 1e5 else f"$10^{{{int(np.log10(v))}}}$"))
    elif zero and ax.get_ylim()[0] > 0:
        ax.set_ylim(bottom=0)
    if rotate:
        for lab in ax.get_xticklabels():
            lab.set_rotation(45); lab.set_ha("right"); lab.set_rotation_mode("anchor")


def save(fig, stem, outdir=".", formats=("png", "svg"), clean_axes=None):
    """Save PNG + SVG (editable in PowerPoint). Add 'pdf' for journals.

    clean_axes: optional list of axes; also writes '<stem>_clean.png' with all
    annotation text/brackets removed, for re-annotation during PowerPoint assembly.
    """
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    for f in formats:
        fig.savefig(out / f"{stem}.{f}")
    if clean_axes:
        hidden = []
        for ax in clean_axes:
            for a in list(ax.texts) + list(ax.lines):
                if a.get_gid() == ANNOT and a.get_visible():
                    a.set_visible(False); hidden.append(a)
        fig.savefig(out / f"{stem}_clean.png")
        for a in hidden:
            a.set_visible(True)
    return out / f"{stem}.png"
