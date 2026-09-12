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

The service is modeled as running in a cloud workload. Callers do not share the workload's network position. The product needs to retrieve ordinary public HTTP and HTTPS resources and support normal redirect chains.

## Repository boundaries

- `src/content_fetcher/api.py` defines the FastAPI boundary and error mapping.
- `src/content_fetcher/service.py` owns fetch behavior and redirect handling.
- `src/content_fetcher/transport.py` adapts the service to `httpx`.
- `tests/` uses deterministic in-memory transports. Tests must not require DNS, external HTTP, cloud services, or credentials.

## What is mocked

Candidate-visible tests replace the outbound transport with a scripted in-memory implementation. Status codes, headers, bodies, and redirect responses are fixed test data.

## Limits of local validation

Passing local tests proves behavior only for the modeled inputs and mocked responses. It does not prove production network policy, DNS behavior, proxy behavior, cloud configuration, certificate handling, remote server behavior, or complete security of the deployed system. Document any assumptions and production controls you would verify separately.
