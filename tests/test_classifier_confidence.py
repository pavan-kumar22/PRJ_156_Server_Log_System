from classifier.model import LogClassifier


classifier = LogClassifier()


TEST_CASES = [
    # Routine Audit
    ("User authentication successful", "Routine Audit"),
    ("Student application submitted successfully", "Routine Audit"),
    ("Document downloaded successfully", "Routine Audit"),

    # Performance Degradation
    ("Payment gateway request timed out", "Performance Degradation"),
    ("Database request latency is high", "Performance Degradation"),
    ("API response time is increasing", "Performance Degradation"),

    # Security Threat
    ("Unauthorized access attempt detected", "Security Threat"),
    ("Multiple failed login attempts detected", "Security Threat"),
    ("Suspicious repeated document access detected", "Security Threat"),
    ("Invalid authentication token detected", "Security Threat"),

    # System Failure
    ("Payment database connection failed", "System Failure"),
    ("Authentication service failed", "System Failure"),
    ("Backend service crashed", "System Failure"),
]


correct = 0
total = len(TEST_CASES)

print("\nDAY 15 - CLASSIFIER CONFIDENCE TEST")
print("=" * 70)

for message, expected in TEST_CASES:
    predicted, confidence = classifier.predict(message)

    status = "PASS" if predicted == expected else "FAIL"

    if predicted == expected:
        correct += 1

    print(f"\n[{status}]")
    print(f"Message    : {message}")
    print(f"Expected   : {expected}")
    print(f"Predicted  : {predicted}")
    print(f"Confidence : {confidence:.4f}")

print("\n" + "=" * 70)
print(f"Accuracy: {correct}/{total} = {(correct / total) * 100:.2f}%")
print("=" * 70)