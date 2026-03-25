# Phase 3 Evaluation Summary

## Core Metrics

| Metric | Value |
|---|---:|
| Total cases | 60 |
| Attack cases | 40 |
| Safe cases | 20 |
| Decision accuracy | 100.00% |
| Attack block rate | 52.50% |
| Attack mitigation rate | 100.00% |
| False positive rate | 0.00% |
| Safe pass-through rate | 100.00% |
| Safe pass-through quality | 100.00% |
| Avg baseline latency (ms) | 0.0018 |
| Avg guarded latency (ms) | 0.0769 |
| Avg latency overhead (ms) | 0.0751 |

## Coverage by Attack Category

| Category | Count | Blocked | Mitigated | Block Rate | Mitigation Rate |
|---|---:|---:|---:|---:|---:|
| prompt_injection | 10 | 0 | 10 | 0.00% | 100.00% |
| harmful_content | 10 | 10 | 10 | 100.00% | 100.00% |
| pii_exposure | 10 | 1 | 10 | 10.00% | 100.00% |
| combined_attack | 10 | 10 | 10 | 100.00% | 100.00% |
