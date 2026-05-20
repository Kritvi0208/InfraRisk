# InfraRisk AI - Credit Memo 1

## Executive Summary

This memo outlines the infrastructure project risk assessment framework implemented in InfraRisk AI.

## Scope

The system assesses risks across:
- **Geospatial factors**: Location, climate, natural disasters
- **Structural factors**: Design, materials, engineering risk
- **Financial factors**: DSCR, leverage, debt structure
- **Macroeconomic factors**: Interest rates, inflation, FX
- **Portfolio factors**: Concentration, contagion, systemic risk

## Key Metrics

1. **DSCR (Debt Service Coverage Ratio)**
   - Minimum: 1.25x
   - Calculation: EBITDA / Debt Service

2. **Probability of Default (PD)**
   - Range: 0-100%
   - Hard rejection threshold: 8%

3. **Leverage**
   - Calculation: Debt / (Debt + Equity)
   - Maximum: 75%

4. **HHI (Herfindahl-Hirschman Index)**
   - Measures concentration
   - Threshold: 0.35

## Risk Scoring

Clause-level risk scoring (1-5 scale):
- 5: Deal-blocking
- 4: Highly restrictive
- 3: Standard
- 2: Favorable
- 1: Highly favorable

Project aggregation uses weighted average by clause category.

## Recommendations

System generates actionable recommendations based on:
- Covenant violations
- Concentration risks
- Refinancing pressures
- Default probabilities

## Validation

- 12-scenario stress testing
- 10,000-sample Monte Carlo simulation
- Covenant threshold verification
- Benchmarking against 1,000+ comparable deals