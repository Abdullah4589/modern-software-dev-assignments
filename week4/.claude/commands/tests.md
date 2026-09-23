# Test Runner

Run the backend test suite and report results.

If $ARGUMENTS is provided, use it to scope the run (e.g. a test file or -k marker).
Otherwise run the full suite.

Steps:
1. Run: pytest -q backend/tests --maxfail=1
2. If tests pass, run coverage (pytest --cov=backend backend/tests) and summarize the results, flagging any low-coverage areas.
3. If tests fail, suggest a fix or next action.
