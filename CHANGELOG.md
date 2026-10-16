# Changelog

## 2.0.0 — 2026-10-16

Initial public-safe research release accompanying the DEA-Leak manuscript.

### Added
- Coordinate-granular T0-X, T0-Y, T1-X, and T1-Y attack-path analysis.
- Three protection levels: `full_exact`, `coordinate_exact`, and `coordinate_exact_plus_conditional`.
- Minimum-declared-utility-loss release hardening.
- Package-aware schema inference for the native `deaR` and `Benchmarking` replication conventions.
- Command-line interface and Python package.
- Exhaustive 128-release-subset audit per orientation.
- 144-instance optimizer-versus-brute-force oracle validation.
- 20-case deterministic public coordinate-reconstruction campaign.
- Frozen native verification records for `Benchmarking` and `deaR`.
- Public-safe reproducibility runner.

### Security scope
The release blocks only the modeled DEA reconstruction paths. It is not a formal privacy mechanism.
