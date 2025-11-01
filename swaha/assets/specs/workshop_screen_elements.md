There are 3 parts to the "Workshop" Screen.

The "Before Training" form is our _blueprint_, but the "During" and "After" panels are our _control room_ and _debriefing room_, respectively.

This is an exhaustive list of the parameters, metrics, and visualizations we need for both phases, based on the full complexity of our design.

---

## "Before Training" (Pre-Experiment Settings)

This is an exhaustive list of parameters required for the model's training form.

This list is designed to give the user complete experimental control over every component of the training system.

### 1. Data Source & Timeframe Parameters

These parameters define the raw data feed _before_ any processing.

- **Market Segment**: Dropdown (e.g., "NSE Equities", "NFO", "MCX"). _Default: NSE Equities._
- **Instrument List**: Text Area or File Upload (e.g., "NIFTY50_stocks.csv", or manual list "RELIANCE, HDFCBANK, TCS").
- **Time Interval**: Dropdown (e.g., "10-minute", "5-minute", "1-minute", "1-hour"). _Default: 10-minute._
- **Chart Type**: Dropdown ("Candlestick", "Heiken-Ashi"). _This selection will determine the underlying OHLCV data used for subsequent calculations._
- **Training Date Range**: Date-Range Picker (Start Date, End Date).
- **Validation Date Range**: Date-Range Picker (Start Date, End Date).

---

### 2. Dynamic Plane Transformation Parameters

This is the core of your thought experiment, defining how we normalize and reconstruct the relational 2D plane from raw T-P-V (Time, Price, Volume) data.

- **Enable Dynamic Plane**: Toggle (True/False). _If False, the model reverts to using static candlestick images (Baseline)._
- **Window Size (N)**: Integer Slider (e.g., 5 to 50). _This is the number of past data points (candles) used to compute each new dynamic plane._
- **Time Normalization Method**:
  - **Method**: Dropdown ("Fractional Elapsed Time", "Linear Index").
  - **Range**: Dropdown ("`[0, 1]`", "`[-1, 1]`"). _As discussed, `[-1, 1]` is preferred._
- **Price Normalization Method**:
  - **Method**: Dropdown ("Log Return", "Percent Return"). _Both are anchored to the start of the window._
  - **Clipping Threshold (Price)**: Dropdown (e.g., "None", "5th/95th Percentile", "1st/99th Percentile"). _This controls how extreme price spikes are handled._
  - **Range**: Dropdown ("`[-1, 1]`", "Raw Scaled").
- **Volume Normalization Method**:
  - **Method**: Dropdown ("Log-Transform + Robust Scaling (IQR)", "Log-Transform + Standard Scaling (Z-score)").
  - **Clipping Threshold (Volume)**: Dropdown (e.g., "None", "5th/95th Percentile").
  - **Range**: Dropdown ("`[-1, 1]`", "Raw Scaled").
- **Basis Method**: Dropdown ("PCA", "ICA", "Raw Normalized"). _This determines how the 2 rotational axes (X', Y') are derived from the 3D (T, P, V) normalized data._

---

### 3. Model Architecture Parameters

These parameters define the "brain" that will read the input snapshot (either static or dynamic).

- **Input Format**: Dropdown ("Image Snapshot", "Raw Numeric Vectors"). _This dictates whether we render the dynamic plane as an image for a CNN/ViT or feed the `N x 2` numeric coordinates directly._
- **Model Type**: Dropdown ("Vision Transformer (ViT)", "Convolutional Neural Network (CNN)").
- **Sequence Handling (if ViT)**:
  - **Enable Sequential Input**: Toggle (True/False). _This activates the "Picture B -> Picture A" logic._
  - **Sequence Length (S)**: Integer Slider (e.g., 2 to 10). _Number of dynamic snapshots to feed as a sequence._
  - **Sequence Handling Method**: Dropdown ("Fixed Length", "Padding + Masking"). _This corresponds to our discussion on Options A vs B._
