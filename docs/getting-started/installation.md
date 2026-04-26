# Installation

## Requirements

- Python 3.12 or higher
- NegMAS 0.10.0 or higher

## Install from PyPI

```bash
pip install negmas-negolog
```

Or with uv:

```bash
uv add negmas-negolog
```

## Install from Source

For development or to get the latest changes:

```bash
git clone https://github.com/yasserfarouk/negmas-negolog.git
cd negmas-negolog
uv sync --dev
```

## Verify Installation

```python
import negmas_negolog

# Check version
print(negmas_negolog.__version__)

# List available agents
print(negmas_negolog.__all__)
```

## Dependencies

The package automatically installs all required dependencies:

- **negmas** - The NegMAS negotiation framework
- **numpy**, **scipy**, **pandas** - Scientific computing
- **matplotlib**, **plotly**, **seaborn** - Visualization
- **scikit-learn** - Machine learning (used by some agents)
- **numba** - JIT compilation for performance
