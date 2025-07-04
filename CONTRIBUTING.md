# Contributing to PowerBiz Developer Analytics

Thank you for your interest in contributing to PowerBiz! This document provides guidelines and instructions for contributors.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Docker (optional, for containerized development)

### Getting Started

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/pallab-saha-git/fika-ai-engineering-insights-bot
   cd fika
   ```

2. **Set up Development Environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   make install
   # or: pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your API tokens
   ```

3. **Verify Setup**:
   ```bash
   # Run smoke test
   python smoke_test.py
   
   # Run full test suite
   make test
   ```

## Code Style and Standards

### Python Code Style

We follow [PEP 8](https://pep8.org/) with these specific guidelines:

- **Line length**: 88 characters (Black default)
- **Import organization**: Use `isort` for consistent import ordering
- **Type hints**: Required for all public functions and methods
- **Docstrings**: Use Google-style docstrings

### Code Formatting

We use automated formatting tools:

```bash
# Format code
black powerbiz/ tests/
isort powerbiz/ tests/

# Check linting
flake8 powerbiz/ tests/
mypy powerbiz/
```

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding missing tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(agents): add forecasting capability to DiffAnalyst
fix(slack): handle rate limiting in bot responses
docs: update API documentation for new endpoints
```

## Architecture Guidelines

### Agent Development

When creating or modifying agents:

1. **Inherit from BaseAgent**: All agents must extend `BaseAgent`
2. **Implement required methods**: `process()` and `get_agent_info()`
3. **Handle errors gracefully**: Use try-catch blocks and proper logging
4. **Add type hints**: Ensure all methods have proper type annotations
5. **Write tests**: Include unit tests for all agent functionality

### Database Changes

For database schema changes:

1. **Create migrations**: Add migration scripts for schema changes
2. **Backward compatibility**: Ensure changes don't break existing data
3. **Test migrations**: Verify migrations work with existing seed data
4. **Update models**: Keep SQLAlchemy models in sync with schema

### LangGraph Workflows

When modifying the agent workflow:

1. **Document state transitions**: Clearly document what triggers each transition
2. **Error handling**: Implement proper error recovery and retry logic
3. **Testing**: Create integration tests for workflow paths
4. **Performance**: Consider the impact on overall processing time

## Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for workflows
├── fixtures/       # Test data and fixtures
└── conftest.py     # Shared test configuration
```

### Writing Tests

1. **Test naming**: Use descriptive names that explain what is being tested
2. **Arrange-Act-Assert**: Structure tests clearly
3. **Mock external APIs**: Use mocks for GitHub, Slack, and OpenAI APIs
4. **Test edge cases**: Include tests for error conditions and edge cases

**Example test:**
```python
def test_data_harvester_processes_commits_correctly():
    # Arrange
    agent = DataHarvesterAgent()
    mock_commits = [create_mock_commit()]
    
    # Act
    result = agent.process_commits(mock_commits)
    
    # Assert
    assert result.total_commits == 1
    assert result.avg_churn > 0
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
python -m pytest tests/test_data_harvester.py -v

# Run with coverage
python -m pytest --cov=powerbiz tests/

# Run integration tests only
python -m pytest tests/integration/ -v
```

## Documentation Standards

### Code Documentation

- **Docstrings**: All public functions, classes, and methods must have docstrings
- **Type hints**: Use type hints for all function parameters and return values
- **Inline comments**: Explain complex logic or business rules

### API Documentation

When adding new features:

1. **Update README**: Add new commands or configuration options
2. **Add examples**: Include usage examples for new functionality
3. **Update architecture diagrams**: Reflect changes in system architecture

## Submitting Changes

### Pull Request Process

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**:
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:
   ```bash
   make test
   python smoke_test.py
   ```

4. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub.

### Pull Request Checklist

- [ ] Tests pass locally (`make test`)
- [ ] Smoke test passes (`python smoke_test.py`)
- [ ] Code is properly formatted (Black, isort)
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages follow conventional format
- [ ] No sensitive data in commits (API keys, etc.)

## Issue Guidelines

### Reporting Bugs

When reporting bugs, include:

- **Environment details**: OS, Python version, dependency versions
- **Steps to reproduce**: Clear steps to recreate the issue
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Error messages**: Full error messages and stack traces
- **Configuration**: Relevant environment variables or config

### Feature Requests

For feature requests, provide:

- **Use case**: Why is this feature needed?
- **Description**: What should the feature do?
- **Acceptance criteria**: How do we know when it's done?
- **Alternatives considered**: What other solutions were considered?

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release notes
4. Tag release: `git tag v1.2.3`
5. Push tags: `git push --tags`

## Code of Conduct

### Our Standards

- **Be respectful**: Treat all contributors with respect
- **Be collaborative**: Work together towards common goals
- **Be inclusive**: Welcome contributors from all backgrounds
- **Be helpful**: Assist others in learning and contributing

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project maintainers. All complaints will be reviewed and investigated promptly and fairly.

## Getting Help

- **Documentation**: Check the README and this contributing guide first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Discord/Slack**: Join our community chat (link in README)

## Recognition

Contributors will be recognized in:

- **CONTRIBUTORS.md**: List of all contributors
- **Release notes**: Major contributions highlighted
- **README**: Special thanks for significant contributions

Thank you for contributing to PowerBiz Developer Analytics! 🚀
