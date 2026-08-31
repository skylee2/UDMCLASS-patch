#!/usr/bin/env python3
# Copyright (c) 2026 Seokcheon Lee
# SPDX-License-Identifier: MIT

"""Generate paper Figure 1 from newly generated benchmark outputs.

The figure uses all six benchmark backgrounds. This script does not run CLASS.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

RELEASE_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = RELEASE_ROOT / "benchmarks"
OUTPUT: Path
MODELS = ("MT100_F005", "MT100_F010", "MT100_F020", "MT090_F010", "MT110_F010")
COLORS = {
    "MT100_F005": "#2878B5", "MT100_F010": "#2C9F45", "MT100_F020": "#D83A32",
    "MT090_F010": "#7A5DC7", "MT110_F010": "#E18727",
}
STYLES = {
    "MT100_F005": "--", "MT100_F010": "-", "MT100_F020": ":",
    "MT090_F010": (0, (5, 2, 1, 2)), "MT110_F010": "-.",
}
Z_PHYS_OSC_REP = 1.1e9
Z_HANDOFF = 1.0e6
Z_EQ_REP = 3402.875
Z_M_MIN = 7603.263
Z_M_MAX = 12070.015


def load_plotting_dependencies() -> None:
    global plt, np
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as pyplot
        import numpy as numpy
    except ModuleNotFoundError as error:
        raise SystemExit(
            f"Missing Python plotting dependency '{error.name}'. Install NumPy and Matplotlib."
        ) from error
    plt = pyplot
    np = numpy


def read_benchmarks() -> dict[str, dict[str, str]]:
    with (ANALYSIS / "final_six_benchmarks.csv").open(newline="") as handle:
        return {row["model"]: row for row in csv.DictReader(handle)}


def source_path(model: str) -> Path:
    return OUTPUT / model / f"{model}_background.dat"


def bin_means(x: np.ndarray, quantities: list[np.ndarray], bins: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
    keep = (x >= bins[0]) & (x <= bins[-1])
    x = x[keep]
    index = np.clip(np.digitize(np.log10(x), np.log10(bins)) - 1, 0, len(bins) - 2)
    count = np.bincount(index, minlength=len(bins) - 1).astype(float)
    means = []
    for quantity in quantities:
        total = np.bincount(index, weights=quantity[keep], minlength=len(bins) - 1)
        means.append(np.divide(total, count, out=np.full_like(total, np.nan), where=count > 0))
    return np.sqrt(bins[:-1] * bins[1:]), means


def read_lcdm(bins: np.ndarray) -> dict[str, np.ndarray]:
    values = np.loadtxt(source_path("LCDM"), comments="#", usecols=(0, 3))
    x, (hubble,) = bin_means(1.0 + values[:, 0], [values[:, 1]], bins)
    return {"x": x, "H": hubble}


def read_mixed(model: str, bins: np.ndarray) -> dict[str, np.ndarray]:
    # z, H, rho_udm, p_udm, rho_tot
    values = np.loadtxt(source_path(model), comments="#", usecols=(0, 3, 13, 14, 20))
    x, (hubble, rho_udm, p_udm, rho_tot) = bin_means(
        1.0 + values[:, 0], [values[:, 1], values[:, 2], values[:, 3], values[:, 4]], bins
    )
    return {"x": x, "H": hubble, "omega_udm": rho_udm / rho_tot, "w_udm": p_udm / rho_udm}


def interp_positive(x: np.ndarray, y: np.ndarray, target: np.ndarray) -> np.ndarray:
    mask = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    return np.exp(np.interp(np.log(target), np.log(x[mask]), np.log(y[mask])))


def model_label(row: dict[str, str]) -> str:
    return rf"$\widetilde m={float(row['mtilde_eV']):.1f}\,$eV, $f_{{\rm UDM}}={float(row['f_UDM']):.2f}$"


def add_global_epochs(axis: plt.Axes) -> None:
    axis.axvline(1.0 + Z_EQ_REP, color="0.55", lw=0.9, ls="--", zorder=0)
    axis.axvline(1.0 + Z_HANDOFF, color="0.45", lw=1.0, ls=":", zorder=0)
    axis.axvline(1.0 + Z_PHYS_OSC_REP, color="0.35", lw=1.0, ls=(0, (5, 2, 1, 2)), zorder=0)


def build_figure(pdf_path: Path, png_path: Path) -> None:
    benchmarks = read_benchmarks()
    bins = np.logspace(0.0, 11.2, 321)
    lcdm = read_lcdm(bins)
    data = {model: read_mixed(model, bins) for model in MODELS}
    plt.rcParams.update({
        "font.size": 10.9, "axes.labelsize": 12.1, "axes.titlesize": 12.6,
        "legend.fontsize": 8.9, "xtick.labelsize": 10.9, "ytick.labelsize": 10.9,
        "figure.dpi": 150, "savefig.bbox": "tight",
    })
    fig, axes = plt.subplots(1, 3, figsize=(13.1, 4.25), constrained_layout=True)
    for model in MODELS:
        item = data[model]
        reference_h = interp_positive(lcdm["x"], lcdm["H"], item["x"])
        label = model_label(benchmarks[model])
        axes[0].plot(item["x"], item["H"] / reference_h, color=COLORS[model],
                     ls=STYLES[model], lw=1.65, label=label)
        axes[1].plot(item["x"], item["omega_udm"], color=COLORS[model],
                     ls=STYLES[model], lw=1.65, label=label)
        axes[2].plot(item["x"], item["w_udm"], color=COLORS[model],
                     ls=STYLES[model], lw=1.45, label=label)
    axes[0].axhline(1.0, color="black", lw=0.9)
    axes[0].set_ylim(0.992, 1.075)
    axes[0].set_ylabel(r"$H(z)/H_{\Lambda{\rm CDM}}(z)$")
    axes[0].set_title("(a) Expansion history")
    axes[1].set_yscale("log")
    axes[1].set_ylim(1e-8, 0.25)
    axes[1].set_ylabel(r"$\Omega_\phi(z)=\rho_\phi/\rho_{\rm tot}$")
    axes[1].set_title("(b) Scalar energy fraction")
    axes[1].legend(loc="lower left", frameon=False)
    axes[2].axhline(-1.0, color="0.7", lw=0.75)
    axes[2].axhline(0.0, color="0.7", lw=0.75)
    axes[2].axhline(1.0 / 3.0, color="0.7", lw=0.75)
    axes[2].set_ylim(-1.12, 0.55)
    axes[2].set_ylabel(r"$\langle p_\phi\rangle_{\rm bin}/\langle\rho_\phi\rangle_{\rm bin}$")
    axes[2].set_title("(c) Binned scalar equation of state")
    for axis in axes:
        axis.axvspan(1.0 + Z_M_MIN, 1.0 + Z_M_MAX, color="0.75",
                    alpha=0.18, lw=0, zorder=0)
        add_global_epochs(axis)
        axis.set_xscale("log")
        axis.set_xlim(1.0, bins[-1])
        axis.set_xlabel(r"$1+z$")
        axis.grid(True, which="major", alpha=0.22)
        axis.tick_params(direction="in", top=True, right=True)
    axes[0].text(1.0 + Z_EQ_REP, 1.071, r"$z_{\rm eq}$", rotation=90, va="top", ha="right", fontsize=8.9)
    axes[0].text(1.0 + Z_HANDOFF, 1.071, r"$z_{\rm handoff}$", rotation=90, va="top", ha="right", fontsize=8.9)
    axes[0].text(1.0 + Z_PHYS_OSC_REP, 1.071, r"$z_{\rm phys,osc}$", rotation=90, va="top", ha="right", fontsize=8.9)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(pdf_path)
    fig.savefig(png_path, dpi=220)
    plt.close(fig)


def main() -> None:
    global OUTPUT
    parser = argparse.ArgumentParser(description="Generate final paper Figure 1.")
    parser.add_argument("--class-root", type=Path, required=True,
                        help="root of the patched CLASS checkout")
    parser.add_argument("--pdf", type=Path, default=RELEASE_ROOT / "figures" / "Fig1.pdf")
    parser.add_argument("--png", type=Path, default=RELEASE_ROOT / "figures" / "Fig1.png")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    OUTPUT = args.class_root.resolve() / "output" / "final_six_spectra"
    required = [ANALYSIS / "final_six_benchmarks.csv", source_path("LCDM")]
    required.extend(source_path(model) for model in MODELS)
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise SystemExit("Missing required reproduction inputs:\n" + "\n".join(map(str, missing)))
    if args.check_only:
        print("reproduction input check:")
        for path in required:
            print(path)
        return
    load_plotting_dependencies()
    build_figure(args.pdf, args.png)
    print(f"wrote {args.pdf}")
    print(f"wrote {args.png}")


if __name__ == "__main__":
    main()
