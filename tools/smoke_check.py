from backend.src.api import get_value_signal, calculate_attribute_coverage


def main():
    signal = get_value_signal()
    assert signal["issue"] == "ISSUE-001"
    assert signal["targetLiftPct"] == 20

    records = [{"title": "A", "doi": "10.1/x"}]
    cov = calculate_attribute_coverage(records, ["title", "doi"])
    assert cov == 1.0

    print("smoke-check:ok")


if __name__ == "__main__":
    main()
