# Git pre-commit script

echo ""
echo "Running pre-commit script..."

# Run all unit tests
python C:/Code/ElectricalBomAnalyser/scripts/run_unit_test.py
if [ $? -ne 0 ]; then
    echo "Abort pre-commit script: Unit test FAILED"
    exit 1
fi

# Increment build number
python C:/Code/ElectricalBomAnalyser/scripts/increment_build.py
if [ $? -ne 0 ]; then
    echo "Abort pre-commit script: Build increment FAILED"
    exit 1
fi

# Stage version.py for commit
git add C:/Code/ElectricalBomAnalyser/src/version.py
if [ $? -ne 0 ]; then
    echo "Abort pre-commit script: Stage version.py for commit FAILED"
    exit 1
else
    echo "version.py staged for commit"
fi

echo "Done with pre-commit"