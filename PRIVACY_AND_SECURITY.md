# Privacy and security controls

This candidate has been assembled according to data minimisation and release-by-exception principles.

## Prohibited content

Do not commit credentials, tokens, private keys, personal phone numbers, private email addresses, direct participant identifiers, confidential data, signed declarations, internal prompts containing restricted material or absolute local working paths.

## Required checks

Before any push or release:

1. run `python scripts/scan_sensitive_content.py --fail-on medium`;
2. review every finding rather than relying on pattern matching alone;
3. remove the content from the complete Git history where necessary;
4. revoke or rotate any exposed credential;
5. re-run the repository validator;
6. record the result in the release checklist.

A clean automated scan is necessary but not sufficient. Human review remains required for contextual privacy, confidentiality and rights risks.
