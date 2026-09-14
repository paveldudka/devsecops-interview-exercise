# Modeled architecture

## Request flow

```text
caller
  -> POST /v1/fetch {"url": "https://public.example/article"}
  -> content_fetcher API
  -> FetchService
  -> outbound HTTP transport
  -> response body returned to caller
```

The API is exposed to external callers and is deployed as a cloud workload. The product needs to retrieve ordinary public HTTP and HTTPS resources and support normal redirect chains.

## Repository boundaries

- `src/content_fetcher/api.py` defines the FastAPI boundary and error mapping.
- `src/content_fetcher/models.py` defines the public request and response shapes.
- `src/content_fetcher/service.py` owns URL validation, fetch behavior, and redirects.
- `src/content_fetcher/transport.py` issues individual requests through `httpx`.
- `tests/` uses deterministic in-memory transports. Tests must not require DNS, external HTTP, cloud services, or credentials.

## What is faked

Candidate-visible tests replace the outbound transport with a scripted in-memory implementation. Status codes, headers, bodies, and redirect responses are fixed test data.

## Limits of local validation

Passing local tests proves behavior only for the modeled inputs and faked responses. It does not reproduce every property of a production deployment or prove that the deployed system is secure. Document assumptions and production controls you would verify separately.
