# Contributing to Voice Inventory Manager

Thank you for your interest in contributing to Voice Inventory Manager! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards others

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Microphone (for voice features)
- Basic understanding of Python and voice processing

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/voice-inventory-manager.git
   cd voice-inventory-manager
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL/voice-inventory-manager.git
   ```

## Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### 3. Run Setup

```bash
python setup.py
```

### 4. Verify Installation

```bash
python -m pytest tests/
```

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Relevant logs or screenshots

### Suggesting Features

1. Check existing feature requests
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach
   - Any relevant examples

### Code Contributions

1. **Find an Issue**: Look for issues tagged with `good first issue` or `help wanted`
2. **Comment**: Let others know you're working on it
3. **Create Branch**: Create a feature branch from `main`
4. **Write Code**: Implement your changes
5. **Test**: Ensure all tests pass
6. **Submit PR**: Create a pull request

## Coding Standards

### Python Style Guide

Follow PEP 8 with these specifics:

- **Line Length**: Maximum 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Use double quotes for strings
- **Imports**: Group and sort imports
  ```python
  # Standard library
  import os
  import sys
  
  # Third-party
  import numpy as np
  
  # Local
  from core.voice_engine import VoiceEngine
  ```

### Type Hints

Use type hints for function signatures:

```python
def add_item(name: str, quantity: int, price: Optional[float] = None) -> int:
    """Add item to inventory."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def process_command(text: str) -> Dict[str, Any]:
    """
    Process a voice command.
    
    Args:
        text: Command text from speech recognition
        
    Returns:
        Dictionary containing:
            - success: Whether processing succeeded
            - intent: Detected intent
            - response: User-facing response
            
    Raises:
        VoiceEngineError: If processing fails
    """
    pass
```

### Code Organization

- **One class per file** (with exceptions for small helper classes)
- **Logical grouping** of related functions
- **Clear separation** of concerns
- **Minimal dependencies** between modules

## Testing Guidelines

### Writing Tests

1. **Test Coverage**: Aim for 80%+ coverage
2. **Test Types**:
   - Unit tests for individual functions
   - Integration tests for component interaction
   - End-to-end tests for complete workflows

3. **Test Structure**:
   ```python
   def test_feature_name():
       # Arrange
       setup_data()
       
       # Act
       result = function_under_test()
       
       # Assert
       assert result == expected_value
   ```

### Running Tests

```bash
# All tests
python -m pytest tests/

# Specific file
python -m pytest tests/test_voice.py

# With coverage
python -m pytest --cov=core tests/

# Verbose
python -m pytest -v tests/
```

### Test Naming

- `test_<function>_<scenario>_<expected_result>`
- Example: `test_add_item_with_valid_data_succeeds`

## Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build process or auxiliary tool changes

### Examples

```
feat(voice): Add support for Whisper STT provider

Implemented Whisper integration for improved accuracy.
Added configuration options for Whisper model selection.

Closes #123
```

```
fix(inventory): Handle negative stock correctly

Fixed bug where negative stock was allowed.
Added validation to prevent negative quantities.

Fixes #456
```

## Pull Request Process

### Before Submitting

1. **Update from upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests**:
   ```bash
   python -m pytest tests/
   ```

3. **Check code style**:
   ```bash
   flake8 .
   black --check .
   ```

4. **Update documentation** if needed

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged

## Development Workflow

### Feature Development

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# ... edit files ...

# Commit changes
git add .
git commit -m "feat(scope): description"

# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub
```

### Bug Fix

```bash
# Create bugfix branch
git checkout -b fix/bug-description

# Make changes
# ... fix bug ...

# Commit
git commit -m "fix(scope): description"

# Push and create PR
git push origin fix/bug-description
```

## Code Review Guidelines

### For Reviewers

- Be respectful and constructive
- Focus on code, not the person
- Explain reasoning for suggestions
- Approve when satisfied

### For Contributors

- Don't take feedback personally
- Ask questions if unclear
- Make requested changes promptly
- Thank reviewers for their time

## Documentation

### When to Update Docs

- New features
- API changes
- Configuration changes
- Bug fixes that affect usage

### Documentation Files

- `README.md`: Overview and quick start
- `docs/ARCHITECTURE.md`: System design
- `docs/COMMANDS.md`: Command reference
- `docs/API_SPEC.md`: API documentation
- Docstrings: In-code documentation

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Discord**: Real-time chat (if available)
- **Email**: For private matters

### Getting Help

- Check documentation first
- Search existing issues
- Ask in discussions
- Create a new issue if needed

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Voice Inventory Manager! 🎉
