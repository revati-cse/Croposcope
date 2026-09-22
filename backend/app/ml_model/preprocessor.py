import cv2
import numpy as np
from PIL import Image, ImageEnhance
import tensorflow as tf
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    """Preprocessing pipeline for crop disease detection images"""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
        self.mean = np.array([0.485, 0.456, 0.406])  # ImageNet means
        self.std = np.array([0.229, 0.224, 0.225])   # ImageNet stds
        
    def load_image(self, image_path: str) -> np.ndarray:
        """Load image from file path"""
        try:
            # Load with PIL first to handle various formats
            pil_image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array
            image = np.array(pil_image)
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {str(e)}")
            raise
    
    def resize_image(self, image: np.ndarray) -> np.ndarray:
        """Resize image while maintaining aspect ratio"""
        h, w = image.shape[:2]
        target_h, target_w = self.target_size
        
        # Calculate scaling factor
        scale = min(target_w / w, target_h / h)
        
        # Calculate new dimensions
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Create padded image
        padded = np.full((target_h, target_w, 3), 128, dtype=np.uint8)  # Gray padding
        
        # Calculate padding offsets
        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2
        
        # Place resized image in center
        padded[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
        
        return padded
    
    def normalize_image(self, image: np.ndarray) -> np.ndarray:
        """Normalize image using ImageNet statistics"""
        # Convert to float32 and scale to [0, 1]
        image = image.astype(np.float32) / 255.0
        
        # Normalize using ImageNet statistics
        normalized = (image - self.mean) / self.std
        
        return normalized
    
    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Apply contrast enhancement using CLAHE"""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        
        # Convert back to RGB
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        return enhanced
    
    def remove_noise(self, image: np.ndarray) -> np.ndarray:
        """Remove noise using bilateral filtering"""
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        return denoised
    
    def adjust_brightness_contrast(self, image: np.ndarray, 
                                 brightness: float = 0.0, 
                                 contrast: float = 1.0) -> np.ndarray:
        """Adjust brightness and contrast"""
        adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
        return adjusted
    
    def apply_gaussian_blur(self, image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """Apply Gaussian blur for noise reduction"""
        blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        return blurred
    
    def detect_edges(self, image: np.ndarray) -> np.ndarray:
        """Detect edges using Canny edge detector"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Convert back to 3-channel
        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        
        return edges_rgb
    
    def crop_leaf_region(self, image: np.ndarray) -> np.ndarray:
        """Automatically crop to focus on leaf regions using color segmentation"""
        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Define range for green colors (leaves)
        lower_green1 = np.array([35, 40, 40])
        upper_green1 = np.array([85, 255, 255])
        
        lower_green2 = np.array([25, 40, 40])
        upper_green2 = np.array([35, 255, 255])
        
        # Create masks for green regions
        mask1 = cv2.inRange(hsv, lower_green1, upper_green1)
        mask2 = cv2.inRange(hsv, lower_green2, upper_green2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Apply morphological operations to clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find largest contour (likely the main leaf)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Add padding
            padding = 20
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)
            
            # Crop image
            cropped = image[y:y+h, x:x+w]
            
            # Resize back to target size
            cropped = cv2.resize(cropped, self.target_size)
            
            return cropped
        
        # If no leaf region found, return original resized image
        return self.resize_image(image)
    
    def augment_image(self, image: np.ndarray, augment_type: str = 'none') -> np.ndarray:
        """Apply data augmentation for training/testing robustness"""
        if augment_type == 'rotation':
            # Random rotation (-15 to 15 degrees)
            angle = np.random.uniform(-15, 15)
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, matrix, (w, h))
            return rotated
            
        elif augment_type == 'flip':
            # Random horizontal flip
            if np.random.random() > 0.5:
                flipped = cv2.flip(image, 1)
                return flipped
                
        elif augment_type == 'brightness':
            # Random brightness adjustment
            factor = np.random.uniform(0.8, 1.2)
            brightened = self.adjust_brightness_contrast(image, contrast=factor)
            return brightened
            
        elif augment_type == 'noise':
            # Add random noise
            noise = np.random.normal(0, 25, image.shape).astype(np.uint8)
            noisy = cv2.add(image, noise)
            return noisy
        
        return image
    
    def preprocess_single_image(self, image_path: str, 
                              enhance: bool = True,
                              crop_leaf: bool = False,
                              augment: str = 'none') -> np.ndarray:
        """Complete preprocessing pipeline for single image"""
        try:
            # Load image
            image = self.load_image(image_path)
            
            # Optional leaf cropping
            if crop_leaf:
                image = self.crop_leaf_region(image)
            else:
                image = self.resize_image(image)
            
            # Optional enhancement
            if enhance:
                image = self.enhance_contrast(image)
                image = self.remove_noise(image)
            
            # Optional augmentation
            if augment != 'none':
                image = self.augment_image(image, augment)
            
            # Final normalization
            normalized = self.normalize_image(image)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Failed to preprocess image {image_path}: {str(e)}")
            raise
    
    def preprocess_batch(self, image_paths: list, 
                        batch_size: int = 32,
                        enhance: bool = True) -> np.ndarray:
        """Preprocess batch of images"""
        processed_images = []
        
        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i + batch_size]
            batch_images = []
            
            for path in batch_paths:
                try:
                    processed = self.preprocess_single_image(path, enhance=enhance)
                    batch_images.append(processed)
                except Exception as e:
                    logger.warning(f"Skipping image {path} due to error: {str(e)}")
                    continue
            
            if batch_images:
                processed_images.extend(batch_images)
        
        return np.array(processed_images)
    
    def preprocess_for_inference(self, image_path: str) -> np.ndarray:
        """Optimized preprocessing for inference"""
        # Load and resize
        image = self.load_image(image_path)
        image = self.resize_image(image)
        
        # Light enhancement
        image = self.enhance_contrast(image)
        
        # Normalize
        normalized = self.normalize_image(image)
        
        # Add batch dimension
        batched = np.expand_dims(normalized, axis=0)
        
        return batched