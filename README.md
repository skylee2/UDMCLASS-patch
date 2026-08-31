# UDMCLASS patch and reproducibility package

UDMCLASS is the project name for the modifications to CLASS used to study the
mixed cold-dark-matter and self-interacting ultralight-dark-matter (UDM)
benchmarks in the accompanying paper. This v1.0.0 package provides the
certified source patch, six frozen benchmark inputs, compact reference tables,
final Figures 1–3, and reproduction scripts.

This repository **does not redistribute the CLASS source tree**. Obtain
official CLASS v3.3.4 separately from `lesgourg/class_public`, check out exact
commit `e85808324f51fc694d12e3ed7439552a3c3f9540`, and apply the patch locally.

## Requirements

- Git;
- the C compiler and other build dependencies documented by upstream CLASS;
- Python 3.10 or newer;
- NumPy and Matplotlib for figure generation.

The benchmark runs produce high-resolution CLASS outputs and may require
substantial time and storage. Those raw outputs are intentionally not included.

## 1. Obtain the exact upstream, patch, and compile

Set `PACKAGE_ROOT` to the absolute path of this package, then run:

```bash
export PACKAGE_ROOT=/path/to/UDMCLASS_patch_v1.0.0
git clone https://github.com/lesgourg/class_public.git class_public
cd class_public
git checkout --detach e85808324f51fc694d12e3ed7439552a3c3f9540
test "$(git rev-parse HEAD)" = "e85808324f51fc694d12e3ed7439552a3c3f9540"
git apply --check "$PACKAGE_ROOT/patches/udmclass.patch"
git apply "$PACKAGE_ROOT/patches/udmclass.patch"
make -j class
```

The patch SHA-256 must be
`5ecf36d851175d5886bdce774635f0633d325d2b9cdd983b56b209ab88fd620d`.
See [UPSTREAM.md](UPSTREAM.md) and [PATCH_MANIFEST.md](PATCH_MANIFEST.md) for
the upstream and patch provenance.

Verify every publication-candidate file from the package root with:

```bash
shasum -a 256 -c SHA256SUMS
```

As usual, `SHA256SUMS` inventories every other package file and omits itself.

## 2. Run one benchmark or all six

Return to the package root. To run one representative mixed case:

```bash
cd "$PACKAGE_ROOT"
./scripts/run_benchmarks.sh /path/to/class_public MT100_F010
```

To run the complete six-case set:

```bash
./scripts/run_benchmarks.sh /path/to/class_public
```

The accepted case names are `LCDM`, `MT100_F005`, `MT100_F010`,
`MT100_F020`, `MT090_F010`, and `MT110_F010`; omitting the second argument is
equivalent to `all`. Outputs are written under
`/path/to/class_public/output/final_six_spectra/<case>/` because the frozen
input files define those relative CLASS output roots.

## 3. Extract and compare compact quantities

After all six cases finish, run:

```bash
python3 scripts/extract_benchmark_quantities.py \
  --class-root /path/to/class_public
```

By default, this writes:

```text
/path/to/class_public/output/final_six_spectra/reproduction_tables/
├── reproduced_benchmarks.csv
├── reproduced_pk_ratios.csv
└── reproduced_tt_ratios.csv
```

Use `--output-dir /another/path` to choose a different destination. The script
extracts sigma8 and the selected TT and physical-unit P(k) ratios, compares
them numerically with the canonical files in `benchmarks/`, prints the maximum
absolute differences, and exits nonzero if the certified tolerances are not
met. The `H0_km_s_Mpc` and `phi_ini` columns in `reproduced_benchmarks.csv`
identify each frozen case; the reproduced numerical check in that table is
sigma8.

The authoritative compact references are:

- `benchmarks/final_six_benchmarks.csv` — case metadata and final compact
  background/growth quantities;
- `benchmarks/selected_tt_ratios.csv` — selected TT ratios to LCDM;
- `benchmarks/selected_pk_ratios.csv` — selected physical P(k) values and
  ratios to LCDM.

## 4. Reproduce paper Figures 1–3

With all six output directories present, run from the package root:

```bash
python3 scripts/generate_fig1.py --class-root /path/to/class_public
python3 scripts/generate_fig2_fig3.py --class-root /path/to/class_public
```

The scripts overwrite `figures/Fig1.pdf`, `figures/Fig1.png`,
`figures/Fig2.pdf`, `figures/Fig2.png`, `figures/Fig3.pdf`, and
`figures/Fig3.png`. Figure 1 reads the six background tables; Figure 2 reads
the six unlensed TT spectra; Figure 3 reads the six linear matter spectra at
z=0. The Figures 2–3 script checks selected TT and P(k) ratios against the
public compact references before writing either figure. Optional output-path
arguments are documented by each script’s `--help` output.

The included PDFs are the publication-quality final figures, and the PNGs are
GitHub-friendly previews. See [figures/README.md](figures/README.md).

## Validation

[docs/VALIDATION.md](docs/VALIDATION.md) records the successful final
implementation and certification: fresh patch application and compilation,
six successful cases, byte identity for the 30 scientific CLASS products, and
compact-reference agreement. The historical development and diagnostic path is
not part of this public reproduction workflow.

## Repository contents

- `patches/udmclass.patch`: certified five-file source delta;
- `input/`: six frozen publication inputs;
- `benchmarks/`: three canonical compact reference CSV files;
- `scripts/`: benchmark, extraction, comparison, and figure entry points;
- `figures/`: final PDFs and PNG previews, reproducible by the scripts;
- `docs/VALIDATION.md`: public final-validation statement;
- `UPSTREAM.md`, `PATCH_MANIFEST.md`, `LICENSE`, `NOTICE`: provenance and scope;
- `VERSION`, `CHANGELOG.md`, `CITATION.cff`, `SHA256SUMS`: release metadata.

No CLASS source tree, raw CLASS output, private validation archive, manuscript
draft, build product, or development chronology is included.

## Citation, provenance, and license scope

When using this package, cite the accompanying manuscript:

Seokcheon Lee and Jae-Weon Lee, “Cosmology of self-interacting ultralight dark
matter: simultaneous shifts in the Hubble constant and structure growth.”

Use the published identifier when one becomes available. Also follow the
upstream CLASS citation guidance and cite:

D. Blas, J. Lesgourgues, and T. Tram, “The Cosmic Linear Anisotropy Solving
System (CLASS). Part II: Approximation schemes,” JCAP 07 (2011) 034,
<https://doi.org/10.1088/1475-7516/2011/07/034>.

`CITATION.cff` provides machine-readable metadata. The MIT License applies to
original repository-authored scripts and documentation as explained in
`NOTICE`; it does not license CLASS and does not relicense the unified patch as
a whole. Obtain CLASS separately and respect all upstream terms and citation
guidance.
