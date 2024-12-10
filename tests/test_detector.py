import pytest
from src.detector import detect_web_technologies

@pytest.mark.network
def test_example_site():
    # This is a placeholder for real tests with a live or mocked response.
    url = "https://www.example.com"
    results = detect_web_technologies(url)
    assert results is not None
    assert 'HTTPS' in results
