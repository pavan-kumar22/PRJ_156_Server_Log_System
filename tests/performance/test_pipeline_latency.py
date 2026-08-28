from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

import requests


ACTION_API_URL = "http://localhost:8002/api/action"
OPENSEARCH_URL = "http://localhost:9200"

TOTAL_TESTS = 30
POLL_INTERVAL_SECONDS = 0.05
TIMEOUT_SECONDS = 15

ACCEPTANCE_BASELINE_MS = 500.0
OPTIMIZATION_TARGET_MS = 150.0

RESULTS_DIR = Path("performance_results")
RESULTS_FILE = RESULTS_DIR / "pipeline_latency.json"


def wait_for_opensearch(event_uuid: str) -> tuple[dict | None, float]:
    """
    Wait until the event UUID appears in OpenSearch.

    Returns:
        (indexed_event, elapsed_seconds)
    """

    search_url = (
        f"{OPENSEARCH_URL}/aicte-classified-*/_search"
    )

    params = {
        "q": f"uuid:{event_uuid}",
        "size": 1,
    }

    start = time.perf_counter()

    deadline = start + TIMEOUT_SECONDS

    while time.perf_counter() < deadline:

        try:
            response = requests.get(
                search_url,
                params=params,
                timeout=3,
            )

            response.raise_for_status()

            data = response.json()

            hits = data.get("hits", {}).get("hits", [])

            if hits:
                elapsed = time.perf_counter() - start
                return hits[0].get("_source"), elapsed

        except requests.RequestException:
            pass

        time.sleep(POLL_INTERVAL_SECONDS)

    elapsed = time.perf_counter() - start

    return None, elapsed


def generate_event(index: int) -> tuple[dict, float]:
    """
    Send one event through Action API.

    Returns:
        (API response JSON, elapsed request time)
    """

    payload = {
        "action": "payment_timeout",
        "data": {
            "source": f"pipeline-latency-test-{index}",
            "student_id": f"LAT-{index:04d}",
        },
    }

    start = time.perf_counter()

    response = requests.post(
        ACTION_API_URL,
        json=payload,
        timeout=10,
    )

    elapsed = time.perf_counter() - start

    response.raise_for_status()

    return response.json(), elapsed


