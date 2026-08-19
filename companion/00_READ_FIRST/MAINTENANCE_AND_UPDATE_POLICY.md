# Maintenance and update policy

## Versioning

- Patch version: corrections that do not alter the record architecture or route logic.
- Minor version: new records, route examples, registry columns or maintenance controls that remain compatible with existing identifiers.
- Major version: changes to route taxonomy, gate chain, record semantics or evidence obligations.

## Registry maintenance

- Verify institutional sources immediately before any consequential action.
- Verify tool capability and privacy boundaries before consequential use and at least monthly during an active project.
- Preserve the old row and add `superseded_by`; do not overwrite history silently.
- Record the official source, verification date, applicable programme/session and uncertainty.
- A search result, cached page or model summary is not the authority when an official source exists.

## Record maintenance

- Assign stable identifiers and explicit versions.
- Preserve candidate, reviewed, accepted, superseded and withdrawn states.
- Link each consequential change to evidence, reviewer and gate consequence.
- Never store credentials, direct identifiers or restricted source content in templates.

## Release maintenance

- Regenerate MANIFEST.csv and SHA256SUMS.txt after every accepted package change.
- Run the release checklist, CSV audit, DOCX accessibility audit and visual proof inspection.
- Public release requires a separate rights, privacy, licence and publisher decision.
