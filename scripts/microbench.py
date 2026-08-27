#!/usr/bin/env python3
"""Validate and score the staged low-credit Codex AIR coding microbenchmark.

This tool never launches a model. It freezes task provenance, enforces the
credit guard, compares measured AIR candidate cells with historical Direct
cells, and stops before the expensive confirmation stage when screening fails.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any


HASH64 = 64
HASH40 = 40


class ContractError(ValueError):
    """Raised when benchmark inputs are incomplete or incomparable."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def is_hex(value: Any, length: int) -> bool:
    return isinstance(value, str) and len(value) == length and all(character in "0123456789abcdef" for character in value)


def is_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def validate_measurement(value: Any, label: str, *, historical_air: bool) -> None:
    require(isinstance(value, dict), f"{label} must be an object")
    require(value.get("resolved") in (0, 1), f"{label}.resolved must be 0 or 1")
    require(is_number(value.get("partial")) and 0 <= value["partial"] <= 1, f"{label}.partial must be in [0, 1]")
    require(is_number(value.get("elapsed_seconds")) and value["elapsed_seconds"] > 0, f"{label}.elapsed_seconds must be positive")
    require(is_number(value.get("pro_credits")) and value["pro_credits"] >= 0, f"{label}.pro_credits must be non-negative")
    if historical_air:
        for metric in ("tool_calls", "short_polls"):
            require(isinstance(value.get(metric), int) and value[metric] >= 0, f"{label}.{metric} must be a non-negative integer")


