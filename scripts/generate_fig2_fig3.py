#!/usr/bin/env python3
# Copyright (c) 2026 Seokcheon Lee
# SPDX-License-Identifier: MIT

"""Generate paper Figures 2 (TT) and 3 (linear P(k)).

Both figures show the final fraction scan and mass-parameter scan. Raw CLASS
k and P(k) are converted to physical Mpc^-1 and Mpc^3. Selected ratios are
checked against the compact reference CSVs before figures are written.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

RELEASE_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = RELEASE_ROOT / "benchmarks"
OUTPUT: Path
ALL_MODELS = ("LCDM", "MT100_F005", "MT100_F010", "MT100_F020", "MT090_F010", "MT110_F010")
F_SCAN = ("MT100_F005", "MT100_F010", "MT100_F020")
M_SCAN = ("MT090_F010", "MT100_F010", "MT110_F010")
COLORS = {
    "MT100_F005": "#2878B5", "MT100_F010": "#2C9F45", "MT100_F020": "#D83A32",
    "MT090_F010": "#7A5DC7", "MT110_F010": "#E18727",
}
STYLES = {
    "MT100_F005": "--", "MT100_F010": "-", "MT100_F020": ":",
    "MT090_F010": (0, (5, 2, 1, 2)), "MT110_F010": "-.",
}


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


def data_path(model: str, suffix: str) -> Path:
    return OUTPUT / model / f"{model}_{suffix}.dat"


def read_model(model: str, benchmark: dict[str, str]) -> dict[str, np.ndarray]:
    cl = np.loadtxt(data_path(model, "cl"), comments="#")
    pk = np.loadtxt(data_path(model, "pk"), comments="#")
    h = float(benchmark["H0_km_s_Mpc"]) / 100.0
    return {"ell": cl[:, 0], "tt": cl[:, 1], "k": pk[:, 0] * h, "p": pk[:, 1] / h**3}


def log_interp(x: np.ndarray, y: np.ndarray, target: float | np.ndarray) -> float | np.ndarray:
    result = np.exp(np.interp(np.log(target), np.log(x), np.log(y)))
    return float(result) if np.ndim(result) == 0 else result


def validate_selected(data: dict[str, dict[str, np.ndarray]]) -> dict[str, float]:
    max_tt = 0.0
    with (ANALYSIS / "selected_tt_ratios.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            ell = int(row["ell"])
            lcdm = data["LCDM"]["tt"][int(np.searchsorted(data["LCDM"]["ell"], ell))]
            for model in ALL_MODELS[1:]:
                actual = data[model]["tt"][int(np.searchsorted(data[model]["ell"], ell))] / lcdm
                max_tt = max(max_tt, abs(actual - float(row[f"TT_{model}_over_LCDM"])))
    max_pk = 0.0
    with (ANALYSIS / "selected_pk_ratios.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            k = float(row["k_Mpc^-1"])
            lcdm = log_interp(data["LCDM"]["k"], data["LCDM"]["p"], k)
            for model in ALL_MODELS[1:]:
                actual = log_interp(data[model]["k"], data[model]["p"], k) / lcdm
                max_pk = max(max_pk, abs(actual - float(row[f"P_{model}_over_LCDM"])))
    if max_tt > 1e-12 or max_pk > 1e-12:
        raise RuntimeError(f"authoritative ratio mismatch: TT={max_tt:.3e}, Pk={max_pk:.3e}")
    return {"max_abs_tt_ratio_error": max_tt, "max_abs_pk_ratio_error": max_pk}


def label(model: str, row: dict[str, str], scan: str) -> str:
    lead = (rf"$f_{{\rm UDM}}={float(row['f_UDM']):.2f}$" if scan == "fraction"
            else rf"$\widetilde m={float(row['mtilde_eV']):.1f}\,$eV")
    return lead + rf", $H_0={float(row['H0_km_s_Mpc']):.2f}$, $\sigma_8={float(row['sigma8']):.4f}$"


def setup_style() -> None:
    plt.rcParams.update({
        "font.size": 9.4, "axes.labelsize": 10.4, "axes.titlesize": 10.9,
        "legend.fontsize": 7.7, "figure.dpi": 150, "savefig.bbox": "tight",
    })


def plot_tt(data: dict[str, dict[str, np.ndarray]], benchmarks: dict[str, dict[str, str]],
            pdf_path: Path, png_path: Path) -> dict[str, float]:
    setup_style()
    fig = plt.figure(figsize=(11.1, 5.55), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=(3.1, 1.15))
    axes = [[fig.add_subplot(grid[row, col]) for col in range(2)] for row in range(2)]
    lcdm = data["LCDM"]
    maxima: dict[str, float] = {}
    scans = ((F_SCAN, "fraction", r"fixed $\widetilde m=1.0\,$eV"),
             (M_SCAN, "mass", r"fixed $f_{\rm UDM}=0.10$"))
    for col, (models, scan, title) in enumerate(scans):
        top, bottom = axes[0][col], axes[1][col]
        top.plot(lcdm["ell"], 1e10 * lcdm["tt"], color="black", lw=2.0, label=r"$\Lambda$CDM")
        for model in models:
            item = data[model]
            reference = np.interp(item["ell"], lcdm["ell"], lcdm["tt"])
            residual = 100.0 * (item["tt"] / reference - 1.0)
            maxima[model] = float(np.max(np.abs(residual)))
            top.plot(item["ell"], 1e10 * item["tt"], color=COLORS[model], ls=STYLES[model],
                     lw=1.7, label=label(model, benchmarks[model], scan))
            bottom.plot(item["ell"], residual, color=COLORS[model], ls=STYLES[model], lw=1.55)
        top.set_title(f"TT spectra: {title}")
        top.set_ylabel(r"$10^{10}D_\ell^{TT}$")
        top.legend(loc="upper right", frameon=False)
        bottom.axhline(0.0, color="black", lw=0.85)
        bottom.set_ylabel(r"$100(D_\ell/D_\ell^{\Lambda{\rm CDM}}-1)$ [\%]")
        bottom.set_xlabel(r"Multipole $\ell$")
        for axis in (top, bottom):
            axis.set_xlim(2, 2500)
            axis.grid(True, which="major", alpha=0.22)
            axis.tick_params(direction="in", top=True, right=True)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(pdf_path)
    fig.savefig(png_path, dpi=220)
    plt.close(fig)
    return maxima


def plot_pk(data: dict[str, dict[str, np.ndarray]], benchmarks: dict[str, dict[str, str]],
            pdf_path: Path, png_path: Path) -> None:
    setup_style()
    fig = plt.figure(figsize=(11.1, 5.55), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=(3.1, 1.15))
    axes = [[fig.add_subplot(grid[row, col]) for col in range(2)] for row in range(2)]
    lcdm = data["LCDM"]
    scans = ((F_SCAN, "fraction", r"fixed $\widetilde m=1.0\,$eV"),
             (M_SCAN, "mass", r"fixed $f_{\rm UDM}=0.10$"))
    for col, (models, scan, title) in enumerate(scans):
        top, bottom = axes[0][col], axes[1][col]
        top.plot(lcdm["k"], lcdm["p"], color="black", lw=2.0, label=r"$\Lambda$CDM")
        for model in models:
            item = data[model]
            mask = (item["k"] >= 1e-4) & (item["k"] <= 5.0)
            ratio = item["p"][mask] / log_interp(lcdm["k"], lcdm["p"], item["k"][mask])
            top.plot(item["k"], item["p"], color=COLORS[model], ls=STYLES[model], lw=1.7,
                     label=label(model, benchmarks[model], scan))
            bottom.plot(item["k"][mask], ratio, color=COLORS[model], ls=STYLES[model], lw=1.55)
        top.set_title(f"Linear matter power: {title}")
        top.set_ylabel(r"$P(k,z=0)\ [{\rm Mpc}^3]$")
        top.legend(loc="lower left", frameon=False)
        bottom.axhline(1.0, color="black", lw=0.85)
        bottom.set_ylabel(r"$P/P_{\Lambda{\rm CDM}}$")
        bottom.set_xlabel(r"$k\ [{\rm Mpc}^{-1}]$")
        for axis in (top, bottom):
            axis.set_xscale("log")
            axis.set_xlim(1e-4, 5.0)
            axis.axvspan(0.02, 0.1, color="0.7", alpha=0.18)
            axis.grid(True, which="major", alpha=0.22)
            axis.tick_params(direction="in", top=True, right=True)
        top.set_yscale("log")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(pdf_path)
    fig.savefig(png_path, dpi=220)
    plt.close(fig)


def main() -> None:
    global OUTPUT
    parser = argparse.ArgumentParser(description="Generate final paper Figures 2 and 3.")
    parser.add_argument("--class-root", type=Path, required=True,
                        help="root of the patched CLASS checkout")
    parser.add_argument("--fig2-pdf", type=Path, default=RELEASE_ROOT / "figures" / "Fig2.pdf")
    parser.add_argument("--fig2-png", type=Path, default=RELEASE_ROOT / "figures" / "Fig2.png")
    parser.add_argument("--fig3-pdf", type=Path, default=RELEASE_ROOT / "figures" / "Fig3.pdf")
    parser.add_argument("--fig3-png", type=Path, default=RELEASE_ROOT / "figures" / "Fig3.png")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    OUTPUT = args.class_root.resolve() / "output" / "final_six_spectra"
    required = [ANALYSIS / "final_six_benchmarks.csv",
                ANALYSIS / "selected_tt_ratios.csv", ANALYSIS / "selected_pk_ratios.csv"]
    for model in ALL_MODELS:
        required.extend((data_path(model, "cl"), data_path(model, "pk")))
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise SystemExit("Missing required reproduction inputs:\n" + "\n".join(map(str, missing)))
    if args.check_only:
        print("reproduction input check:")
        for path in required:
            print(path)
        return
    load_plotting_dependencies()
    benchmarks = read_benchmarks()
    data = {model: read_model(model, benchmarks[model]) for model in ALL_MODELS}
    validation = validate_selected(data)
    maxima = plot_tt(data, benchmarks, args.fig2_pdf, args.fig2_png)
    plot_pk(data, benchmarks, args.fig3_pdf, args.fig3_png)
    print(validation)
    print("full-grid maximum absolute TT residuals [%]:", maxima)
    for path in (args.fig2_pdf, args.fig2_png, args.fig3_pdf, args.fig3_png):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
