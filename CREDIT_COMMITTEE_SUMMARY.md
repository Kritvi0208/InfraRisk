# InfraRisk AI: Credit Committee Summary for CRO/CFO

---

## 1. Executive Overview

InfraRisk AI is a quantitative risk management platform for infrastructure portfolios. It integrates satellite data, climate science, and machine learning to deliver forward-looking default probability (PD) estimates that improve capital allocation and covenant monitoring.

**For CFOs/CROs**: Enables systematic risk measurement, early warning capabilities, and stress testing beyond traditional debt coverage ratios.

---

## 2. Risk Metrics: From DSCR to PD

### 2.1 The Shift

**Traditional Approach**:
```
Risk Assessment = Debt Service Coverage Ratio (DSCR)
```
- Simple: (Operating Cash Flow / Annual Debt Service)
- Backward-looking: Based on historical 2-3 years
- Static: Updated quarterly/annually
- Limited signals: Ignores climate, geospatial, counterparty factors

**InfraRisk Approach**:
```
Default Probability = f(Financial, Geospatial, Macro, Climate, Portfolio Context)
```
- Comprehensive: 113 features across four modalities
- Forward-looking: 24-month revenue forecasts, climate scenarios
- Dynamic: Updated daily
- Holistic: Captures tail risks traditional models miss

### 2.2 Comparative Validation

**Historical Backtest** (850 projects, 2005-2015):

| Model | AUC-ROC | Gini | Precision @ 5% FPR | Recall @ 10% FNR |
|-------|---------|------|-------------------|-----------------|
| DSCR only | 0.615 | 0.42 | 32% | 45% |
| InfraRisk ML | 0.942 | 0.82 | 58% | 72% |
| **Improvement** | **+52%** | **+95%** | **+81%** | **+60%** |

**Interpretation**:
- Gini 0.82 = InfraRisk captures 82% of predictive power on binary default outcome
- Precision 58% = When InfraRisk flags "high risk" (top 10% PD), 58% of those actually defaulted
- Recall 72% = Of projects that actually defaulted, 72% were flagged in advance

### 2.3 PD Calibration: Aligned with Market Standards

**Basel III PD Buckets**:
- PD < 0.5%: Excellent
- 0.5% - 1.5%: Good
- 1.5% - 3%: Satisfactory
- 3% - 10%: Fair
- > 10%: Weak

**InfraRisk Portfolio** (47 projects):
- Excellent: 8% (4 projects)
- Good: 26% (12 projects)
- Satisfactory: 45% (21 projects)
- Fair: 18% (8 projects)
- Weak: 3% (1 project flagged for reduction)

**vs. Peer Benchmark**:
- Industry average: 28% in "Fair" or "Weak"
- Your portfolio (InfraRisk): 21% in Fair or Weak
- Conclusion: Slightly above-average portfolio quality

---

## 3. Debt Structure & Covenant Optimization

### 3.1 From DSCR Floors to Climate-Adjusted Stress Scenarios

**Traditional**: "Maintain minimum DSCR of 1.25x"
- Ignores revenue volatility, refinancing risk, climate scenarios

**InfraRisk**: Multi-dimensional covenant structure

```
Primary Covenant: DSCR >= 1.30x (quarterly average)
Stress Covenant: DSCR >= 1.15x (in 50% revenue shock scenario)
Climate Covenant: RUL_CA >= tenor + 2 years (asset outlives debt)
Contagion Covenant: Portfolio systemic PD <= 10%
```

### 3.2 Debt Sizing: Traditional vs. Climate-Adjusted

**Case Study: Toll Road, India**

| Metric | Traditional | Climate-Adjusted | Rationale |
|--------|-------------|-----------------|-----------|
| Base DSCR | 1.62x | 1.62x | Same cash flow base |
| Stress DSCR (50% shock) | 1.08x | 1.08x | Same |
| Climate-Adjusted RUL 2050 | Ignored | 16 years | RCP 4.5 scenario |
| Debt tenor | 18 years | 14 years | Shorter to match RUL |
| Senior debt capacity | $150M | $95M | Lower leverage |
| Refinancing risk | High (bullet maturity year 18, asset deteriorating) | Medium (maturity year 14, asset still viable) | Risk mitigation |

**Implication**: Climate-aware debt sizing reduces refinancing risk by 60%; total debt slightly lower but risk profile materially improved.

### 3.3 Reserve Accounts & Escrow

**Traditional**: Fixed reserve (e.g., 6 months debt service)

**InfraRisk Enhanced**:
- **Base Reserve**: 6 months debt service (standard)
- **Climate Buffer**: 2 additional months if RUL < tenor + 3 years (compensate for accelerated deterioration)
- **Contagion Reserve**: 1 month if project centrality > median (hub projects with counterparty risk)
- **Total**: 6-9 months depending on risk profile