def validate_manifest(data: Any) -> dict[str, Any]:
    require(isinstance(data, dict), "manifest must be an object")
    require(data.get("schema_version") == 1, "unsupported manifest schema")
    require(data.get("evidence_class") == "historical_direct_replay_development_gate", "invalid evidence_class")

    source = data.get("source")
    require(isinstance(source, dict), "source must be an object")
    require(is_hex(source.get("git_sha"), HASH40), "source.git_sha must be a lowercase SHA-1")
    require(isinstance(source.get("codex_cli"), str) and source["codex_cli"], "source.codex_cli is required")
    require(source.get("tests_tree_hash_algorithm") == "sha256(relative_path_utf8 NUL file_sha256_hex LF for sorted regular files)", "tests-tree hash algorithm is invalid")

    pricing = data.get("pricing")
    require(isinstance(pricing, dict), "pricing must be an object")
    require(pricing.get("unit") == "Pro credits per 1M tokens", "pricing unit is invalid")
    require(isinstance(pricing.get("source"), str) and pricing["source"].startswith("https://"), "pricing source is required")
    require(isinstance(pricing.get("speed_source"), str) and pricing["speed_source"].startswith("https://"), "speed pricing source is required")
    models = pricing.get("models")
    require(isinstance(models, dict) and set(models) == {"gpt-5.6-sol", "gpt-5.6-luna"}, "pricing must contain exactly Sol and Luna")
    for model, rates in models.items():
        require(isinstance(rates, dict), f"pricing.{model} must be an object")
        for key in ("input", "cached_input", "output", "requested_tier_multiplier"):
            require(is_number(rates.get(key)) and rates[key] > 0, f"pricing.{model}.{key} must be positive")

    budget = data.get("budget")
    require(isinstance(budget, dict), "budget must be an object")
    for key in ("screen_credit_cap", "cumulative_credit_hard_cap", "full_historical_ab_credits"):
        require(is_number(budget.get(key)) and budget[key] > 0, f"budget.{key} must be positive")
    require(budget["screen_credit_cap"] < budget["cumulative_credit_hard_cap"], "screen cap must be below cumulative cap")
    require(budget["cumulative_credit_hard_cap"] < budget["full_historical_ab_credits"], "microbench cap must be below the full A/B cost")

    stages = data.get("stages")
    require(isinstance(stages, list) and [stage.get("id") for stage in stages if isinstance(stage, dict)] == ["screen", "confirm"], "stages must be screen then confirm")
    stage_task_ids: list[str] = []
    required_gates = {
        "min_resolved_delta",
        "min_mean_partial_delta",
        "min_task_partial_delta",
        "max_median_time_ratio",
        "max_cost_ratio",
        "min_luna_token_share",
        "max_tool_calls",
        "max_short_polls",
        "max_credits",
    }
    for stage in stages:
        require(stage.get("scope") in {"stage", "cumulative"}, f"invalid scope for {stage.get('id')}")
        task_ids = stage.get("task_ids")
        require(isinstance(task_ids, list) and len(task_ids) == 2, f"{stage.get('id')} must contain exactly two tasks")
        require(all(isinstance(task_id, str) and task_id for task_id in task_ids), f"invalid task id in {stage.get('id')}")
        stage_task_ids.extend(task_ids)
        gates = stage.get("gates")
        require(isinstance(gates, dict) and set(gates) == required_gates, f"gate set is invalid for {stage.get('id')}")
        for key in ("max_tool_calls", "max_short_polls"):
            require(isinstance(gates[key], int) and gates[key] >= 0, f"{key} must be non-negative")
        for key in required_gates - {"max_tool_calls", "max_short_polls", "min_resolved_delta"}:
            require(is_number(gates[key]), f"{stage.get('id')}.{key} must be numeric")
        require(isinstance(gates["min_resolved_delta"], int), "min_resolved_delta must be an integer")
        require(0 <= gates["min_luna_token_share"] <= 1, "min_luna_token_share must be in [0, 1]")

    tasks = data.get("tasks")
    require(isinstance(tasks, list) and len(tasks) == 4, "exactly four tasks are required")
    task_ids = [task.get("id") for task in tasks if isinstance(task, dict)]
    require(task_ids == stage_task_ids, "task order must match the staged order")
    require(len(set(task_ids)) == len(task_ids), "task ids must be unique")
    for task in tasks:
        label = task["id"]
        require(task.get("stage") in {"screen", "confirm"}, f"{label}.stage is invalid")
        require(task.get("language") in {"python", "go", "typescript"}, f"{label}.language is invalid")
        require(task.get("expected_worker_profile") in {"air-efficient-worker", "air-complex-worker"}, f"{label}.expected_worker_profile is invalid")
        require(task.get("verifier_home") in {"/root", "/tmp/home"}, f"{label}.verifier_home is invalid")
        require(isinstance(task.get("signal"), str) and task["signal"], f"{label}.signal is required")
        require(isinstance(task.get("image_digest"), str) and task["image_digest"].startswith("sha256:") and is_hex(task["image_digest"][7:], HASH64), f"{label}.image_digest is invalid")
        require(is_hex(task.get("base_commit"), HASH40), f"{label}.base_commit is invalid")
        for key in ("instruction_sha256", "tests_tree_sha256"):
            require(is_hex(task.get(key), HASH64), f"{label}.{key} is invalid")
        validate_measurement(task.get("historical_direct"), f"{label}.historical_direct", historical_air=False)
        validate_measurement(task.get("historical_air"), f"{label}.historical_air", historical_air=True)
    return data


def validate_usage_bucket(value: Any, label: str) -> None:
    require(isinstance(value, dict), f"{label} must be an object")
    require(isinstance(value.get("sessions"), int) and value["sessions"] > 0, f"{label}.sessions must be positive")
    for key in ("input_tokens", "cached_input_tokens", "output_tokens"):
        require(isinstance(value.get(key), int) and value[key] >= 0, f"{label}.{key} must be a non-negative integer")
    require(value["cached_input_tokens"] <= value["input_tokens"], f"{label}.cached_input_tokens exceeds input_tokens")
    require(is_number(value.get("pro_credits")) and value["pro_credits"] >= 0, f"{label}.pro_credits must be non-negative")


def priced_credits(manifest: dict[str, Any], model: str, usage: dict[str, Any]) -> float:
    rates = manifest["pricing"]["models"][model]
    uncached = usage["input_tokens"] - usage["cached_input_tokens"]
    base = (
        uncached * rates["input"]
        + usage["cached_input_tokens"] * rates["cached_input"]
        + usage["output_tokens"] * rates["output"]
    ) / 1_000_000
    return base * rates["requested_tier_multiplier"]


