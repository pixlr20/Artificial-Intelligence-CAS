import tensorflow as tf
model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(
            64, (3, 3), activation='relu', input_shape=(30, 30, 3)
        ),

        tf.keras.layers.MaxPool2D(pool_size=(2,2)),

        tf.keras.layers.Flatten(),

        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),

        tf.keras.layers.Dense(3, activation='sigmoid')
    ])
for layer in model.layers:
    print(layer.output_shape)