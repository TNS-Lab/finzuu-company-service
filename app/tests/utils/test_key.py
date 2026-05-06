from app.utils.key import generate_key, generate_reference


def test_generate_reference():
    reference = generate_reference(12)

    assert len(reference) == 12
    assert reference.isalnum()
    assert reference.upper() == reference


def test_generate_key():
    key = generate_key(16)

    assert len(key) == 16
