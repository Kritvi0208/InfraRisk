# InfraRisk AI: Executive Summary for Portfolio Managers

---

## 1. Introduction

InfraRisk AI is a comprehensive infrastructure project risk assessment platform designed for portfolio managers, institutional investors, and development finance institutions managing 50-500 infrastructure assets across emerging markets. The platform integrates satellite imagery, climate science, machine learning, and financial analysis to provide real-time, forward-looking risk signals that traditional debt coverage ratio methodologies miss.

**Key Question We Answer**: *In a portfolio of 50 infrastructure projects spread across 10 countries, which assets face real default risk, and what scenarios trigger distress?*

---

## 2. The Problem: Why Traditional Models Fail

### 2.1 Limitations of Historical Approaches

**Traditional Model**:
```
Default Probability = f(DSCR, Leverage, Debt/Assets)
```

**Drawbacks**:
- **Static**: Only looks at historical coverage ratios; ignores forward-looking indicators
- **Incomplete**: Missing geospatial, climate, and portfolio-level contagion effects
- **Delayed**: Updated annually or quarterly; market shocks manifest in weeks
- **Opaque**: Contracts and covenants manually reviewed; 30% of key terms missed

**Real-World Example**: A hydroelectric project in Brazil reported 1.65x DSCR (healthy) but faced 23% RUL degradation by 2050 due to projected drought. Traditional model flagged it as "low risk"; climate-adjusted model raised PD by 180bps.

### 2.2 Market Consequences

Infrastructure fund managers face:
- **Capital Inefficiency**: Unable to distinguish signal from noise in 50-project portfolios
- **Tail Risk**: Correlated failures during sector shocks go undetected
- **Climate Blind Spots**: Long-tenure assets (20-40 year concessions) face material physical risks
- **Refinancing Surprises**: Lenders unexpectedly require higher covenants; portfolio reprice

---

## 3. The Solution: InfraRisk AI Platform

### 3.1 Core Innovation: Four Integrated Pillars

#### **Pillar 1: Satellite Intelligence**
- Monthly monitoring of 500+ projects via Sentinel-2 imagery (10m resolution)
- Construction progress detection: Which projects are on/off schedule?
- Asset degradation assessment: Pavement cracks, vegetation loss, water infiltration
- Early warning: Detect revenue impact before financial data arrives

**Example**: A toll road satellite imagery showed 4% YoY decline in lane utilization (NDBI index) three months before revenue reporting. Alert issued before financials available.

#### **Pillar 2: Physics-Informed Climate Risk**
- Remaining Useful Life (RUL) adjusted for climate scenarios: RCP 2.6, 4.5, 8.5
- Integration with IPCC AR6 projections + AASHTO pavement design standards
- Asset-level granularity: Does this specific road survive to 2050 at current design standards?

**Formula**:
```
CA-RUL = RUL₀ × (1 - 0.08 × ΔT) × (1 - 0.12 × |ΔP|)
```

where ΔT = temperature change, ΔP = precipitation change by 2050

**Impact on Debt**:
- Traditional DSCR: 1.65x (supported $150M senior debt)
- Climate-Adjusted: RUL shortened by 20%; support only $85M senior debt
- Refinancing Risk: After 13-14 years, asset may not support remaining tenor

#### **Pillar 3: Ensemble Machine Learning**
- **94% Gini coefficient** on unseen historical defaults (vs. 42% for DSCR-only)
- 4-model ensemble (XGBoost, Neural Network, Random Forest, SVM) with sector weights
- Sector-specific calibration: Toll roads weight traffic data differently than hydroelectric

**Validation on 850 historical projects (2005-2015)**:
| Metric | Value | Interpretation |
|--------|-------|-----------------|
| AUC-ROC | 0.942 | 94% ability to separate defaults from non-defaults |
| Gini | 0.824 | Captures 82% of predictive power |
| Precision @ 5% false positive rate | 58% | When we flag "high risk," 58% actually defaulted |
| Recall @ 10% false negative rate | 72% | We catch 72% of eventual defaults |

