# Contributing to InfraRisk AI

Thank you for your interest in contributing to InfraRisk AI! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/InfraRisk.git`
3. Create a virtual environment: `python -m venv venv`
4. Install development dependencies: `pip install -r requirements.txt`
5. Create a feature branch: `git checkout -b feature/your-feature-name`

## Development Workflow

### Code Style
- Follow PEP 8 conventions
- Use Black for code formatting: `black src/`
- Use isort for import sorting: `isort src/`
- Run flake8 for linting: `flake8 src/`

### Testing
- Write tests for all new features: `pytest tests/`
- Maintain test coverage > 80%: `pytest --cov=src tests/`
- Run pre-commit hooks: `pre-commit run --all-files`

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Refactor, etc.)
- Include the phase/component reference if applicable
- Example: `Add: Siamese CNN with anomaly detection head (Phase 3)`

### Pull Requests
1. Push your branch to your fork
2. Create a PR with clear description
3. Link related issues
4. Ensure all CI/CD checks pass
5. Request review from maintainers

## Code Review Process

- At least one approval required before merge
- Address all comments before final approval
- Ensure CI/CD pipeline passes
- Update documentation if necessary

## Reporting Issues

- Check existing issues first
- Provide clear description and reproduction steps
- Include relevant code snippets or logs
- Add labels (bug, enhancement, documentation, etc.)

## Questions?

Open an issue or contact the maintainers.

Thank you for contributing!
