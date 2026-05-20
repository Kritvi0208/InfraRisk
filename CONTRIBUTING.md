# Contributing to InfraRisk AI

## Code Style

- Python: PEP 8
- Type hints required
- Docstrings for all functions
- Max line length: 100 characters

## Development Setup

```bash
python3 -m venv infrariskai-dev
source infrariskai-dev/bin/activate
pip install -r requirements-app.txt
pip install -r requirements_ml.txt
pip install -r requirements_nlp.txt
pip install pytest black flake8 mypy
```

## Making Changes

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes with proper documentation
3. Run tests: `pytest tests/ -v`
4. Format code: `black src/`
5. Run linter: `flake8 src/`
6. Commit: `git commit -m "feature: description"`
7. Push and create pull request

## Pull Request Process

- Ensure all tests pass
- Add tests for new functionality
- Update documentation
- Request review from maintainers

## Reporting Issues

Please include:
- Python version
- Full error traceback
- Steps to reproduce
- Expected vs actual behavior