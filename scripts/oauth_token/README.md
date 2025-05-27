# OAuth Token

To interact with the QI platform authorization is required. The QI CLI (which a user would normally use) is not a suitable tool for authorization in M2M use cases as it is designed for user interactions. Also, in many cases it is not practical to have a dependency on the `quantuminspire` package. This script exists to enable authorization in M2M interactions with the QI platform (e.g. for E2E tests). The following environment variables need to be set:

```
E2E_USERNAME
E2E_PASSWORD
DEFAULT_HOST
```

Note that this requires a user for which password authentication flow is enabled, which is not the case by default for security reasons.
