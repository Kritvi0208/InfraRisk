# InfraRisk

InfraRisk is an AI-native infrastructure project finance platform for **DFIs, commercial banks, and infrastructure funds**.

## Project 1C: Data Scientist InfraRisk AI

InfraRisk delivers a unified system across:

- **Geospatial intelligence** for site, climate, logistics, and hazard exposure
- **Macroeconomic modelling** for inflation, rates, FX, growth, commodity, and sovereign stress
- **Construction engineering analytics** for schedule slippage, cost overrun, contractor performance, and technical risk
- **Financial risk quantification** for debt service resilience, covenant pressure, refinancing, and expected credit loss

The platform produces:

- **Bankable credit risk assessments** (PD/LGD/ECL views with transparent drivers)
- **Optimised debt structuring recommendations** (tenor, grace, amortisation, DSCR covenants, hedging)
- **Portfolio-level stress testing** across sectors, countries, and funding structures

---

## InfraRisk Lab (Gamified Simulation)

InfraRisk Lab is a simulation environment where learners manage a live portfolio of deals in:

- Transportation
- Energy
- Social infrastructure
- Telecommunications

### Core simulation loop

1. Build and allocate a multi-sector project pipeline
2. Structure debt and equity for each deal
3. Advance through time periods (development → construction → operations)
4. Respond to event cards and market shocks:
   - Construction delays and cost escalation
   - Sovereign risk and policy shocks
   - Revenue shortfalls and demand weakness
   - Refinancing crises and liquidity squeezes
5. Rebalance portfolio and re-optimise debt structures
6. Review risk, returns, and development impact outcomes

### Learning and decision objectives

- Keep projects bankable under uncertainty
- Protect covenant headroom and refinancing capacity
- Balance risk-adjusted return with resilience and impact
- Understand how technical, macro, and sovereign dynamics propagate into credit outcomes

---

## Unified AI Architecture

### 1) Data & Intelligence Layer

- Geospatial datasets: hazard maps, terrain, logistics corridors, climate scenarios
- Macroeconomic datasets: CPI, policy rates, FX, sovereign spreads, GDP, commodity prices
- Engineering datasets: schedules, EPC milestones, claims history, productivity metrics
- Financial datasets: term sheets, cash-flow assumptions, debt profiles, historical defaults

### 2) Domain Engines

- **GeoRisk Engine**: computes location risk factors and physical disruption probabilities
- **Macro Engine**: generates baseline and stressed macro paths with country-specific regimes
- **Engineering Risk Engine**: predicts delay/overrun distributions and completion risk
- **Credit Engine**: converts project economics into PD/LGD/ECL and internal rating signals

### 3) Optimisation & Decision Layer

- Debt structuring optimiser (tenor, pricing, grace, sculpting, reserve sizing)
- Hedging recommender (rate/FX risk mitigation under scenario constraints)
- Portfolio allocator balancing concentration, risk budget, and expected return

### 4) Simulation & Game Layer (InfraRisk Lab)

- Scenario/event generator and time-step simulator
- Player actions: approve, restructure, hedge, refinance, divest, inject equity
- Scoring: solvency, portfolio resilience, impact, and risk-adjusted performance

### 5) Reporting Layer

- Investment-committee credit memos
- Covenant and liquidity dashboards
- Portfolio stress-test heatmaps and tail-risk summaries

---

## Analytics Outputs

For each deal and each portfolio period, InfraRisk should generate:

- Credit grade with explainable risk drivers
- Construction risk score and completion confidence interval
- Base and stressed DSCR/LLCR trajectories
- Refinancing risk score and debt maturity wall exposure
- Recommended debt structure adjustments
- Portfolio concentration, contagion, and capital-at-risk metrics

---

## Sector Coverage

The default taxonomy for deals includes:

- **Transportation**: roads, rail, ports, airports, metro
- **Energy**: generation, transmission, storage, distributed systems
- **Social infrastructure**: hospitals, schools, water/waste, municipal assets
- **Telecommunications**: fiber, towers, data infrastructure, connectivity backbones

---

## Risk Events Included by Design

InfraRisk Lab explicitly models:

- Construction delays and contractor underperformance
- Sovereign downgrade, convertibility, and policy reversal risk
- Revenue volatility and offtake/demand underperformance
- Refinancing lockouts and spread-widening crises

---

## Target Users

- Development Finance Institutions (DFIs)
- Commercial project finance banks
- Infrastructure debt/equity fund managers

This repository currently defines the core product specification and operating blueprint for implementing the full InfraRisk AI platform.
