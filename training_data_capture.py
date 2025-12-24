import serial
import sys
import time
import csv
import os

SERIAL_PORT = "COM4"
BAUD_RATE = 115200
SAMPLE_SIZE = 2000
GESTURES = [
    'Light Touch',
    'Hard Touch',
    'Left Light',
    'Left Hard',
    'Right Light',
    'Right Hard',
    'Middle',
    'Indeterminate'
]


def is_left_light(s1,s2,s3):   return (0.1 <= s1 <= 0.3) and (s2 <= 0.1) and (s3 <= 0.1)
def is_right_light(s1,s2,s3):  return (s1 <= 0.1) and (s2 <= 0.1) and (0.1 <= s3 <= 0.3)
def is_middle(s1,s2,s3):       return (s1 <= 0.2) and (s2 >= 0.7) and (s3 <= 0.2)
def is_left_hard(s1,s2,s3):    return (s1 >= 0.7) and (s2 <= 0.3) and (s3 <= 0.2)
def is_right_hard(s1,s2,s3):   return (s1 <= 0.2) and (s2 <= 0.3) and (s3 >= 0.7)
def is_hard(s1,s2,s3):         return (s1 >= 0.7) and (s2 >= 0.7) and (s3 >= 0.7)
def is_light(s1,s2,s3):        return (s1 <= 0.3) and (s2 <= 0.3) and (s3 <= 0.3)
def is_indeterminate(s1, s2, s3):  return not any(rule(s1, s2, s3) for rule in [is_left_light, is_right_light, is_middle, is_left_hard, is_right_hard, is_hard, is_light])



GESTURE_FUNCTION_NAME_DICT = {
    "Light Touch": is_light,
    "Hard Touch": is_hard,
    "Left Light": is_left_light,
    "Left Hard": is_left_hard,
    "Right Light": is_right_light,
    "Right Hard": is_right_hard,
    "Middle": is_middle,
    "Indeterminate": is_indeterminate,
}

def parse_line(line: str):

    line = line.strip()
    if not line:
        return None
    try:
        p = line.split(",")
        return (
            float(p[0].split("=")[1]),
            float(p[1].split("=")[1]),
            float(p[2].split("=")[1]),
        )
    except:
        return None

def main():
    if len(sys.argv) != 2:
        print('Usage: python capture_gesture.py "Gesture Name"')
        print("Allowed gestures:")
        for gesture in GESTURES:
            print(f"  - \"{gesture}\"")
        sys.exit(1)

    gesture_input = sys.argv[1].strip()

    if gesture_input not in GESTURES:
        print(f"❌ Invalid gesture: '{sys.argv[1]}'")
        print("Allowed gestures:")
        for gesture in GESTURES:
            print(f"  - \"{gesture}\"")
        sys.exit(1)

    filename = gesture_input.lower().replace(" ", "_") + ".csv"
    gesture_validation_function = GESTURE_FUNCTION_NAME_DICT[gesture_input]

    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

    try:
        time.sleep(1.5)
        ser.reset_input_buffer()
        file_exists = os.path.isfile(filename)

        with open(filename, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["s1", "s2", "s3", "gesture"])
                
            valid_data_points = 0

            while True:
                raw_line = ser.readline().decode("utf-8", errors="ignore")
                parsed_line = parse_line(raw_line)
                if parsed_line is None:
                    continue

                s1, s2, s3 = parsed_line

                if not gesture_validation_function(s1, s2, s3):
                    continue

                writer.writerow([f"{s1:.4f}", f"{s2:.4f}", f"{s3:.4f}", gesture_input])
                valid_data_points += 1
                print(f"Num valid: {valid_data_points} | value=({s1:.3f}, {s2:.3f}, {s3:.3f})")

                
                if SAMPLE_SIZE and valid_data_points >= SAMPLE_SIZE:
                    print(f"Reached {SAMPLE_SIZE} kept samples. Done.")
                    break

    finally:
        ser.close()


if __name__ == "__main__":
    main()