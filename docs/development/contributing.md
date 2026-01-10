# Contributing

Contributions are welcome! Here's how to get started.

## Development Setup

1. Clone the repository:

```bash
git clone https://github.com/yasserfarouk/negmas-negolog.git
cd negmas-negolog
```

2. Install with development dependencies:

```bash
uv sync --dev
```

3. Run tests:

```bash
uv run pytest tests/ -v
```

## Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_wrapper.py -v

# Run with coverage
uv run pytest tests/ --cov=negmas_negolog
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public APIs

## Adding New Agents

To wrap a new NegoLog agent:

1. Import the agent class from `vendor/NegoLog/agents/`
2. Create a wrapper class in `src/negmas_negolog/wrapper.py`
3. Add to `__all__` in both `wrapper.py` and `__init__.py`
4. Add tests in `tests/test_wrapper.py`
5. Document in `docs/user-guide/agents.md`

Example:

```python
# In wrapper.py
from agents.NewAgent.NewAgent import NewAgent as _NLNewAgent

class NewAgent(NegologNegotiatorWrapper):
    """NegMAS wrapper for NegoLog's NewAgent."""
    negolog_agent_class = _NLNewAgent
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Reporting Issues

Please report issues on GitHub with:

- Python version
- NegMAS version
- Minimal reproducible example
- Full error traceback
