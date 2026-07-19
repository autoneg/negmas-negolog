#!/bin/bash
# Script to update the vendored NegoLog from GitHub
# Usage: ./scripts/update_vendor.sh [branch]
#   branch: Optional branch/tag/commit to checkout (default: master)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENDOR_DIR="$PROJECT_ROOT/vendor"
NEGOLOG_DIR="$VENDOR_DIR/NegoLog"
REPO_URL="https://github.com/aniltrue/NegoLog.git"
BRANCH="${1:-master}"

echo "Updating vendored NegoLog from GitHub..."
echo "  Repository: $REPO_URL"
echo "  Branch/Tag: $BRANCH"
echo "  Target: $NEGOLOG_DIR"
echo

# Create vendor directory if it doesn't exist
mkdir -p "$VENDOR_DIR"

# Remove existing NegoLog directory if it exists
if [ -d "$NEGOLOG_DIR" ]; then
    echo "Removing existing NegoLog directory..."
    rm -rf "$NEGOLOG_DIR"
fi

# Clone the repository
echo "Cloning NegoLog repository..."
git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$NEGOLOG_DIR"

# Remove .git directory to make it a plain vendor copy (not a submodule)
echo "Removing .git directory from vendored copy..."
rm -rf "$NEGOLOG_DIR/.git"

# Remove unnecessary files for the wrapper (optional cleanup)
echo "Cleaning up unnecessary files..."
rm -rf "$NEGOLOG_DIR/web_framework"
rm -rf "$NEGOLOG_DIR/docs"
rm -rf "$NEGOLOG_DIR/domain_generator"
rm -rf "$NEGOLOG_DIR/tournament_configurations"
rm -f "$NEGOLOG_DIR/app.py"
rm -f "$NEGOLOG_DIR/run.py"
rm -f "$NEGOLOG_DIR/tournament_example.yaml"

# Re-sync the in-package bundle from the freshly vendored upstream.
#
# Only the `nenv` and `agents` subtrees of NegoLog are needed at runtime, and
# they live OUTSIDE `src/` here (vendor/ is just the upstream mirror), so they
# would NOT be included in the built wheel. We therefore keep a copy inside the
# package at `src/negmas_negolog/_vendor/NegoLog/{nenv,agents}` which DOES ship
# in the wheel (see common.py NEGOLOG_PATH). Re-syncing it here ensures the
# bundled copy never silently drifts from upstream after an update.
BUNDLE_DIR="$PROJECT_ROOT/src/negmas_negolog/_vendor/NegoLog"
echo "Re-syncing in-package bundle at $BUNDLE_DIR ..."
rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR"
cp -R "$NEGOLOG_DIR/nenv" "$BUNDLE_DIR/nenv"
cp -R "$NEGOLOG_DIR/agents" "$BUNDLE_DIR/agents"

# Get the commit hash for reference
echo
echo "NegoLog vendored successfully!"
echo "Note: .git was removed. To track the version, check the GitHub repository."
echo
echo "Done!"