def validate_results(manifest: dict[str, Any], data: Any) -> dict[str, dict[str, Any]]:
    require(isinstance(data, dict), "results must be an object")
    require(data.get("schema_version") == 1, "unsupported results schema")
    require(data.get("evidence_class") == "measured_candidate_cells", "results evidence_class is invalid")
    require(data.get("manifest_sha256") == sha256(manifest), "results use a different manifest")
    candidate = data.get("candidate")
    require(isinstance(candidate, dict), "candidate identity is required")
    require(is_hex(candidate.get("repo_commit"), HASH40), "candidate.repo_commit is invalid")
    for key in ("skill_sha256", "agent_bundle_sha256"):
        require(is_hex(candidate.get(key), HASH64), f"candidate.{key} is invalid")
    require(candidate.get("codex_cli") == manifest["source"]["codex_cli"], "candidate Codex CLI differs from the historical baseline")
    runtime_contract = candidate.get("runtime_contract")
    require(isinstance(runtime_contract, dict), "candidate.runtime_contract is required")
    expected_contract = {
        "controller_model": "gpt-5.6-sol",
        "controller_effort": "xhigh",
        "controller_requested_tier": "default",
        "worker_model": "gpt-5.6-luna",
        "worker_effort": "max",
        "worker_requested_tier": "fast",
        "fast_mode": True,
        "terra_allowed": False,
    }
    for key, value in expected_contract.items():
        require(runtime_contract.get(key) == value, f"candidate.runtime_contract.{key} must be {value!r}")

    tasks = {task["id"]: task for task in manifest["tasks"]}
    rows = data.get("cells")
    require(isinstance(rows, list), "cells must be a list")
    observed: dict[str, dict[str, Any]] = {}
    for row in rows:
        require(isinstance(row, dict), "every cell must be an object")
        task_id = row.get("task_id")
        require(task_id in tasks, f"unexpected task_id: {task_id}")
        require(task_id not in observed, f"duplicate cell: {task_id}")
        require(row.get("valid") is True, f"invalid cell must not be scored: {task_id}")
        task = tasks[task_id]
        for key in ("base_commit", "image_digest", "instruction_sha256", "tests_tree_sha256"):
            require(row.get(key) == task[key], f"{task_id}.{key} does not match the frozen task")
        require(row.get("resolved") in (0, 1), f"{task_id}.resolved must be 0 or 1")
        require(is_number(row.get("partial")) and 0 <= row["partial"] <= 1, f"{task_id}.partial must be in [0, 1]")
        for key in ("elapsed_seconds", "pro_credits"):
            require(is_number(row.get(key)) and row[key] >= 0, f"{task_id}.{key} must be non-negative")
        for key in ("input_tokens", "cached_input_tokens", "output_tokens", "tool_calls", "short_polls", "correction_count"):
            require(isinstance(row.get(key), int) and row[key] >= 0, f"{task_id}.{key} must be a non-negative integer")
        require(row["cached_input_tokens"] <= row["input_tokens"], f"{task_id}.cached_input_tokens exceeds input_tokens")

        runtime = row.get("runtime")
        require(isinstance(runtime, dict), f"{task_id}.runtime is required")
        require(runtime.get("worker_profile") == task["expected_worker_profile"], f"{task_id}.worker_profile does not match the frozen route")
        require(runtime.get("controller_sessions") == 1, f"{task_id}.controller_sessions must be 1")
        require(runtime.get("worker_sessions") == 1, f"{task_id}.worker_sessions must be 1")
        require(runtime.get("challenger_sessions") == 0, f"{task_id}.challenger_sessions must be 0")
        require(runtime.get("worker_actual_tier") in {"priority", "unobserved"}, f"{task_id}.worker_actual_tier is incompatible with Fast")
        require(runtime.get("terra_calls") == 0 and runtime.get("terra_tokens") == 0, f"{task_id}: Terra calls and tokens must remain zero")

        usage = row.get("usage_by_model")
        require(isinstance(usage, dict) and set(usage) == {"gpt-5.6-sol", "gpt-5.6-luna"}, f"{task_id}.usage_by_model must contain exactly Sol and Luna")
        for model, bucket in usage.items():
            validate_usage_bucket(bucket, f"{task_id}.usage_by_model.{model}")
            require(math.isclose(bucket["pro_credits"], priced_credits(manifest, model, bucket), rel_tol=1e-9, abs_tol=1e-6), f"{task_id}.{model}.pro_credits does not match frozen pricing")
        require(usage["gpt-5.6-sol"]["sessions"] == runtime["controller_sessions"], f"{task_id}.Sol session count mismatch")
        require(usage["gpt-5.6-luna"]["sessions"] == runtime["worker_sessions"], f"{task_id}.Luna session count mismatch")
        for key in ("input_tokens", "cached_input_tokens", "output_tokens"):
            require(sum(bucket[key] for bucket in usage.values()) == row[key], f"{task_id}.{key} total does not match usage_by_model")
        require(math.isclose(sum(bucket["pro_credits"] for bucket in usage.values()), row["pro_credits"], rel_tol=1e-9, abs_tol=1e-6), f"{task_id}.pro_credits total does not match usage_by_model")
        observed[task_id] = row
    return observed


