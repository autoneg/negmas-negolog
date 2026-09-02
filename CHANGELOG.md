# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-09-02

### Changed

- **Require `negmas>=0.16.0`** (was `>=0.15.2`). Older NegMAS releases are no
  longer supported; upgrade NegMAS before upgrading this package.
- `Preference.copy()` now copies the preference itself rather than reloading it
  from its source file path.
- Dropped the redundant `EstimatedPreference` patch, which discarded the
  reserved value.

### Added

- The NegoLog agents' private RNGs are now hooked onto NegMAS's global seed, so
  seeding NegMAS makes wrapped NegoLog agents reproducible.

### Fixed

- Caduceus no longer crashes on indifferent issues or single-issue domains.
- Non-string issue values are translated back from NegoLog strings to the
  original NegMAS values, instead of leaking their string forms.

### Performance

- HardHeaded's `TreeMap` lookups use a binary search instead of re-sorting.
- AgentGG no longer recomputes its own importance map every round.
- AhBuNe no longer rescans the whole outcome space to build its value sets.
- The bid key list is built once per iteration step instead of twice.
- The presorted inverse from NegMAS is reused and the bid order cached, rather
  than being rebuilt locally.

## [0.2.4] - 2026-07-19

### Added

- Strategy descriptions registered for all NegoLog negotiators.

### Fixed

- Vendored NegoLog is bundled inside the package so it ships in the wheel.

### Changed

- Declared AGPL-3.0 license metadata and reconciled it with the bundled
  GPL-3.0 NegoLog; both license texts ship in the distribution.
- Removed the root `vendor/` tree; `_vendor` is now the sole NegoLog source.

## [0.2.3] - 2026-01-17

### Changed

- Updated the registry integration for the new NegMAS registry API.

## [0.2.2] - 2026-01-13

### Added

- NegMAS registry integration for all NegoLog agents.

### Changed

- The package version is loaded dynamically from the installed package metadata.

### Fixed

- Removed the local editable NegMAS source from `pyproject.toml`, with a
  pre-commit hook to keep `tool.uv.sources` out of it.

## [0.2.1] - 2026-01-11

### Added

- MathJax support so math formulas render in the generated documentation.
- Documentation links in the README and a link to the agents page from the index.

### Fixed

- Corrected the MkDocs site URL to the `autoneg` organization.

## [0.2.0] - 2026-01-11

### Changed

- Split the agents into individual modules, each with comprehensive docstrings.

### Added

- A comprehensive agent table with descriptions and links.

## [0.1.2] - 2026-01-10

### Fixed

- Removed the forced `Agg` matplotlib backend so interactive plots work.

## [0.1.1] - 2026-01-10

### Added

- Support for Python 3.10, 3.11 and 3.14.
- Pre-commit hooks and a ruff configuration.

### Fixed

- Flaky utility-progression tests.

## [0.1.0] - 2026-01-10

### Added

- Initial release: NegMAS wrappers for the NegoLog negotiating agents, with
  full NegoLog attribution, documentation, and CI for tests and PyPI publishing.

[0.3.0]: https://github.com/autoneg/negmas-negolog/compare/v0.2.4...v0.3.0
[0.2.4]: https://github.com/autoneg/negmas-negolog/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/autoneg/negmas-negolog/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/autoneg/negmas-negolog/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/autoneg/negmas-negolog/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/autoneg/negmas-negolog/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/autoneg/negmas-negolog/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/autoneg/negmas-negolog/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/autoneg/negmas-negolog/releases/tag/v0.1.0
