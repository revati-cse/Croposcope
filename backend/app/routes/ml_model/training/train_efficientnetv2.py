# ml-model/training/train_efficientnetv2.py
import os
import argparse
import json
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.keras.applications import EfficientNetV2S, efficientnet  # you can choose EfficientNetV2S/V2M
from tensorflow.keras.mixed_precision import experimental as mixed_precision

def build_model(num_classes: int, input_shape=(384, 384, 3), dropout_rate=0.3):
    base = EfficientNetV2S(include_top=False, input_shape=input_shape, weights="imagenet")
    base.trainable = False  # freeze initially
    x = layers.GlobalAveragePooling2D()(base.output)
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Dense(512, activation="swish")(x)
    x = layers.BatchNormalization()(x)
    out = layers.Dense(num_classes, activation="softmax")(x)
    model = models.Model(inputs=base.input, outputs=out)
    return model

def main(args):
    # Mixed precision if requested
    if args.mixed_precision:
        policy = mixed_precision.Policy('mixed_float16')
        mixed_precision.set_policy(policy)

    train_ds = image_dataset_from_directory(
        args.data_dir,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch_size
    )
    val_ds = image_dataset_from_directory(
        args.data_dir,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch_size
    )
    class_names = train_ds.class_names
    num_classes = len(class_names)
    AUTOTUNE = tf.data.experimental.AUTOTUNE

    # Augmentations
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.08),
        layers.RandomZoom(0.08),
    ])

    def prep(ds, training=True):
        ds = ds.map(lambda x, y: (data_augmentation(x, training=training), y), num_parallel_calls=AUTOTUNE) if training else ds
        ds = ds.prefetch(AUTOTUNE)
        return ds

    train_ds = prep(train_ds, training=True)
    val_ds = prep(val_ds, training=False)

    model = build_model(num_classes, input_shape=(args.img_size, args.img_size, 3), dropout_rate=args.dropout)
    optimizer = optimizers.Adam(learning_rate=args.lr)
    model.compile(optimizer=optimizer, loss="sparse_categorical_crossentropy", metrics=["accuracy", tf.keras.metrics.AUC(name="auc")])

    # Callbacks
    os.makedirs(args.output_dir, exist_ok=True)
    checkpoint = callbacks.ModelCheckpoint(os.path.join(args.output_dir, "best_model.h5"), save_best_only=True, monitor="val_accuracy")
    reduce_lr = callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3)
    es = callbacks.EarlyStopping(monitor="val_loss", patience=8, restore_best_weights=True)
    tensorboard = callbacks.TensorBoard(log_dir=os.path.join(args.output_dir, "logs"))

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=[checkpoint, reduce_lr, es, tensorboard]
    )

    # Save class names
    with open(os.path.join(args.output_dir, "class_names.json"), "w", encoding="utf-8") as f:
        json.dump(class_names, f, ensure_ascii=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, required=True, help="path to directory with subfolders per class")
    parser.add_argument("--output-dir", type=str, default="/app/ml-model/models/saved_models")
    parser.add_argument("--img-size", type=int, default=384)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--dropout", type=float, default=0.3)
    parser.add_argument("--mixed-precision", action="store_true")
    args = parser.parse_args()
    main(args)