**Example**: Hydroelectric project (Brazil)
- Standard reserve: 6 months = $7.2M
- Climate buffer: +2 months (RUL compressed by 20%) = +$2.4M
- Total: 8 months = $9.6M

**Benefit**: Higher buffer cushion protects lender during drought stress; reduces risk of covenant breach.

---

## 4. Risk Limits & Portfolio Concentration

### 4.1 Sector Concentration Limits

**Policy**: No single sector > 40% of portfolio

**Current Portfolio (47 projects, $4.2B)**:
- Power generation: 35% ✓
- Toll roads: 25% ✓
- Water utilities: 18% ✓
- Ports: 12% ✓
- Airports: 10% ✓

**Climate-Adjusted Risk**:
- Power generation heavily impacted by drought (avg RUL 2050: 18.1 years)
- Toll roads resilient to climate (RUL 2050: 20.3 years)
- **Recommendation**: Gradually shift from hydro to solar (1-2% rebalance/year)

### 4.2 Single-Counterparty Limits

**Policy**: No single sponsor/operator > 15% of portfolio exposure

**InfraRisk Findings**:
- Sponsor "ABC Infrastructure": 14% (3 projects)
  - Contagion factor: 1.08x (if one project fails, portfolio PD increases 80bps)
  - Recommendation: Monitor; acceptable at 14% but flag for reduction if sponsor credit deteriorates

### 4.3 Geographic Concentration

**Policy**: Single country < 40%

**Current**:
- India: 28% (good diversification)
- Brazil: 18%
- Mexico: 15%
- Other: 39%

**Climate Risk by Geography**:
- India: High precipitation volatility; 5 water projects flagged
- Brazil: Drought risk (hydroelectric); 3 hydro projects in high-risk zone
- Mexico: Stable; no material climate flags

**Recommendation**: Geographic diversification is adequate; focus on sector/asset-level diversification instead.

---

## 5. Early Warning System & Covenant Monitoring

### 5.1 Daily Alert Framework

**InfraRisk generates 3-5 actionable alerts/month** from 47-project portfolio

**Alert Severity Levels**:

| Level | PD Change | Revenue Change | Action | Response Time |
|-------|-----------|----------------|--------|----------------|
| High | +500bps month | -15% YoY | Proactive contact | Within 24 hours |
| Medium | +200bps month | -8% YoY | Review; escalate if recurring | Within 1 week |
| Low | +100bps month | -3% YoY | Monitor | Bi-weekly review |

### 5.2 Recent Alerts (Last 90 Days)

**Alert 1: Revenue Decline (India Toll Road)**
- Trigger: 12% YoY revenue decline; satellite NDBI showed -4% lane utilization
- Covenant Status: DSCR 1.32x vs. covenant floor 1.30x; breached
- Action Taken: Proactive covenant waiver discussion with lender; extension granted for 1 quarter
- Outcome: Lender confident in sponsor recovery plan; toll rate increase approved for Q2 2024

**Alert 2: Climate RUL Degradation (Brazil Hydroelectric)**
- Trigger: Drought stress indicator trending negative (NDMI anomaly -2σ); water availability forecast down 8%
- Impact: Projected generation down 15% in 2025 vs. base case; RUL shortened by 2 years
- Action Taken: Sponsor engaged for capex plan (spillway upgrade, enhanced storage); insurance review
- Outcome: Sponsor confirmed budgeted capex; insurance quote obtained (acceptable)

**Alert 3: Counterparty Risk (Colombian Port)**
- Trigger: Operator credit rating downgraded by rating agency; portfolio contagion factor increased to 1.15x
- Impact: Two co-located port projects affected; operational synergies at risk if operator fails
- Action Taken: Reviewed step-in rights in concession; confirmed lender can assume operations
- Outcome: Step-in feasible; acceptable risk but escalate monitoring

### 5.3 Covenant Triggers & Waiver Process

**Automated Covenant Monitoring**:

```
Daily: Compare actual DSCR vs. covenant floor
│
If breach detected:
├─ Alert CRO (email + SMS)
├─ Contact borrower for explanation
└─ If systemic (not temporary), escalate to credit committee
   └─ Decision: Waiver (1-2 quarter grace) or Restructuring
```

**Last 12 Months**: 2 DSCR breaches detected; 1 waived (temporary revenue shock); 1 restructured (permanent deterioration)

**vs. Historical**: Previously 3-4 breaches/year caught in annual/quarterly review; now 100% real-time detection

---

## 6. Stress Testing & Scenario Analysis

### 6.1 Standard Scenarios

**Scenario 1: Macro Recession (50% Revenue Shock)**
- Assumption: Global trade collapse; toll traffic down 50%, port throughput down 40%, power demand down 30%
- Portfolio Impact:
  - Baseline systemic PD: 3.2%
  - Stressed systemic PD: 12.8% (4x amplification)
  - Projects breaching DSCR < 1.15x: 5 (out of 47)
  - Expected loss (40% recovery rate): $420M

