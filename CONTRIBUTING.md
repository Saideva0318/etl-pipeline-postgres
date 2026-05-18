# Contributing to etl-pipeline-postgres

Thank you for your interest in contributing! This project follows standard open-source practices.

## Getting Started

1. **Fork** the repository and clone your fork
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
3. **Set up the environment**:
   ```bash
   make install        # install deps + pre-commit hooks
   make setup-env     # copy .env.example to .env
   make docker-up     # start PostgreSQL
   ```

## Development Standards

### Code Style
- Formatter: **Black** (line length 120)
- Linter: **flake8** with bugbear + comprehensions plugins
- Import order: **isort** (Black-compatible profile)
- Pre-commit hooks run automatically on `git commit`
- To format manually: `make format`

### Testing
- All new features must include unit tests in `tests/`
- Run tests: `make test`
- Coverage target: **>80%**
- Run coverage: `make test-cov`

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat(scope): description       # new feature
fix(scope): description        # bug fix
docs(scope): description       # documentation
chore(scope): description      # maintenance
refactor(scope): description   # code restructuring
test(scope): description       # tests
ci(scope): description         # CI/CD changes
```

## Pull Request Process

1. Ensure all tests pass: `make test`
2. Ensure code is formatted: `make format && make lint`
3. Update `README.md` if you change any public interfaces
4. Create a Pull Request with a clear description of changes
5. Reference any related issues in the PR description

## Reporting Issues

- Use GitHub Issues to report bugs or request features
- Include steps to reproduce for bug reports
- Include the expected vs actual behavior

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
