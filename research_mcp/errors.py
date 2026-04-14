class ResearchMCPError(Exception):
    """Base application error."""


class ProviderConfigurationError(ResearchMCPError):
    """Raised when provider configuration is incomplete."""


class ProviderRequestError(ResearchMCPError):
    """Raised when an upstream provider request fails."""


class AnalysisConfigurationError(ResearchMCPError):
    """Raised when an analysis backend or profile is unavailable."""


class IngestionError(ResearchMCPError):
    """Raised when full-text ingestion fails."""
