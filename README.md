# Touch Gesture ML Pipeline (STM32 + Python + TensorFlow)

This repository contains an **end‑to‑end pipeline** for collecting touch‑gesture sensor data from an **STM32**, training a **neural network in TensorFlow**, and exporting weights for **embedded inference**.

The project is split into two main stages:

1. **Data Capture (UART → CSV)**
2. **Neural Network Training & Evaluation**

---

## Repository Contents

```
.
├── training_data_capture.py   # UART data capture + gesture filtering
├── gesture_nn.py              # Neural network training + evaluation
├── README.md
```

---

## 1. Data Capture: `training_data_capture.py`

This script connects to an STM32 over **UART**, parses normalized sensor readings, filters them using strict gesture rules, and writes **clean labeled data** to CSV.

### Data Flow

```
STM32 Sensors → UART → Python → Filtered CSV
```

### Expected UART Format

STM32 must stream data in the following format:

```
s1=0.25,s2=0.03,s3=0.02
```

- Sensor values **must already be normalized to 0.0 – 1.0**
- Each line represents a single sample

---

### Supported Gestures

Only the following gestures are allowed:

- Light Touch
- Hard Touch
- Left Light
- Left Hard
- Right Light
- Right Hard
- Middle
- Indeterminate (catch‑all)

Gesture names are **case‑sensitive** and must match exactly.

---

### Gesture Filtering

Each gesture has a strict acceptance rule (threshold‑based).

Example:
- **Left Light**
  - `s1 ∈ [0.1, 0.3]`
  - `s2 ≤ 0.1`
  - `s3 ≤ 0.1`

Samples that do **not** match the selected gesture are **discarded**.

**Indeterminate** is treated specially:
> A sample is kept *only if it matches none of the other gesture rules.*

This prevents class contamination.

---

### Install Dependencies

```bash
pip install pyserial
```

---

### Run Data Capture

```bash
python training_data_capture.py "Left Light"
```

This will create:

```
left_light.csv
```

Example output:

```csv
s1,s2,s3,gesture
0.2431,0.0214,0.0189,Left Light
0.2512,0.0198,0.0221,Left Light
```

---

### Configuration

Edit these constants at the top of `training_data_capture.py`:

```python
SERIAL_PORT = "COM4"
BAUD_RATE   = 115200
SAMPLE_SIZE = 4000
```

---

## 2. Neural Network Training: `gesture_nn.py`

This script trains a **fully‑connected neural network** using TensorFlow/Keras and evaluates it on **train / validation / test** splits.

### Model Architecture

- Input: 3 sensor values (`s1, s2, s3`)
- Hidden layer: Dense(5) + ReLU
- Output layer: Dense(8) (logits)

```text
3 → 5 → 8
```

- Loss: `SparseCategoricalCrossentropy(from_logits=True)`
- Optimizer: Adam
- Output uses **logits** (no softmax)

---

### Dataset Loading

Datasets are loaded from Hugging Face:

- `gesture_dataset_train.csv`
- `gesture_dataset_val.csv`
- `gesture_dataset_test.csv`

Each file contains:

```csv
s1,s2,s3,label
```

---

### Install Dependencies

```bash
pip install numpy pandas tensorflow
```

---

### Run Training

```bash
python gesture_nn.py
```

The script will:

1. Train for 200 epochs
2. Report final training & validation accuracy
3. Evaluate on a held‑out test set
4. Print **C‑compatible weight arrays** for embedded inference

---

### Example Output

```
Final val accuracy: 0.9825
Test accuracy: 0.9781
```

Followed by:

```c
float W1[3][5] = { ... };
float B1[5]    = { ... };
float W2[5][8] = { ... };
float B2[8]    = { ... };
```

These arrays can be copied directly into STM32 firmware.

---

## Typical Workflow

1. Flash STM32 with UART streaming firmware
2. Capture data per gesture using `training_data_capture.py`
3. Merge CSVs into labeled datasets
4. Train the network with `gesture_nn.py`
5. Export weights to C
6. Run inference on STM32
7. Validate predictions over UART

---

## Notes

- Generated CSV files should be ignored in git
- This pipeline is **intentionally strict** to keep datasets clean
- Designed for **embedded ML**, not generic serial logging

---

## License

MIT (or project‑specific)