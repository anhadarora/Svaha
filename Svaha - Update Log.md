# Svaha: Update Log

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
