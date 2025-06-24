# Git pre-commit script

echo ""
echo "Running pre-commit script..."

# Run all unit tests
python "$(dirname "$0")/run_unit_test.py"
if [ $? -ne 0 ]; then
    echo "Abort pre-commit script: Unit test FAILED"
    exit 1
fi

# Increment build number
python "$(dirname "$0")/increment_build.py"
if [ $? -ne 0 ]; then
    echo "Abort pre-commit script: Build increment FAILED"
    exit 1
fi

# Stage version.py for commit
git add "$(dirname "$0")/../src/version.py"
echo ""
if [ $? -ne 0 ]; then
    echo "Abort pre-commit script: Stage version.py for commit FAILED"
    exit 1
else
    echo "Staged version.py for commit due to build number increment."
fi

echo ""
echo "Done with pre-commit"
