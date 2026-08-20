from notification.sanitizer import sanitize_text


def test_email_masking():
    text = "User email is student@example.gov.in"

    result = sanitize_text(text)

    assert "student@example.gov.in" not in result
    assert "@example.gov.in" in result


def test_phone_masking():
    text = "Student phone is 9876543210"

    result = sanitize_text(text)

    assert "9876543210" not in result
    assert result.endswith("3210")


def test_pan_masking():
    text = "PAN number is ABCDE1234F"

    result = sanitize_text(text)

    assert "ABCDE1234F" not in result
    assert "1234F" in result


def test_student_id_masking():
    text = "Student ID is STU918054"

    result = sanitize_text(text)

    assert "STU918054" not in result
    assert "STU" in result


def test_ip_masking():
    text = "Client IP is 10.20.30.40"

    result = sanitize_text(text)

    assert "10.20.30.40" not in result
    assert "10.20.*.*" in result


def test_normal_message():
    text = "Authentication service failed"

    result = sanitize_text(text)

    assert result == text


if __name__ == "__main__":
    print("DAY 24 - SANITIZER TEST")
    print("=" * 60)

    tests = [
        test_email_masking,
        test_phone_masking,
        test_pan_masking,
        test_student_id_masking,
        test_ip_masking,
        test_normal_message,
    ]

    for test in tests:
        test()
        print(f"[PASS] {test.__name__}")

    print("=" * 60)
    print("All sanitization tests passed.")