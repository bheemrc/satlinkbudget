"""SaaS API layer: schemas, services, serializers, errors."""

from satlinkbudget.api._schemas import (
    PlotFormat,
    TimeSeriesData,
    PlotData,
    LinkBudgetRequest,
    LinkBudgetResponse,
    LinkBudgetSummary,
    MaxDataRateRequest,
    MaxDataRateResponse,
    RequiredPowerRequest,
    RequiredPowerResponse,
    PassSimulationRequest,
    PassSimulationResponse,
    PassSummary,
    SimulationSummary,
    PresetSimulationRequest,
    ComponentInfo,
    ComponentListResponse,
    ComponentDetailResponse,
    PresetInfo,
    PresetListResponse,
)
from satlinkbudget.api._services import (
    run_link_budget,
    run_link_budget_async,
    run_max_data_rate,
    run_required_power,
    run_pass_simulation,
    run_pass_simulation_async,
    run_preset,
    run_preset_async,
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
    # Enums
    "PlotFormat",
    # Data models
    "TimeSeriesData",
    "PlotData",
    # Link budget
    "LinkBudgetRequest",
    "LinkBudgetResponse",
    "LinkBudgetSummary",
    "MaxDataRateRequest",
    "MaxDataRateResponse",
    "RequiredPowerRequest",
    "RequiredPowerResponse",
    # Pass simulation
    "PassSimulationRequest",
    "PassSimulationResponse",
    "PassSummary",
    "SimulationSummary",
    # Preset
    "PresetSimulationRequest",
    # Components
    "ComponentInfo",
    "ComponentListResponse",
    "ComponentDetailResponse",
    "PresetInfo",
    "PresetListResponse",
    # Services
    "run_link_budget",
    "run_link_budget_async",
    "run_max_data_rate",
    "run_required_power",
    "run_pass_simulation",
    "run_pass_simulation_async",
    "run_preset",
    "run_preset_async",
    "list_components",
    "get_component",
    "get_presets",
    # Errors
    "SatLinkBudgetError",
    "ConfigurationError",
    "ValidationError",
    "ComponentNotFoundError",
]
