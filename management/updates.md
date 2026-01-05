# Scova: Updates

#### Created at: 1:37 AM on November 18, 2025 at Home

---

### 1:39 AM | November 18, 2025 | Tuesday | Home

## KivyMD vs Flutter for Backtesting MVP

<u>KivyMD</u>
**Pros**

1. Faster to prototype, frictionliess integration with python backend
2. Useful for future python application ideas (of which there are always plenty)
3. local sqlite db usage
4. Easy files IO integration
5. will have UI perfected when it's time for flutter

**Cons**

1. Will have to repeat the whole UI process for flutter final product (but works out since we might have had to build a new project anyway to remove artefacts)
2. Never done before
   2.1. But same goes for Flutter. Last used properly in 2021, so long forgotten.
   2.2. All heavy-lifting will be done by Gemini anyway. So what gives.

<u>Flutter</u>
**Pros**

1. One time coding.
2. Practice of syntax while building.

**Cons**

1. Artefacts from development and trial periods might persist in polished contruction.
2. File IO integration is much harder, and has always been a pain since forever.
3. Will have to account for firestore 1.**COSTS** and 2. Integration Time
4. Now that development is local instead of Google IDX, doesn't entirely make sence if iPad is not the main device anymore.
   4.1. iPad has just as much free space as Mac SSD.
   4.2. Mac SSD can expand if ever needed with 1. Dock and 2. Extra SSD.
   4.3. Can't expand at all if iPad ever runs out of space.
5. iPad is much more complicated setup anyway because of Swift integration.

### Decision: Settled on KivyMD

---

---

### 5:35 PM | November 18, 2025 | Tuesday | Home

## Started working on Python MVP

1. Updated new code structure to github
2. Made skeleton project for KivyMD
3. Subscribed to Zerodha Historical API
4. Integrated Zerodha API with project
5. integrated auto-project restart in project on code-changes without restarting debug session
6. Persisting Zerodha login across debug sessions

---

---

### 11:36 PM | November 22, 2025 | Saturday | Home

## Building Download Screen and Backend

**Brief note about why go for UI first approach, instead of CLI or Jupyter Notebook if the goal was getting to proof of concept ASAP:**

1. CLI has no organisation. I would lose the time I supposedly saved from ignoring the UI and spent it on keeping track of haphazardly created files and downloads and script versios.
2. Jupyter Notebook is too slow with neural networks. Jupyter doesn't use all available compute power like a terminal level script does.

**Tasks:**

1. Shifted login logic to the User Screen.
2. Added dock for navigation between Downloader, Trainer, and Backtester Screens.
3. Complete UI implemented
4. Download destination picker / file browser took 3 hours.

---

---

### 2:32 AM | November 23, 2025 | Sunday | Home

## Abandoned KivyMD and Switched to PySide6 / PyQt

1. UI worked surprisingly well. Hopeful now.

---

---

### 3:29 AM | November 27, 2025 | Thursday | Home

1. Refactored files to remove KivyMD references.
2. Scrip selection is better, with multiple select/deselect options.
3. Parquet download is also working now.
4. Downloaded file naming convention sorted. Using metadata.json to track constituent parameters of each download.
5. Built UI for Trainer Screen: Accordion, Pre-training, Training, Post-Training, History.

---

---

### 5:41 AM | November 28, 2025 | Friday | Home

1. Finished initial UI for all sections of trainer Screen.
2. Revised Trainer Screen UI to feel more like a proper dashboard, rather than a really long and complicated form.
3.

---

---

### 02:33 PM | December 9, 2025 | Tuesday | Home

## Implemented Dynamic Trainer Configuration and Experiment Workflow

1.  **Modular UI Refactor:** Broke down the monolithic trainer UI into individual, modular widgets for each pre-training step (e.g., `DataSourceWidget`, `ModelInputParametersWidget`).
2.  **Centralized Configuration:** The `SetupTabWidget` now gathers settings from all child widgets into a single configuration object.
3.  **Experiment Persistence:** Added an "Apply" button that saves the complete experiment configuration to `build/last_applied_config.json`.
4.  **Automated Experiment Naming:** The system now automatically generates a unique experiment ID (a hash of the settings) to ensure every run is traceable. The name can still be manually overridden.
5.  **Integrated Workflow:** Implemented an "Apply & Run" button that saves the configuration, switches to the "Monitor" tab, and starts the training process, creating a seamless user experience.
6.  **New Widgets:**
    - Added `FileSavingWidget` to define output paths for models and data.
    - Completely overhauled `ModelInputParametersWidget` with advanced options for different chart types (including a "Dynamic 2D Plane"), image styling, and technical overlays.
