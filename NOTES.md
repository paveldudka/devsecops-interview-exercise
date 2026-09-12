# Worked reference notes — interviewer only

## Prioritized risks and repository evidence

1. **Critical — server-side request forgery.** `FetchRequest.url` reaches `HttpxTransport.get` after only scheme/hostname validation. A caller can make the cloud workload request loopback, private, link-local, and cloud-provider service addresses that the caller cannot reach directly. Redirect targets take the same path and are also unchecked.
2. **High — unbounded work.** Redirects have no hop limit, and response content is buffered without a service-owned byte limit. A remote endpoint can consume connections, time, memory, or CPU. `httpx` has a default timeout, but it is not an explicit product budget and does not bound response size.
3. **Medium — sensitive logging.** Failures log the caller's full URL and error context. URLs can contain secrets in paths or query strings, making application logs a secondary disclosure surface.

## Chosen improvement and rationale

The reference change evaluates every outbound destination before issuing the request. IP literals and all resolved IPv4/IPv6 answers must be globally routable. The check runs on the initial URL and every redirect target, and redirect chains are capped at five hops. This addresses the highest-impact path while preserving supported public HTTP/HTTPS redirects.

## Validation and limits

Deterministic tests cover direct IPv4/IPv6 protected destinations, a hostname with mixed public/protected answers, a public-to-protected redirect, legitimate public redirect chains, and a redirect cycle. They prove that the application invokes its policy before each mocked outbound hop and that denied requests do not reach the mocked transport.

They do **not** prove complete DNS-rebinding resistance. The reference policy resolves for classification, while `httpx` independently resolves again when connecting; an answer may change between check and use. Production validation must include the actual resolver, proxy, container network, and egress controls. A stronger design would connect to a validated/pinned address while preserving the original host for TLS and HTTP semantics, or delegate resolution and connection enforcement to a trusted egress proxy.

## Residual risks and next actions

1. Enforce workload egress policy or a trusted outbound proxy so application defects cannot reach protected networks.
2. Remove the DNS check/use gap through connection pinning or proxy-side destination enforcement.
3. Stream responses with explicit connect/read/total time and byte budgets.
4. Redact or hash URL paths and query strings in logs; add safe structured failure codes.
5. Define redirect downgrade, port, content-type, and decompression policies from product requirements.

## Requirement update

Public redirects remain supported. `FetchService.fetch` validates the destination policy immediately before each `transport.get`, so every hop is evaluated independently. The adversarial redirect test proves the protected target is never requested, while the positive chain test proves ordinary redirects still work in the model.

## AI usage

Reference solution; not scored. The implementation intentionally uses only standard-library address classification plus the existing transport seam. It rejects mixed DNS answers rather than choosing a public answer, and explicitly rejects the claim that application pre-resolution alone eliminates rebinding.
