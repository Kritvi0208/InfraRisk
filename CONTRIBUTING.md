# Contributing to InfraRisk AI

Thank you for your interest in contributing to InfraRisk AI! This guide provides everything you need to contribute effectively to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Code Style Guide](#code-style-guide)
5. [Branch Naming Conventions](#branch-naming-conventions)
6. [Making Changes](#making-changes)
7. [Pull Request Process](#pull-request-process)
8. [Testing Requirements](#testing-requirements)
9. [Documentation Standards](#documentation-standards)
10. [Commit Message Guidelines](#commit-message-guidelines)
11. [Review Process](#review-process)

---

## Code of Conduct

### Our Commitment

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background, experience level, or identity.

### Expected Behavior

- **Respectful Communication:** Treat all contributors with respect and kindness
- **Constructive Feedback:** Provide thoughtful, actionable feedback in code reviews
- **Inclusive Language:** Use inclusive language and respect diverse perspectives
- **Professional Conduct:** Maintain professional standards in all interactions

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting comments, or personal attacks
- Publishing private information without consent
- Other conduct inappropriate for a professional environment

### Reporting Issues

Report inappropriate behavior to: conduct@infrariskai.com

---

## Getting Started

### Prerequisites

- Python 3.9+
- Git 2.30+
- Docker 20.10+ (for containerized development)
- PostgreSQL 12+ (for database work)
- Familiarity with Git workflows

### First-Time Contributors

1. **Fork the Repository**
   ```bash
   # On GitHub, click "Fork" button
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/infrariskai.git
   cd infrariskai
   ```

3. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/official/infrariskai.git
   git remote -v  # Verify both origin and upstream
   ```

4. **Keep Fork Updated**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### Finding Issues to Work On

- **Good First Issues:** Labeled `good-first-issue` - suitable for newcomers
- **Help Wanted:** Labeled `help-wanted` - community contributions encouraged
- **Documentation:** Labeled `documentation` - help improve docs
- **Bug Fixes:** Labeled `bug` - fix reported issues

---

## Development Setup

### Local Development Environment

**Step 1: Create Virtual Environment**
```bash
python3 -m venv infrariskai-dev
source infrariskai-dev/bin/activate  # On Linux/macOS
# Or on Windows:
infrariskai-dev\Scripts\activate
```

**Step 2: Install Dependencies**
```bash
pip install -r requirements_ml.txt
pip install -r requirements_nlp.txt
pip install -r requirements_phase2.txt

# Development dependencies
pip install -r requirements-dev.txt  # pytest, black, flake8, mypy, etc.
```

**Step 3: Setup Pre-commit Hooks**
```bash
pip install pre-commit
pre-commit install
```

**Step 4: Initialize Database**
```bash
# Start services
docker-compose up -d postgres redis

# Run migrations
python -m alembic upgrade head

# Load test data
python scripts/load_test_data.py
```

**Step 5: Verify Setup**
```bash
# Run tests
pytest tests/ -v

# Run linters
flake8 src/
black --check src/
mypy src/
```

### Docker Development

**Build Development Container**
```bash
docker build -t infrariskai-dev:latest -f Dockerfile.dev .
```

**Run Development Container**
```bash
docker run -it --rm \
  -v $(pwd):/workspace \
  -p 8000:8000 \
  -p 8501:8501 \
  infrariskai-dev:latest
```

---

## Code Style Guide

### Python Style

**Follow PEP 8 with These Standards:**

**Imports**
```python
# Standard library imports first
import os
import sys
from typing import List, Optional

# Third-party imports
import numpy as np
import pandas as pd
from tensorflow import keras

# Local imports
from src.models import RiskModel
from src.utils import process_data
```

**Naming Conventions**
```python
# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_BATCH_SIZE = 32

# Functions/Variables: lower_snake_case
def calculate_risk_score(project_data):
    result = process_features(project_data)
    return result

# Classes: PascalCase
class RiskAssessmentModel:
    pass

# Private methods: _leading_underscore
def _validate_input(data):
    pass
```

**Type Hints**
```python
from typing import List, Dict, Tuple, Optional

def predict_risk(
    project_data: Dict[str, float],
    confidence_threshold: float = 0.5
) -> Tuple[float, List[str]]:
    """
    Predict risk for a project.
    
    Args:
        project_data: Project features dictionary
        confidence_threshold: Minimum confidence for prediction
        
    Returns:
        Tuple of (risk_score, risk_factors)
    """
    risk_score = 0.75
    risk_factors = ["structural_age", "maintenance_required"]
    return risk_score, risk_factors
```

**Docstrings**
```python
def analyze_contract(
    contract_text: str,
    risk_threshold: float = 0.7
) -> Dict[str, any]:
    """
    Analyze contract for risk factors using NLP.
    
    Args:
        contract_text: Raw contract text to analyze
        risk_threshold: Score threshold above which factors are flagged
        
    Returns:
        Dictionary containing:
        - risk_score: Float between 0 and 1
        - risk_factors: List of identified risk factors
        - confidence: Confidence in the assessment
        - extracted_entities: Named entities from contract
        
    Raises:
        ValueError: If contract_text is empty
        ProcessingError: If NLP analysis fails
        
    Example:
        >>> result = analyze_contract(contract_text)
        >>> print(result['risk_score'])
        0.65
    """
    pass
```

**Line Length**
```python
# Maximum 100 characters per line
# If line exceeds, break into multiple lines

# Good: Multiple lines
query = (
    "SELECT project_id, risk_score "
    "FROM projects "
    "WHERE created_at > %s "
    "AND risk_score > %s"
)

# Avoid: Line too long
query = "SELECT project_id, risk_score FROM projects WHERE created_at > %s AND risk_score > %s"
```

### Format with Black

```bash
# Format all Python files
black src/ tests/

# Check formatting without changing
black --check src/

# Format with specific line length
black --line-length 100 src/
```

### Linting with Flake8

```bash
# Check code style
flake8 src/ --max-line-length=100

# Ignore specific warnings
flake8 src/ --ignore=E203,W503
```

### Type Checking with Mypy

```bash
# Type check Python files
mypy src/

# Check with strict mode
mypy --strict src/
```

---

## Branch Naming Conventions

**Branch Format:**
```
{type}/{issue-number}/{description}
```

### Types

| Type | Purpose | Example |
|------|---------|---------|
| `feature` | New feature | `feature/123/add-risk-scoring` |
| `bugfix` | Bug fix | `bugfix/456/fix-model-loading` |
| `hotfix` | Critical production fix | `hotfix/789/fix-db-connection` |
| `docs` | Documentation | `docs/update-api-reference` |
| `refactor` | Code refactoring | `refactor/improve-performance` |
| `test` | Testing improvements | `test/increase-coverage` |
| `chore` | Maintenance tasks | `chore/update-dependencies` |

### Examples

```bash
# Good branch names
git checkout -b feature/123/add-ensemble-model
git checkout -b bugfix/456/fix-memory-leak
git checkout -b docs/update-installation-guide

# Avoid these patterns
git checkout -b my_feature         # No issue number
git checkout -b 123                # No description
git checkout -b update_stuff       # Too vague
```

---

## Making Changes

### Before Starting

1. **Sync with upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Create feature branch:**
   ```bash
   git checkout -b feature/123/descriptive-name
   ```

3. **Keep commits atomic:** Each commit should represent one logical change

### During Development

**Commit Frequently:**
```bash
# Make small, focused commits
git add src/models/risk_model.py
git commit -m "feat: improve risk model inference speed"

git add tests/test_risk_model.py
git commit -m "test: add performance benchmarks for risk model"
```

**Keep Code Clean:**
```bash
# Run formatters before commit
black src/
flake8 src/
mypy src/

# Run tests
pytest tests/ -v
```

**Create Descriptive Commit Messages:**
```bash
git commit -m "feat: add risk factor feature importance calculation

- Implemented SHAP-based feature importance
- Added visualization component
- Updated API endpoint to include importance scores
- Tested with 10K projects (5ms overhead)"
```

---

## Pull Request Process

### Before Submitting PR

1. **Ensure branch is up to date:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   git push --force-with-lease origin feature/123/your-feature
   ```

2. **Run full test suite:**
   ```bash
   pytest tests/ -v --cov=src/ --cov-report=html
   ```

3. **Check code quality:**
   ```bash
   black --check src/
   flake8 src/
   mypy src/
   ```

4. **Update documentation:**
   - Add docstrings for new functions
   - Update relevant markdown files
   - Update API documentation if applicable

### Creating Pull Request

**PR Title Format:**
```
{type}({scope}): {description}

feature(models): add ensemble stacking support
bugfix(api): fix rate limiting bug in predict endpoint
docs(installation): update database setup instructions
```

**PR Description Template:**
```markdown
## Description
Brief description of changes.

## Related Issue
Closes #123

## Type of Change
- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Implemented feature X
- Fixed bug Y
- Added test case Z

## Testing
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual testing completed
- [x] Edge cases tested

## Performance Impact
- Model inference: -5% latency
- Database queries: -10% time
- Memory usage: +2% (acceptable)

## Checklist
- [x] Code follows style guidelines
- [x] Comments added for complex logic
- [x] Documentation updated
- [x] Tests added/updated
- [x] No new warnings introduced
```

### PR Guidelines

**Size:**
- Keep PRs focused on single feature/fix
- Aim for <400 lines changed
- Large refactors: break into multiple PRs

**Reviewability:**
- Make logical commits that are easy to review
- Avoid mixing style changes with logic
- Use clear commit messages

**Testing:**
- Include unit tests for new code
- Update integration tests as needed
- Test edge cases and error conditions

---

## Testing Requirements

### Unit Tests

**Test File Structure:**
```
tests/
├── test_models/
│   ├── test_risk_model.py
│   ├── test_ensemble_model.py
│   └── test_nlp_models.py
├── test_api/
│   ├── test_endpoints.py
│   └── test_authentication.py
├── test_features/
│   ├── test_feature_extraction.py
│   └── test_feature_engineering.py
└── conftest.py  # Shared fixtures
```

**Test Example:**
```python
import pytest
from src.models import RiskModel
from src.utils import load_test_data

@pytest.fixture
def risk_model():
    return RiskModel(weights_path="models/risk_model.h5")

@pytest.fixture
def test_data():
    return load_test_data("tests/data/sample_projects.json")

def test_risk_model_prediction(risk_model, test_data):
    """Test risk model produces valid predictions."""
    result = risk_model.predict(test_data[0])
    
    assert isinstance(result, dict)
    assert "risk_score" in result
    assert 0 <= result["risk_score"] <= 1
    assert result["risk_score"] > 0.3  # Reasonable threshold

def test_risk_model_handles_invalid_input(risk_model):
    """Test risk model handles invalid input gracefully."""
    with pytest.raises(ValueError):
        risk_model.predict({})

def test_risk_model_batch_prediction(risk_model, test_data):
    """Test batch prediction matches single predictions."""
    single_results = [risk_model.predict(item) for item in test_data]
    batch_results = risk_model.predict_batch(test_data)
    
    assert len(single_results) == len(batch_results)
    for single, batch in zip(single_results, batch_results):
        assert single["risk_score"] == batch["risk_score"]
```

**Running Tests:**
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models/test_risk_model.py -v

# Run with coverage
pytest tests/ --cov=src/ --cov-report=html

# Run only fast tests
pytest tests/ -m "not slow"

# Run in parallel
pytest tests/ -n 4
```

### Minimum Coverage Requirements

- **New code:** 80% coverage
- **Modified code:** Maintain or improve coverage
- **Critical paths:** 95%+ coverage
- **Tests themselves:** Not counted in coverage

### Integration Tests

```python
def test_end_to_end_prediction_pipeline(client, test_db):
    """Test complete prediction pipeline."""
    # 1. Upload project
    response = client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "data": {...}}
    )
    project_id = response.json()["id"]
    
    # 2. Trigger prediction
    response = client.post(f"/api/v1/projects/{project_id}/predict")
    assert response.status_code == 200
    
    # 3. Retrieve results
    response = client.get(f"/api/v1/projects/{project_id}/risk")
    result = response.json()
    
    assert "risk_score" in result
    assert result["risk_score"] > 0
    
    # 4. Verify database state
    from src.database import Session
    project = Session.query(Project).filter_by(id=project_id).first()
    assert project.risk_score == result["risk_score"]
```

---

## Documentation Standards

### Code Documentation

**Module Docstrings:**
```python
"""
Risk assessment module for infrastructure projects.

This module provides functionality for calculating comprehensive
risk assessments for infrastructure projects using multiple data
sources and machine learning models.

Key Components:
- RiskAssessmentModel: Main model class
- FeatureExtractor: Feature engineering
- RiskCalculator: Risk aggregation

Example:
    >>> from src.models import RiskAssessmentModel
    >>> model = RiskAssessmentModel()
    >>> risk_score = model.predict(project_data)
"""
```

**Function Docstrings:**
```python
def calculate_portfolio_risk(
    projects: List[Dict],
    weights: Optional[Dict[str, float]] = None,
    include_correlation: bool = True
) -> Dict[str, float]:
    """
    Calculate aggregated risk for a project portfolio.
    
    Implements Markowitz portfolio theory to calculate
    portfolio-level risk accounting for project correlations.
    
    Args:
        projects: List of project data dictionaries
        weights: Optional portfolio weights. If None, equal-weighted.
        include_correlation: Whether to account for correlations
        
    Returns:
        Dictionary containing:
        - portfolio_risk: Weighted portfolio risk score
        - diversification_benefit: Risk reduction from diversification
        - concentration: Portfolio concentration metric
        - correlation_matrix: Pairwise project correlations
        
    Raises:
        ValueError: If projects list is empty or weights don't sum to 1
        
    Note:
        - Requires all projects have valid risk scores
        - Correlation calculation requires 2+ projects
        - Computation time: O(n²) where n is number of projects
        
    Example:
        >>> projects = [
        ...     {"id": 1, "risk_score": 0.6},
        ...     {"id": 2, "risk_score": 0.5}
        ... ]
        >>> result = calculate_portfolio_risk(projects)
        >>> print(result["portfolio_risk"])
        0.52
    """
    pass
```

### README Files

**Project-Level README:**
- Project description and purpose
- Key features
- Quick start guide
- Important architecture decisions
- Links to detailed documentation

**Module README (if needed):**
```markdown
# Module Name

Brief description.

## Key Components

- Component 1: Description
- Component 2: Description

## Usage

```python
from src.module import Component
component = Component()
```

## Performance Considerations

- Note 1
- Note 2
```

---

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code refactoring without feature changes
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, etc.

### Scope

Component affected: `models`, `api`, `database`, `nlp`, `ui`, etc.

### Subject Line

- Use imperative mood ("add" not "added")
- Don't capitalize first letter
- No period at end
- Limit to 50 characters

### Body

- Explain what and why, not how
- Wrap at 72 characters
- Separate from subject with blank line
- List related issues

### Footer

```
Fixes #123
Related-to #456
Breaking-change: description of breaking change
```

### Examples

```
feat(models): add ensemble stacking for risk prediction

Implement stacking metamodel that combines 5 base models
to improve risk prediction accuracy. Stack uses logistic
regression as metamodel.

- Added StackingModel class
- Integrated into prediction pipeline
- Added cross-validation for stack weights

Fixes #123
Related-to #456

feat(api): implement pagination for project listing

Add offset/limit pagination parameters to
GET /api/v1/projects endpoint.

- Default limit: 50 projects
- Maximum limit: 1000 projects
- Returns total count in response

fix(nlp): handle edge case in contract parsing

Fix null pointer exception when parsing contracts
with empty clause sections. Add validation for
empty elements before processing.

Fixes #789

refactor(database): simplify query builder

Extract common query patterns into helper methods
for better readability and maintainability.

Performance impact: None (refactoring only)
```

---

## Review Process

### Code Review Workflow

1. **Automated Checks** (GitHub Actions)
   - Unit tests pass (pytest)
   - Code style check (flake8, black)
   - Type checking (mypy)
   - Coverage thresholds met (>80%)
   - No security issues (bandit)

2. **Human Review** (1-2 reviewers)
   - Code quality and design
   - Testing adequacy
   - Documentation completeness
   - Performance considerations
   - Security concerns

3. **Approval & Merge**
   - 2 approvals required
   - All checks must pass
   - Commits must be rebased
   - Merge via "Squash and Merge"

### What Reviewers Look For

**Code Quality:**
- Follows style guide
- Appropriate abstractions
- No code duplication
- Proper error handling

**Testing:**
- Unit tests for all new code
- Edge cases covered
- Test coverage > 80%
- Integration tests for features

**Documentation:**
- Docstrings present
- Comments for complex logic
- README updated if needed
- API docs updated

**Performance:**
- No obvious inefficiencies
- Appropriate algorithms
- Benchmarks for critical paths
- Regression not introduced

**Security:**
- No hardcoded credentials
- Input validation present
- SQL injection prevention
- Authentication checks

### Providing Feedback

**Do:**
```
This is great work! A few suggestions:

- Consider using a list comprehension here for clarity
- Have you thought about performance with large datasets?
- This logic might be easier to follow if split into helper functions
```

**Avoid:**
```
This code is bad. Rewrite it.
You're doing it wrong.
This is inefficient.
```

---

## Getting Help

### Resources

- **Documentation:** See [docs/](docs/) directory
- **Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Reference:** See [API_REFERENCE.md](API_REFERENCE.md)
- **Issues:** Browse [GitHub Issues](issues/)
- **Discussions:** See [GitHub Discussions](discussions/)

### Communication Channels

- **Slack:** #infrariskai-dev (for development discussions)
- **Email:** dev@infrariskai.com
- **Standup:** Weekly on Tuesdays at 10:00 AM (UTC)

### Debugging Help

When asking for help:
1. Describe what you're trying to do
2. Show the error message
3. Provide minimal reproducible example
4. Share relevant code snippets
5. Include environment info (Python, OS, etc.)

---

## Contributor Recognition

We value all contributions! Contributors are recognized through:

- **Changelog:** Listed in release notes
- **Contributors Page:** Featured on project website
- **README:** Added to contributor list
- **Badges:** Special badges for significant contributions

---

**Thank you for contributing to InfraRisk AI!**

For questions about contributing, please open an issue or ask in discussions.

---

**Last Updated:** 2024  
**Version:** 1.0.0  
**Maintained By:** Engineering Team
