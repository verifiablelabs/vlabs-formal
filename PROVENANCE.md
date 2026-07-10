# Provenance

Clean import (no history rewrite) from the archived legacy workspace at commit
`a0f30dc547a73aaae8608d193f94035192404627`. Imported paths were `formal/`
(Lake project, Lean+Mathlib v4.28.0), the compatibility Python mirror,
property tests, and `formal-verification.yml`.

`vlabs-formal` is now canonical for the Lean development. New production
integrations should use `vlabs_sdk.formal_spec`; the wheel packages its local
property-test mirror as `vlabs_formal.formal_spec` and never publishes the
SDK-owned `verifiable_labs_envs` namespace.
