# Touch Gesture Data Capture (STM32 + Python)

This repository contains a **Python-based data capture pipeline** for collecting touch/gesture sensor data streamed over **UART from an STM32** and saving **clean, filtered training data** for machine-learning models.

The system is designed to:
- Read deterministic UART output from an STM32
- Validate and filter samples by gesture-specific rules
- Save normalized sensor data (`0..1`) to CSV
- Keep datasets clean and consistent for NN training

---

## Overview

**Data flow:**

```
STM32 Sensors → UART → Python Script → Filtered CSV → ML Training
```

- STM32 sends sensor data in a fixed format:
  ```
  s1=0.5,s2=0.5,s3=0.5
  ```
- Python script:
  - Parses each line
  - Applies gesture-specific filtering rules
  - Saves only valid samples
  - Drops noisy / mislabeled data automatically

---

## Supported Gestures

Only the following gestures are allowed:

- Light Touch
- Hard Touch
- Left Light
- Left Hard
- Right Light
- Right Hard
- Middle
- Indeterminate (catch-all / none-of-the-above)

Gesture names are **case-insensitive** on the command line.

---

## Sensor Value Assumptions

- UART sensor values are **normalized to `0..1`**
- Example:
  ```
  s1=0.25,s2=0.03,s3=0.02
  ```
- All filtering rules operate directly in `0..1` space

---

## Gesture Filtering Rules

Each gesture has a strict acceptance rule.  
Samples that do **not** match the selected gesture are **discarded**.

Example rules (simplified):

- **Left Light**
  - `s1 ∈ [0.1, 0.3]`
  - `s2 ≤ 0.1`
  - `s3 ≤ 0.1`

- **Hard Touch**
  - `s1 ≥ 0.7`
  - `s2 ≥ 0.7`
  - `s3 ≥ 0.7`

### Indeterminate (Catch-All)

`Indeterminate` is treated as **none-of-the-above**:

> A sample is kept *only if it does not match ANY other gesture rule.*

This prevents clean gesture data from polluting the indeterminate class.

---

## Usage

### Install dependencies
```bash
pip install pyserial
```

### Run data capture
```bash
python capture_gesture.py "Left Light"
```

This will create:
```
left_light.csv
```

### Example output CSV
```csv
s1,s2,s3,gesture
0.2431,0.0214,0.0189,Left Light
0.2512,0.0198,0.0221,Left Light
```

- Values are saved in **0..1**
- Only valid samples are written

---

## Configuration

Edit these constants at the top of `capture_gesture.py` if needed:

```python
SERIAL_PORT = "COM5"
BAUD_RATE   = 115200
MAX_SAMPLES = 2000   # 0 = unlimited
```

---

## File Naming Convention

Output files are generated automatically:

```
<gesture_name_lowercase_with_underscores>.csv
```

Examples:
- `left_light.csv`
- `hard_touch.csv`
- `indeterminate.csv`

---

## Version Control

Generated CSV files are ignored via `.gitignore`:

```gitignore
*.csv
```

If CSVs were previously committed, remove them with:
```bash
git rm --cached *.csv
```

---

## Intended Use

This repo is intended for:
- Collecting clean training data
- Feeding TensorFlow / PyTorch models
- Exporting weights to embedded inference (STM32)

It is **not** a general-purpose serial logger — it is intentionally strict to keep datasets high-quality.

---

## Typical Workflow

1. Capture data for each gesture
2. Combine CSVs into a training dataset
3. Train NN (Python)
4. Export weights
5. Run inference on STM32
6. Validate predictions over UART
