"""
Hardcoded risk scoring rules for Phase 4 NLP pipeline.
Defines risk multipliers, red flags, and scoring logic.
"""

from typing import Dict, List, Tuple
from contract_types import RiskCategory, SeverityLevel

# Risk weights for each category (importance multiplier)
CATEGORY_WEIGHTS: Dict[RiskCategory, float] = {
    RiskCategory.FORCE_MAJEURE: 1.8,
    RiskCategory.TERMINATION: 2.0,
    RiskCategory.COVENANTS: 2.2,
    RiskCategory.FINANCIAL: 2.5,
    RiskCategory.ENVIRONMENTAL: 1.9,
    RiskCategory.LABOR: 1.6,
    RiskCategory.SAFETY: 1.9,
    RiskCategory.INTELLECTUAL_PROPERTY: 1.4,
    RiskCategory.DISPUTES: 1.7,
    RiskCategory.INSURANCE: 1.8,
    RiskCategory.PENALTIES: 2.0,
    RiskCategory.OTHER: 1.0,
}

# Red flag keywords and their severity impact
RED_FLAG_KEYWORDS: Dict[str, Tuple[SeverityLevel, float]] = {
    # Force Majeure red flags
    'force majeure': (SeverityLevel.HIGH, 1.5),
    'unforeseeable circumstances': (SeverityLevel.HIGH, 1.4),
    'act of god': (SeverityLevel.MEDIUM, 1.2),
    
    # Termination red flags
    'termination for convenience': (SeverityLevel.CRITICAL, 2.0),
    'early termination': (SeverityLevel.HIGH, 1.7),
    'termination without cause': (SeverityLevel.CRITICAL, 1.9),
    'perpetual termination right': (SeverityLevel.CRITICAL, 2.1),
    
    # Covenant red flags
    'covenant breach': (SeverityLevel.CRITICAL, 2.0),
    'financial covenant': (SeverityLevel.HIGH, 1.8),
    'debt service coverage ratio': (SeverityLevel.HIGH, 1.9),
    'leverage ratio': (SeverityLevel.HIGH, 1.8),
    'minimum liquidity': (SeverityLevel.HIGH, 1.7),
    'mandatory prepayment': (SeverityLevel.MEDIUM, 1.3),
    
    # Financial red flags
    'negative pledge': (SeverityLevel.MEDIUM, 1.4),
    'unsecured debt': (SeverityLevel.HIGH, 1.6),
    'cross-default': (SeverityLevel.CRITICAL, 1.9),
    'cross-acceleration': (SeverityLevel.CRITICAL, 1.8),
    'currency fluctuation': (SeverityLevel.MEDIUM, 1.3),
    'interest rate swap': (SeverityLevel.MEDIUM, 1.2),
    
    # Environmental red flags
    'environmental liability': (SeverityLevel.HIGH, 1.8),
    'remediation requirement': (SeverityLevel.HIGH, 1.7),
    'hazardous materials': (SeverityLevel.CRITICAL, 2.0),
    'pollution': (SeverityLevel.HIGH, 1.6),
    'climate risk': (SeverityLevel.MEDIUM, 1.4),
    
    # Labor red flags
    'labor dispute': (SeverityLevel.MEDIUM, 1.3),
    'strike action': (SeverityLevel.MEDIUM, 1.4),
    'union agreement': (SeverityLevel.MEDIUM, 1.2),
    'employment contract': (SeverityLevel.LOW, 0.9),
    
    # Safety red flags
    'safety violation': (SeverityLevel.CRITICAL, 1.9),
    'occupational hazard': (SeverityLevel.HIGH, 1.5),
    'health and safety': (SeverityLevel.MEDIUM, 1.2),
    
    # IP red flags
    'intellectual property': (SeverityLevel.LOW, 0.8),
    'patent infringement': (SeverityLevel.MEDIUM, 1.3),
    'confidentiality': (SeverityLevel.LOW, 0.7),
    
    # Dispute red flags
    'dispute resolution': (SeverityLevel.MEDIUM, 1.2),
    'arbitration': (SeverityLevel.LOW, 0.8),
    'litigation': (SeverityLevel.MEDIUM, 1.3),
    'governing law': (SeverityLevel.LOW, 0.7),
    
    # Insurance red flags
    'insurance requirement': (SeverityLevel.MEDIUM, 1.1),
    'insurance coverage': (SeverityLevel.MEDIUM, 1.0),
    'self-insurance': (SeverityLevel.MEDIUM, 1.4),
    
    # Penalty red flags
    'penalty clause': (SeverityLevel.HIGH, 1.6),
    'liquidated damages': (SeverityLevel.HIGH, 1.7),
    'indemnification': (SeverityLevel.MEDIUM, 1.4),
    'limitation of liability': (SeverityLevel.MEDIUM, 1.1),
}

# Green flag keywords (risk mitigators)
GREEN_FLAG_KEYWORDS: List[str] = [
    'comprehensive insurance',
    'strong financial covenant',
    'experienced sponsor',
    'positive cash flow',
    'established revenue stream',
    'diversified revenue',
    'strong reserves',
    'government guarantee',
    'investment grade',
    'credit rating',
    'audited financials',
    'transparent reporting',
    'experienced operator',
    'proven track record',
    'market-tested',
    'fully hedged',
    'performance bond',
    'parent company guarantee',
    'strong liquidity',
    'robust controls',
]

