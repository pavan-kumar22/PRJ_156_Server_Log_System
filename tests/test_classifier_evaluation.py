from classifier.model import LogClassifier


TEST_CASES = [
    # Routine Audit
    ("User login completed successfully", "Routine Audit"),
    ("Student profile updated successfully", "Routine Audit"),
    ("Application submitted successfully", "Routine Audit"),
    ("Document downloaded successfully", "Routine Audit"),
    ("User logout completed successfully", "Routine Audit"),
    ("Student registration completed", "Routine Audit"),
    ("Faculty profile updated successfully", "Routine Audit"),
    ("Payment receipt generated successfully", "Routine Audit"),

    # Performance Degradation
    ("Payment gateway request timed out", "Performance Degradation"),
    ("Database response latency is high", "Performance Degradation"),
    ("API response time is increasing", "Performance Degradation"),
    ("Server response is very slow", "Performance Degradation"),
    ("Database query took too long to complete", "Performance Degradation"),
    ("High latency detected in payment service", "Performance Degradation"),
    ("API request timeout detected", "Performance Degradation"),
    ("Service response time exceeded threshold", "Performance Degradation"),

    # Security Threat
    ("Unauthorized access attempt detected", "Security Threat"),
    ("Multiple failed login attempts detected", "Security Threat"),
    ("Suspicious authentication activity detected", "Security Threat"),
    ("Invalid authentication token detected", "Security Threat"),
    ("Repeated unauthorized login attempts detected", "Security Threat"),
    ("Suspicious document access detected", "Security Threat"),
    ("Unauthorized user attempting to access account", "Security Threat"),
    ("Multiple authentication failures detected", "Security Threat"),

    # System Failure
    ("Payment database connection failed", "System Failure"),
    ("Authentication service failed", "System Failure"),
    ("Backend service crashed", "System Failure"),
    ("Database connection was lost", "System Failure"),
    ("Application server crashed unexpectedly", "System Failure"),
    ("Payment service unavailable", "System Failure"),
    ("Internal database error occurred", "System Failure"),
    ("Backend application failed to start", "System Failure"),
]


def main():
    classifier = LogClassifier()

    print()
    print("DAY 16 - CLASSIFIER EVALUATION")
    print("=" * 70)

    correct = 0
    total = len(TEST_CASES)

    category_results = {}

    confidences = []

    for message, expected in TEST_CASES:

        predicted, confidence = classifier.predict(message)

        passed = predicted == expected

        if passed:
            correct += 1

        if expected not in category_results:
            category_results[expected] = {
                "total": 0,
                "correct": 0,
            }

        category_results[expected]["total"] += 1

        if passed:
            category_results[expected]["correct"] += 1

        confidences.append(confidence)

        status = "PASS" if passed else "FAIL"

        print(f"[{status}]")
        print(f"Message    : {message}")
        print(f"Expected   : {expected}")
        print(f"Predicted  : {predicted}")
        print(f"Confidence : {confidence:.4f}")
        print("-" * 70)

    accuracy = correct / total * 100

    average_confidence = sum(confidences) / len(confidences)
    minimum_confidence = min(confidences)
    maximum_confidence = max(confidences)

    print()
    print("=" * 70)
    print(f"Overall Accuracy: {correct}/{total} = {accuracy:.2f}%")
    print("=" * 70)

    print()
    print("CONFIDENCE SUMMARY")
    print("=" * 70)
    print(f"Average Confidence : {average_confidence:.4f}")
    print(f"Minimum Confidence : {minimum_confidence:.4f}")
    print(f"Maximum Confidence : {maximum_confidence:.4f}")
    print("=" * 70)

    print()
    print("CATEGORY-WISE RESULTS")
    print("=" * 70)

    for category, result in category_results.items():

        category_accuracy = (
            result["correct"] / result["total"] * 100
        )

        print(
            f"{category:25} "
            f"{result['correct']}/{result['total']} "
            f"= {category_accuracy:.2f}%"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()