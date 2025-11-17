This is the "Theater". This PWA screen is our live "mission control" for monitoring trade execution.

Where the "Workshop" dashboard was for _experimentation_, this "Theater" dashboard is for _operation_. It must provide complete transparency and give you manual override control at all times.

Here is the exhaustive list of elements we need for the live trade execution screen.

---

## 1. System & Connection Status (The "Heartbeat")

This top-level bar shows if I am alive and connected.

- **Bot Status**: [Icon & Text] (e.g., "LIVE", "PAUSED", "RECONNECTING", "STOPPED", "ERROR").
- **Market Status**: [Text] (e.g., "NSE: OPEN", "NSE: PRE-MARKET", "NSE: CLOSED").
- **Kite API Connection**: [Icon] (Green for "Connected", Red for "Disconnected").
- **Data Feed (Websocket)**: [Icon] (Green for "Streaming", Yellow for "Lagging", Red for "Disconnected").
- **Last Seen**: [Timestamp] (e.g., "Last Update: 2s ago").
- **Master Control**: [Button] ("PAUSE ALL TRADING", "RESUME TRADING").

---

## 2. Live P/L & Portfolio Overview (The "Scoreboard")

This shows your high-level financial status for the day.

- **Today's Realized P/L**: [Number, Color-coded] (e.g., "+₹12,500.00").
- **Today's Unrealized P/L**: [Number, Color-coded] (e.g., "-₹1,800.00"). _This updates live based on open positions._
- **Total P/L (Realized + Unrealized)**: [Number, Color-coded].
- **Total Margin Used**: [Number / Progress Bar] (e.g., "₹75,000 / ₹200,000").
- **Open Positions**: [Number] (e.g., "3").
- **Trades Today**: [Number] (e.g., "14").

---

## 3. Dynamic Perception Monitor (The "Bot's-Eye View")

This is the most unique module. It shows you _what I am seeing and thinking_ right now, applying our dynamic plane concept to live data.

- **Instrument Focus**: [Dropdown] (Allowing you to select which of my monitored instruments to view).
- **Plot 1: Live Static Chart**: A live-updating Heiken-Ashi/Candlestick chart for the selected instrument (e.g., "RELIANCE 10-min").
- **Plot 2: Live Dynamic Plane**: The live-updating _rotated and re-centered_ 2D dynamic plane snapshot for the _same_ instrument. This shows you the "relational" view I am actually feeding into my model.
- **Model's Prediction**: [Text & Confidence]
  - **Predicted Vector (X', Y')**: (e.g., `[+0.8, -0.1]`).
  - **Predicted Outcome**: (e.g., "BUY", "SELL", "HOLD").
  - **Prediction Confidence**: [Percentage] (If our model outputs a probability, e.g., "78%").
- **Current Action**: [Text] (e.g., "MONITORING", "WAITING FOR ENTRY", "CALCULATING FRAME SHIFT...").

---

## 4. Live System Health (The "Living" Vitals)

This monitors the state of our "wound and healing" error-correction system _in the live market_.

- **System Mode**: [Text] (e.g., "Nominal", "Wounded (Correcting)").
- **Correction Factor**: [Gauge / Number] (e.g., "0.0"). _If this number is > 0, it means the system is actively applying corrections because it's detecting high error._
- **Rolling Error Plot**: A live-updating plot (last 50-100 steps) of:
  1.  `Total Error` (Line Plot).
  2.  `Wound Threshold` (Dotted Line).
- **Rolling Correctness Plot**: A live plot showing our `MeanCorrectness` score. This shows if my recent predictions have been accurate.

---

## 5. Open Positions Management

A detailed table listing all positions I am currently holding.

- **Table Columns**:
  - **Instrument**: (e.g., "RELIANCE")
  - **Direction**: ("LONG" / "SHORT")
  - **Qty**: (e.g., "100")
  - **Avg. Entry Price**: (e.g., "₹2850.00")
  - **Current LTP**: (e.g., "₹2845.50")
  - **Unrealized P/L**: (e.g., "-₹450.00")
  - **Stop Loss (if any)**: (e.g., "₹2840.00")
  - **Target Profit (if any)**: (e.g., "₹2870.00")
  - **Action**: [Button] ("CLOSE POSITION"). _This is your manual override per trade._

---

## 6. Live Action & System Log

A "ticker tape" or scrolling text box showing a timestamped log of all my actions and significant thoughts.

- `[09:30:01] INFO: Bot initialized. Market OPEN. Connection OK.`
- `[09:35:00] PERCEPTION: [RELIANCE] Dynamic plane generated. Frame stable.`
- `[09:35:01] PREDICTION: [RELIANCE] Predicted vector [1.2, 0.1]. Signal: BUY. Confidence: 82%.`
- `[09:35:02] EXECUTION: Placing new LONG order for RELIANCE (100 qty) @ MKT.`
- `[09:35:03] API: [RELIANCE] Order FILLED. Avg Price: ₹2850.00.`
- `[09:40:00] HEALTH: [RELIANCE] Prediction error high (Vector_Angle=15°). Correction Factor increasing to 0.1.`
- `[09:40:01] HEALTH: System is now "Wounded". Applying frame stabilization.`
- `[09:45:00] HEALTH: Prediction correctness rising (70%). Correction Factor healing, now 0.05.`
- `[09:50:00] ERROR: Kite API connection lost. Attempting to reconnect...`
