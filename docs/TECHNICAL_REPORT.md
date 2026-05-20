# Technical Report: InfraRisk AI Platform

**Date:** 2026-05-20  
**Version:** Submission Draft  
**Repository:** InfraRisk

## 1. Executive Summary

InfraRisk AI is an infrastructure project finance platform that combines data ingestion, financial analytics, engineering risk scoring, contract review, and portfolio simulation. The repository now reflects a more honest implementation boundary: several core data loaders and backend services are fully wired, while some advanced model families remain prototype-level or rely on controlled synthetic fallbacks until the final live-data integrations are completed.

The current submission focus is not to overstate completeness. Instead, the goal is to provide a credible, auditable codebase with:

- real-data loaders for infrastructure and macroeconomic sources,
- a deployable FastAPI backend,
- a dockerized deployment path,
- Streamlit-based visualization support,
- test coverage for the data-loading layer,
- documentation that separates live components from simulated ones.

## 2. System Boundary and Implementation Status

| Component | Status | Evidence in Repo | Notes |
|---|---|---|---|
| Real data ingestion | Implemented | `src/data/real_data_loader.py` | Loads PPI, WDI, CDS, and NBI CSVs from `data/raw/` or `INFRARISK_DATA_PATH`. |
| API backend | Implemented | `src/api/backend.py` | FastAPI service with project, portfolio, contract, and simulation endpoints. |
| Docker deployment | Implemented | `Dockerfile`, `docker-compose.yml` | Secure environment-variable based deployment path. |
| Data validation tests | Implemented | `tests/test_real_data.py` | Covers loading success and empty-source fallback behavior. |
| Documentation site | Implemented | `mkdocs.yml`, `docs/README.md`, `docs/api.md` | Buildable MkDocs docs tree. |
| Advanced ML models | Partial / prototype | `src/models/`, `src/features/` | Present in repository but not all are production-calibrated on live data yet. |
| Satellite pipeline | Partial | Data loaders and dashboard hooks exist | Requires final live Sentinel-2 / Earth Engine wiring for every project site. |
| Feature store | Partial | In-repo feature modules exist | Not yet a fully governed Feast deployment in this submission. |
| SHAP explainability | Partial | `src/models/shap_interpreter.py` | Hooks are present; productionized reporting still needs final integration. |
| Gamified simulation | Partial | `src/simulation/`, `p5_*` modules | Simulation scaffolding exists; final game-flow tuning can continue after submission. |

## 3. Data Architecture and Provenance

The repository distinguishes between data that is loaded from actual files and data that is generated or approximated for scenario analysis.

### 3.1 Real data sources

The primary real-data sources already supported by the repo are:

- World Bank PPI project data for infrastructure project attributes.
- World Bank WDI macroeconomic indicators for GDP growth, inflation, debt burden, and related country metrics.
- Sovereign CDS spread data for credit risk and macro stress calibration.
- National Bridge Inventory data for physical-asset condition and degradation use cases.

These sources are consumed through the real-data loader layer and can be validated locally through the test suite.

### 3.2 Controlled synthetic and fallback data

Some modules still use synthetic or fallback logic by design:

- stress scenario generation,
- some portfolio simulation outputs,
- certain model wrappers where a full trained production model is not yet pinned to a live data pipeline,
- dashboard demo values where a source file is absent.

This is not a defect in itself; it is a normal boundary for a staged submission. What matters is that the repo now makes the distinction explicit instead of implying everything is already production-grade.

### 3.3 Data quality approach

The data layer follows four rules:

1. Prefer real files when available.
2. Return empty frames rather than crashing when a source is missing.
3. Preserve schema expectations in tests.
4. Keep the data path configurable through `INFRARISK_DATA_PATH`.

That approach reduces CI fragility and makes local review easier.

## 4. Financial and Engineering Feature Layer

InfraRisk’s analytical value comes from combining project finance metrics with engineering risk proxies.

### 4.1 Core finance metrics

The main metrics used throughout the repo are:

- DSCR: debt service coverage ratio,
- LLCR: loan life coverage ratio,
- PLCR: project life coverage ratio,
- leverage ratio,
- portfolio-level average PD,
- contract risk score,
- covenant breach flags.

A simplified relationship is:

```text
DSCR = Operating Cash Flow / Debt Service
LLCR = NPV(Cash Flow over remaining loan life) / Outstanding Debt
PLCR = NPV(Cash Flow over project life) / Outstanding Debt
```

These metrics are important because they are familiar to lenders, sponsors, and DFIs, and they map cleanly to portfolio-risk review.

### 4.2 Engineering and climate features

The repo’s engineering feature set includes:

- asset condition scoring,
- bridge fatigue and pavement degradation proxies,
- construction delay indicators,
- climate-adjusted remaining useful life logic,
- geospatial and location-risk hooks.

A typical climate-adjusted useful-life formulation used in the project family is:

```text
RUL_CA = RUL_0 × (1 - k_t × ΔT) × (1 - k_p × |ΔP|)
```

where temperature and precipitation shifts reduce expected useful life relative to a baseline.

## 5. Model and Simulation Stack

The repository contains a broad model stack intended to support project finance decisioning.

### 5.1 Model families

The codebase includes or references:

