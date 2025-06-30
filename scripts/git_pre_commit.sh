# *** Git pre-commit script ***
#
# This script is called by the Git pre-commit hook file located at:
#   .git/hooks/pre-commit
#
# The pre-commit hook file must contain the following (or equivalent):
#
#   #!/usr/bin/bash
#
#   # Navigate to the root of the repository (assuming this script is in ./scripts/)
#   SCRIPT_DIR="$(dirname "$0")" # Step 1: Get the directory of this script
#   REPO_ROOT="$SCRIPT_DIR/.." # Step 2: Move one directory up (repo root)
#   cd "$REPO_ROOT" || { echo "Failed to change to repo root"; exit 1; } # Step 3: Change to the repo root directory
#
#   # Call the actual pre-commit script
#   bash scripts/git_pre_commit.sh
#   if [ $? -ne 0 ]; then
#       echo "Commit aborted. Git pre-commit shell script FAILED."
#       exit 1
#   fi

echo ""
echo "Running pre-commit script..."

# Navigate to the root of the repository (assuming this script is in ./scripts/)
SCRIPT_DIR="$(dirname "$0")" # Step 1: Get the directory of this script
REPO_ROOT="$SCRIPT_DIR/.." # Step 2: Move one directory up (repo root)
cd "$REPO_ROOT" || { echo "Failed to change to repo root"; exit 1; } # Step 3: Change to the repo root directory

# Run all unit tests
python scripts/run_unit_test.py
if [ $? -ne 0 ]; then
    echo "Abort pre-commit script: Unit test FAILED"
    exit 1
fi

# Increment build number
python scripts/increment_build.py
if [ $? -ne 0 ]; then
    echo "Abort pre-commit script: Build increment FAILED"
    exit 1
fi

# Stage version.py for commit
git add src/version.py
echo ""
if [ $? -ne 0 ]; then
    echo "Abort pre-commit script: Stage version.py for commit FAILED"
    exit 1
else
    echo "Staged version.py for commit due to build number increment."
fi

echo ""
echo "Done with pre-commit"