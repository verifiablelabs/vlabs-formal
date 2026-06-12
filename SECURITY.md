# Security Policy

## Reporting a vulnerability

Please report suspected vulnerabilities **privately** to
**security@verifiable-labs.com**. Do not open public issues for security
reports. We aim to acknowledge reports within 72 hours.

## Scope notes

This repository never contains hidden evaluation content, gold answers,
anti-hack detection details, private verifier logic, customer data, or
secrets. If you believe any such material has leaked here, treat it as a
security report and contact us privately.

## Hardening recommendations (maintainers)

- Branch protection on `main`: require pull requests, at least one review,
  and passing status checks; no force pushes.
- Enable **CodeQL** default setup and **Dependabot** alerts + security updates.
- Pin GitHub Actions to specific versions.
