# Testing

This page covers testing strategies for negmas-negolog, including unit tests and behavior comparison between native NegoLog and wrapped NegMAS agents.

## Running Unit Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run wrapper functionality tests
uv run pytest tests/test_wrapper.py -v

# Run equivalence tests
uv run pytest tests/test_equivalence.py -v
```

## Behavior Comparison

The project includes a comprehensive behavior comparison tool that validates wrapped agents behave equivalently to their native NegoLog counterparts.

### Running the Comparison

```bash
uv run python scripts/compare_behavior.py
```

This script:

1. Creates a test negotiation domain with 3 issues (price, quantity, delivery)
2. Runs each of the 25 agents against a Boulware opponent in **both**:
   - Native NegoLog environment
   - NegMAS with wrapped agents
3. Compares the results and generates reports

### Output

Reports are generated in the `reports/` directory:

| File | Description |
|------|-------------|
| `behavior_comparison_report.md` | Human-readable Markdown report with tables |
| `behavior_comparison_report.json` | Machine-readable JSON for programmatic analysis |

### Metrics

The comparison measures several behavioral metrics:

#### Agreement Consistency

Whether both environments reach the same agreement outcome:

- **Both agreed** - Native and wrapped both reached agreement
- **Neither agreed** - Native and wrapped both failed to agree
- **Mismatch** - One agreed while the other didn't (indicates a bug)

#### Similarity Score

A composite score (0.0 - 1.0) based on:

- Same agreement outcome (+1.0)
- Similar round count (proportional)
- Similar first offer utility (+1.0 if within 0.1, +0.5 if within 0.2)
- Similar final utilities when both agreed (+1.0 if within 0.1)

Interpretation:

| Score | Category | Meaning |
|-------|----------|---------|
| >= 0.75 | High | Excellent equivalence |
| 0.5 - 0.75 | Medium | Good equivalence, minor differences |
| < 0.5 | Low | Significant differences, investigate |

### Understanding Results

#### Expected Differences

Small differences (1-2 rounds) are expected due to:

- **Timing precision** - NegMAS and NegoLog calculate relative time slightly differently
- **Round semantics** - NegMAS alternating offers vs NegoLog's session-based model

#### Issues to Investigate

Look for:

- **Agreement mismatches** - One environment agrees while other doesn't
- **Large utility differences** - Same agreement but different utilities (shouldn't happen)
- **Large round differences** - More than 5-10 rounds different

### Example Report

```markdown
## Summary

| Metric | Value |
|--------|-------|
| Total agents tested | 25 |
| Both agreed | 13 |
| Neither agreed | 12 |
| Agreement mismatch | 0 |

### Behavior Similarity

| Category | Count |
|----------|-------|
| High (>= 0.75) | 14 |
| Medium (0.5 - 0.75) | 11 |
| Low (< 0.5) | 0 |
| **Average** | **0.71** |
```

### Extending the Comparison

To add custom tests, modify `scripts/compare_behavior.py`:

```python
# Add new agents to test
AGENTS = [
    (BoulwareAgent, NativeBoulware, "Boulware"),
    # Add your agent here:
    (MyAgent, NativeMyAgent, "MyAgent"),
]

# Modify the test domain
def create_test_domain():
    # Customize issues, weights, etc.
    ...
```

## Continuous Integration

Tests run automatically on:

- Every push to main branch
- Every pull request

See `.github/workflows/test.yml` for the CI configuration.