# Severity thresholds
SEVERITY_THRESHOLDS: Dict[SeverityLevel, Tuple[float, float]] = {
    SeverityLevel.CRITICAL: (4.5, 5.0),
    SeverityLevel.HIGH: (3.5, 4.5),
    SeverityLevel.MEDIUM: (2.5, 3.5),
    SeverityLevel.LOW: (1.5, 2.5),
    SeverityLevel.MINIMAL: (1.0, 1.5),
}

# Missing element penalties
MISSING_ELEMENT_PENALTIES: Dict[str, float] = {
    'missing_milestones': 0.8,
    'missing_financial_covenants': 1.2,
    'weak_financial_covenants': 0.6,
    'missing_insurance': 0.5,
    'missing_termination_clause': 1.0,
    'missing_force_majeure': 0.4,
    'missing_dispute_resolution': 0.3,
    'missing_performance_metrics': 0.7,
    'weak_lender_protections': 0.9,
    'weak_sponsor_obligations': 0.8,
}

# Industry-specific risk factors
INDUSTRY_RISK_FACTORS: Dict[str, float] = {
    'renewable_energy': 0.9,
    'water_infrastructure': 0.95,
    'toll_roads': 1.1,
    'airports': 1.2,
    'ports': 1.15,
    'rail': 1.1,
    'telecom': 1.0,
    'power_generation': 1.05,
    'oil_and_gas': 1.5,
    'mining': 1.3,
    'real_estate': 1.25,
    'default': 1.0,
}

# Country/Region risk factors (political, economic)
COUNTRY_RISK_FACTORS: Dict[str, float] = {
    'usa': 0.8,
    'canada': 0.85,
    'uk': 0.85,
    'germany': 0.85,
    'france': 0.9,
    'japan': 0.85,
    'singapore': 0.9,
    'india': 1.3,
    'brazil': 1.4,
    'mexico': 1.3,
    'uae': 1.0,
    'australia': 0.95,
    'emerging_markets': 1.5,
    'developed_markets': 0.85,
    'default': 1.1,
}

def get_severity_from_score(score: float) -> SeverityLevel:
    """Map numerical score (1-5) to severity level."""
    for severity, (min_val, max_val) in SEVERITY_THRESHOLDS.items():
        if min_val <= score <= max_val:
            return severity
    return SeverityLevel.CRITICAL if score > 4.5 else SeverityLevel.MINIMAL


def get_category_weight(category: RiskCategory) -> float:
    """Get importance weight for a risk category."""
    return CATEGORY_WEIGHTS.get(category, 1.0)


def get_red_flag_impact(keyword: str) -> Tuple[SeverityLevel, float]:
    """Get severity and impact factor for a red flag keyword."""
    keyword_lower = keyword.lower()
    for flag, impact in RED_FLAG_KEYWORDS.items():
        if flag in keyword_lower:
            return impact
    return (SeverityLevel.LOW, 1.0)


def is_green_flag(text: str) -> bool:
    """Check if text contains green flag keywords."""
    text_lower = text.lower()
    for flag in GREEN_FLAG_KEYWORDS:
        if flag in text_lower:
            return True
    return False


def get_industry_risk_factor(industry: str) -> float:
    """Get industry-specific risk multiplier."""
    industry_lower = industry.lower()
    return INDUSTRY_RISK_FACTORS.get(industry_lower, INDUSTRY_RISK_FACTORS['default'])


def get_country_risk_factor(country: str) -> float:
    """Get country/region-specific risk multiplier."""
    country_lower = country.lower()
    return COUNTRY_RISK_FACTORS.get(country_lower, COUNTRY_RISK_FACTORS['default'])


def calculate_base_score(
    category: RiskCategory,
    has_red_flags: bool = False,
    has_green_flags: bool = False,
    red_flag_count: int = 0,
    green_flag_count: int = 0,
) -> float:
    """Calculate base risk score (1-5) from components."""
    # Start with category base score
    base = 2.5
    
    # Apply category weight
    weight = get_category_weight(category)
    base = base * (weight / 1.5)  # Normalize
    
    # Apply red flags
    if has_red_flags:
        base += 0.5 * min(red_flag_count, 3)
    
    # Apply green flags (mitigate risk)
    if has_green_flags:
        base -= 0.3 * min(green_flag_count, 3)
    
    # Clamp to 1-5 range
    return max(1.0, min(5.0, base))


def apply_adjustment_factors(
    score: float,
    industry: str = 'default',
    country: str = 'default',
    missing_penalties: float = 0.0,
) -> float:
    """Apply industry, country, and missing element adjustments."""
    adjusted = score
    
    # Apply industry risk factor
    industry_factor = get_industry_risk_factor(industry)
    adjusted = adjusted * (industry_factor / 1.0)
    
    # Apply country risk factor
    country_factor = get_country_risk_factor(country)
    adjusted = adjusted * (country_factor / 1.0)
    
    # Apply missing penalties
    adjusted += missing_penalties
    
    # Clamp to 1-5 range
    return max(1.0, min(5.0, adjusted))
