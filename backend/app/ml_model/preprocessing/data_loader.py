import os
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
import tensorflow as tf
from sklearn.model_selection import train_test_split
from typing import Tuple, List, Dict, Optional
import logging
import json
from concurrent.futures import ThreadPoolExecutor
import shutil

logger = logging.getLogger(__name__)

class PlantVillageDataLoader:
    """Data loader for PlantVillage dataset and other crop disease datasets"""
    
    def __init__(self, 
                 raw_data_path: str = "ml-model/datasets/raw",
                 processed_data_path: str = "ml-model/datasets/processed",
                 image_size: Tuple[int, int] = (224, 224),
                 val_split: float = 0.2,
                 test_split: float = 0.1):
        
        self.raw_data_path = Path(raw_data_path)
        self.processed_data_path = Path(processed_data_path)
        self.image_size = image_size
        self.val_split = val_split
        self.test_split = test_split
        
        # Create directories
        self.processed_data_path.mkdir(parents=True, exist_ok=True)
        
        # Dataset statistics
        self.class_counts = {}
        self.total_images = 0
        self.class_names = []
        
    def download_plantvillage_dataset(self):
        """Download PlantVillage dataset from Kaggle"""
        try:
            import kaggle
            
            # Download dataset
            dataset_name = "emmarex/plantdisease"
            download_path = self.raw_data_path
            
            logger.info(f"Downloading PlantVillage dataset to {download_path}")
            
            kaggle.api.dataset_download_files(
                dataset_name, 
                path=download_path, 
                unzip=True
            )
            
            logger.info("Dataset downloaded successfully")
            
        except ImportError:
            logger.error("Kaggle API not installed. Install with: pip install kaggle")
            raise
        except Exception as e:
            logger.error(f"Failed to download dataset: {str(e)}")
            raise
    
    def scan_dataset_structure(self, dataset_path: Path) -> Dict[str, int]:
        """Scan dataset directory structure and count images per class"""
        class_counts = {}
        total_images = 0
        
        if not dataset_path.exists():
            logger.error(f"Dataset path does not exist: {dataset_path}")
            return class_counts
        
        # Look for class directories
        for class_dir in dataset_path.iterdir():
            if class_dir.is_dir() and not class_dir.name.startswith('.'):
                # Count images in class directory
                image_count = 0
                for img_file in class_dir.iterdir():
                    if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                        image_count += 1
                
                if image_count > 0:
                    class_counts[class_dir.name] = image_count
                    total_images += image_count
                    
                    logger.info(f"Found class '{class_dir.name}': {image_count} images")
        
        self.class_counts = class_counts
        self.total_images = total_images
        self.class_names = list(class_counts.keys())
        
        logger.info(f"Total dataset: {len(self.class_names)} classes, {total_images} images")
        
        return class_counts
    
    def validate_image(self, image_path: Path) -> bool:
        """Validate if image file is readable and not corrupted"""
        try:
            # Try to read with OpenCV
            img = cv2.imread(str(image_path))
            if img is None:
                return False
            
            # Check if image has valid dimensions
            if img.shape[0] < 32 or img.shape[1] < 32:
                return False
            
            return True
            
        except Exception:
            return False
    
    def process_single_image(self, 
                           src_path: Path, 
                           dst_path: Path, 
                           resize: bool = True) -> bool:
        """Process and copy single image"""
        try:
            # Validate image
            if not self.validate_image(src_path):
                logger.warning(f"Invalid image skipped: {src_path}")
                return False
            
            # Create destination directory
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            if resize:
                # Load and resize image
                img = cv2.imread(str(src_path))
                img = cv2.resize(img, self.image_size, interpolation=cv2.INTER_LANCZOS4)
                
                # Save processed image
                cv2.imwrite(str(dst_path), img, [cv2.IMWRITE_JPEG_QUALITY, 95])
            else:
                # Just copy the file
                shutil.copy2(src_path, dst_path)
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to process image {src_path}: {str(e)}")
            return False
    
    def balance_dataset(self, 
                       class_counts: Dict[str, int], 
                       method: str = 'undersample',
                       max_samples_per_class: int = 1000) -> Dict[str, int]:
        """Balance dataset by under/oversampling"""
        
        if method == 'undersample':
            # Use minimum class count or specified max
            target_count = min(min(class_counts.values()), max_samples_per_class)
            balanced_counts = {class_name: target_count for class_name in class_counts.keys()}
            
        elif method == 'oversample':
            # Use maximum class count
            target_count = max(class_counts.values())
            balanced_counts = {class_name: target_count for class_name in class_counts.keys()}
            
        elif method == 'fixed':
            # Use fixed number per class
            balanced_counts = {class_name: max_samples_per_class for class_name in class_counts.keys()}
            
        else:
            # No balancing
            balanced_counts = class_counts.copy()
        
        logger.info(f"Balancing strategy '{method}': {target_count if method != 'none' else 'no balancing'} samples per class")
        
        return balanced_counts
    
    def create_balanced_dataset(self, 
                              source_path: Path,
                              target_counts: Dict[str, int],
                              augment_minority: bool = True):
        """Create balanced dataset in processed directory"""
        
        processed_counts = {}
        
        for class_name, target_count in target_counts.items():
            class_src_dir = source_path / class_name
            class_dst_dir = self.processed_data_path / class_name
            
            if not class_src_dir.exists():
                logger.warning(f"Source class directory not found: {class_src_dir}")
                continue
            
            # Get all valid images from source
            source_images = []
            for img_file in class_src_dir.iterdir():
                if (img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp'] and 
                    self.validate_image(img_file)):
                    source_images.append(img_file)
            
            source_count = len(source_images)
            logger.info(f"Processing class '{class_name}': {source_count} source images -> {target_count} target images")
            
            # Create destination directory
            class_dst_dir.mkdir(parents=True, exist_ok=True)
            
            # Process images
            if source_count >= target_count:
                # Undersample: randomly select subset
                np.random.shuffle(source_images)
                selected_images = source_images[:target_count]
            else:
                # Oversample: use all images and repeat/augment
                selected_images = source_images.copy()
                
                # Repeat images to reach target count
                while len(selected_images) < target_count:
                    remaining = target_count - len(selected_images)
                    to_add = min(remaining, source_count)
                    selected_images.extend(source_images[:to_add])
            
            # Process and save images
            processed_count = 0
            for i, src_img in enumerate(selected_images):
                dst_path = class_dst_dir / f"{class_name}_{i:04d}.jpg"
                
                if self.process_single_image(src_img, dst_path, resize=True):
                    processed_count += 1
            
            processed_counts[class_name] = processed_count
            logger.info(f"Processed {processed_count} images for class '{class_name}'")
        
        return processed_counts
    
    def split_dataset(self, 
                     processed_path: Path = None,
                     stratify: bool = True) -> Tuple[List, List, List]:
        """Split processed dataset into train/val/test sets"""
        
        if processed_path is None:
            processed_path = self.processed_data_path
        
        # Collect all image paths and labels
        image_paths = []
        labels = []
        class_to_idx = {}
        
        # Create class mapping
        class_dirs = [d for d in processed_path.iterdir() if d.is_dir()]
        class_dirs.sort()  # Ensure consistent ordering
        
        for idx, class_dir in enumerate(class_dirs):
            class_name = class_dir.name
            class_to_idx[class_name] = idx
            
            # Collect images from this class
            for img_file in class_dir.iterdir():
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    image_paths.append(str(img_file))
                    labels.append(idx)
        
        # Convert to numpy arrays
        image_paths = np.array(image_paths)
        labels = np.array(labels)
        
        logger.info(f"Total images for splitting: {len(image_paths)}")
        logger.info(f"Classes: {list(class_to_idx.keys())}")
        
        # First split: separate test set
        X_temp, X_test, y_temp, y_test = train_test_split(
            image_paths, labels,
            test_size=self.test_split,
            stratify=labels if stratify else None,
            random_state=42
        )
        
        # Second split: separate train and validation
        val_size_adjusted = self.val_split / (1 - self.test_split)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_size_adjusted,
            stratify=y_temp if stratify else None,
            random_state=42
        )
        
        # Create split information
        splits = {
            'train': {'paths': X_train.tolist(), 'labels': y_train.tolist()},
            'val': {'paths': X_val.tolist(), 'labels': y_val.tolist()},
            'test': {'paths': X_test.tolist(), 'labels': y_test.tolist()},
            'class_to_idx': class_to_idx,
            'idx_to_class': {v: k for k, v in class_to_idx.items()}
        }
        
        # Save split information
        splits_file = processed_path / 'dataset_splits.json'
        with open(splits_file, 'w') as f:
            json.dump(splits, f, indent=2)
        
        logger.info(f"Dataset split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
        logger.info(f"Split information saved to {splits_file}")
        
        return X_train, X_val, X_test
    
    def create_tensorflow_dataset(self, 
                                image_paths: List[str], 
                                labels: List[int],
                                batch_size: int = 32,
                                shuffle: bool = True,
                                cache: bool = False) -> tf.data.Dataset:
        """Create TensorFlow dataset from image paths and labels"""
        
        def load_and_preprocess_image(path, label):
            # Load image
            image = tf.io.read_file(path)
            image = tf.image.decode_image(image, channels=3)
            image = tf.image.convert_image_dtype(image, tf.float32)
            
            # Resize if necessary
            image = tf.image.resize(image, self.image_size)
            
            return image, label
        
        # Create dataset
        dataset = tf.data.Dataset.from_tensor_slices((image_paths, labels))
        
        if shuffle:
            dataset = dataset.shuffle(buffer_size=len(image_paths))
        
        # Map preprocessing function
        dataset = dataset.map(
            load_and_preprocess_image,
            num_parallel_calls=tf.data.AUTOTUNE
        )
        
        if cache:
            dataset = dataset.cache()
        
        # Batch and prefetch
        dataset = dataset.batch(batch_size)
        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        
        return dataset
    
    def save_dataset_statistics(self, processed_counts: Dict[str, int]):
        """Save dataset statistics and metadata"""
        
        stats = {
            'total_images': sum(processed_counts.values()),
            'num_classes': len(processed_counts),
            'class_counts': processed_counts,
            'class_names': list(processed_counts.keys()),
            'image_size': self.image_size,
            'splits': {
                'validation_split': self.val_split,
                'test_split': self.test_split,
                'train_split': 1 - self.val_split - self.test_split
            },
            'processing_info': {
                'resize_method': 'LANCZOS4',
                'jpeg_quality': 95,
                'validation_performed': True
            }
        }
        
        # Save statistics
        stats_file = self.processed_data_path / 'dataset_statistics.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Dataset statistics saved to {stats_file}")
        
        return stats
    
    def prepare_complete_dataset(self, 
                               download: bool = False,
                               balance_method: str = 'undersample',
                               max_samples_per_class: int = 1000):
        """Complete pipeline to prepare dataset for training"""
        
        logger.info("Starting complete dataset preparation pipeline...")
        
        # Step 1: Download dataset if requested
        if download:
            self.download_plantvillage_dataset()
        
        # Step 2: Find dataset directory
        possible_paths = [
            self.raw_data_path / "PlantVillage",
            self.raw_data_path / "plantvillage",
            self.raw_data_path / "plant_village",
            self.raw_data_path / "New Plant Diseases Dataset(Augmented)",
            self.raw_data_path
        ]
        
        dataset_path = None
        for path in possible_paths:
            if path.exists() and any(path.iterdir()):
                dataset_path = path
                break
        
        if dataset_path is None:
            raise FileNotFoundError(f"No dataset found in {self.raw_data_path}")
        
        logger.info(f"Using dataset from: {dataset_path}")
        
        # Step 3: Scan dataset structure
        class_counts = self.scan_dataset_structure(dataset_path)
        
        if not class_counts:
            raise ValueError("No valid classes found in dataset")
        
        # Step 4: Balance dataset
        target_counts = self.balance_dataset(
            class_counts, 
            method=balance_method,
            max_samples_per_class=max_samples_per_class
        )
        
        # Step 5: Create processed dataset
        processed_counts = self.create_balanced_dataset(
            dataset_path, 
            target_counts
        )
        
        # Step 6: Split dataset
        X_train, X_val, X_test = self.split_dataset()
        
        # Step 7: Save statistics
        stats = self.save_dataset_statistics(processed_counts)
        
        logger.info("Dataset preparation completed successfully!")
        logger.info(f"Final dataset: {stats['num_classes']} classes, {stats['total_images']} images")
        
        return {
            'train_paths': X_train,
            'val_paths': X_val, 
            'test_paths': X_test,
            'statistics': stats
        }

def main():
    """Main function for dataset preparation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Prepare PlantVillage Dataset')
    parser.add_argument('--download', action='store_true', help='Download dataset from Kaggle')
    parser.add_argument('--raw_path', type=str, default='ml-model/datasets/raw', 
                       help='Raw dataset path')
    parser.add_argument('--processed_path', type=str, default='ml-model/datasets/processed',
                       help='Processed dataset path') 
    parser.add_argument('--balance', type=str, default='undersample',
                       choices=['undersample', 'oversample', 'fixed', 'none'],
                       help='Dataset balancing method')
    parser.add_argument('--max_samples', type=int, default=1000,
                       help='Maximum samples per class')
    parser.add_argument('--image_size', type=int, nargs=2, default=[224, 224],
                       help='Target image size (height width)')
    
    args = parser.parse_args()
    
    # Initialize data loader
    loader = PlantVillageDataLoader(
        raw_data_path=args.raw_path,
        processed_data_path=args.processed_path,
        image_size=tuple(args.image_size)
    )
    
    try:
        # Prepare dataset
        result = loader.prepare_complete_dataset(
            download=args.download,
            balance_method=args.balance,
            max_samples_per_class=args.max_samples
        )
        
        print("Dataset preparation completed successfully!")
        print(f"Classes: {result['statistics']['num_classes']}")
        print(f"Total images: {result['statistics']['total_images']}")
        
    except Exception as e:
        logger.error(f"Dataset preparation failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()