def score_stage(manifest: dict[str, Any], stage: dict[str, Any], rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    stage_index = [item["id"] for item in manifest["stages"]].index(stage["id"])
    if stage["scope"] == "cumulative":
        task_ids = [task_id for item in manifest["stages"][: stage_index + 1] for task_id in item["task_ids"]]
    else:
        task_ids = list(stage["task_ids"])
    tasks = {task["id"]: task for task in manifest["tasks"]}

    direct = [tasks[task_id]["historical_direct"] for task_id in task_ids]
    candidate = [rows[task_id] for task_id in task_ids]
    partial_deltas = [candidate_row["partial"] - direct_row["partial"] for candidate_row, direct_row in zip(candidate, direct)]
    time_ratios = [candidate_row["elapsed_seconds"] / direct_row["elapsed_seconds"] for candidate_row, direct_row in zip(candidate, direct)]
    direct_credits = sum(row["pro_credits"] for row in direct)
    candidate_credits = sum(row["pro_credits"] for row in candidate)
    model_usage = {
        model: {
            metric: sum(row["usage_by_model"][model][metric] for row in candidate)
            for metric in ("sessions", "input_tokens", "cached_input_tokens", "output_tokens", "pro_credits")
        }
        for model in ("gpt-5.6-sol", "gpt-5.6-luna")
    }
    total_model_tokens = sum(bucket["input_tokens"] + bucket["output_tokens"] for bucket in model_usage.values())
    luna_model_tokens = model_usage["gpt-5.6-luna"]["input_tokens"] + model_usage["gpt-5.6-luna"]["output_tokens"]
    metrics = {
        "task_ids": task_ids,
        "direct_resolved": sum(row["resolved"] for row in direct),
        "candidate_resolved": sum(row["resolved"] for row in candidate),
        "resolved_delta": sum(row["resolved"] for row in candidate) - sum(row["resolved"] for row in direct),
        "direct_mean_partial": statistics.fmean(row["partial"] for row in direct),
        "candidate_mean_partial": statistics.fmean(row["partial"] for row in candidate),
        "mean_partial_delta": statistics.fmean(partial_deltas),
        "min_task_partial_delta": min(partial_deltas),
        "median_time_ratio": statistics.median(time_ratios),
        "direct_credits": direct_credits,
        "candidate_credits": candidate_credits,
        "cost_ratio": candidate_credits / direct_credits,
        "luna_token_share": luna_model_tokens / total_model_tokens,
        "usage_by_model": model_usage,
        "unobserved_fast_tier_tasks": [row["task_id"] for row in candidate if row["runtime"]["worker_actual_tier"] == "unobserved"],
        "short_polls": sum(row["short_polls"] for row in candidate),
        "tool_calls": sum(row["tool_calls"] for row in candidate),
        "input_tokens": sum(row["input_tokens"] for row in candidate),
        "cached_input_tokens": sum(row["cached_input_tokens"] for row in candidate),
        "output_tokens": sum(row["output_tokens"] for row in candidate),
        "correction_count": sum(row["correction_count"] for row in candidate),
    }
    gates = stage["gates"]
    failed = []
    if metrics["resolved_delta"] < gates["min_resolved_delta"]:
        failed.append("resolved_delta")
    if metrics["mean_partial_delta"] < gates["min_mean_partial_delta"]:
        failed.append("mean_partial_delta")
    if metrics["min_task_partial_delta"] < gates["min_task_partial_delta"]:
        failed.append("min_task_partial_delta")
    if metrics["median_time_ratio"] > gates["max_median_time_ratio"]:
        failed.append("median_time_ratio")
    if metrics["cost_ratio"] > gates["max_cost_ratio"]:
        failed.append("cost_ratio")
    if metrics["luna_token_share"] < gates["min_luna_token_share"]:
        failed.append("luna_token_share")
    if metrics["tool_calls"] > gates["max_tool_calls"]:
        failed.append("tool_calls")
    if metrics["short_polls"] > gates["max_short_polls"]:
        failed.append("short_polls")
    if metrics["candidate_credits"] > gates["max_credits"]:
        failed.append("credits")
    return {"scope": stage["scope"], "metrics": metrics, "gates": gates, "failed_gates": failed, "pass": not failed}


def evaluate(manifest: dict[str, Any], data: Any) -> dict[str, Any]:
    rows = validate_results(manifest, data)
    warnings = []
    if any(row["runtime"]["worker_actual_tier"] == "unobserved" for row in rows.values()):
        warnings.append("unobserved_fast_tier")
    stage_results: dict[str, Any] = {}
    for index, stage in enumerate(manifest["stages"]):
        later_task_ids = {
            task_id
            for later_stage in manifest["stages"][index + 1 :]
            for task_id in later_stage["task_ids"]
        }
        missing = [task_id for task_id in stage["task_ids"] if task_id not in rows]
        if missing:
            require(
                not later_task_ids.intersection(rows),
                f"out-of-order results: {stage['id']} must complete before a later stage",
            )
            return {
                "schema_version": 1,
                "evidence_class": "microbench_decision",
                "manifest_sha256": sha256(manifest),
                "decision": "CONTINUE",
                "next_stage": stage["id"],
                "next_task_ids": missing,
                "stage_results": stage_results,
                "warnings": warnings,
                "claim_boundary": "Development regression evidence only; not a fresh matched A/B or general coding score.",
            }
        result = score_stage(manifest, stage, rows)
        stage_results[stage["id"]] = result
        if not result["pass"]:
            require(
                not later_task_ids.intersection(rows),
                f"out-of-order results: later-stage cells exist after {stage['id']} failed",
            )
            return {
                "schema_version": 1,
                "evidence_class": "microbench_decision",
                "manifest_sha256": sha256(manifest),
                "decision": "STOP",
                "next_stage": None,
                "next_task_ids": [],
                "stage_results": stage_results,
                "warnings": warnings,
                "claim_boundary": "Development regression evidence only; not a fresh matched A/B or general coding score.",
            }
    return {
        "schema_version": 1,
        "evidence_class": "microbench_decision",
        "manifest_sha256": sha256(manifest),
        "decision": "PASS",
        "next_stage": None,
        "next_task_ids": [],
        "stage_results": stage_results,
        "warnings": warnings,
        "claim_boundary": "Development regression evidence only; not a fresh matched A/B or general coding score.",
    }


def render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("manifest", type=Path)
    evaluate_parser = subparsers.add_parser("evaluate")
    evaluate_parser.add_argument("manifest", type=Path)
    evaluate_parser.add_argument("results", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = validate_manifest(load_json(args.manifest))
        if args.command == "validate":
            result = {
                "status": "PASS",
                "manifest_sha256": sha256(manifest),
                "tasks": len(manifest["tasks"]),
                "screen_credit_cap": manifest["budget"]["screen_credit_cap"],
                "cumulative_credit_hard_cap": manifest["budget"]["cumulative_credit_hard_cap"],
            }
        else:
            result = evaluate(manifest, load_json(args.results))
    except ContractError as exc:
        print(f"microbench.py: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
