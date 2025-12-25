import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models

TRAIN_CSV = "gesture_dataset_train.csv"
VALIDATION_CSV   = "gesture_dataset_val.csv"
TEST_CSV  = "gesture_dataset_test.csv"

def load_dataset(file_name):
    url = f"https://huggingface.co/datasets/jsherman10/gesture_dataset/resolve/main/{file_name}"
    dataset = pd.read_csv(url)
    x = dataset[["s1", "s2", "s3"]].to_numpy(dtype=np.float32)
    y = dataset["label"].to_numpy(dtype=np.int32)
    return x, y

def evaluate_test(model, X_test, y_test):
    """Evaluate the model on the held-out test split."""
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print("Test accuracy:", test_acc)
    return test_loss, test_acc

# print out weight matrices help with chatGPT here
def print_weights_in_c(model):
    W1, B1 = model.get_layer("hidden").get_weights()
    W2, B2 = model.get_layer("output").get_weights()

    def print_c_2d(name, A):
        r, c = A.shape
        print(f"float {name}[{r}][{c}] = {{")
        for i in range(r):
            row = ", ".join(f"{A[i,j]:.9f}f" for j in range(c))
            print(f"  {{ {row} }},")
        print("};\n")

    def print_c_1d(name, v):
        n = v.shape[0]
        row = ", ".join(f"{v[i]:.9f}f" for i in range(n))
        print(f"float {name}[{n}] = {{ {row} }};\n")


    print_c_2d("W1", W1)
    print_c_1d("B1", B1)
    print_c_2d("W2", W2)
    print_c_1d("B2", B2)


def main():
    x_train, y_train = load_dataset(TRAIN_CSV)
    x_validation, y_validation   = load_dataset(VALIDATION_CSV)
    x_test,  y_test  = load_dataset(TEST_CSV)

    model = models.Sequential([
        layers.Input(shape=(3,)),
        layers.Dense(5, activation="relu", name="hidden"),
        layers.Dense(8, activation=None, name="output"),
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"]
    )

    history = model.fit(
        x_train, y_train,
        validation_data=(x_validation, y_validation),
        epochs=200,
        batch_size=128,
        verbose=1
    )

    print("Final val accuracy:", history.history["val_accuracy"][-1])
    evaluate_test(model, x_test, y_test)
    print_weights_in_c(model)



if __name__ == "__main__":
    main()