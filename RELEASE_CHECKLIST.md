# Release checklist

Use this checklist before making the repository public and creating the archived release.

- [x] Run `python run_all.py` from a clean environment; require `OVERALL PASS`.
- [x] Verify `DATA_AVAILABILITY.md` and confirm no KOSGEB row-level or derived numerical result files are present.
- [x] Software license selected: MIT. `LICENSE` added.
- [x] Confirm author name, ORCID, version, and release date in `CITATION.cff`.
- [ ] Create GitHub release `v2.0.0`.
- [ ] Archive the GitHub release on Zenodo and reserve/publish the DOI.
- [ ] Add the Zenodo DOI to README, CITATION metadata, and the manuscript Code/Data Availability statements.
- [ ] Freeze the exact commit hash and release tag cited by the manuscript.
