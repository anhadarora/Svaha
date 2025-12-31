# Chaos Monkey (Fuzz Testing) Protocols

## Overview
The "Chaos Monkey" (formerly Phoenix) process is designed to ensure application robustness by subjecting the UI to random, automated interactions ("monkey testing"). The goal is to identify crashes, segfaults, and unhandled exceptions before they reach the user.

## Infrastructure
-   **Core Class**: `Monkey` classes (e.g., `TrainerMonkey` in `tests/chaos_monkey.py`).
    -   Uses `pytest-qt` and `qtbot` to interact with widgets.
    -   Randomly clicks buttons, enters text, and navigates the 'Trainer Setup' wizard.
-   **Supervisor**: `run_chaos_monkey.py`
    -   Runs the Chaos Monkey test in a continuous loop.
    -   Detects process crashes (segfaults).
    -   Saves crash artifacts/logs to the `crashes/` directory.

## Testing Rules
1.  **Scope**: Primarily targets complex UI workflows like the Trainer Wizard.
2.  **Safety**: Chaos Monkey testing must run in a sandboxed manner (e.g., using dummy data or a separate test environment) if possible, though currently it often runs on the main app structure.
3.  **Reporting**: All crashes must be logged with a stack trace.

## Future Improvements
-   Expand coverage to the 'Backtester' and 'Downloader' screens.
-   Implement "smart" chaos that uses state awareness rather than pure randomness.