- **Delta Features (if Sequential)**:
  - **Enable Delta Features**: Toggle (True/False).
  - **Delta Method**: Dropdown ("Feature Subtraction (Latent)", "Image Subtraction (Pixel)").
- **Network Hyperparameters**:
  - **Learning Rate**: Float Input (e.g., 0.001).
  - **Batch Size**: Integer Input (e.g., 32).
  - **Epochs**: Integer Input (e.g., 100).
  - **Optimizer**: Dropdown ("Adam", "SGD", "RMSprop").

---

### 4. Prediction Target (Label) Parameters

This section defines _what_ the model is trying to predict.

- **Prediction Target Type**: Dropdown (
  "Vectorial Movement (in Dynamic Plane)",
  "Image-to-Image (Next Dynamic Plane)",
  "Scalar Return (Regression)",
  "Signal Class (Buy/Sell/Hold)"
  ).
- **Prediction Horizon (H)**: Integer Slider (e.g., 1 to 10). _How many steps (candles) into the future to predict._
- **Target (if Vectorial)**:
  - **Vector Type**: Dropdown ("Single-Step Vector `(ΔX', ΔY')`", "Full Trajectory (H steps)").
- **Target (if Class)**:
  - **Buy Threshold (%)**: Float Input (e.g., +1.0).
  - **Sell Threshold (%)**: Float Input (e.g., -1.0).
- **Auxiliary Prediction Targets**:
  - **Predict Rally Time**: Toggle (True/False).

---

### 5. Dynamic Error Correction & Healing Parameters

This is the most advanced module, governing the "living" error-feedback loop.

- **Enable Dynamic Correction**: Toggle (True/False). _If True, activates the full error detection and healing system._
- **Error Computation Weights**:
  - `gamma_1` (Vector Deviation Weight): Slider [0.0 - 1.0].
  - `gamma_2` (Frame Shift Weight): Slider [0.0 - 1.0].
  - `alpha_1` (Vector Distance Weight): Slider [0.0 - 1.0].
  - `alpha_2` (Vector Angle Weight): Slider [0.0 - 1.0].
  - `beta_1` (PCA1 Angle Weight): Slider [0.0 - 1.0].
  - `beta_2` (PCA2 Angle Weight): Slider [0.0 - 1.0].
- **Wound Detection**:
  - **Error Buffer Size**: Integer Input (e.g., 20).
  - **Wound Threshold Multiplier (k)**: Float Input (e.g., 2.5). _Triggers correction if `MeanError > k _ StdError`.\*
- **Correction Mechanism**:
  - **Correction Step**: Float Input (e.g., 0.1). _How much to increase `correction_factor` when wounded._
  - **Max Correction Factor**: Float Input (e.g., 1.0).
- **Performance-Based Healing**:
  - **Correctness Buffer Size**: Integer Input (e.g., 20).
  - **Prediction Accuracy Method**: Dropdown ("Vector Cosine Similarity", "Directional Accuracy"). _How we define a "correct" prediction._
  - **Healing Threshold**: Float Slider (e.g., 0.75). _Starts healing if `MeanCorrectness > 75%`._
  - **Healing Rate Function**: Dropdown ("Proportional", "Linear Step"). _Determines how fast `correction_factor` decays based on `MeanCorrectness`._

---

### 6. Run & Output Parameters

- **Experiment Name**: Text Input.
- **Save Model**: Toggle (True/False).
- **Output Metrics**: Checkboxes (Loss Curve, Accuracy Curve, Sharpe Ratio, Frame Drift Log).

---

## "During Training" (Live Monitoring Dashboard)

This dashboard is for _real-time_ visibility. Its purpose is to help you identify if a training run is behaving as expected, learning effectively, or failing, so you can stop it early. It should be dominated by live-updating plots.

### 1. Run Status & Controls