def main() -> None:

    print()
    print("=" * 75)
    print("AICTE SERVER LOG MONITORING SYSTEM")
    print("FORMAL END-TO-END PIPELINE LATENCY EVALUATION")
    print("=" * 75)
    print()

    print(f"Total latency tests : {TOTAL_TESTS}")
    print(f"Acceptance baseline : {ACCEPTANCE_BASELINE_MS:.0f} ms")
    print(f"Optimization target : {OPTIMIZATION_TARGET_MS:.0f} ms")
    print()

    print(
        "Measurement method  : "
        "Action API request start -> OpenSearch persistence"
    )
    print()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    latency_results = []
    failed_tests = []

    print("Starting latency measurements...")
    print()

    for index in range(1, TOTAL_TESTS + 1):

        try:

            # --------------------------------------------------
            # 1. Send event through Action API
            # --------------------------------------------------

            action_start = time.perf_counter()

            action_response, action_request_seconds = generate_event(index)

            event = action_response.get("event", {})

            event_uuid = event.get("uuid")

            if not event_uuid:
                raise RuntimeError(
                    "Action API response did not contain event UUID."
                )

            # --------------------------------------------------
            # 2. Wait for OpenSearch persistence
            # --------------------------------------------------

            indexed_event, search_seconds = wait_for_opensearch(
                event_uuid
            )

            if indexed_event is None:

                failed_tests.append(
                    {
                        "test": index,
                        "uuid": event_uuid,
                        "reason": "OpenSearch timeout",
                    }
                )

                print(
                    f"[FAIL] Test {index:02d} - "
                    "OpenSearch timeout"
                )

                continue

            # --------------------------------------------------
            # 3. Measure REAL wall-clock pipeline latency
            # --------------------------------------------------

            total_elapsed_seconds = (
                time.perf_counter() - action_start
            )

            latency_ms = total_elapsed_seconds * 1000.0

            indexed_timestamp = indexed_event.get("timestamp")

            category = indexed_event.get("category")

            confidence = indexed_event.get("confidence")

            # --------------------------------------------------
            # 4. Store measurement
            # --------------------------------------------------

            latency_results.append(
                {
                    "test": index,
                    "uuid": event_uuid,
                    "application_timestamp": event.get(
                        "timestamp"
                    ),
                    "indexed_event_timestamp": indexed_timestamp,
                    "action_api_request_ms": round(
                        action_request_seconds * 1000,
                        3,
                    ),
                    "opensearch_wait_ms": round(
                        search_seconds * 1000,
                        3,
                    ),
                    "end_to_end_latency_ms": round(
                        latency_ms,
                        3,
                    ),
                    "category": category,
                    "confidence": confidence,
                    "within_acceptance": (
                        latency_ms <= ACCEPTANCE_BASELINE_MS
                    ),
                    "within_optimization": (
                        latency_ms <= OPTIMIZATION_TARGET_MS
                    ),
                }
            )

            status = (
                "PASS"
                if latency_ms <= ACCEPTANCE_BASELINE_MS
                else "FAIL"
            )

            print(
                f"[{status}] Test {index:02d} | "
                f"Latency: {latency_ms:.3f} ms | "
                f"Action API: "
                f"{action_request_seconds * 1000:.3f} ms | "
                f"OpenSearch wait: "
                f"{search_seconds * 1000:.3f} ms"
            )

        except Exception as exc:

            failed_tests.append(
                {
                    "test": index,
                    "reason": str(exc),
                }
            )

            print(
                f"[FAIL] Test {index:02d} | {exc}"
            )

    # ----------------------------------------------------------
    # FINAL STATISTICS
    # ----------------------------------------------------------

    latencies = [
        result["end_to_end_latency_ms"]
        for result in latency_results
    ]

    if not latencies:

        raise RuntimeError(
            "No successful latency measurements were obtained."
        )

    latencies_sorted = sorted(latencies)

    average_latency = statistics.mean(latencies)

    median_latency = statistics.median(latencies)

    minimum_latency = min(latencies)

    maximum_latency = max(latencies)

    p95_index = max(
        0,
        int(len(latencies_sorted) * 0.95) - 1,
    )

    p95_latency = latencies_sorted[p95_index]

    acceptance_pass_count = sum(
        latency <= ACCEPTANCE_BASELINE_MS
        for latency in latencies
    )

    optimization_pass_count = sum(
        latency <= OPTIMIZATION_TARGET_MS
        for latency in latencies
    )

    acceptance_rate = (
        acceptance_pass_count / len(latencies)
    ) * 100

    optimization_rate = (
        optimization_pass_count / len(latencies)
    ) * 100

    # Formal acceptance decision:
    # BOTH average and P95 must remain within baseline.

    acceptance_status = (
        "PASS"
        if (
            average_latency <= ACCEPTANCE_BASELINE_MS
            and p95_latency <= ACCEPTANCE_BASELINE_MS
        )
        else "FAIL"
    )

    optimization_status = (
        "TARGET ACHIEVED"
        if (
            average_latency <= OPTIMIZATION_TARGET_MS
            and p95_latency <= OPTIMIZATION_TARGET_MS
        )
        else "NOT ACHIEVED"
    )

    results = {
        "test": "End-to-End Pipeline Latency",

        "measurement_method": (
            "Wall-clock elapsed time from Action API request "
            "start until event persistence is confirmed in OpenSearch"
        ),

        "pipeline": [
            "action-api",
            "application.log",
            "Vector",
            "classifier",
            "OpenSearch",
        ],

        "total_tests": TOTAL_TESTS,

        "successful_tests": len(latencies),

        "failed_tests": len(failed_tests),

        "acceptance_baseline_ms": ACCEPTANCE_BASELINE_MS,

        "optimization_target_ms": OPTIMIZATION_TARGET_MS,

        "minimum_latency_ms": round(
            minimum_latency,
            3,
        ),

        "maximum_latency_ms": round(
            maximum_latency,
            3,
        ),

        "average_latency_ms": round(
            average_latency,
            3,
        ),

        "median_latency_ms": round(
            median_latency,
            3,
        ),

        "p95_latency_ms": round(
            p95_latency,
            3,
        ),

        "acceptance_pass_count": acceptance_pass_count,

        "acceptance_pass_rate_percent": round(
            acceptance_rate,
            2,
        ),

        "optimization_pass_count": optimization_pass_count,

        "optimization_pass_rate_percent": round(
            optimization_rate,
            2,
        ),

        "acceptance_status": acceptance_status,

        "optimization_status": optimization_status,

        "measurements": latency_results,

        "failures": failed_tests,
    }

    RESULTS_FILE.write_text(
        json.dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )

    # ----------------------------------------------------------
    # DISPLAY RESULTS
    # ----------------------------------------------------------

    print()
    print("=" * 75)
    print("FORMAL PIPELINE LATENCY RESULTS")
    print("=" * 75)

    print(
        f"Successful tests       : {len(latencies)}"
    )

    print(
        f"Failed tests           : {len(failed_tests)}"
    )

    print(
        f"Minimum latency        : "
        f"{minimum_latency:.3f} ms"
    )

    print(
        f"Maximum latency        : "
        f"{maximum_latency:.3f} ms"
    )

    print(
        f"Average latency        : "
        f"{average_latency:.3f} ms"
    )

    print(
        f"Median latency         : "
        f"{median_latency:.3f} ms"
    )

    print(
        f"P95 latency            : "
        f"{p95_latency:.3f} ms"
    )

    print(
        f"Within 500 ms          : "
        f"{acceptance_pass_count}/{len(latencies)} "
        f"({acceptance_rate:.2f}%)"
    )

    print(
        f"Within 150 ms          : "
        f"{optimization_pass_count}/{len(latencies)} "
        f"({optimization_rate:.2f}%)"
    )

    print()

    print(
        f"Acceptance baseline    : "
        f"{ACCEPTANCE_BASELINE_MS:.0f} ms"
    )

    print(
        f"Acceptance status      : "
        f"{acceptance_status}"
    )

    print()

    print(
        f"Optimization target    : "
        f"{OPTIMIZATION_TARGET_MS:.0f} ms"
    )

    print(
        f"Optimization status    : "
        f"{optimization_status}"
    )

    print()

    print(
        f"Results saved to       : "
        f"{RESULTS_FILE}"
    )

    print("=" * 75)


if __name__ == "__main__":
    main()