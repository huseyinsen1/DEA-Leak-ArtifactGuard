# DEA-Leak / DEA ArtifactGuard 2.0

Public-safe source code and reproducibility materials for the manuscript:

**DEA-Leak: Post-Computation Record Reconstruction and Automated Release Hardening for Data Envelopment Analysis**

DEA ArtifactGuard 2.0 analyzes the post-computation result-release surface of radial CCR/BCC Data Envelopment Analysis (DEA). It compiles DEA-specific reconstruction conditions into machine-checkable attack paths, audits intended export schemas, and can compute a minimum-declared-utility-loss suppression plan for a selected protection level.

## Why this repository exists

DEA software often exports more than an efficiency score: lambda intensities, slacks, peer/reference information, and absolute targets may also be released. Under explicit conditions, combinations of these outputs can algebraically determine a confidential DMU record or individual input/output coordinates.

This repository provides the public, non-confidential implementation and validation materials used to test those reconstruction paths and the ArtifactGuard 2.0 release-hardening layer.

## Quick start

Requires Python 3.10+.

```bash
python -m pip install -e .
python run_all.py
```

Expected final line:

```text
OVERALL PASS
```

## Command-line example

```bash
artifactguard \
  --orientation out \
  --release score,target_x,target_y,slack_x,slack_y,lambda \
  --aux peer_x,peer_y \
  --protection coordinate_exact \
  --mandatory score
```

## Reproducibility coverage

The public suite includes:

- 1,000-trial algebra self-test;
- 20 deterministic synthetic CCR/BCC × input/output coordinate-reconstruction cases;
- exhaustive enumeration of all 128 release subsets per orientation;
- 144 risky optimizer-vs-brute-force oracle checks;
- 12 ArtifactGuard core unit tests;
- frozen native verification-record checks for `Benchmarking` and `deaR`.

The real KOSGEB case is intentionally not executable from this repository because the administrative source table is confidential. No KOSGEB row-level data or KOSGEB-derived numerical result files are included.

## Repository structure

```text
src/dea_artifactguard/     ArtifactGuard 2.0 Python package and CLI
experiments/               Public deterministic experiments and validation campaigns
tests/                     Unit and native-record tests
native_replication/        R replication scripts/protocol for Benchmarking and deaR
native_results/            Frozen public-safe native verification summaries
results/                   Frozen public-safe validation outputs
docs/                      Research/reproducibility notes
run_all.py                 Full public-safe validation runner
```

## Security scope

ArtifactGuard 2.0 blocks only the DEA-specific reconstruction paths encoded by its rule compiler. It is **not** differential privacy, cryptographic privacy, an information-theoretic leakage bound, or a guarantee against unmodeled inference, repeated releases, side channels, collusion, or adaptive querying.

See [`SECURITY_SCOPE.md`](SECURITY_SCOPE.md).

## Data availability

See [`DATA_AVAILABILITY.md`](DATA_AVAILABILITY.md). Do not upload confidential or institutionally protected records to issues or pull requests.

## Citation

Citation metadata are provided in [`CITATION.cff`](CITATION.cff). The version-specific archived research software DOI is [`10.5281/zenodo.23423474`](https://doi.org/10.5281/zenodo.23423474) (reserved on Zenodo; activates when the deposit is published).

This DOI identifies the archived `v2.0.0` software release. The underlying GitHub source release is [`v2.0.0`](https://github.com/huseyinsen1/DEA-Leak-ArtifactGuard/releases/tag/v2.0.0).

## License

The source code in this repository is released under the [MIT License](LICENSE). Third-party dependencies retain their own licenses.
