# GitHub and Zenodo controlled release plan

## Current decision

Keep the candidate private and unpublished. Do not create a release or Zenodo record in the current phase.

## GitHub gate sequence

1. Confirm repository owner and private destination.
2. Obtain written coauthor and publisher decisions.
3. Approve the asset-level rights matrix and public exclusions.
4. Re-run privacy, secret and absolute-path scans.
5. Validate CITATION.cff, manifests, links and figure hashes.
6. Decide the public licence for each asset class.
7. Create the repository privately and push the candidate branch.
8. Configure least-privilege Actions permissions, branch protection and secret controls.
9. Conduct private review and correct findings.
10. Change visibility only after recorded release approval.
11. Create a signed or annotated release tag only after the same approval.

## Zenodo gate sequence

1. Decide whether the repository or a curated subset is the deposit object.
2. Confirm creator order, affiliations and identifiers without inference.
3. Select resource type and description.
4. Decide one licence or a documented mixed-licence arrangement.
5. Exclude the manuscript and any restricted assets unless permission exists.
6. Decide whether to reserve a DOI in draft only after metadata are stable.
7. Publish only after the GitHub release and rights decisions are final.
8. Record the DOI in CITATION.cff and repository metadata only after registration.

## Non-compensation rule

A technically clean repository cannot repair an absent rights grant, an unsafe privacy decision or a publisher conflict.
