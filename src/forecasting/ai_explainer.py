"""Generate a grounded, plain-English historical market forecast summary.

This version deliberately does not call Groq: unchecked model prose must not be
presented as verified market evidence. An optional validated AI layer can be
added later without changing the existing API response contract.
"""

from src.forecasting.explanations import build_market_changes, build_market_evidence


def safe_market_explanation(evidence: dict, changes: dict) -> str:
    """Describe only the forecast values and comparisons calculated in Python."""
    low_time = evidence["cheapest_hour"]
    high_time = evidence["most_expensive_hour"]
    low_price = evidence["cheapest_price_eur_mwh"]
    high_price = evidence["highest_price_eur_mwh"]
    spread = evidence["price_spread_eur_mwh"]

    if low_time == high_time:
        comparison = "The lowest and highest predicted prices occur at the same hour."
    else:
        comparison = (
            f"Comparing those two hours, forecast solar generation "
            f"{changes['solar']['direction']}, wind generation "
            f"{changes['wind']['direction']}, and electricity demand "
            f"{changes['demand']['direction']}."
        )

    return (
        "Historical forecast replay: "
        f"the lowest predicted electricity price is at {low_time} "
        f"(€{low_price:,.2f}/MWh), and the highest is at {high_time} "
        f"(€{high_price:,.2f}/MWh). "
        f"The difference is €{spread:,.2f}/MWh. "
        f"{comparison} "
        "These conditions coincide with the predicted prices; they do not prove what caused them. "
        "This is not a live market forecast."
    )


def generate_market_explanation(forecast):
    """Return the same JSON fields expected by the existing FastAPI endpoint."""
    evidence = build_market_evidence(forecast)
    changes = build_market_changes(evidence)
    return {
        "explanation": safe_market_explanation(evidence, changes),
        "evidence": evidence,
        "market_changes": changes,
        "generated_by": "verified_python_summary",
        "analysis_type": "historical_forecast_replay",
    }
