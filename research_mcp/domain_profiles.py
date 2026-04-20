from __future__ import annotations

from dataclasses import dataclass, field

from research_mcp.query_expansion import is_sbi_calibration_query


@dataclass(frozen=True)
class DomainProfile:
    name: str
    section_weights: dict[str, float] = field(default_factory=dict)
    evidence_markers: tuple[str, ...] = ()
    unsupported_markers: tuple[str, ...] = ()


GENERAL_PROFILE = DomainProfile(
    name="general",
    section_weights={
        "abstract": 0.08,
        "introduction": 0.04,
        "method": 0.08,
        "results": 0.06,
        "conclusion": 0.04,
        "body": 0.02,
    },
    evidence_markers=("method", "experiment", "result", "limitation", "assumption", "conclusion"),
    unsupported_markers=("not explicit", "manual inspection", "manual verification", "not clearly"),
)

SBI_CALIBRATION_PROFILE = DomainProfile(
    name="sbi_calibration",
    section_weights={
        "abstract": 0.10,
        "introduction": 0.04,
        "method": 0.14,
        "results": 0.12,
        "conclusion": 0.05,
        "body": 0.04,
    },
    evidence_markers=(
        "calibration",
        "coverage",
        "rank",
        "posterior",
        "simulation",
        "benchmark",
        "misspecification",
        "diagnostic",
        "failure",
        "bias",
    ),
    unsupported_markers=("not explicit", "manual inspection", "manual verification", "not clearly"),
)


PROFILES = {
    GENERAL_PROFILE.name: GENERAL_PROFILE,
    SBI_CALIBRATION_PROFILE.name: SBI_CALIBRATION_PROFILE,
}


def resolve_domain_profile(profile: str | None, topic: str | None = None) -> DomainProfile:
    normalized = (profile or "auto").strip().lower()
    if normalized == "auto":
        return SBI_CALIBRATION_PROFILE if topic and is_sbi_calibration_query(topic) else GENERAL_PROFILE
    return PROFILES.get(normalized, GENERAL_PROFILE)
