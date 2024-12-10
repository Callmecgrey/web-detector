import sys
import logging
from src.detector import detect_web_technologies
from src.utils import validate_and_normalize_url

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    if len(sys.argv) > 1:
        url = sys.argv[1].strip()
    else:
        url = input("Enter the website URL (including http:// or https://): ").strip()

    validated_url = validate_and_normalize_url(url)
    if not validated_url:
        logging.error("Invalid URL. Please include 'http://' or 'https://'.")
        sys.exit(1)

    results = detect_web_technologies(validated_url)
    if results is None:
        logging.error("Could not detect technologies due to an error.")
        sys.exit(1)

    print("\nDetected Technologies on", validated_url)
    for tech, values in results.items():
        if isinstance(values, set) and values:
            print(f"{tech}: {', '.join(sorted(values))}")
        elif values:
            print(f"{tech}: {values}")
        else:
            print(f"{tech}: Not detected")

if __name__ == "__main__":
    main()
