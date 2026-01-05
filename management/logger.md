# Logger Protocols

## Overview
This document outlines the standards for application logging in Scova. We use the standard Python `logging` library with a centralized configuration.

## Current Implementation
-   **Initialization**: `lib/logger.py` acts as the central setup point.
    -   It should be imported and initialized at the very start of `main_pyside.py`.
-   **Handlers**:
    -   `StreamHandler`: Outputs `INFO` and higher to the console (stdout).
    -   `RotatingFileHandler`: Writes logs to `logs/app.log` (or similar).
        -   Rotates files to prevent disk saturation.
-   **Formatting**: Standard format including timestamp, level, logger name, and message.

## Rules
1.  **Use `logging.getLogger(__name__)`**: Every module must create its own logger instance using its name. Never use the root logger directly (`logging.info`) in library code.
2.  **Levels**:
    -   `DEBUG`: Detailed flow information (e.g., "Entered function X", "Variable y = 5").
    -   `INFO`: High-level events (e.g., "Application started", "Download job resumed").
    -   `WARNING`: Recoverable issues (e.g., "Config file missing, using defaults").
    -   `ERROR`: Operations failed but app continues (e.g., "Failed to save file").
    -   `CRITICAL`: App cannot continue (e.g., "Database corruption").
3.  **No `print()`**: Use logging instead of `print()` statements for all runtime info.

## File Locations
-   Log configuration: `lib/logger.py`
-   Log output directory: `logs/`
