# Contributing to MLAOS Infrastructure

Thank you for your interest! This project follows **Google's Rules of Machine Learning** for production readiness.

## 📋 Pull Request Checklist

Before submitting a PR, ensure:

- [ ] **Feature Registry Updated (Rule #11):** New features added to `sql/001_feature_registry.sql` with owner/description.
- [ ] **Shared Extractor Used (Rule #32):** No duplicate preprocessing code between train/serve.
- [ ] **Tests Added (Rule #5):** Unit tests for all new code (coverage >85%).
- [ ] **Skew Audit Run (Rule #37):** Verify no training-serving skew introduced.
- [ ] **Unused Features Pruned (Rule #22):** Remove any deprecated features/code.
- [ ] **Documentation Updated:** README and API docs reflect changes.

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Check coverage
coverage report --fail-under=85
```

## 📝 Code Style

- Follow PEP 8 for Python code.
- Use type hints for all function signatures.
- Docstrings required for all public methods.

## 🚀 Release Process

1. Create feature branch
2. Implement changes + tests
3. Run skew audit
4. Submit PR
5. Code review (owner approval required)
6. Merge to main
7. Tag release

## 📤 Contact

Questions? Email [kennydallmier@gmail.com](mailto:kennydallmier@gmail.com).
