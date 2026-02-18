"""Domain exceptions."""


class SatLinkBudgetError(Exception):
    """Base exception for satlinkbudget."""


class ConfigurationError(SatLinkBudgetError):
    """Invalid configuration."""


class ValidationError(SatLinkBudgetError):
    """Validation check failed."""


class ComponentNotFoundError(SatLinkBudgetError):
    """Component not found in registry."""