- **Experiment Name**: [Text Display] (e.g., "Run_10m_HeikenAshi_ViT_Heal_v2")
- **Current Status**: [Text] (e.g., "RUNNING", "PAUSED", "COMPLETING EPOCH")
- **Elapsed Time**: [Timer] (e.g., "01:23:45")
- **Control Buttons**: [Button] (PAUSE, STOP TRAINING)

### 2. Progress Indicators

- **Epoch Progress**: [Text & Progress Bar] (e.g., "Epoch 12 / 100")
- **Batch Progress**: [Text & Progress Bar] (e.g., "Batch 1,500 / 2,500")
- **Data Throughput**: [Number] (e.g., "120 samples/sec")
- **Estimated Time Remaining (ETR)**: [Timer] (e.g., "03:15:10")

### 3. Core Performance Plots (Live Updating)

These plots show _if_ the model is learning, in the most traditional sense.

- **Plot 1: Training Loss (per Batch)**
  - **X-Axis**: Batch Number (Step)
  - **Y-Axis**: Loss Value
  - **Purpose**: To see the raw learning progress. Should be decreasing and noisy.
- **Plot 2: Validation Loss (per Epoch)**
  - **X-Axis**: Epoch Number
  - **Y-Axis**: Loss Value
  - **Purpose**: To check for generalization. This is the most important plot for identifying overfitting (when this line starts to go _up_ while training loss goes down).
- **Plot 3: Prediction Correctness (per Epoch, Train vs. Val)**
  - **X-Axis**: Epoch Number
  - **Y-Axis**: Correctness Score (e.g., `MeanCorrectness` [0.0-1.0])
  - **Lines**: Two lines (Training, Validation).
  - **Purpose**: Shows if the model is actually getting better at predicting the _true_ outcome, which (as you noted) is our "healing" signal.

### 4. Dynamic System Monitor (The "Living" System Vitals)

This is the most critical section for our unique architecture. It shows if the _dynamic rotating plane_ and _error correction_ systems are stable.

- **Plot 4: Frame Shift Error (Live)**
  - **X-Axis**: Batch Number (Step)
  - **Y-Axis**: Angle (Degrees or Radians)
  - **Lines**: Two lines: `beta_1 * theta_PCA1` (PC1 Drift) and `beta_2 * theta_PCA2` (PC2 Drift).
  - **Purpose**: To monitor frame stability. If these lines are extremely noisy or spike wildly, it means our normalization window (N) might be too small or the market is too chaotic for the PCA to be stable.
- **Plot 5: Correction & Healing (Live)**
  - **X-Axis**: Batch Number (Step)
  - **Y-Axis 1**: `Correction Factor` [0.0 - 1.0] (Line Plot)
  - **Y-Axis 2**: `Total Error` (Rolling Mean) (Line Plot)
  - **Purpose**: This is the "wound and healing" chart. We can watch the `Total Error` spike, see the `Correction Factor` ramp up in response, and then (hopefully) see the `Correction Factor` decay back to zero as the model's `Prediction Correctness` (from Plot 3) improves and the error subsides.
- **Plot 6: Error Component Contribution (Live)**
  - **X-Axis**: Batch Number (Step)
  - **Y-Axis**: Error Value (Stacked Bar or Area Chart)
  - **Components**: `Vector Distance Error`, `Vector Angle Error`, `Frame Shift Error`.
  - **Purpose**: To see _why_ the `Total Error` is high. Is the model bad at predicting distance, direction, or is the frame itself just unstable?

### 5. Live Snapshot Visualization

- **Image 1: Last Input Snapshot (Dynamic Plane)**: A visual rendering of the most recent `[N x 2]` dynamic plane image (or numeric matrix) fed into the model.
- **Image 2: Corresponding Static Chart**: The original Heiken-Ashi/Candlestick chart for the same window, for human comparison.
- **Image 3: Predicted Output (if Image-to-Image)**: If we are predicting the _next_ dynamic plane, show the model's visual output here.
- **Purpose**: A real-time sanity check to visually confirm the transformation is working and the model is seeing what we _think_ it's seeing.