**Scenario 2: Currency Crisis (30% Devaluation)**
- Assumption: Local currency weakens 30% vs. USD (relevant for Mexico, Colombia)
- Impact:
  - Revenue (local) unaffected
  - Debt service (USD) increases 30% in local terms
  - DSCR decline: 15-25% depending on FX hedge ratio
  - Portfolio impact:
    - 3 projects with >50% unhedged exposure; DSCR stress to 1.20x
    - Manageable with existing hedging (60-70% average hedge ratio)

**Scenario 3: Climate Shock (Extreme Drought)**
- Assumption: Precipitation 30% below 20-year average for 2 consecutive years
- Impact:
  - Hydroelectric generation down 35%
  - Thermal power demand up (spot price +50%)
  - Port throughput down 20% (reduced agricultural exports)
  - Portfolio impact:
    - 8 projects affected; 3 breaching DSCR < 1.25x
    - Total revenue loss: $120M
    - Estimated loss (50% recovery): $60M

### 6.2 Reverse Stress Testing

**Question**: What shock would cause portfolio-level default?

**Finding**: Portfolio default requires ~85% revenue decline (extreme scenario; AEP: 0.1%)

**Trigger Scenarios**:
1. Global pandemic + 50% traffic/trade collapse (rare; 2-3 year intervals)
2. Sovereign debt crisis + currency crisis + inflation shock (emerging market tail risk)

**Mitigation**: Current portfolio adequately diversified; tail risk acceptable

---

## 7. Credit Risk Metrics Dashboard

### 7.1 Portfolio-Level KPIs

**Risk Metrics** (Updated Daily):
| KPI | Value | Target | Status |
|-----|-------|--------|--------|
| Weighted Avg PD | 3.1% | < 4.5% | Green ✓ |
| % Portfolio PD > 3% | 12% | < 20% | Green ✓ |
| Systemic PD | 4.8% | < 6% | Green ✓ |
| Avg DSCR | 1.52x | > 1.40x | Green ✓ |
| Projects breaching covenants | 0 | < 2 | Green ✓ |
| Climate-flagged projects | 8 | < 12 | Green ✓ |
| Counterparty concentration (top 3) | 38% | < 45% | Green ✓ |

**Trend Analysis** (Last 12 Months):
- Weighted avg PD: 2.9% → 3.1% (slight deterioration; driven by India toll road alert)
- Systemic PD: 4.2% → 4.8% (contagion amplification increasing; monitor)

### 7.2 Sector-Level View

| Sector | # Projects | Avg PD | Avg RUL 2050 | Alert Count | Status |
|--------|-----------|--------|-------------|-------------|--------|
| Power Gen | 16 | 2.8% | 18.1y | 2 (drought) | Caution |
| Toll Roads | 12 | 3.3% | 20.3y | 2 (traffic) | Caution |
| Water | 9 | 3.5% | 19.2y | 1 (capex) | Monitor |
| Ports | 6 | 2.9% | 22.1y | 0 | Stable |
| Airports | 4 | 3.0% | 21.5y | 0 | Stable |

**Recommendation**:
- Power generation: Gradual shift to solar (less climate vulnerable)
- Toll roads: Focus on urban highways (higher traffic resilience)
- Monitor capital expenditure across water utilities

---

## 8. Credit Losses & Recoveries

### 8.1 Expected Credit Loss (ECL) Model

**Basel III ECL Framework**:
```
ECL = PD × LGD × EAD
```

**Portfolio ECL** (47 projects):

| Metric | Value |
|--------|-------|
| Total portfolio value | $4.2B |
| Average PD | 3.1% |
| Average LGD (Loss Given Default) | 40% |
| Average EAD (Exposure at Default) | $89M |
| **Total ECL** | **$52M** |
| **ECL as % of portfolio** | **1.2%** |

**vs. Peer Benchmark**: Infrastructure portfolios typically 1.5-2.0% ECL
**Conclusion**: Your portfolio is 20-40% better-than-benchmark ECL

### 8.2 Recovery Rate Assumptions

**Infrastructure projects**: 40-60% recovery typical (vs. 35% for corporate)
- Senior debt: 50-70% recovery
- Mezzanine: 20-40% recovery
- Equity: 0-20% recovery

**Your Portfolio**:
- 92% senior debt; 7% mezzanine; 1% equity
- Blended recovery rate: 45% (moderate; conservative relative to peers at 50%)

**Stress Scenario**: Major portfolio shock (4x systemic amplification)
- Projected loss: $420M
- Recovery at 40%: $168M
- Net loss: $252M
- Impact on capital: <2% (acceptable)

---

## 9. Covenant Waiver Process & Governance

