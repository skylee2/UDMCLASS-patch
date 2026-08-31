# Certified patch manifest

## Identity

- Patch: `patches/udmclass.patch`
- Exact base: official CLASS `v3.3.4`, commit
  `e85808324f51fc694d12e3ed7439552a3c3f9540`
- Certified SHA-256:
  `5ecf36d851175d5886bdce774635f0633d325d2b9cdd983b56b209ab88fd620d`
- Size at certification: 142,353 bytes and 2,998 lines
- Delta at certification: five files, 2,345 insertions, 34 deletions

The patch was derived from the final frozen UDMCLASS implementation, reduced
to the production source delta needed by the six public inputs, and certified
against the exact upstream commit above. It was applied to fresh upstream
checkouts, compiled, and used in the successful final six-case validation
described in `docs/VALIDATION.md`.

## Files modified by the patch

| Path | Project-authored modification |
|---|---|
| `include/background.h` | UDM background parameters, state indices, transition controls, and query interfaces. |
| `include/perturbations.h` | UDM perturbation variables and KG-to-effective-fluid matching state. |
| `source/background.c` | Homogeneous scalar evolution, abundance handling, averaged-fluid handoff, and UDM background columns. |
| `source/input.c` | Parsing, validation, and defaults for UDM parameters used by the public inputs. |
| `source/perturbations.c` | Exact KG perturbations, effective-fluid evolution, sources, state transfer, and matching. |

No other path is modified by the certified patch.

## Provenance and licensing boundary

This is a unified diff. Unchanged context lines and removed lines in the patch
originate from upstream CLASS; added lines are the project-authored
modifications relative to the exact base. Consequently, the patch file is not
represented as wholly original MIT-licensed material and does not relicense
any portion of CLASS. See `UPSTREAM.md`, `NOTICE`, and obtain CLASS separately.

The certified patch is immutable. Do not edit headers, context, whitespace, or
metadata inside it. Verify its SHA-256 before use and against `SHA256SUMS`.
