#!/usr/bin/env bash
# Copyright (c) 2026 Seokcheon Lee
# SPDX-License-Identifier: MIT

set -euo pipefail

release_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
class_root="${1:-}"
requested_case="${2:-all}"

if [[ -z "$class_root" ]]; then
  echo "usage: $0 /path/to/class_public [all|LCDM|MT100_F005|MT100_F010|MT100_F020|MT090_F010|MT110_F010]" >&2
  exit 2
fi
if [[ ! -d "$class_root" ]]; then
  echo "CLASS checkout directory not found: $class_root" >&2
  exit 2
fi
class_root="$(cd "$class_root" && pwd)"
if [[ ! -x "$class_root/class" ]]; then
  echo "CLASS executable not found at $class_root/class; compile the patched checkout first." >&2
  exit 2
fi

cases=(LCDM MT100_F005 MT100_F010 MT100_F020 MT090_F010 MT110_F010)
if [[ "$requested_case" != "all" ]]; then
  found=no
  for case_name in "${cases[@]}"; do
    [[ "$requested_case" == "$case_name" ]] && found=yes
  done
  if [[ "$found" != yes ]]; then
    echo "unknown benchmark: $requested_case" >&2
    exit 2
  fi
  cases=("$requested_case")
fi

for case_name in "${cases[@]}"; do
  mkdir -p "$class_root/output/final_six_spectra/$case_name"
  echo "running $case_name"
  (cd "$class_root" && ./class "$release_root/input/$case_name.ini")
done