7.  **Activated Monitor Tab:** The "Begin Experiment" button on the monitor tab is now functional and loads the saved configuration to kick off the training run.

---

---

### 02:45 PM | December 9, 2025 | Tuesday | Home

1. Added custom command "/sync" to auto-write the latest changes to the update log, and commit message, and sync with github remote's main branch.

---

---

### 03:38 PM | December 9, 2025 | Tuesday | Home

## Refactored Trainer Setup UI to Stepped Wizard

To improve user experience and fix UI scaling issues, the Trainer Setup tab has been completely redesigned.

1.  **New Layout:** Replaced the unbalanced two-column layout with a guided, step-by-step wizard.
2.  **Navigation Sidebar:** A sidebar on the left now shows all the setup steps, providing a clear overview of the process.
3.  **"Visited" Icons:** The sidebar uses `○` and `✔` icons to give users a visual cue of which steps they have already visited.
4.  **Scrollability:** The main content area is now wrapped in a `QScrollArea`, which resolves the issue where the app would not fit on smaller screens like an iPad via Sidecar.
5.  **Focused Steps:** Each configuration widget is now on its own page, reducing clutter and guiding the user through the setup one step at a time.

---

---

### 08:55 PM | December 9, 2025 | Tuesday | Home

## Overhauled Trainer Setup UI & Added Advanced Parameters

Completed a major refactoring of the Trainer Setup UI to create a more intuitive, powerful, and aesthetically consistent experience.

1.  **New Hyperparameter Sections:** Added comprehensive controls for "Training Hyperparameters", "Prediction Target" logic, and the "Error Correction Healing Phase" to allow for fine-grained experimental setup.
2.  **UI/UX Refactoring:**
    *   Replaced all custom `Accordion` and `QFormLayout` based UIs with a standardized system of `QGroupBox` and `QGridLayout`. This creates a cleaner, more compact, and consistent look across all setup screens.
    *   Adjusted layouts to be vertical, eliminating horizontal scrolling and improving usability on smaller screens.
3.  **Conditional Visibility:** Implemented robust signal/slot logic to dynamically show or hide entire configuration sections based on user selections, reducing clutter and guiding the user.
4.  **Bug Fixes & Enhancements:**
    *   Fixed a critical bug where conditional UI sections were not appearing correctly.
    *   Added a "Line Color" option to the chart styling parameters.
    *   Styled the primary "Apply & Run" button to be visually distinct.

---

---

### 07:51 PM | December 10, 2025 | Wednesday | Home

## Implemented Chaos Monkey Testing and Overhauled Trainer UI

1.  **Chaos Monkey Infrastructure:**
    *   Added `pytest`, `pytest-qt`, and `pytest-json-report` to the project.
    *   Created `Monkey` classes (like `TrainerMonkey`) to perform automated "chaos testing" on the wizard, randomly interacting with UI elements to find bugs.
    *   Implemented a supervisor script (`run_chaos_monkey.py`) to run the chaos test in a loop, detect crashes (segfaults), and save crash reports to a `crashes/` directory.
    *   Added a VS Code launch configuration to easily run the chaos loop from the debugger.

2.  **Trainer UI/UX Overhaul:**
    *   **Fully Connected Pipeline:** Implemented the backend `TrainingWorker` and connected it to the UI. The "Monitor" tab now shows live plot updates during a training run.
    *   **Functional Results & History:** The "Results" and "History" tabs are now fully functional, loading and displaying data from completed runs.
    *   **Dynamic UI Logic:** Added logic to the 'Error Correction' step to show different parameters based on the selected chart type.
    *   **UI Polish:** Fixed various layout and spacing issues to improve UI density and corrected the "Apply and Run" button text to prevent rendering issues.

3.  **Downloader UI Refactor:**
    *   Redesigned the Downloader screen with a tabbed interface to clearly separate "New Job" from "Resume Job" workflows, improving usability.

---

---