### 9.1 Automated Escalation

```
Daily covenant monitoring
│
DSCR < covenant floor for 2 consecutive months
│
├─ Tier 1: Portfolio manager contact borrower
│          (goal: identify issue, temporary vs. permanent)
│
├─ Tier 2: If unresolved after 2 weeks → escalate to CRO
│          (decision: waiver vs. restructuring)
│
└─ Tier 3: If material (>$50M exposure) → credit committee vote
           (formal waiver documentation + new covenant structure)
```

### 9.2 Waiver Criteria

**Automatic Waiver** (CRO discretion):
- Temporary shock (weather, macro event) with clear recovery plan
- Projected DSCR recovery within 1-2 quarters
- No indicator of sponsor credit deterioration
- **Example**: 1-month toll road revenue decline due to temporary construction; expected to recover in Q2

**Committee Review** (Credit Committee vote):
- Structural deterioration; DSCR decline persistent >3 months
- Sponsor credit rating downgrade
- Contagion risk to other portfolio projects
- **Example**: Port throughput trend down for 6 months due to trade shifts; waiver plus restructuring needed

---

## 10. Regulatory & Reporting

### 10.1 Stress Testing Compliance

**Required by Central Banks**: Annual Adverse Scenario (AAS) stress tests

**InfraRisk Enables**:
- Rapid scenario generation (50% revenue shock, currency, interest rate, climate)
- Granular project-level impact assessment
- Portfolio-level aggregation and risk measure (EL, EVaR, systemic contribution)

**Efficiency Gain**: 3-week process → 2-day process

### 10.2 ESG Risk Reporting

**For LP Disclosures**:
- Environmental risk: Climate RUL degradation, transition risk
- Social risk: Toll road revenue as proxy for mobility access
- Governance risk: Covenant monitoring, sponsor credit quality

**InfraRisk ESG Score** (Q3 2024):
- Portfolio weighted ESG: 6.2/10 (median for infrastructure)
- Improvement areas: Increase renewable (solar) exposure; reduce fossil fuel concentration

---

## 11. Pricing & Implementation

### 11.1 Cost Structure

**Annual Fee**: $280k (50-project portfolio)

**Included**:
- Daily risk monitoring & alerts
- Satellite imagery (500+ projects)
- Climate scenario analysis
- Covenant extraction (NLP)
- Monthly credit committee reports

**Additional Services** (Optional):
- Custom stress scenarios: $5k/scenario
- Training workshops: $10k/day
- API integration: $50k one-time

### 11.2 ROI Analysis

**Base Case**:
- Avoided refinancing costs (2 deals, 10bps savings): $4M/year
- Improved debt sizing (4 deals, extra $100M capacity): $2M/year
- Reduced credit losses (1 early detection): $5M one-time
- **Total annual benefit**: $11M
- **ROI**: 39x annual fee

---

## 12. Next Steps: Credit Committee

1. **Review**: InfraRisk PD scores for your current portfolio (30-min demo)
2. **Validate**: Cross-check vs. your existing credit decisions; assess calibration
3. **Pilot**: Load 5-10 deals from deal pipeline; use PD + climate flags for screening
4. **Integrate**: Incorporate climate-adjusted RUL + covenant extraction into credit memos (Q2 2024)
5. **Monitor**: Daily alerts feed into monthly credit committee package (Q3 2024)

**Expected Timeline**: 2-month implementation; payoff within 6 months

---

## Appendix A: Glossary

- **PD**: Probability of default over 1-year horizon (0-100%)
- **LGD**: Loss given default; % of exposure lost after recovery
- **EAD**: Exposure at default; principal outstanding at time of default
- **ECL**: Expected credit loss = PD × LGD × EAD
- **DSCR**: Debt service coverage ratio = operating CF / annual debt service
- **RUL**: Remaining useful life (years until end-of-life)
- **CA-RUL**: Climate-adjusted RUL incorporating temperature + precipitation stress
- **Contagion**: Portfolio-level risk amplification due to interconnected projects
- **Systemic PD**: Portfolio PD accounting for contagion (higher than sum of individual PDs)

---

## Appendix B: Model Validation

**Backtest Period**: 2005-2015 (850 projects, 32 defaults)

**Key Results**:
- AUC-ROC: 0.942 (excellent discrimination)
- Gini: 0.824 (captures 82% of predictive power)
- Calibration (Spearman rank correlation): 0.76 (good)
- Out-of-sample validation: 10-fold cross-validation; results consistent

**Stress Testing**:
- Holdout test set: 170 projects (20% of backtest)
- Gini: 0.81 (minimal overfitting)
- Conclusion: Model generalizes well to new data

---

**Document Prepared By**: InfraRisk AI Credit Analytics Team  
**Date**: January 2024  
**Confidentiality**: Internal Use Only
