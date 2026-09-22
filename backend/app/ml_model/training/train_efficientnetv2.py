import os
import sys
import json
import logging
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

import tensorflow as tf
from tensorflow.keras import layers, Model, optimizers, callbacks
from tensorflow.keras.applications import EfficientNetV2B0
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CropDiseaseTrainer:
    """Complete training pipeline for crop disease detection"""
    
    def __init__(self, config_path: str = None):
        self.config = self.load_config(config_path)
        self.model = None
        self.base_model = None
        self.history = None
        self.class_names = []
        
        # Create directories
        self.create_directories()
        
        # Set random seeds for reproducibility
        self.set_random_seeds()
    
    def load_config(self, config_path: str) -> dict:
        """Load training configuration"""
        default_config = {
            'model': {
                'input_shape': [224, 224, 3],
                'num_classes': 38,
                'dropout_rate': 0.3,
                'freeze_base': True
            },
            'training': {
                'batch_size': 32,
                'epochs': 50,
                'initial_lr': 0.001,
                'fine_tune_lr': 0.0001,
                'fine_tune_at': 20,
                'validation_split': 0.2,
                'test_split': 0.1
            },
            'data': {
                'dataset_path': 'ml-model/datasets/processed',
                'augmentation': True,
                'cache_dataset': True
            },
            'callbacks': {
                'early_stopping_patience': 10,
                'reduce_lr_patience': 5,
                'reduce_lr_factor': 0.2,
                'min_lr': 1e-7
            },
            'paths': {
                'model_save_dir': 'ml-model/models/saved_models',
                'logs_dir': 'ml-model/training/logs',
                'results_dir': 'ml-model/evaluation/results'
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def create_directories(self):
        """Create necessary directories"""
        dirs = [
            self.config['paths']['model_save_dir'],
            self.config['paths']['logs_dir'],
            self.config['paths']['results_dir']
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def set_random_seeds(self, seed: int = 42):
        """Set random seeds for reproducibility"""
        np.random.seed(seed)
        tf.random.set_seed(seed)
    
    def load_dataset(self):
        """Load and prepare dataset"""
        dataset_path = Path(self.config['data']['dataset_path'])
        
        if not dataset_path.exists():
            logger.error(f"Dataset path not found: {dataset_path}")
            raise FileNotFoundError(f"Dataset not found at {dataset_path}")
        
        # Load dataset using tf.keras.utils.image_dataset_from_directory
        logger.info("Loading dataset...")
        
        # Get all data first
        full_dataset = tf.keras.utils.image_dataset_from_directory(
            dataset_path,
            image_size=tuple(self.config['model']['input_shape'][:2]),
            batch_size=None,  # We'll batch later
            seed=42,
            shuffle=True
        )
        
        self.class_names = full_dataset.class_names
        self.config['model']['num_classes'] = len(self.class_names)
        
        logger.info(f"Found {len(self.class_names)} classes: {self.class_names}")
        
        # Split dataset
        val_split = self.config['training']['validation_split']
        test_split = self.config['training']['test_split']
        
        # Calculate sizes
        dataset_size = len(full_dataset)
        train_size = int(dataset_size * (1 - val_split - test_split))
        val_size = int(dataset_size * val_split)
        test_size = dataset_size - train_size - val_size
        
        # Split dataset
        train_dataset = full_dataset.take(train_size)
        temp_dataset = full_dataset.skip(train_size)
        val_dataset = temp_dataset.take(val_size)
        test_dataset = temp_dataset.skip(val_size)
        
        logger.info(f"Dataset split - Train: {train_size}, Val: {val_size}, Test: {test_size}")
        
        return train_dataset, val_dataset, test_dataset
    
    def preprocess_dataset(self, train_ds, val_ds, test_ds):
        """Preprocess and augment datasets"""
        batch_size = self.config['training']['batch_size']
        
        # Normalization function
        def normalize_img(image, label):
            image = tf.cast(image, tf.float32) / 255.0
            return image, label
        
        # Data augmentation for training
        if self.config['data']['augmentation']:
            data_augmentation = tf.keras.Sequential([
                layers.RandomFlip("horizontal"),
                layers.RandomRotation(0.1),
                layers.RandomZoom(0.1),
                layers.RandomBrightness(0.1),
                layers.RandomContrast(0.1),
            ])
            
            def augment_data(image, label):
                image = data_augmentation(image, training=True)
                return image, label
            
            # Apply augmentation to training set
            train_ds = train_ds.map(normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
            train_ds = train_ds.map(augment_data, num_parallel_calls=tf.data.AUTOTUNE)
        else:
            train_ds = train_ds.map(normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
        
        # Preprocess validation and test sets (no augmentation)
        val_ds = val_ds.map(normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
        test_ds = test_ds.map(normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
        
        # Batch and prefetch
        if self.config['data']['cache_dataset']:
            train_ds = train_ds.cache()
            val_ds = val_ds.cache()
        
        train_ds = train_ds.shuffle(1000).batch(batch_size).prefetch(tf.data.AUTOTUNE)
        val_ds = val_ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
        test_ds = test_ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
        
        return train_ds, val_ds, test_ds
    
    def create_model(self):
        """Create EfficientNetV2 model"""
        input_shape = tuple(self.config['model']['input_shape'])
        num_classes = self.config['model']['num_classes']
        dropout_rate = self.config['model']['dropout_rate']
        
        # Load pre-trained EfficientNetV2B0
        base_model = EfficientNetV2B0(
            input_shape=input_shape,
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model initially if specified
        base_model.trainable = not self.config['model']['freeze_base']
        
        # Add custom classification head
        inputs = tf.keras.Input(shape=input_shape)
        
        # Preprocessing (already done in dataset pipeline)
        x = base_model(inputs, training=False)
        
        # Global pooling
        x = layers.GlobalAveragePooling2D()(x)
        
        # Classification layers
        x = layers.Dropout(dropout_rate)(x)
        x = layers.Dense(512, activation='relu', name='dense_1')(x)
        x = layers.Dropout(dropout_rate)(x)
        x = layers.Dense(256, activation='relu', name='dense_2')(x)
        x = layers.Dropout(dropout_rate / 2)(x)
        
        # Output layer
        outputs = layers.Dense(num_classes, activation='softmax', name='predictions')(x)
        
        model = Model(inputs, outputs, name='EfficientNetV2_CropDisease')
        
        self.model = model
        self.base_model = base_model
        
        # Print model summary
        logger.info("Model created successfully")
        model.summary()
        
        return model
    
    def compile_model(self, learning_rate: float = None):
        """Compile model with optimizer and loss"""
        if learning_rate is None:
            learning_rate = self.config['training']['initial_lr']
        
        optimizer = optimizers.Adam(learning_rate=learning_rate)
        
        self.model.compile(
            optimizer=optimizer,
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', 'top_3_accuracy']
        )
        
        logger.info(f"Model compiled with learning rate: {learning_rate}")
    
    def get_callbacks(self):
        """Create training callbacks"""
        callbacks_list = []
        
        # Model checkpoint
        checkpoint_path = os.path.join(
            self.config['paths']['model_save_dir'],
            'efficientnetv2_crop_disease_best.h5'
        )
        
        checkpoint_cb = callbacks.ModelCheckpoint(
            checkpoint_path,
            monitor='val_accuracy',
            save_best_only=True,
            save_weights_only=False,
            verbose=1
        )
        callbacks_list.append(checkpoint_cb)
        
        # Early stopping
        early_stopping_cb = callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=self.config['callbacks']['early_stopping_patience'],
            restore_best_weights=True,
            verbose=1
        )
        callbacks_list.append(early_stopping_cb)
        
        # Reduce learning rate on plateau
        reduce_lr_cb = callbacks.ReduceLROnPlateau(
            monitor='val_accuracy',
            factor=self.config['callbacks']['reduce_lr_factor'],
            patience=self.config['callbacks']['reduce_lr_patience'],
            min_lr=self.config['callbacks']['min_lr'],
            verbose=1
        )
        callbacks_list.append(reduce_lr_cb)
        
        # TensorBoard logging
        log_dir = os.path.join(
            self.config['paths']['logs_dir'],
            f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        tensorboard_cb = callbacks.TensorBoard(
            log_dir=log_dir,
            histogram_freq=1,
            write_graph=True,
            write_images=True,
            update_freq='epoch'
        )
        callbacks_list.append(tensorboard_cb)
        
        # CSV Logger
        csv_logger_cb = callbacks.CSVLogger(
            os.path.join(self.config['paths']['logs_dir'], 'training_log.csv'),
            append=False
        )
        callbacks_list.append(csv_logger_cb)
        
        return callbacks_list
    
    def train_model(self, train_ds, val_ds):
        """Train the model with two phases"""
        epochs = self.config['training']['epochs']
        fine_tune_at = self.config['training']['fine_tune_at']
        
        # Phase 1: Train with frozen base
        logger.info("Phase 1: Training with frozen base model...")
        
        callbacks_list = self.get_callbacks()
        
        # Initial training
        history1 = self.model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=fine_tune_at,
            callbacks=callbacks_list,
            verbose=1
        )
        
        # Phase 2: Fine-tuning
        logger.info("Phase 2: Fine-tuning entire model...")
        
        # Unfreeze base model
        self.base_model.trainable = True
        
        # Use lower learning rate for fine-tuning
        fine_tune_lr = self.config['training']['fine_tune_lr']
        self.compile_model(learning_rate=fine_tune_lr)
        
        # Update checkpoint callback to save final model
        final_checkpoint_path = os.path.join(
            self.config['paths']['model_save_dir'],
            'efficientnetv2_crop_disease_final.h5'
        )
        
        callbacks_list[0] = callbacks.ModelCheckpoint(
            final_checkpoint_path,
            monitor='val_accuracy',
            save_best_only=True,
            save_weights_only=False,
            verbose=1
        )
        
        # Continue training
        history2 = self.model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=epochs,
            initial_epoch=fine_tune_at,
            callbacks=callbacks_list,
            verbose=1
        )
        
        # Combine histories
        combined_history = {}
        for key in history1.history.keys():
            combined_history[key] = history1.history[key] + history2.history[key]
        
        self.history = combined_history
        
        # Save final model
        final_model_path = os.path.join(
            self.config['paths']['model_save_dir'],
            'efficientnetv2_crop_disease.h5'
        )
        self.model.save(final_model_path)
        logger.info(f"Final model saved to {final_model_path}")
        
        return combined_history
    
    def evaluate_model(self, test_ds):
        """Evaluate model on test set"""
        logger.info("Evaluating model on test set...")
        
        # Evaluate model
        test_loss, test_accuracy, test_top3_accuracy = self.model.evaluate(test_ds, verbose=1)
        
        logger.info(f"Test Results:")
        logger.info(f"  Loss: {test_loss:.4f}")
        logger.info(f"  Accuracy: {test_accuracy:.4f}")
        logger.info(f"  Top-3 Accuracy: {test_top3_accuracy:.4f}")
        
        # Get predictions for detailed analysis
        y_pred = []
        y_true = []
        
        for images, labels in test_ds:
            predictions = self.model.predict(images, verbose=0)
            y_pred.extend(np.argmax(predictions, axis=1))
            y_true.extend(labels.numpy())
        
        # Classification report
        report = classification_report(
            y_true, y_pred,
            target_names=self.class_names,
            output_dict=True
        )
        
        # Save detailed results
        results = {
            'test_loss': float(test_loss),
            'test_accuracy': float(test_accuracy),
            'test_top3_accuracy': float(test_top3_accuracy),
            'classification_report': report,
            'class_names': self.class_names,
            'config': self.config
        }
        
        # Save results to file
        results_path = os.path.join(
            self.config['paths']['results_dir'],
            'evaluation_results.json'
        )
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Detailed results saved to {results_path}")
        
        return results
    
    def plot_training_history(self):
        """Plot training history"""
        if self.history is None:
            logger.warning("No training history available")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Training History', fontsize=16)
        
        # Accuracy
        axes[0, 0].plot(self.history['accuracy'], label='Training Accuracy')
        axes[0, 0].plot(self.history['val_accuracy'], label='Validation Accuracy')
        axes[0, 0].set_title('Model Accuracy')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Loss
        axes[0, 1].plot(self.history['loss'], label='Training Loss')
        axes[0, 1].plot(self.history['val_loss'], label='Validation Loss')
        axes[0, 1].set_title('Model Loss')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Top-3 Accuracy
        axes[1, 0].plot(self.history['top_3_accuracy'], label='Training Top-3 Accuracy')
        axes[1, 0].plot(self.history['val_top_3_accuracy'], label='Validation Top-3 Accuracy')
        axes[1, 0].set_title('Top-3 Accuracy')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Top-3 Accuracy')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Learning rate (if available)
        if 'lr' in self.history:
            axes[1, 1].plot(self.history['lr'], label='Learning Rate')
            axes[1, 1].set_title('Learning Rate Schedule')
            axes[1, 1].set_xlabel('Epoch')
            axes[1, 1].set_ylabel('Learning Rate')
            axes[1, 1].set_yscale('log')
            axes[1, 1].legend()
            axes[1, 1].grid(True)
        else:
            axes[1, 1].axis('off')
        
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(
            self.config['paths']['results_dir'],
            'training_history.png'
        )
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info(f"Training history plot saved to {plot_path}")
    
    def save_model_artifacts(self):
        """Save model artifacts"""
        artifacts_dir = Path(self.config['paths']['model_save_dir'])
        
        # Save class names
        class_names_path = artifacts_dir / 'class_names.json'
        with open(class_names_path, 'w') as f:
            json.dump(self.class_names, f, indent=2)
        
        # Save model metadata
        metadata = {
            'version': '1.0',
            'architecture': 'EfficientNetV2B0',
            'input_shape': self.config['model']['input_shape'],
            'num_classes': len(self.class_names),
            'class_names': self.class_names,
            'training_config': self.config,
            'training_date': datetime.now().isoformat(),
            'framework': 'TensorFlow',
            'framework_version': tf.__version__
        }
        
        metadata_path = artifacts_dir / 'model_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("Model artifacts saved successfully")

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description='Train Crop Disease Detection Model')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--dataset', type=str, help='Path to dataset directory')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    
    args = parser.parse_args()
    
    try:
        # Initialize trainer
        trainer = CropDiseaseTrainer(config_path=args.config)
        
        # Override config with command line arguments
        if args.dataset:
            trainer.config['data']['dataset_path'] = args.dataset
        if args.epochs:
            trainer.config['training']['epochs'] = args.epochs
        if args.batch_size:
            trainer.config['training']['batch_size'] = args.batch_size
        if args.lr:
            trainer.config['training']['initial_lr'] = args.lr
        
        # Load and preprocess dataset
        logger.info("Loading dataset...")
        train_ds, val_ds, test_ds = trainer.load_dataset()
        train_ds, val_ds, test_ds = trainer.preprocess_dataset(train_ds, val_ds, test_ds)
        
        # Create and compile model
        logger.info("Creating model...")
        trainer.create_model()
        trainer.compile_model()
        
        # Train model
        logger.info("Starting training...")
        trainer.train_model(train_ds, val_ds)
        
        # Evaluate model
        logger.info("Evaluating model...")
        trainer.evaluate_model(test_ds)
        
        # Plot results
        trainer.plot_training_history()
        
        # Save artifacts
        trainer.save_model_artifacts()
        
        logger.info("Training completed successfully!")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()