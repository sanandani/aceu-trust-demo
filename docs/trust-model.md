# ACE-U trust model

ACE-U is a transparent, rule-based triage score for application registrations. It is not a proof of security, a compliance result, or a substitute for tenant-specific review. Results depend on the completeness and freshness of Graph data and on the configured permissions.

## Formula and bands

Each pillar is bounded to 0–100. Total = `0.4 × A + 0.2 × U + 0.4 × C`. A total of 80 or more is **trusted**, 55–79.99 is **review**, and below 55 is **risky**. “Trusted” only means the configured rules did not lower the score significantly.

## Rules

| Rule | Pillar | Effect |
|---|---|---|
| ACEU001 | Authenticity | Client secret gives A=40; federated or managed identity gives A=100; certificate-only gives A=75. |
| ACEU002 | Authenticity | Secret older than 180 days: −15 per qualifying secret. |
| ACEU003 | Authenticity | Certificate older than 365 days: −10 per qualifying certificate. |
| ACEU010 | Uniqueness | Duplicate display name: −40. Names compare case-insensitively after trimming. |
| ACEU011 | Uniqueness | Multi-tenant or personal account audience: −30. |
| ACEU012 | Uniqueness | No listed owner: −20. |
| ACEU020 | Credibility | Any expired credentials: −25 once per identity. |
| ACEU021 | Credibility | More than five app role assignments: −10 each over five, capped at −50. |

When an identity has multiple authentication methods, federated credentials or managed identity establish A=100; otherwise a secret takes precedence over certificates, then certificate-only A=75. Age deductions apply to all listed credentials. This deterministic precedence makes mixed configurations visible while rewarding a configured federated path.

## Data and limitations

The reader requests only Graph v1.0 application, service principal, federated credential, owner, and app role assignment data. No write operation is implemented. A missing relation can mean an empty relation or insufficient Graph permission; use the report with that limitation in mind. Sign-in behavior, Conditional Access, privilege sensitivity, and managed identity inventory are not fully modeled in v0.1.

Homepage: [https://imshubh.com](https://imshubh.com).
