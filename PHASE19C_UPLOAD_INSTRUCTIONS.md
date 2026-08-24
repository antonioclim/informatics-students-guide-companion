# Phase 19C controlled upload

This temporary private staging branch accepts only the following two root-level files in one browser commit:

1. `Students_Guide_Digital_Companion_v1.2.0_PUBLIC_PAYLOAD.zip`
2. `Students_Guide_Digital_Companion_v1.2.0_PUBLIC_PAYLOAD.zip.sha256`

Do not upload the book manuscript, technical proof, submission package, QA registry, correspondence, signed forms or personal data.

The Phase 19C workflow verifies the sidecar checksum, exact repository structure, internal manifests, final version and title, licence architecture, book–companion bindings, package safety and forbidden-content gates. It refuses publication if `main` has moved from commit `7d570d21a12b739f25fdc586adc8106c92b5d4c2`, if tag `v1.2.0` already exists or if any gate fails.

This file and the staging history are temporary and are not part of the final public payload.
