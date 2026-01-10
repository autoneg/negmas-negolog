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

# Get the commit hash for reference
echo
echo "NegoLog vendored successfully!"
echo "Note: .git was removed. To track the version, check the GitHub repository."
echo
echo "Done!"
