from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class JournalProfile:
    key: str
    label: str
    issn: str
    doi_prefixes: tuple[str, ...]
    article_base_url: str
    query_terms: tuple[str, ...]
    domain_terms: dict[str, float] = field(default_factory=dict)
    method_terms: dict[str, float] = field(default_factory=dict)


DEFAULT_DOMAIN_TERMS = {
    "atmospheric": 3.0,
    "atmosphere": 2.5,
    "troposphere": 4.0,
    "stratosphere": 3.0,
    "air quality": 4.0,
    "ozone": 4.0,
    "nox": 5.0,
    "methane": 3.5,
    "aerosol": 3.5,
    "volatile organic": 3.0,
    "emission": 2.5,
    "emissions": 2.5,
    "convection": 2.5,
    "lightning": 4.0,
    "aircraft": 3.5,
    "field observation": 3.5,
    "remote sensing": 2.5,
    "chemical transport": 4.0,
    "earth system": 2.0,
    "climate": 1.5,
}

DEFAULT_METHOD_TERMS = {
    "bayesian": 5.0,
    "posterior": 5.0,
    "inverse": 5.0,
    "inference": 4.0,
    "uncertainty": 4.0,
    "calibration": 4.0,
    "constraint": 3.5,
    "constrained": 3.5,
    "machine learning": 3.0,
    "deep learning": 3.0,
    "neural": 3.0,
    "emulator": 3.5,
    "surrogate": 3.0,
    "simulation": 2.0,
    "model evaluation": 3.0,
    "model": 1.0,
    "diagnostic": 2.5,
    "ensemble": 2.5,
}


JOURNAL_PROFILES: dict[str, JournalProfile] = {
    "nature-communications": JournalProfile(
        key="nature-communications",
        label="Nature Communications",
        issn="2041-1723",
        doi_prefixes=("10.1038/s41467-",),
        article_base_url="https://www.nature.com/articles/",
        query_terms=(
            "atmospheric chemistry",
            "air quality",
            "upper troposphere",
            "NOx ozone",
            "methane emissions inverse model",
            "aerosol chemistry",
            "volatile organic compounds",
            "chemical transport model",
            "field observations model",
            "climate model uncertainty",
            "Bayesian inference",
            "inverse modeling",
            "calibration uncertainty",
            "posterior predictive",
            "machine learning climate",
            "deep learning atmosphere",
            "Earth system model",
            "model constraint observations",
            "emission inventory uncertainty",
            "remote sensing atmospheric",
        ),
        domain_terms=DEFAULT_DOMAIN_TERMS,
        method_terms=DEFAULT_METHOD_TERMS,
    ),
    "npj-cas": JournalProfile(
        key="npj-cas",
        label="npj Climate and Atmospheric Science",
        issn="2397-3722",
        doi_prefixes=("10.1038/s41612-",),
        article_base_url="https://www.nature.com/articles/",
        query_terms=(
            "climate atmospheric science",
            "air quality",
            "chemical transport model",
            "model constraint observations",
            "machine learning atmosphere",
            "uncertainty climate",
        ),
        domain_terms=DEFAULT_DOMAIN_TERMS,
        method_terms=DEFAULT_METHOD_TERMS,
    ),
}


def get_journal_profile(key: str) -> JournalProfile:
    normalized = key.strip().lower()
    if normalized not in JOURNAL_PROFILES:
        choices = ", ".join(sorted(JOURNAL_PROFILES))
        raise ValueError(f"Unknown journal profile: {key}. Available profiles: {choices}")
    return JOURNAL_PROFILES[normalized]


def profile_choices() -> list[str]:
    return sorted(JOURNAL_PROFILES)
