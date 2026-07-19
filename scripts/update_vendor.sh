#!/bin/bash
# Script to update the vendored NegoLog from GitHub
# Usage: ./scripts/update_vendor.sh [branch]
#   branch: Optional branch/tag/commit to checkout (default: master)
#
# NegoLog is vendored INSIDE the package at
# src/negmas_negolog/_vendor/NegoLog/{nenv,agents} so it ships in the built
# wheel and resolves identically in editable and installed (PyPI) modes
# (see common.py NEGOLOG_PATH). Upstream is cloned into a throwaway temp dir;
# no `vendor/` tree is ever created in the project root.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUNDLE_DIR="$PROJECT_ROOT/src/negmas_negolog/_vendor/NegoLog"
REPO_URL="https://github.com/aniltrue/NegoLog.git"
BRANCH="${1:-master}"

# Clone upstream into a throwaway temp dir; always clean it up on exit.
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
NEGOLOG_DIR="$TMP_DIR/NegoLog"

echo "Updating vendored NegoLog from GitHub..."
echo "  Repository: $REPO_URL"
echo "  Branch/Tag: $BRANCH"
echo "  Target:     $BUNDLE_DIR"
echo

# Clone the repository (shallow) into the temp dir.
echo "Cloning NegoLog repository..."
git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$NEGOLOG_DIR"

# Re-sync the in-package bundle from the freshly cloned upstream.
#
# Only the `nenv` and `agents` subtrees are needed at runtime; we copy them
# into the package so they ship in the wheel. Re-syncing here ensures the
# bundled copy never silently drifts from upstream after an update.
echo "Re-syncing in-package bundle at $BUNDLE_DIR ..."
rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR"
cp -R "$NEGOLOG_DIR/nenv" "$BUNDLE_DIR/nenv"
cp -R "$NEGOLOG_DIR/agents" "$BUNDLE_DIR/agents"
# Ship upstream's license alongside the bundled code for attribution.
cp "$NEGOLOG_DIR/LICENSE" "$BUNDLE_DIR/LICENSE"

echo
echo "NegoLog vendored successfully into the package!"
echo "Note: the upstream .git was not kept. To track the version, check the GitHub repository."
echo
echo "Done!"