#### **Pillar 4: Portfolio Contagion Modeling**
- Graph neural network models 500-project portfolios as interconnected system
- Identifies hub projects whose failure cascades to others (common sponsor, operator, lender)
- Quantifies systemic amplification: Single-project PD → portfolio PD

**Example**: Portfolio systemic PD = 4.8% vs. sum of individual PDs = 3.2%
- Amplification factor: 1.50x (50% of portfolio risk comes from contagion)
- Root cause: 15% of projects share common operator with failing project

### 3.2 Real-Time Monitoring

**Dashboard Delivers**:
1. **Project Risk Card**: PD, climate-adjusted metrics, early warning flags (daily)
2. **Portfolio Heat Map**: Sector risk, geographic concentration, systemic exposure
3. **Alert Engine**: Triggers when PD increases >500bps, revenue declines >10% YoY, covenants breach imminent
4. **Stress Test Module**: "What if" scenarios (50% revenue shock, 200bps CDS widening, 30% currency devaluation)

---

## 4. Key Findings from Live Deployments

### 4.1 Deal Pipeline: What Changed

**Historical**: Credit committee screened 20 LOI deals/month using DSCR, leverage, sponsor credit
**Now**: InfraRisk AI flags 15% as "climate at-risk" (20+ year asset, >15% RUL degradation by 2050)

**Actions Taken**:
- 8 deals restructured: lower debt tenor (17y → 15y), higher equity requirement
- 3 deals rejected: RUL projection incompatible with debt tenor
- $200M capital redeployed to climate-resilient assets (solar, water resilience)

### 4.2 Portfolio Monitoring: Active Alerts

**Historical**: Annual review cycle; surprises emerge at refinancing
**Now**: 47-project portfolio monitored daily; 3-5 actionable alerts/month

**Example Alerts Issued** (Last 90 Days):
1. **High Severity**: India toll road revenue down 12% YoY; satellite NDBI showed -4% lane utilization. Covenant breach imminent (DSCR 1.32x, covenant floor 1.30x). **Action**: Proactive covenant waiver discussion with lender.

2. **Medium Severity**: Brazilian hydroelectric drought stress indicator trending up (NDMI anomaly -2σ). Water availability forecast down 8% by 2030. **Action**: Diversify renewable portfolio; consider hydro to solar transition.

3. **Low Severity**: Colombian port throughput tracking below forecast (+2.3% actual vs. +6.5% plan). Macro headwinds (slower trade). **Action**: Monitor; no immediate action.

### 4.3 Covenant Extraction: From Manual to Automated

**Historical**: 30 hours per deal to extract DSCR, tenor, step-in terms from 200-page contracts
**Now**: LayoutLM + NER extracts key terms in <30 seconds; 94% accuracy

**Terms Extracted** (Example Deal):
- Loan amount: $150M ✓
- DSCR covenant: 1.30x ✓
- Step-in rights period: 90 days ✓
- Currency hedging requirement: 75% ✓
- Refinancing restrictions: Yes, pre-approval required ✓

**Risk Classification**: Standard market terms (green), not distressed

---

## 5. Financial Impact

### 5.1 Capital Allocation Improvement

**Portfolio**: 50 projects, $4.2B AUM

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Weighted avg PD | 4.2% | 3.1% | Better risk-adjusted allocation |
| % projects >3% PD | 24% | 12% | Reduced tail risk |
| Undetected climate vulnerabilities | 35 projects | 8 projects | Climate-resilience improved |
| Refinancing surprises/year | 3-4 | 0-1 | Fewer covenant breaches |
| Revenue forecasting MAPE | 25% | 12.3% | Better cash flow projection |

**Dollar Impact**:
- Avoided refinancing costs: $8M (lower repricing on 4 deals)
- Improved debt sizing: $65M additional capacity across 8 deals (better leverage)
- Climate risk mitigation: $120M redeployment to resilient assets

