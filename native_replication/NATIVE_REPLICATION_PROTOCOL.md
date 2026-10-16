# Native-package replication protocol

The frozen JSON records in `native_results/` were produced from native R package exports. The Python public suite does **not** re-solve those R DEA models. To regenerate the native evidence, run the R scripts in an environment with `Benchmarking` and `deaR`, export their native result files, and pass them to the corresponding verifier workflow used by the study. Benchmarking supports the T1 claim; deaR supports T0 and T1. Do not infer a Benchmarking T0 result from this package.
