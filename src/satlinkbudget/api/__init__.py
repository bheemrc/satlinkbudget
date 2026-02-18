"""SaaS API layer: schemas, services, serializers, errors."""

from satlinkbudget.api._schemas import (
    LinkBudgetRequest,
    LinkBudgetResponse,
    PassSimulationRequest,
    PassSimulationResponse,
)
from satlinkbudget.api._services import (
    run_link_budget,
    run_pass_simulation,
    list_components,
    get_component,
    get_presets,
)
from satlinkbudget.api._errors import (
    SatLinkBudgetError,
    ConfigurationError,
    ValidationError,
    ComponentNotFoundError,
)

__all__ = [
    "LinkBudgetRequest",
    "LinkBudgetResponse",
    "PassSimulationRequest",
    "PassSimulationResponse",
    "run_link_budget",
    "run_pass_simulation",
    "list_components",
    "get_component",
    "get_presets",
    "SatLinkBudgetError",
    "ConfigurationError",
    "ValidationError",
    "ComponentNotFoundError",
]
