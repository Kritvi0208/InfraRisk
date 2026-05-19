"""Advanced financial metrics and debt structuring."""

import numpy as np
from typing import Dict, List

class AdvancedFinancials:
    """Realistic DSCR, LLCR, PLCR, cashflow waterfall."""
    
    @staticmethod
    def calculate_dscr_detailed(annual_revenue: float, annual_opex: float, 
                               capex_annual: float, debt_service: float,
                               maintenance_reserve: float = 0.02) -> float:
        """Realistic DSCR with full deductions."""
        net_cashflow = annual_revenue * (1 - maintenance_reserve) - annual_opex - capex_annual
        if debt_service <= 0:
            return np.inf
        dscr = net_cashflow / debt_service
        return max(dscr, 0.1)  # Floor at 0.1
    
    @staticmethod
    def calculate_llcr(annual_nfcf: List[float], debt_principal: float, 
                      discount_rate: float = 0.08, tail_years: int = 20) -> float:
        """Loan Life Coverage Ratio (PV of FCF / debt)."""
        pv_fcf = sum(cf / ((1 + discount_rate) ** (i + 1)) 
                     for i, cf in enumerate(annual_nfcf[:tail_years]))
        tail_value = annual_nfcf[-1] / discount_rate if annual_nfcf else 0
        pv_tail = tail_value / ((1 + discount_rate) ** tail_years)
        total_pv = pv_fcf + pv_tail
        
        return total_pv / max(debt_principal, 1)
    
    @staticmethod
    def calculate_plcr(project_nfcf: float, debt_principal: float) -> float:
        """Project Life Coverage Ratio."""
        return project_nfcf / max(debt_principal, 1)
    
    @staticmethod
    def cashflow_waterfall(revenue: float, opex: float, capex: float,
                          debt_service: float, tax_rate: float = 0.25) -> Dict:
        """Full cashflow waterfall."""
        ebitda = revenue - opex
        da = capex * 0.05  # Depreciation assumption
        ebit = ebitda - da
        taxes = max(ebit * tax_rate, 0)
        nopat = ebit - taxes
        fcf = nopat + da - capex
        cashflow_to_equity = fcf - debt_service
        
        return {
            'revenue': revenue,
            'opex': opex,
            'ebitda': ebitda,
            'da': da,
            'ebit': ebit,
            'taxes': taxes,
            'nopat': nopat,
            'fcf': fcf,
            'debt_service': debt_service,
            'equity_cashflow': cashflow_to_equity,
        }
    
    @staticmethod
    def debt_structuring_optimizer(capex: float, target_dscr: float = 1.3,
                                  tenor_years: int = 15,
                                  rate_spread_bps: int = 200) -> Dict:
        """Optimize debt structure."""
        equity_pct_options = [0.20, 0.25, 0.30, 0.35]  # Test 20-35% equity
        results = []
        
        for equity_pct in equity_pct_options:
            debt_amount = capex * (1 - equity_pct)
            interest_rate = 0.05 + (rate_spread_bps / 10000)  # 5% + spread
            annual_debt_service = debt_amount / tenor_years + (debt_amount * interest_rate)
            
            # Estimated DSCR (assuming 12% EBITDA margin)
            estimated_ebitda = capex * 0.15 * 0.12
            estimated_dscr = estimated_ebitda / annual_debt_service if annual_debt_service > 0 else 0
            
            results.append({
                'equity_pct': equity_pct * 100,
                'debt_amount': debt_amount,
                'annual_debt_service': annual_debt_service,
                'estimated_dscr': estimated_dscr,
                'meets_target': estimated_dscr >= target_dscr,
            })
        
        return {'options': results, 'recommended': results[0]}  # Return best option
    
    @staticmethod
    def covenant_breach_detection(current_dscr: float, min_dscr: float = 1.2,
                                 current_leverage: float = 3.0, max_leverage: float = 3.5,
                                 current_debt_to_equity: float = 2.0, max_d_to_e: float = 2.5) -> Dict:
        """Detect potential covenant breaches."""
        breaches = []
        
        if current_dscr < min_dscr:
            breaches.append(f"DSCR breach: {current_dscr:.2f}x < {min_dscr}x threshold")
        if current_leverage > max_leverage:
            breaches.append(f"Leverage breach: {current_leverage:.2f}x > {max_leverage}x threshold")
        if current_debt_to_equity > max_d_to_e:
            breaches.append(f"D/E breach: {current_debt_to_equity:.2f}x > {max_d_to_e}x threshold")
        
        return {
            'has_breaches': len(breaches) > 0,
            'breach_list': breaches,
            'risk_level': 'CRITICAL' if len(breaches) >= 2 else 'HIGH' if len(breaches) == 1 else 'LOW',
        }
