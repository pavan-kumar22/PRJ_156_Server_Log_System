import concurrent.futures
import json
import os
import time
import uuid
import urllib.request
import urllib.parse
from datetime import datetime, timezone


ACTION_URL = "http://localhost:8002/api/action"
OPENSEARCH_URL = "http://localhost:9200"

TOTAL_EVENTS = 1000
CONCURRENT_WORKERS = 50

SOURCE = "throughput-concurrent-test"


def send_event(index):
    test_id = f"C-CONCURRENT-{uuid.uuid4().hex[:12]}"

    payload = {
        "action": "payment_timeout",
        "data": {
            "source": SOURCE,
            "test_id": test_id,
            "student_id": f"THROUGHPUT-{index:04d}"
        }
    }

    body = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        ACTION_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    start = time.perf_counter()

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            response_body = json.loads(response.read().decode("utf-8"))

        elapsed = time.perf_counter() - start

        event = response_body.get("event", {})

        return {
            "success": response.status == 200,
            "test_id": test_id,
            "uuid": event.get("uuid"),
            "latency_ms": elapsed * 1000,
            "error": None
        }

    except Exception as exc:
        return {
            "success": False,
            "test_id": test_id,
            "uuid": None,
            "latency_ms": None,
            "error": str(exc)
        }


def query_opensearch(test_ids):
    """
    Query OpenSearch for the generated test events.

    We use a terms query against payload.test_id.
    """
    query = {
        "size": 0,
        "query": {
            "terms": {
                "payload.test_id.keyword": test_ids
            }
        }
    }

    url = (
        f"{OPENSEARCH_URL}/aicte-classified-*/_search"
    )

    body = json.dumps(query).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["hits"]["total"]["value"]


def main():

    print("=" * 75)
    print("AICTE SERVER LOG MONITORING SYSTEM")
    print("FORMAL CONCURRENT + PERSISTENCE-VALIDATED")
    print("INGESTION THROUGHPUT EVALUATION")
    print("=" * 75)

    print(f"Total events         : {TOTAL_EVENTS}")
    print(f"Concurrent workers   : {CONCURRENT_WORKERS}")
    print("Acceptance target    : >= 1000 events/sec")
    print()

    print("Phase 1: Sending concurrent events to Action API...")
    print()

    start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=CONCURRENT_WORKERS
    ) as executor:

        futures = [
            executor.submit(send_event, i)
            for i in range(TOTAL_EVENTS)
        ]

        results = [
            future.result()
            for future in concurrent.futures.as_completed(futures)
        ]

    end = time.perf_counter()

    duration = end - start

    successful = [
        result for result in results
        if result["success"]
    ]

    failed = [
        result for result in results
        if not result["success"]
    ]

    api_throughput = (
        len(successful) / duration
        if duration > 0
        else 0
    )

    success_rate = (
        len(successful) / TOTAL_EVENTS * 100
        if TOTAL_EVENTS > 0
        else 0
    )

    print("=" * 75)
    print("ACTION API INGESTION RESULTS")
    print("=" * 75)

    print(f"Events submitted       : {TOTAL_EVENTS}")
    print(f"Successful requests    : {len(successful)}")
    print(f"Failed requests        : {len(failed)}")
    print(f"Concurrent duration    : {duration:.3f} seconds")
    print(f"API throughput         : {api_throughput:.2f} events/sec")
    print(f"API success rate       : {success_rate:.2f}%")
    print()

    if failed:
        print("Sample failures:")
        for item in failed[:10]:
            print(f"  {item['error']}")

    # ---------------------------------------------------------
    # Wait for Vector → Classifier → OpenSearch
    # ---------------------------------------------------------

    print()
    print("Phase 2: Waiting for downstream pipeline persistence...")

    persistence_start = time.perf_counter()

    persisted = 0

    successful_test_ids = [
        result["test_id"]
        for result in successful
    ]

    # Poll OpenSearch instead of assuming a fixed delay.
    max_wait_seconds = 60
    poll_interval = 2

    while (
        time.perf_counter() - persistence_start
        < max_wait_seconds
    ):

        try:
            persisted = query_opensearch(
                successful_test_ids
            )
        except Exception:
            persisted = 0

        if persisted >= len(successful):
            break

        print(
            f"  OpenSearch persisted "
            f"{persisted}/{len(successful)} events..."
        )

        time.sleep(poll_interval)

    persistence_duration = (
        time.perf_counter() - persistence_start
    )

    persistence_rate = (
        persisted / len(successful) * 100
        if successful
        else 0
    )

    # ---------------------------------------------------------
    # Final results
    # ---------------------------------------------------------

    print()
    print("=" * 75)
    print("PERSISTENCE VALIDATION")
    print("=" * 75)

    print(f"Successful API events   : {len(successful)}")
    print(f"Persisted in OpenSearch : {persisted}")
    print(f"Missing events          : {len(successful) - persisted}")
    print(f"Persistence rate        : {persistence_rate:.2f}%")
    print(f"Persistence wait        : {persistence_duration:.3f} seconds")
    print()

    acceptance_target = 1000

    throughput_pass = api_throughput >= acceptance_target
    persistence_pass = (
        persisted == len(successful)
        and len(successful) > 0
    )

    overall_pass = (
        throughput_pass
        and persistence_pass
    )

    print("=" * 75)
    print("FORMAL TEST C RESULT")
    print("=" * 75)

    print(
        f"Concurrent API throughput : "
        f"{api_throughput:.2f} events/sec"
    )

    print(
        f"Throughput target         : "
        f">= {acceptance_target} events/sec"
    )

    print(
        f"Persistence validation    : "
        f"{'PASS' if persistence_pass else 'FAIL'}"
    )

    print(
        f"Throughput acceptance     : "
        f"{'PASS' if throughput_pass else 'FAIL'}"
    )

    print(
        f"Overall Test C status     : "
        f"{'PASS' if overall_pass else 'FAIL'}"
    )

    # ---------------------------------------------------------
    # Save results
    # ---------------------------------------------------------

    results_file = {
        "test": "Ingestion Throughput - Concurrent + Persistence Validated",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_events": TOTAL_EVENTS,
        "concurrent_workers": CONCURRENT_WORKERS,
        "successful_api_requests": len(successful),
        "failed_api_requests": len(failed),
        "api_duration_seconds": round(duration, 6),
        "api_throughput_events_per_second": round(
            api_throughput, 3
        ),
        "api_success_rate_percent": round(
            success_rate, 3
        ),
        "opensearch_persisted_events": persisted,
        "missing_events": len(successful) - persisted,
        "persistence_rate_percent": round(
            persistence_rate, 3
        ),
        "persistence_wait_seconds": round(
            persistence_duration, 6
        ),
        "minimum_acceptable_throughput": acceptance_target,
        "throughput_acceptance_status": (
            "PASS" if throughput_pass else "FAIL"
        ),
        "persistence_acceptance_status": (
            "PASS" if persistence_pass else "FAIL"
        ),
        "overall_acceptance_status": (
            "PASS" if overall_pass else "FAIL"
        )
    }

    os.makedirs("performance_results", exist_ok=True)

    output_file = (
        "performance_results/"
        "ingestion_throughput_concurrent.json"
    )

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(results_file, file, indent=2)

    print()
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()