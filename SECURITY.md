# Security Policy

## Status

Calyx Command Bridge v0.5.0 is experimental software.
It has not undergone an independent security audit.

## Security boundaries

- The HTTP receiver binds to loopback.
- Remote access is intended through authenticated HTTPS.
- Bash scripts execute inside a restricted Podman container.
- Device tokens expire after 30 days.
- Device credentials can be revoked.

These controls reduce risk but do not guarantee isolation.

## Deployment

Do not expose the receiver directly to the public internet.
Do not publish credentials, cookies, or local device databases.
Do not use this software for safety-critical operations.

## Vulnerability reporting

Until a private GitHub security reporting channel is configured,
do not post vulnerability details or exploit code in public issues.

## Supported versions

Only the current development preview is maintained.
