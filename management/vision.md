# Svaha: Project Vision

## 1. Project Vision
Svaha is a high-performance, CNN-driven algorithmic training, and trading application. The goal is to create a unified ecosystem that seamlessly integrates data acquisition, model training, and paper trading, live trading, error-debugging, and compliance reporting into a single tailored desktop application. It prioritizes a "UI-First" approach to ensure complex workflows (like deep learning model configuration) are intuitive, reproducible, and error-resistant.

## 2. Technology Stack
-   **Language**: Python 3+
-   **UI Framework**: PySide6 (Qt)
-   **Data Storage**: Parquet (for market data), SQLite (for app state/logs), JSON (metadata/configs)
-   **Machine Learning**: PyTorch / Custom Implementations (Dynamic 2D Plane, CNN, Vision Transformer)
-   **Data Source**: Zerodha Historical API

## 3. System Architecture & Modules

### 3.1. Data Acquisition (Downloader)
-   **Purpose**: Fetch and manage historical market data efficiently.
-   **Key Features**:
    -   Integration with Zerodha Kite Connect API.
    -   Parquet storage for high-performance I/O.
    -   Metadata tracking (`downloader_screen_metadata.json`) to preserve download context.
    -   Resume capability for interrupted jobs.

### 3.2. Model Training (Trainer)
-   **Purpose**: A modular, wizard-based interface for designing and training predictive models.
-   **Key Features**:
    -   **Dynamic 2D Plane Processor**: A novel approach using PCA and motion compensation to transform time-series data into vector space.
    -   **Modular Wizard UI**: Step-by-step configuration for Data Source, Input Parameters, Hyperparameters, and Error Correction.
    -   **Experiment Tracking**: Automatic hashing of configurations to create unique experiment IDs. Persistence of all settings for reproducibility.
    -   **Real-time Monitoring**: Live visualization of loss, accuracy, and predictions during training.

### 3.3. Trading Engine (Trader)
-   **Status**: *In Development / Roadmap*
-   **Purpose**: To rigorously paper and live trade the Trained Models om actual market conditions.
-   **Vision**:
    -   Event-driven, tick-level simulation.
    -   Full integration with the `Trainer`'s output models.

## 4. Development Principles / "Rules" Context
-   **UI First**: If a feature is complex, build a UI for it. Avoid CLI/Scripts for core workflows.
-   **Reproducibility**: Experiments and data downloads must be metadata-rich and reproducible.
-   **Robustness**: Use Chaos Monkey testing (`Monkey` classes) to harden the UI against crashes.
