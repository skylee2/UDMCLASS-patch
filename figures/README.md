# Final paper figures

This directory contains the publication-quality PDF and GitHub-preview PNG for
each final figure:

- `Fig1.pdf` and `Fig1.png`: six-case background evolution;
- `Fig2.pdf` and `Fig2.png`: unlensed CMB TT spectra and LCDM residuals;
- `Fig3.pdf` and `Fig3.png`: linear matter spectra at z=0 and LCDM ratios.

The PDFs are the preferred publication and detailed-comparison assets. The PNGs
are convenient previews. They show the same scientific content.

After generating all six CLASS output directories, reproduce these files from
the package root with:

```bash
python3 scripts/generate_fig1.py --class-root /path/to/class_public
python3 scripts/generate_fig2_fig3.py --class-root /path/to/class_public
```

These commands overwrite the six default files in this directory. Use each
script’s `--help` output to select alternate destinations. The scripts read
only the public compact references and the newly generated CLASS output tree;
they contain no private Archive path.
