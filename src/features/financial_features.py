"""Financial features: DSCR, LLCR, PLCR, leverage."""

import numpy as np
import pandas as pd

def calculate_dscr(annual_revenue, annual_opex, debt_service) -> float:
    """Debt Service Coverage Ratio."""
    if debt_service == 0:
        return np.inf
    return (annual_revenue - annual_opex) / debt_service

def calculate_llcr(annual_revenue, opex, capex, debt_service, fcf_tail=20) -> float:
    """Loan Life Coverage Ratio (PV of cash flows / debt)."""
    cf_stream = [max(0, annual_revenue - opex - capex - debt_service) for _ in range(fcf_tail)]
    pv = sum(cf / (1.08 ** i) for i, cf in enumerate(cf_stream))
    return pv / max(1, debt_service * 20)

def calculate_plcr(project_nfcf, debt_principal) -> float:
    """Project Life Coverage Ratio."""
    return project_nfcf / max(1, debt_principal)

def calculate_leverage(debt_principal, equity) -> float:
    """Debt-to-equity ratio."""
    return debt_principal / max(1, equity)
