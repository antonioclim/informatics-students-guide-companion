# Privacy and security

The public payload follows data minimisation and release-by-exception principles. It must not contain credentials, private keys, direct participant identifiers, private contact details, confidential project records, signed forms, restricted full texts or absolute private working paths.

Before each release, run `python scripts/scan_sensitive_content.py --fail-on medium`, inspect every finding contextually and remove sensitive content from both the current tree and Git history where necessary. Automated scanning is necessary but not sufficient.
