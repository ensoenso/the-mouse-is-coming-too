# Security

## Reporting

Please report suspected vulnerabilities privately through GitHub's security
advisory feature rather than a public issue.

## Trust model

The application talks only to the local Plugin Service installed by Logi
Options+. It opens no network listener, sends no telemetry, stores no device
data, and requires no administrator privileges. Device display names and model
identifiers are read in memory only to construct one fixed switching action.

The application does not change the Plugin Service, its permissions, or its
authentication behavior. It deliberately provides no user-facing arbitrary
request facility.

Release apps are ad-hoc signed rather than Developer ID signed or notarized.
The signature contains no person, organization, Team ID, certificate, or Apple
account. Verify the published SHA-256 checksum before overriding Gatekeeper.
