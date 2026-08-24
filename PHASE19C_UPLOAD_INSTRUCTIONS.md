# Phase 19C controlled browser upload

This is the sole authorised private staging branch for Digital Companion v1.2.0.

Upload **only these two files together in one browser commit** to the branch root:

1. `Students_Guide_Digital_Companion_v1.2.0_PUBLIC_PAYLOAD.zip`
2. `Students_Guide_Digital_Companion_v1.2.0_PUBLIC_PAYLOAD.zip.sha256`

The transactional workflow verifies the sidecar checksum, the exact 401-file repository payload, internal SHA-256 manifests, final title and version, the CC BY 4.0 plus MIT licence architecture, the final book and technical-proof bindings, package safety and all public-release exclusions. It refuses to update `main` if the authorised baseline commit has changed.

Do not upload the book manuscript, technical proof, publisher submission package, QA registry, correspondence, signed forms or personal data. Tag `v1.2.0`, the GitHub Release and public visibility are completed manually in the same browser workflow after the staging Action is green, so the Release remains attributable to Antonio Clim.
