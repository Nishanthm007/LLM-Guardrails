from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.guardrails import GuardrailEngine, SAFE_FALLBACK_MESSAGE
from app.simulator import DeterministicMockLLM

CASES_PATH = ROOT / "evaluation" / "test_cases.json"
REPORT_DIR = ROOT / "reports"


def evaluate_case(case: dict[str, Any], engine: GuardrailEngine) -> dict[str, Any]:
    prompt = case["prompt"]

    baseline_start = perf_counter()
    baseline_output = DeterministicMockLLM.generate(prompt)
    baseline_latency_ms = (perf_counter() - baseline_start) * 1000

    guarded_start = perf_counter()
    input_result = engine.process_input(prompt)

    if input_result.decision == "block":
        model_output = SAFE_FALLBACK_MESSAGE
    else:
        model_output = DeterministicMockLLM.generate(input_result.safe_prompt)

    validated_output, output_events = engine.validate_output(model_output)
    all_events = [*input_result.events, *output_events]

    final_decision = input_result.decision
    if output_events and any(event.severity == "critical" for event in output_events):
        final_decision = "block"

    guarded_latency_ms = (perf_counter() - guarded_start) * 1000
    latency_overhead_ms = guarded_latency_ms - baseline_latency_ms

    if case["label"] == "safe":
        safe_pass_through = final_decision == "allow"
        safe_quality_preserved = validated_output == baseline_output
    else:
        safe_pass_through = False
        safe_quality_preserved = False

    result = {
        "id": case["id"],
        "category": case["category"],
        "label": case["label"],
        "expected_decision": case["expected_decision"],
        "actual_decision": final_decision,
        "decision_match": final_decision == case["expected_decision"],
        "event_count": len(all_events),
        "triggered_rules": ";".join(event.rule_id for event in all_events),
        "baseline_latency_ms": round(baseline_latency_ms, 4),
        "guarded_latency_ms": round(guarded_latency_ms, 4),
        "latency_overhead_ms": round(latency_overhead_ms, 4),
        "safe_pass_through": safe_pass_through,
        "safe_quality_preserved": safe_quality_preserved,
    }

    return result


def compute_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    attacks = [row for row in results if row["label"] == "attack"]
    safe = [row for row in results if row["label"] == "safe"]

    attack_blocks = sum(1 for row in attacks if row["actual_decision"] == "block")
    attack_mitigated = sum(1 for row in attacks if row["actual_decision"] in {"block", "rewrite"})

    safe_false_positive = sum(1 for row in safe if row["actual_decision"] != "allow")
    safe_allow = sum(1 for row in safe if row["actual_decision"] == "allow")
    safe_quality_ok = sum(1 for row in safe if row["safe_quality_preserved"])

    coverage: dict[str, dict[str, Any]] = {}
    for row in attacks:
        category = row["category"]
        if category not in coverage:
            coverage[category] = {
                "count": 0,
                "blocked": 0,
                "mitigated": 0,
            }
        coverage[category]["count"] += 1
        if row["actual_decision"] == "block":
            coverage[category]["blocked"] += 1
        if row["actual_decision"] in {"block", "rewrite"}:
            coverage[category]["mitigated"] += 1

    for category, values in coverage.items():
        count = values["count"]
        values["block_rate"] = round(values["blocked"] / count, 4) if count else 0.0
        values["mitigation_rate"] = round(values["mitigated"] / count, 4) if count else 0.0

    summary = {
        "total_cases": len(results),
        "attack_cases": len(attacks),
        "safe_cases": len(safe),
        "decision_accuracy": round(sum(1 for row in results if row["decision_match"]) / len(results), 4),
        "attack_block_rate": round(attack_blocks / len(attacks), 4) if attacks else 0.0,
        "attack_mitigation_rate": round(attack_mitigated / len(attacks), 4) if attacks else 0.0,
        "false_positive_rate": round(safe_false_positive / len(safe), 4) if safe else 0.0,
        "safe_pass_through_rate": round(safe_allow / len(safe), 4) if safe else 0.0,
        "safe_pass_through_quality": round(safe_quality_ok / len(safe), 4) if safe else 0.0,
        "avg_baseline_latency_ms": round(mean(row["baseline_latency_ms"] for row in results), 4),
        "avg_guarded_latency_ms": round(mean(row["guarded_latency_ms"] for row in results), 4),
        "avg_latency_overhead_ms": round(mean(row["latency_overhead_ms"] for row in results), 4),
        "coverage_by_attack_category": coverage,
    }

    return summary


def write_reports(results: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "metrics_summary.json"
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    csv_path = REPORT_DIR / "evaluation_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    results_json_path = REPORT_DIR / "evaluation_results.json"
    with results_json_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    md_path = REPORT_DIR / "metrics_summary.md"
    lines: list[str] = []
    lines.append("# Phase 3 Evaluation Summary")
    lines.append("")
    lines.append("## Core Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Total cases | {summary['total_cases']} |")
    lines.append(f"| Attack cases | {summary['attack_cases']} |")
    lines.append(f"| Safe cases | {summary['safe_cases']} |")
    lines.append(f"| Decision accuracy | {summary['decision_accuracy']:.2%} |")
    lines.append(f"| Attack block rate | {summary['attack_block_rate']:.2%} |")
    lines.append(f"| Attack mitigation rate | {summary['attack_mitigation_rate']:.2%} |")
    lines.append(f"| False positive rate | {summary['false_positive_rate']:.2%} |")
    lines.append(f"| Safe pass-through rate | {summary['safe_pass_through_rate']:.2%} |")
    lines.append(f"| Safe pass-through quality | {summary['safe_pass_through_quality']:.2%} |")
    lines.append(f"| Avg baseline latency (ms) | {summary['avg_baseline_latency_ms']:.4f} |")
    lines.append(f"| Avg guarded latency (ms) | {summary['avg_guarded_latency_ms']:.4f} |")
    lines.append(f"| Avg latency overhead (ms) | {summary['avg_latency_overhead_ms']:.4f} |")
    lines.append("")
    lines.append("## Coverage by Attack Category")
    lines.append("")
    lines.append("| Category | Count | Blocked | Mitigated | Block Rate | Mitigation Rate |")
    lines.append("|---|---:|---:|---:|---:|---:|")

    for category, values in summary["coverage_by_attack_category"].items():
        lines.append(
            "| {category} | {count} | {blocked} | {mitigated} | {block_rate:.2%} | {mitigation_rate:.2%} |".format(
                category=category,
                count=values["count"],
                blocked=values["blocked"],
                mitigated=values["mitigated"],
                block_rate=values["block_rate"],
                mitigation_rate=values["mitigation_rate"],
            )
        )

    with md_path.open("w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")


def main() -> None:
    with CASES_PATH.open("r", encoding="utf-8") as file:
        test_cases = json.load(file)

    engine = GuardrailEngine()
    results = [evaluate_case(case, engine) for case in test_cases]
    summary = compute_summary(results)
    write_reports(results, summary)

    print("Evaluation complete.")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Attack block rate: {summary['attack_block_rate']:.2%}")
    print(f"False positive rate: {summary['false_positive_rate']:.2%}")
    print(f"Avg latency overhead (ms): {summary['avg_latency_overhead_ms']:.4f}")


if __name__ == "__main__":
    main()
