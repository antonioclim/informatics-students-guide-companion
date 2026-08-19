# The Informatics Student’s Guide to Research Projects, Theses and Dissertations — private repository candidate

**Authors:** Antonio Clim and Martino Aldrigo  
**Candidate version:** 1.1.1-rc.3  
**Status:** PRIVATE REVIEW CANDIDATE - PUBLIC RELEASE HOLD  
**Source manuscript SHA-256:** `b275e30b0f9139ae134d7d94fd8c5ccf891fcd95be0e4b562d286d69c9558ab7`  
**Native figure derivatives:** v3.2

This candidate contains selected authorial companion records and the 18 figure sets associated with *The Informatics Student’s Guide to Research Projects, Theses and Dissertations*. It is an internal release-engineering object. It is not a public release, a Zenodo deposit, a DOI-bearing record or a publisher-issued edition.

## What is included

- `companion/` - active Digital Companion v1.1.1 content only
- `figures/01_SVG_AUTHORITATIVE/` - 18 canonical SVG sources
- `figures/02_PNG_TECHNICAL_FALLBACK/` - 18 technical PNG fallbacks
- `figures/06_ODG_NATIVE_EDITABLE_INDIVIDUAL/` - 18 ODG files with native, ungrouped editable objects
- `figures/07_ODG_NATIVE_EDITABLE_CONSOLIDATED/` - one 18-page native editable ODG
- `figures/08_PPTX_NATIVE_EDITABLE_INDIVIDUAL/` - 18 PPTX files with native editable shapes
- `figures/09_PPTX_NATIVE_EDITABLE_CONSOLIDATED/` - one 18-slide native editable PPTX
- `figures/10_NATIVE_EDITABILITY_QA/` - object counts, edit-persistence tests and visual comparison evidence
- `manifests/` - file decisions, rights/privacy classifications and repository inventory
- `scripts/` - local validation and sensitive-content scanning
- `docs/` - controlled release plan and GitHub/Zenodo decision gates

## What is excluded

The repository candidate does not contain the book manuscript, a book PDF, signed declarations, identity documents, confidential records, participant data, restricted full texts, obsolete archived institutional HTML or v1.0 provenance payloads. The detailed basis is recorded in `manifests/EXCLUSIONS_REGISTER.csv`.

## Validation

```bash
python scripts/validate_repository.py
python scripts/scan_sensitive_content.py --fail-on medium
```

These checks do not grant publication rights. They establish only that the candidate matches its declared structure and contains no detected high- or medium-severity sensitive patterns.

## Figure authority

SVG remains the canonical figure format for the book. ODG and PPTX files are object-level editable derivatives. Any accepted edit must be reconciled across the canonical SVG and the derivative formats before release. PNG is a technical preview and fallback only.

## Rights and release boundary

No public licence is granted. Do not change the repository visibility to public, create a release, enable GitHub Pages, reserve or publish a Zenodo DOI, or upload the manuscript unless the author, coauthor, publisher and institutional gates listed in `PUBLIC_RELEASE_HOLD.md` have been closed explicitly. See `RIGHTS_AND_RELEASE_STATUS.md`.

Current official regulations, programme instructions and forms prevail over all dated companion summaries.