### 08:37 AM | December 21, 2025 | Sunday | Home

## Implement Dynamic 2D Plane and Production-Ready Features

1.  **Core Feature: Dynamic 2D Plane**
    *   Implements `DynamicPlaneProcessor` to transform time-series data into motion-compensated vector space using PCA.
    *   Integrates processor into `TrainingWorker` for parallel data pipeline and LSTM modeling.
    *   Adds 'decoder' for inverse-transforming model outputs back to scalar price movements.
    *   Enables K-Fold cross-validation for the Dynamic Plane pipeline.

2.  **Trainer UI and Workflow Enhancements:**
    *   **Monitor Tab:** Dynamic monitoring of model configuration with real-time plots for loss and accuracy of every active prediction head.
    *   **Results Tab:** Dynamic visualization of training output (scatter plots for regression, confusion matrices for classification).
    *   **History Tab:** 
        *   Added 'Reload Configuration' to load parameters from past runs.
        *   Added 'Compare Selected Runs' for side-by-side parameter comparison.
    *   **Setup Tab:** Background-threaded disk space calculator; removed unsupported 'Swin-Transformer' and 'Point & Figure' options.

3.  **Charting and Image Generation:**
    *   Implemented 'Hollow Candlestick' rendering.
    *   Added support for Moving Average overlays and Volume subplots.
    *   Implemented 'Renko' charts via `stocktrends`.

---

---

### 03:00 PM | December 31, 2025 | Wednesday | Home

## Refactored Management Structure and Chaos Monkey Terminology

1.  **Management Directory Structure:**
    *   Centralized all governance documents into a new `management/` directory.
    *   Created `management/mcp.json` (Management Context Protocol) to serve as a navigable index for the agent.
    *   Established `.cursorrules` at the project root as the single source of truth for agent bootstrapping.

2.  **Chaos Monkey Refactor:**
    *   Renamed all "Phoenix" and "Fuzz Testing" terminology to "Chaos Monkey".
    *   Refactored `WizardWalker` class to `Monkey` classes (e.g., `TrainerMonkey`).
    *   Renamed supervisor scripts to `run_chaos_monkey.py` and updated all test/history filenames.

3.  **Sync Protocol:**
    *   Created `management/sync.md` to formally document the `git` synchronization workflow.
    *   Enforced a new rule: Commit messages must strictly match the `updates.md` entry in content and tone.

---

---

### 03:02 PM | January 03, 2026 | Saturday | Home

## Implemented Project Logger System

1.  Implemented `lib/logger.py` to handle centralized logging configuration.
2.  Replaced all `print()` statements with `logging` calls across `ui_pyside6` and `main_pyside.py`.
3.  Logs are now saved to the `logs/` directory with unique timestamps for each run.

---

---

### 03:45 PM | January 03, 2026 | Saturday | Home

## Expanded Chaos Monkey Testing and Repaired Training Backend

1.  **Trainer Chaos Monkey Expansion**:
    *   Implemented `TrainerResultsMonkey` to verify dynamic result loading (plots, confusion matrices) without mocks.
    *   Implemented `TrainerHistoryMonkey` to test "Refresh", "Compare Selected Runs", and "Reload Configuration" workflows.
    *   Achieved true end-to-end status by using `qtbot` to interact with real modal dialogs (`QMessageBox`, `ComparisonDialog`).

2.  **Critical Backend Repairs**:
    *   Diagnosed and fixed a broken inheritance chain in `TrainingWorker`. The worker was relying on base class methods (`_load_and_filter_data`, etc.) that did not exist.
    *   Re-implemented the complete data loading, dataset generation, and model saving logic within `TrainingWorker` to restore functionality.
    *   Patched `MonitorTabWidget` to prevent race conditions during worker queue shutdown.
    *   Made `vit_keras` import conditional to allow the application to function on systems missing `tensorflow-addons`.

---

---

### 12:25 AM | January 06, 2026 | Tuesday | Home

## Renamed Project to Scova

1.  **Global Renaming**:
    *   Renamed the project from **Svaha** to **Scova**.
    *   Performed comprehensive text replacement across the entire codebase.
2.  **Log Management**:
    *   Renamed all historical logs in `logs/` from `svaha_*.log` to `scova_*.log`.
3.  **Documentation**:
    *   Updated all documentation to reflect the new name.