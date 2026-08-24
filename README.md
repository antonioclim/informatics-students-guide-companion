# Student’s Guide Digital Companion

This repository provides the public Digital Companion to *Student’s Guide to Research Projects, Theses and Dissertations: From Topic Selection to Evidence, Implementation, Writing and Defence* by Antonio Clim and Martino Aldrigo.

## Release identity

- Digital Companion version: **1.2.0**
- Associated book: **v3.9.0 — Final Publisher Master**
- Figure authority: **v4.3**
- Repository creator and curator: **Antonio Clim**
- Associated book authors: **Antonio Clim and Martino Aldrigo**
- Stable repository: https://github.com/antonioclim/informatics-students-guide-companion

## Contents

The release contains the companion workbook, minimum and full templates, eight route kits with privacy-safe synthetic worked examples, AI-use TRACE and disclosure records, submission and defence controls, institutional-source registers, schemas, validators and 18 figure sets in SVG, PNG, ODG and PPTX formats. Formal Appendices A–E are absent from the final book. Their stable methodological principles are integrated in the book, while editable operational resources are provided through modules DC-A–DC-E.

The book manuscript, technical proof, publisher-facing files, correspondence, signed forms, personal data, restricted full texts and real student records are excluded.

## Licensing

Documentation, the workbook, templates, synthetic examples, schemas, registers and SVG, PNG, ODG and PPTX files are licensed under **CC BY 4.0**. Scripts and code are licensed under the **MIT License**. The authoritative mapping is in `manifests/FILE_CLASS_LICENCE_REGISTER.csv`.

## Use and limitations

This companion supplements rather than replaces the book, current regulations, official forms, programme instructions or competent written decisions. Institutional links and session-specific values are dated records and must be reverified before consequential use. Synthetic examples illustrate workflow and record structure; they are not empirical findings.

## Validation

Run:

```bash
python scripts/validate_release_candidate.py
```

The validation suite checks release structure, manifests, internal links, file-class licensing, sensitive-content patterns, the v3.9.0 book binding, figure assets and workbook integrity. Automated checks do not replace contextual review of rights, privacy or current institutional requirements.

## Citation and archival preservation

Use `CITATION.cff` for repository citation metadata. Versioned archival preservation is managed through Zenodo. No Zenodo DOI is asserted in this release asset; consult verified release metadata for the archived identifier of the version used.