### 5.2 Risk Committee Confidence

"Before InfraRisk, we managed by consensus and historical gut check. Now we have a systematic framework—climate-adjusted RUL, contagion modeling, early warnings. The board asks harder questions; we have data-driven answers." — Infrastructure fund CRO

---

## 6. Climate Risk: The Hidden Factor

### 6.1 Why It Matters

Infrastructure concessions are 20-40 year bets on climate. Yet most credit decisions ignore it.

**Case Study: Pavement Degradation**
- Toll road in Gujarat, India
- AASHTO design life: 35 years
- Current age: 15 years
- Baseline RUL: 20 years

**Climate Adjustment (RCP 4.5, +2.4°C, -8% precipitation)**:
- Temperature stress: asphalt binder degrades faster
- Moisture stress: less rainfall means less flushing of contaminants; paradoxically worse for fatigue
- CA-RUL: 20 × 0.800 = 16 years

**Implication**: Asset reaches end-of-life ~4 years earlier. If debt is 18-year tenor with bullet maturity, refinancing needed by year 16. But asset deteriorating; refinance at higher rates or with lower leverage.

### 6.2 Portfolio-Level Climate Risk

**InfraRisk Assessment of 47-Project Portfolio**:

| Scenario | Avg RUL 2050 | Projects >15% degradation | Recommended Action |
|----------|-------------|-------------------------|-------------------|
| RCP 2.6 (1.5°C) | 22.3 years | 2 projects | Routine monitoring |
| RCP 4.5 (2.4°C) | 19.1 years | 8 projects | Refinancing plans for 6 |
| RCP 8.5 (4.1°C) | 14.7 years | 18 projects | Major capex/asset replacement needed |

**Recommendation**: 
- Immediate: Accept RCP 4.5 as planning baseline (60% of climate models converge here)
- Debt structuring: Cap tenor at 13-14 years for infrastructure in high-climate-risk zones
- Capex budget: Allocate 2-3% of annual revenue for climate adaptation (earlier pavement overlays, etc.)

---

## 7. ESG & Sustainability Alignment

### 7.1 Environmental Assessment

InfraRisk AI provides:
- **Physical Climate Risk**: Asset-level RUL degradation (quantified)
- **Transition Risk**: Fossil fuel assets (thermal power) face stranding risk (separately scored)
- **Environmental Compliance**: Satellite monitoring detects permit violations (habitat loss, water discharge)

### 7.2 Social Assessment

- **Community Impact**: Toll road revenue as proxy for mobility access; reduced tolls → higher poverty alleviation
- **Labor Standards**: Operator track record flagged in counterparty assessment
- **Equity Distribution**: Sponsor credit rating reflects governance

### 7.3 Governance Assessment

- **Covenant Monitoring**: Step-in rights, audit requirements extracted and scored
- **Anti-Corruption**: Sponsor sanctions screening (external data feed)
- **Transparency**: Document classification flags "distressed terms" (sign of prior restructuring)

**ESG Score Integration** (Q3 2024):
- Combine PD + climate risk + ESG score for holistic rating
- Weight: 70% credit risk, 20% climate risk, 10% ESG
- Portfolio-level ESG reporting for LP disclosure

---

## 8. Competitive Advantages

### 8.1 Speed
- **Data Latency**: Daily updates vs. quarterly financials
- **Decision Latency**: Real-time alerts vs. annual review cycles
- **Action Latency**: Proactive covenant discussions vs. reactive restructuring

### 8.2 Accuracy
- **Backtested Gini**: 0.824 (vs. 0.42 for DSCR-only)
- **Satellite Coverage**: 500+ projects monitored; 90% of portfolio has monthly geospatial data
- **Climate Calibration**: LTPP-based (8,000+ pavement sections); IPCC AR6 scenarios

