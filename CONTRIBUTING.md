# Contributing

This repository accompanies a research article and prioritizes reproducibility of the frozen release.

## Before opening an issue or pull request
- Reproduce the problem with public or synthetic data.
- Do not submit confidential KOSGEB records or any other protected third-party data.
- Run `python run_all.py` and report whether the suite passes.
- Keep changes within the stated security scope unless clearly labeled as an extension.

## Development setup

```bash
python -m pip install -e .
python run_all.py
```

## Research extensions

Extensions to non-radial, network, dynamic, SBM, DDF, super-efficiency, or repeated-release settings should be treated as new model-specific work rather than assumed to inherit the current reconstruction rules.
