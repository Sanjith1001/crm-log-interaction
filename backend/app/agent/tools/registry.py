from typing import Dict, Any
from app.agent.tools import (
    log_interaction,
    edit_interaction,
    search_interaction,
    hcp_lookup,
    followup_recommendation,
    schedule_followup,
    product_lookup,
    compliance_audit,
    sales_summary,
    add_hcp
)

TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "log_interaction": {
        "run": log_interaction.run,
        "description": "Extract structured details and save a new HCP interaction"
    },
    "edit_interaction": {
        "run": edit_interaction.run,
        "description": "Edit or update an existing logged interaction"
    },
    "search_interaction": {
        "run": search_interaction.run,
        "description": "Search past interactions using text filters"
    },
    "hcp_lookup": {
        "run": hcp_lookup.run,
        "description": "Look up specialty, hospital, city, and history of an HCP"
    },
    "followup_recommendation": {
        "run": followup_recommendation.run,
        "description": "Analyze history and recommend next steps for an HCP"
    },
    "schedule_followup": {
        "run": schedule_followup.run,
        "description": "Schedule a follow-up meeting with an HCP"
    },
    "product_lookup": {
        "run": product_lookup.run,
        "description": "Query indications, dosage, inventory and therapeutic details of a product"
    },
    "compliance_audit": {
        "run": compliance_audit.run,
        "description": "Perform compliance audit of samples given to a doctor"
    },
    "sales_summary": {
        "run": sales_summary.run,
        "description": "Generate performance sales reporting metrics and activity statistics"
    },
    "add_hcp": {
        "run": add_hcp.run,
        "description": "Create and add a new Healthcare Professional (HCP) profile to the database"
    }
}
