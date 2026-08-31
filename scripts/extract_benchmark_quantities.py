#!/usr/bin/env python3
# Copyright (c) 2026 Seokcheon Lee
# SPDX-License-Identifier: MIT

"""Extract compact TT, P(k), and sigma8 checks from six CLASS outputs."""

from __future__ import annotations

import argparse
import csv
import math
from bisect import bisect_left
from pathlib import Path


RELEASE_ROOT = Path(__file__).resolve().parents[1]
REFERENCE = RELEASE_ROOT / "benchmarks"
MODELS = ("LCDM", "MT100_F005", "MT100_F010", "MT100_F020", "MT090_F010", "MT110_F010")
MIXED = MODELS[1:]
TARGET_ELL = (30, 100, 200, 500, 1000, 1500, 2000, 2500)
TARGET_K = (0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.50, 1.00, 1.20, 1.50, 2.00, 5.00)
COMPACT_TOLERANCE = 1.0e-12


def rows(path: Path) -> list[list[float]]:
    with path.open() as handle:
        return [[float(item) for item in line.split()] for line in handle
                if line.strip() and not line.lstrip().startswith("#")]


def interpolate(x: list[float], y: list[float], target: float) -> float:
    index = bisect_left(x, target)
    if index == 0:
        return y[0]
    if index == len(x):
        return y[-1]
    x0, x1 = math.log(x[index - 1]), math.log(x[index])
    weight = (math.log(target) - x0) / (x1 - x0)
    return math.exp(math.log(y[index - 1]) + weight * math.log(y[index] / y[index - 1]))


def sigma8(k: list[float], power: list[float], h: float) -> float:
    radius = 8.0 / h

    def window(value: float) -> float:
        if abs(value) < 1.0e-3:
            return 1.0 - value * value / 10.0 + value**4 / 280.0
        return 3.0 * (math.sin(value) - value * math.cos(value)) / value**3

    values = [ki**3 * pi * window(ki * radius) ** 2 / (2.0 * math.pi**2)
              for ki, pi in zip(k, power)]
    integral = sum(0.5 * (values[i] + values[i - 1]) * math.log(k[i] / k[i - 1])
                   for i in range(1, len(k)))
    return math.sqrt(integral)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract compact quantities and compare them with the certified references."
    )
    parser.add_argument("--class-root", type=Path, required=True,
                        help="root of the patched CLASS checkout")
    parser.add_argument("--output-dir", type=Path,
                        help="destination (default: CLASS output/reproduction_tables)")
    args = parser.parse_args()
    class_root = args.class_root.resolve()
    if not class_root.is_dir():
        raise SystemExit(f"CLASS checkout directory not found: {class_root}")
    output_root = class_root / "output" / "final_six_spectra"
    target = args.output_dir or (output_root / "reproduction_tables")

    required = [REFERENCE / "final_six_benchmarks.csv",
                REFERENCE / "selected_tt_ratios.csv",
                REFERENCE / "selected_pk_ratios.csv"]
    for model in MODELS:
        required.extend((output_root / model / f"{model}_cl.dat",
                         output_root / model / f"{model}_pk.dat"))
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise SystemExit("Missing required reproduction inputs:\n" +
                         "\n".join(map(str, missing)))

    target.mkdir(parents=True, exist_ok=True)

    with (REFERENCE / "final_six_benchmarks.csv").open(newline="") as handle:
        reference = {row["model"]: row for row in csv.DictReader(handle)}
    with (REFERENCE / "selected_tt_ratios.csv").open(newline="") as handle:
        tt_reference = {int(row["ell"]): row for row in csv.DictReader(handle)}
    with (REFERENCE / "selected_pk_ratios.csv").open(newline="") as handle:
        pk_reference = {float(row["k_Mpc^-1"]): row for row in csv.DictReader(handle)}

    data: dict[str, dict[str, object]] = {}
    for model in MODELS:
        h = float(reference[model]["H0_km_s_Mpc"]) / 100.0
        cl = rows(output_root / model / f"{model}_cl.dat")
        pk = rows(output_root / model / f"{model}_pk.dat")
        k = [row[0] * h for row in pk]
        power = [row[1] / h**3 for row in pk]
        data[model] = {
            "ell": {int(row[0]): row[1] for row in cl},
            "k": k,
            "power": power,
            "sigma8": sigma8(k, power, h),
        }

    benchmark_path = target / "reproduced_benchmarks.csv"
    with benchmark_path.open("w", newline="") as handle:
        fields = ("model", "H0_km_s_Mpc", "phi_ini", "sigma8", "reference_sigma8", "delta_sigma8")
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for model in MODELS:
            measured = float(data[model]["sigma8"])
            expected = float(reference[model]["sigma8"])
            writer.writerow({"model": model, "H0_km_s_Mpc": reference[model]["H0_km_s_Mpc"],
                             "phi_ini": reference[model]["phi_ini"], "sigma8": measured,
                             "reference_sigma8": expected, "delta_sigma8": measured - expected})

    tt_path = target / "reproduced_tt_ratios.csv"
    with tt_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["ell"] + [f"TT_{model}_over_LCDM" for model in MIXED])
        for ell in TARGET_ELL:
            baseline = data["LCDM"]["ell"][ell]
            writer.writerow([ell] + [data[model]["ell"][ell] / baseline for model in MIXED])

    pk_path = target / "reproduced_pk_ratios.csv"
    with pk_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["k_Mpc^-1"] + [f"P_{model}_over_LCDM" for model in MIXED])
        for k_value in TARGET_K:
            baseline = interpolate(data["LCDM"]["k"], data["LCDM"]["power"], k_value)
            writer.writerow([k_value] + [interpolate(data[model]["k"], data[model]["power"], k_value) / baseline
                                         for model in MIXED])

    max_sigma8 = max(abs(float(data[model]["sigma8"]) - float(reference[model]["sigma8"]))
                     for model in MODELS)
    max_tt = max(
        abs(data[model]["ell"][ell] / data["LCDM"]["ell"][ell]
            - float(tt_reference[ell][f"TT_{model}_over_LCDM"]))
        for ell in TARGET_ELL for model in MIXED
    )
    max_pk = max(
        abs(interpolate(data[model]["k"], data[model]["power"], k_value)
            / interpolate(data["LCDM"]["k"], data["LCDM"]["power"], k_value)
            - float(pk_reference[k_value][f"P_{model}_over_LCDM"]))
        for k_value in TARGET_K for model in MIXED
    )

    print(benchmark_path)
    print(tt_path)
    print(pk_path)
    print("maximum absolute differences: "
          f"sigma8={max_sigma8:.3e}, TT ratio={max_tt:.3e}, P(k) ratio={max_pk:.3e}")
    if max(max_sigma8, max_tt, max_pk) > COMPACT_TOLERANCE:
        raise SystemExit(f"reference comparison: FAIL (tolerance {COMPACT_TOLERANCE:.1e})")
    print(f"reference comparison: PASS (tolerance {COMPACT_TOLERANCE:.1e})")


if __name__ == "__main__":
    main()
