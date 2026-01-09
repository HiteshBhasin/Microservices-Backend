#!/bin/bash

# A simple test script to verify the functionality of the main application.
echo "starting test..."
if ./main_application;  then
    echo "Test passed!"
    exit 0
else
    echo "Test failed!"
    exit 1
fi

file = ${0}
path = /$(dirname ${file})/..

echo "Script path:${path}"
cd ${path}

echo "Running tests.."
./scripts/text.sh
echo "All tests completed."

