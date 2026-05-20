"""
Opponent Rules Engine - Hard constraints and covenant enforcement
Complete implementation: 250 lines
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

from p5_game_state import Portfolio, Deal, DealStatus


@dataclass
class RuleViolation:
    """Rule violation record"""
    rule_name: str
    severity: str  # "warning", "violation", "critical"
    affected_deals: List[str]
    current_value: float
    limit_value: float
    message: str


class OpponentRules:
    """Hard rules for deal selection and portfolio management (250 lines)"""
    
    def __init__(self):
        self.violations: List[RuleViolation] = []
        self.rule_log: List[Dict] = []
    
    # Rule 1: PD Threshold
    def check_pd_limit(self, deal: Deal, max_pd: float = 0.08) -> bool:
        """Hard rule: Reject any deal with PD > 8%"""
        if deal.probability_of_default > max_pd:
            self.violations.append(RuleViolation(
                rule_name="PD_LIMIT",
                severity="critical",
                affected_deals=[deal.deal_id],
                current_value=deal.probability_of_default,
                limit_value=max_pd,
                message=f"Deal PD {deal.probability_of_default:.2%} exceeds limit {max_pd:.2%}"
            ))
            self.rule_log.append({
                "rule": "PD_LIMIT",
                "result": "REJECTED",
                "deal_id": deal.deal_id,
                "value": deal.probability_of_default,
            })
            return False
        return True
    
    # Rule 2: DSCR Minimum
    def check_dscr_minimum(self, deal: Deal, min_dscr: float = 1.25) -> bool:
        """Hard rule: Minimum DSCR of 1.25x"""
        annual_dscr = deal.get_annual_dscr()
        
        if annual_dscr < min_dscr:
            self.violations.append(RuleViolation(
                rule_name="DSCR_MINIMUM",
                severity="critical",
                affected_deals=[deal.deal_id],
                current_value=annual_dscr,
                limit_value=min_dscr,
                message=f"Deal DSCR {annual_dscr:.2f}x below minimum {min_dscr:.2f}x"
            ))
            self.rule_log.append({
                "rule": "DSCR_MINIMUM",
                "result": "REJECTED",
                "deal_id": deal.deal_id,
                "value": annual_dscr,
            })
            return False
        return True
    
    # Rule 3: Portfolio DSCR
    def check_portfolio_dscr_minimum(self, portfolio: Portfolio, min_dscr: float = 1.25) -> bool:
        """Portfolio-level DSCR minimum"""
        portfolio_dscr = portfolio.get_portfolio_dscr()
        
        if portfolio_dscr < min_dscr:
            self.violations.append(RuleViolation(
                rule_name="PORTFOLIO_DSCR_MINIMUM",
                severity="critical",
                affected_deals=list(portfolio.deals.keys()),
                current_value=portfolio_dscr,
                limit_value=min_dscr,
                message=f"Portfolio DSCR {portfolio_dscr:.2f}x below minimum {min_dscr:.2f}x"
            ))
            return False
        return True
    
    # Rule 4: HHI Concentration - Sector
    def check_sector_concentration(
        self, portfolio: Portfolio, sector: str, max_concentration: float = 0.35
    ) -> bool:
        """HHI Rule: No sector > 35% of portfolio"""
        concentration = portfolio.get_sector_concentration(sector)
        
        if concentration > max_concentration:
            self.violations.append(RuleViolation(
                rule_name="SECTOR_CONCENTRATION",
                severity="warning",
                affected_deals=[d.deal_id for d in portfolio.deals.values() if d.sector == sector],
                current_value=concentration,
                limit_value=max_concentration,
                message=f"{sector} concentration {concentration:.2%} exceeds limit {max_concentration:.2%}"
            ))
            return False
        return True
    
    # Rule 5: Single Deal Size Limit
    def check_single_deal_limit(
        self, portfolio: Portfolio, deal: Deal, max_pct: float = 0.15
    ) -> bool:
        """HHI Rule: No single deal > 15% of portfolio"""
        deal_size = deal.equity_amount + deal.debt_amount
        portfolio_value = portfolio.get_portfolio_value()
        
        if portfolio_value == 0:
            return True
        
        pct = deal_size / portfolio_value
        
        if pct > max_pct:
            self.violations.append(RuleViolation(
                rule_name="SINGLE_DEAL_LIMIT",
                severity="warning",
                affected_deals=[deal.deal_id],
                current_value=pct,
                limit_value=max_pct,
                message=f"Deal {deal.deal_id} size {pct:.2%} exceeds limit {max_pct:.2%}"
            ))
            return False
        return True
    
    # Rule 6: Leverage Maximum
    def check_leverage_limit(self, portfolio: Portfolio, max_leverage: float = 0.75) -> bool:
        """Hard rule: Leverage maximum 75% (Debt/Equity)"""
        if portfolio.total_equity_invested == 0:
            return True
        
        leverage = portfolio.total_debt_raised / portfolio.total_equity_invested
        
        if leverage > max_leverage:
            self.violations.append(RuleViolation(
                rule_name="LEVERAGE_LIMIT",
                severity="critical",
                affected_deals=list(portfolio.deals.keys()),
                current_value=leverage,
                limit_value=max_leverage,
                message=f"Portfolio leverage {leverage:.2f}x exceeds maximum {max_leverage:.2f}x"
            ))
            return False
        return True
    
    # Rule 7: Debt/EBITDA Maximum
    def check_debt_to_ebitda_limit(self, portfolio: Portfolio, max_de: float = 6.0) -> bool:
        """Hard rule: Debt/EBITDA maximum 6.0x"""
        total_ebitda = sum(d.get_annual_ebitda() for d in portfolio.deals.values())
        
        if total_ebitda <= 0:
            return False
        
        debt_to_ebitda = portfolio.total_debt_raised / total_ebitda
        
        if debt_to_ebitda > max_de:
            self.violations.append(RuleViolation(
                rule_name="DEBT_TO_EBITDA_LIMIT",
                severity="critical",
                affected_deals=list(portfolio.deals.keys()),
                current_value=debt_to_ebitda,
                limit_value=max_de,
                message=f"Portfolio Debt/EBITDA {debt_to_ebitda:.2f}x exceeds limit {max_de:.2f}x"
            ))
            return False
        return True
    
    # Rule 8: Covenant Enforcement
    def check_covenant_compliance(
        self, deal: Deal, active_events: List[str] = None
    ) -> bool:
        """Enforce debt covenants"""
        if active_events is None:
            active_events = []
        
        # If in active refinancing or default, covenant breach
        if deal.status in (DealStatus.REFINANCING, DealStatus.DEFAULT):
            self.violations.append(RuleViolation(
                rule_name="COVENANT_ENFORCEMENT",
                severity="critical",
                affected_deals=[deal.deal_id],
                current_value=0,
                limit_value=0,
                message=f"Deal {deal.deal_id} in {deal.status.value} - covenant breach"
            ))
            return False
        
        # DSCR covenant
        if deal.get_annual_dscr() < 1.1:  # Covenant DSCR
            deal.status = DealStatus.REFINANCING
            return False
        
        return True
    
    # Rule 9: Maximum Default Rate
    def check_portfolio_default_rate(self, portfolio: Portfolio, max_default_rate: float = 0.15) -> bool:
        """Portfolio default rate < 15%"""
        if len(portfolio.deals) == 0:
            return True
        
        default_count = portfolio.get_default_count()
        default_rate = default_count / len(portfolio.deals)
        
        if default_rate > max_default_rate:
            self.violations.append(RuleViolation(
                rule_name="PORTFOLIO_DEFAULT_RATE",
                severity="critical",
                affected_deals=[d.deal_id for d in portfolio.deals.values() if d.is_in_default()],
                current_value=default_rate,
                limit_value=max_default_rate,
                message=f"Portfolio default rate {default_rate:.2%} exceeds limit {max_default_rate:.2%}"
            ))
            return False
        return True
    
    # Rule 10: Country Concentration
    def check_country_concentration(
        self, portfolio: Portfolio, country: str, max_concentration: float = 0.40
    ) -> bool:
        """Country concentration limit"""
        total_value = portfolio.get_portfolio_value()
        if total_value == 0:
            return True
        
        country_value = sum(
            d.equity_amount + d.debt_amount
            for d in portfolio.deals.values()
            if d.country == country
        )
        
        concentration = country_value / total_value
        
        if concentration > max_concentration:
            self.violations.append(RuleViolation(
                rule_name="COUNTRY_CONCENTRATION",
                severity="warning",
                affected_deals=[d.deal_id for d in portfolio.deals.values() if d.country == country],
                current_value=concentration,
                limit_value=max_concentration,
                message=f"{country} concentration {concentration:.2%} exceeds limit {max_concentration:.2%}"
            ))
            return False
        return True
    
    def validate_deal_for_inclusion(self, portfolio: Portfolio, deal: Deal) -> Tuple[bool, List[str]]:
        """Comprehensive deal validation"""
        issues = []
        
        if not self.check_pd_limit(deal):
            issues.append("PD exceeds 8% limit")
        
        if not self.check_dscr_minimum(deal):
            issues.append("DSCR below 1.25x minimum")
        
        if not self.check_single_deal_limit(portfolio, deal):
            issues.append("Deal size would exceed 15% of portfolio")
        
        if not self.check_sector_concentration(portfolio, deal.sector):
            issues.append(f"{deal.sector} concentration would exceed 35% limit")
        
        if not self.check_country_concentration(portfolio, deal.country):
            issues.append(f"{deal.country} concentration would exceed 40% limit")
        
        return (len(issues) == 0, issues)
    
    def validate_portfolio(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Full portfolio validation"""
        self.violations.clear()
        
        results = {
            "portfolio_valid": True,
            "violations": [],
            "warnings": [],
        }
        
        if not self.check_portfolio_dscr_minimum(portfolio):
            results["portfolio_valid"] = False
            results["violations"].append("Portfolio DSCR below minimum")
        
        if not self.check_leverage_limit(portfolio):
            results["portfolio_valid"] = False
            results["violations"].append("Portfolio leverage exceeds limit")
        
        if not self.check_debt_to_ebitda_limit(portfolio):
            results["portfolio_valid"] = False
            results["violations"].append("Debt/EBITDA ratio exceeds limit")
        
        if not self.check_portfolio_default_rate(portfolio):
            results["portfolio_valid"] = False
            results["violations"].append("Portfolio default rate exceeds limit")
        
        results["violations"] = [v.message for v in self.violations]
        
        return results
    
    def get_compliance_score(self, portfolio: Portfolio) -> float:
        """Get compliance score 0-100"""
        self.validate_portfolio(portfolio)
        
        violations = len([v for v in self.violations if v.severity == "critical"])
        warnings = len([v for v in self.violations if v.severity == "warning"])
        
        score = 100 - (violations * 20) - (warnings * 5)
        return max(0, score)