### 8.3 Completeness
- **Integration**: Combines 6 data modalities (financial, geospatial, macro, climate, contracts, sentiment)
- **Forward-Looking**: Future cash flows, climate scenarios, technological disruption
- **Systemic**: Portfolio-level contagion, not just project-level risk

---

## 9. Implementation Roadmap

### Phase 1: Foundation (Months 1-2)
- Deploy InfraRisk API in sandbox environment
- Ingest your 50-project portfolio data
- Validate climate risk assessments against your assumptions
- Train credit committee on platform

### Phase 2: Monitoring (Months 3-4)
- Enable daily risk monitoring
- Calibrate alert thresholds to your risk tolerance
- Use satellite data + TFT revenue forecasts for monthly portfolio review
- Integrate with existing credit systems

### Phase 3: Deal Screening (Months 5-6)
- Screen new originations through platform
- Use covenant extraction for faster doc review
- Require climate-adjusted RUL in credit committee memos

### Phase 4: Portfolio Optimization (Months 6+)
- Run stress tests (macro shock, sector crisis, contagion)
- Optimize debt structure using climate scenarios
- Rebalance toward climate-resilient assets
- Report ESG risk to LPs

---

## 10. Pricing & ROI

### 10.1 Typical Pricing (Annual)

| Size | Annual Fee | Per-Project | Comments |
|------|-----------|-----------|----------|
| 25 projects | $150k | $6k | Small fund tier |
| 50 projects | $280k | $5.6k | Standard tier |
| 100 projects | $450k | $4.5k | Large fund tier |
| 200+ projects | Custom | Custom | Enterprise pricing |

Includes: API access, daily monitoring, satellite imagery, climate scenarios, NLP document processing

### 10.2 ROI Model

**Base Case (50-project portfolio, $4.2B AUM)**:
- Subscription: $280k/year
- Avoided refinancing costs: $8M (lower repricing on 4 deals, 10bps savings)
- Improved debt sizing: $2M additional interest savings (better leverage)
- Reduced credit losses: $5M (early warning on 1 distressed project; structured earlier)
- **Total annual benefit**: $15M
- **ROI**: 54x

---

## 11. Frequently Asked Questions

**Q: How accurate is the climate-adjusted RUL?**  
A: MAE = 1.8 years on holdout pavement test sections. Uncertainty bands provided (5th-95th percentile). Use ranges for scenarios, not point estimates.

**Q: What if my portfolio is outside the modeled countries?**  
A: We support 135+ countries with transaction data. For new markets, we use regional transfer learning (e.g., India model applied to Bangladesh). Accuracy typically 10-15% lower until local data accumulated.

**Q: Can InfraRisk replace my credit committee?**  
A: No. InfraRisk is decision support. Credit committee should use PD scores + climate flags + contagion factors as inputs, but final credit decision remains human responsibility.

**Q: How long until I see value?**  
A: Quick wins: Week 1 (portfolio overview), Month 1 (early warnings on existing deals), Month 3 (integrated into deal screening).

**Q: What about data privacy?**  
A: All data encrypted at rest (AES-256) and in transit (TLS 1.3). Multi-tenant architecture isolates your portfolio from other investors. SOC 2 Type II certified.

---

## 12. Next Steps

1. **Schedule 30-min demo**: See live dashboard with sample portfolio
2. **Proof-of-concept**: Load your 50-project portfolio; validate climate risk on 5 assets
3. **Onboarding**: 2-week implementation; training for credit team
4. **Go-live**: Integrated monitoring in your credit workflow

**Contact**: sales@infrarisk.local | +1 (650) 555-0101

---

## 13. Conclusion

Infrastructure project finance is at an inflection point. Climate change, geopolitical volatility, and portfolio complexity demand better risk tools. InfraRisk AI combines satellite intelligence, climate physics, and machine learning to detect signals traditional models miss.

The result: smarter capital allocation, lower refinancing surprises, and climate-resilient portfolios.

**Join 50+ institutional investors already using InfraRisk AI to manage $85B+ in infrastructure assets.**
