# Data-license matrix

Only server-side **daily aggregates** (counts per day × native category)
are redistributed here, never record-level data. Exact query URLs,
retrieval timestamps, and SHA-256 checksums are in
`data/raw/*/*_manifest.json`.

| Layer | Source | License / terms | Redistribution of aggregates |
|---|---|---|---|
| NYC 311 (`erm2-nwe9`) | NYC Open Data | NYC Open Data terms of use (free use, no registration) | Permitted with attribution |
| Chicago 311 (`v6vf-nfxy`) | Chicago Data Portal | Chicago data terms of use | Permitted with attribution |
| San Francisco 311 (`vw6y-z8j6`) | DataSF | PDDL (Public Domain Dedication and License) | Permitted |
| Austin 311 (`xwdj-i9he`) | City of Austin Open Data | Austin open-data terms (public domain dedication) | Permitted |
| Weather | NOAA GHCN-Daily via AWS Open Data Program | U.S. Government work / NOAA open-data policy | Permitted |

Code in this repository is MIT-licensed (`LICENSE`). The manuscript and
supplement PDFs are © the author; see the paper for its copyright notice.

**Frozen data vs. live portals.** The aggregates here are frozen as of the
acquisition timestamps in the manifests. City portals backfill and revise
historical records continuously, so a fresh re-acquisition WILL differ
slightly from the frozen layer; the paper's numbers are defined against
the frozen layer only.
