# Final implementation and validation

## Certified implementation

The v1.0.0 patch targets official CLASS v3.3.4 at exact commit
`e85808324f51fc694d12e3ed7439552a3c3f9540`. Its certified SHA-256 is
`5ecf36d851175d5886bdce774635f0633d325d2b9cdd983b56b209ab88fd620d`.

The final implementation evolves the UDM scalar with the exact
Klein–Gordon (KG) treatment before the configured numerical handoff and with
the production effective-fluid treatment afterward. At the handoff it uses
oscillation-averaged scalar stress-energy and transfers the non-UDM state
continuously. Smooth activation is used for the effective-fluid contribution.
The physical onset of rapid scalar oscillations, the numerical KG-to-fluid
handoff, and the quartic-to-quadratic transition remain distinct quantities.

## What was validated

The final certification used the six frozen public inputs: one LCDM baseline
and five mixed UDM cases spanning the fixed-mass fraction scan and the
fixed-fraction mass-parameter scan.

- The certified patch applied cleanly to the exact upstream and compiled.
- All six supplied inputs completed successfully.
- Each case produced regular background and thermodynamics tables, complete
  finite unlensed TT spectra through multipole 2500, and finite positive linear
  matter spectra over the paper range.
- Background, thermodynamics, TT, P(k), and transfer products for every case
  were byte-identical to the immutable final scientific products: 30/30 files.
- The public compact reference CSV files are byte-identical to their canonical
  frozen counterparts.
- The public extractor agreed in sigma8 to a maximum absolute difference of
  `4.44e-16`, in selected TT ratios to `0`, and in selected P(k) ratios to
  `1.78e-15`.
- Final Figures 1–3 were produced from the successful six-case products.

The certification tolerances were `1e-12` for sigma8 and compact ratios and
`1e-10 Mpc` for the recorded background distance quantities. The stronger
full-product check required byte identity and passed.

## How to verify the public package

Follow `README.md` to obtain the exact upstream commit, verify and apply the
patch, compile, and run all six inputs. Then run
`scripts/extract_benchmark_quantities.py`: it writes reproduced compact tables,
compares sigma8 and selected ratios with `benchmarks/`, reports the maximum
absolute differences, and fails if the certified compact tolerances are
exceeded. Finally, run the two plotting scripts and compare their outputs with
the supplied final PDF figures and PNG previews.

The compact references are scientific checkpoints, not substitutes for the
new six-case run. Raw CLASS outputs and the private immutable validation archive
are intentionally not distributed.
