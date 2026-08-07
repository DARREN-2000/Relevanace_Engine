from prometheus_client import Counter, Gauge, Histogram

DECISION_LATENCY = Histogram(
    "decision_latency_seconds",
    "Latency of NBA decisions",
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

DECISION_COUNT = Counter(
    "decision_count_total", "Total number of decisions made", ["suppressed", "channel"]
)

CONSENT_COVERAGE = Gauge(
    "consent_coverage_ratio", "Ratio of users with active consents"
)
