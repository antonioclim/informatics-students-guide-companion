# GitHub and Zenodo controlled release plan

## Current decision

Keep candidate `1.1.1-rc.3` private and unpublished. Complete the browser-only patch, obtain a green validation run and perform a live connector audit before creating any Zenodo draft. Do not create a GitHub release or Zenodo record in the current phase.

## GitHub gate sequence

1. Upload the v3.2 native ODG/PPTX patch while the repository remains private.
2. Confirm the final workflow is green and the repository reports candidate `1.1.1-rc.3`.
3. Confirm repository owner and private destination.
4. Obtain written coauthor and publisher decisions.
5. Approve the asset-level rights matrix and public exclusions.
6. Re-run privacy, secret and absolute-path scans.
7. Validate `CITATION.cff`, manifests, links and all figure hashes.
8. Decide the public licence for each asset class.
9. Configure least-privilege Actions permissions, branch protection and secret controls.
10. Conduct private review and correct findings.
11. Change visibility only after recorded release approval.
12. Create a release tag only after the same approval.

## Zenodo gate sequence

1. Do not create a Zenodo draft until the live GitHub rc.3 audit passes.
2. Decide whether the repository or a curated subset is the deposit object.
3. Confirm creator order, affiliations and identifiers without inference.
4. Select resource type and description.
5. Decide one licence or a documented mixed-licence arrangement.
6. Exclude the manuscript and any restricted assets unless permission exists.
7. Decide whether to reserve a DOI in draft only after metadata are stable.
8. Publish only after GitHub and rights decisions are final.
9. Record a DOI in `CITATION.cff` only after registration.

## Non-compensation rule

A technically clean repository cannot repair an absent rights grant, an unsafe privacy decision or a publisher conflict.
