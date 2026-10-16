# Security policy

DEA ArtifactGuard 2.0 is research software for analyzing post-computation disclosure paths in DEA result exports.

## Reporting a security issue
Do not open a public issue containing confidential DEA records, proprietary export bundles, credentials, or institutionally protected data. Report only a minimal public-safe reproduction.

## Scope
The software detects and blocks only the DEA-specific reconstruction paths encoded by its rule compiler for the selected protection level. It does not provide differential privacy, cryptographic confidentiality, or protection against unmodeled inference, repeated releases, side channels, collusion, or adaptive querying.

See `SECURITY_SCOPE.md` for the scientific scope statement.