---

## "After Training" (Final Evaluation Dashboard)

This is the static report generated _after_ a training run is complete. It is the final judgment on the experiment's viability.

### 1. Experiment Summary

- **Experiment Name**: [Text]
- **Final Status**: [Text] (e.g., "COMPLETED", "STOPPED BY USER", "ERROR")
- **Total Training Time**: [Text] (e.g., "04:38:52")
- **Best Model Checkpoint**: [Link] (e.g., `/models/Run_10m_HeikenAshi_ViT_Heal_v2/best_model.pth`)

### 2. Parameter Configuration (Recap)

- **Static Display**: A read-only view of _all_ the parameters selected in the "Before Training" form. This is essential for reproducibility, so you know exactly what settings produced this result.

### 3. Final Performance Plots (Full History)

- **Plot 1: Loss vs. Epoch (Train & Validation)**: The complete, high-resolution history of training and validation loss, making it easy to see the exact point of overfitting.
- **Plot 2: Prediction Correctness vs. Epoch (Train & Validation)**: The complete history of our primary "healing" metric.

### 4. Backtesting & Financial Viability Report (Test Set)

This is the ultimate test. These metrics are calculated by running the _best_ saved model over the _test set_ (data it has never seen) and simulating trades.

- **Plot 3: Equity Curve**: A line chart showing the cumulative P/L (Portfolio Value) over the test period vs. a "Buy and Hold" benchmark of the underlying (e.g., NIFTY 50).
- **Key Performance Indicators (KPIs)**:
  - **Total Return (%)**
  - **Sharpe Ratio**
  - **Sortino Ratio** (focuses on downside volatility)
  - **Calmar Ratio** (Total Return vs. Max Drawdown)
  - **Maximum Drawdown (%)**: The largest peak-to-trough drop in portfolio value.
- **Trade Statistics**:
  - **Total Trades**: [Number]
  - **Win Rate (%)**: (Number of Winning Trades / Total Trades)
  - **Loss Rate (%)**: (Number of Losing Trades / Total Trades)
  - **Profit Factor**: (Gross Profit / Gross Loss)
  - **Average Win ($/Pts)**
  - **Average Loss ($/Pts)**

### 5. Deep Dive: Dynamic System Analysis (Full History)

This section provides a post-mortem on our unique architecture's behavior over the _entire_ training run.

- **Plot 4: Correction Factor History**: A full time-series plot of the `Correction Factor`. This shows _when_ and _how often_ the system felt it was "wounded" and applied corrections.
- **Plot 5: Error Component Histogram**: A histogram showing the distribution of the four error components (`d_vec`, `theta_vec`, `theta_PCA1`, `theta_PCA2`). This tells us what _type_ of error was most common.
- **Plot 6: Frame Shift Stability Histogram**: A histogram of the `Frame Shift Error` values. A sharply peaked-at-zero distribution is good (stable frame). A wide distribution is bad (chaotic frame).

### 6. Sample Prediction Analysis (Test Set)

- **Visual Grid**: Show a grid of 10-20 sample predictions from the test set.
- **Each Sample Includes**:
  1.  **Input (Dynamic Plane)**: The snapshot fed to the model.
  2.  **Model's Prediction**: The predicted vector/image.
  3.  **Realized Outcome**: The actual vector/image that occurred.
  4.  **Error Breakdown**: (e.g., `d_vec=0.1`, `theta_vec=5°`, `frame_shift=2°`).
  5.  **Trade Result**: (e.g., "Correct (Profit)", "Incorrect (Loss)").
- **Purpose**: To build qualitative intuition. You can look at _why_ the model failed. Did it fail during high frame shifts? Did it misjudge direction or just magnitude?