- Siamese CNN change detection for satellite progress,
- Temporal Fusion Transformer style forecasting,
- Physics-informed degradation models,
- Graph-based portfolio contagion analysis,
- ensemble and Monte Carlo stress testing,
- SHAP-based explainability.

### 5.2 Current status of the stack

The important distinction is that the repository currently mixes three types of artifacts:

- working implementation code,
- prototype wrappers with realistic interfaces,
- simulated outputs used to keep the dashboard and demo workflows operational.

That mix is acceptable for a staged release, but it should be described accurately. The repo is strongest where the input data is real and the calculations are deterministic. It is weakest where it still depends on fully trained live models that have not been pinned to a production data pipeline.

### 5.3 Simulation and scenario engine

The simulation layer is useful for submission because it demonstrates the workflow from input to risk response. It supports stress scenarios, portfolio propagation, and counterfactual decisioning. For the current release, the objective is to show the control flow, the scoring logic, and the output structure, while explicitly noting where final calibration is still pending.

## 6. Backend, Dashboard, and Deployment

### 6.1 FastAPI backend

The FastAPI backend exposes core endpoints for project prediction, portfolio metrics, contract analysis, and simulation. It is small enough to deploy cleanly, which makes it a good submission anchor even while some advanced model layers continue evolving.

### 6.2 Streamlit dashboard

The dashboard layer is designed to help reviewers see the platform’s outputs quickly. It is now better aligned with the real data layer because the loaders return empty frames safely, the portfolio path is resilient to missing data, and the UI can distinguish between loaded and unloaded sources.

### 6.3 Docker and compose

The deployment story now uses a buildable Docker image and a compose file that reads configuration from environment variables instead of hardcoding credentials. That is critical for two reasons:

1. it avoids leaking secrets in the repository,
2. it improves reproducibility for reviewers and future maintainers.

## 7. Testing and Validation

The test suite now includes focused coverage for the real-data loader layer:

- loading a minimal PPI CSV,
- loading macro data,
- loading CDS spreads,
- loading NBI bridge data,
- verifying that all sources are returned together,
- verifying empty-frame fallback when files are missing.

That test pattern is intentional. It checks the loader contract without requiring huge external datasets in CI.

The CI workflow also builds the MkDocs documentation site so that the docs layer is part of the submission quality gate rather than a standalone markdown folder.

## 8. Security and Governance

The repo now avoids hardcoded deployment credentials in the compose file. Instead, secrets and environment-specific values are expected to come from `.env` based configuration, with `.env.example` providing safe placeholders.

That makes the submission easier to review and safer to run locally.

## 9. Current Limitations and Remaining Work

The remaining work is real, but it is now clearly bounded.

### 9.1 Data integration gaps

- Not every satellite or remote-sensing path is fully wired to a live Earth Engine deployment.
- Some advanced source directories still expect future data governance work.
- A formal feature-store deployment is still a natural next step.

### 9.2 Model calibration gaps

- Several advanced model families still need end-to-end retraining on the final chosen data snapshots.
- Some simulation outputs remain controlled approximations rather than fully calibrated production predictions.
- Explainability outputs should be expanded into a more polished report view for final banking review.

### 9.3 Productization gaps

- Final ownership transfer and submission packaging still need the repository’s release branch process.
- A polished PDF export of the technical report can be generated from the Markdown source if the submission requires it.

## 10. Conclusion

This version of InfraRisk is materially stronger than a mock demo because it contains genuine real-data ingestion, a runnable backend, a secure deployment pattern, testable data contracts, and buildable documentation.

It is also more credible because the documentation now states what is real, what is synthetic, and what still needs calibration. That honesty is valuable in a financial-risk submission: a reviewer is more likely to trust a system that clearly marks its boundaries than one that overclaims completeness.

The repo is now in a better state for submission, review, and follow-on development.

## References

1. World Bank. Project Preparation and PPP / PPI databases.
2. World Bank. World Development Indicators (WDI).
3. World Bank / market data sources for sovereign credit spreads and macro risk signals.
4. Federal Highway Administration. National Bridge Inventory documentation.
5. Copernicus Programme. Sentinel-2 mission and product guide.
6. IPCC. Climate Change 2021: The Physical Science Basis.
7. AASHTO. Pavement design and performance guide references.
8. Paris, P. C. (1963). The fracture mechanics approach to fatigue crack growth.
9. Vaswani, A., et al. (2017). Attention Is All You Need.
10. Lim, B., et al. (2021). Temporal Fusion Transformers for interpretable multi-horizon forecasting.
11. Kipf, T. N., & Welling, M. (2017). Semi-Supervised Classification with Graph Convolutional Networks.
12. Goodfellow, I., Bengio, Y., & Courville, A. Deep Learning.
13. Lundberg, S. M., & Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions.
14. Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why Should I Trust You?" Explaining the Predictions of Any Classifier.
15. Breiman, L. (2001). Random Forests.
16. Sculley, D., et al. (2015). Hidden Technical Debt in Machine Learning Systems.
17. Project Finance International. Market and transaction benchmarks.
18. International Finance Corporation. Project finance and environmental/social performance standards.
19. FastAPI documentation.
20. Docker documentation for containerized deployment.
21. MkDocs documentation for static documentation sites.
22. MLflow documentation for experiment tracking and model registry.
