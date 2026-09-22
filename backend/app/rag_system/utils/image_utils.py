import cv2
import numpy as np
from PIL import Image, ImageEnhance, ExifTags
import os
import tempfile
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Utility class for image processing operations"""
    
    @staticmethod
    def validate_image(file_path: str) -> bool:
        """Validate if file is a valid image"""
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.error(f"Image validation failed: {str(e)}")
            return False
    
    @staticmethod
    def get_image_info(file_path: str) -> dict:
        """Get basic image information"""
        try:
            with Image.open(file_path) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
        except Exception as e:
            logger.error(f"Failed to get image info: {str(e)}")
            return {}
    
    @staticmethod
    def fix_image_orientation(image_path: str) -> str:
        """Fix image orientation based on EXIF data"""
        try:
            with Image.open(image_path) as img:
                # Check if image has EXIF data
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif = img._getexif()
                    
                    # Find orientation tag
                    orientation_tag = None
                    for tag, value in ExifTags.TAGS.items():
                        if value == 'Orientation':
                            orientation_tag = tag
                            break
                    
                    if orientation_tag and orientation_tag in exif:
                        orientation = exif[orientation_tag]
                        
                        # Rotate based on orientation
                        if orientation == 3:
                            img = img.rotate(180, expand=True)
                        elif orientation == 6:
                            img = img.rotate(270, expand=True)
                        elif orientation == 8:
                            img = img.rotate(90, expand=True)
                        
                        # Save corrected image
                        img.save(image_path, quality=95)
            
            return image_path
            
        except Exception as e:
            logger.error(f"Failed to fix image orientation: {str(e)}")
            return image_path
    
    @staticmethod
    def resize_image(image_path: str, target_size: Tuple[int, int] = (224, 224)) -> str:
        """Resize image while maintaining aspect ratio"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Calculate new size maintaining aspect ratio
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
                
                # Create new image with target size and paste resized image
                new_img = Image.new('RGB', target_size, (255, 255, 255))
                
                # Calculate position to center the image
                x = (target_size[0] - img.size[0]) // 2
                y = (target_size[1] - img.size[1]) // 2
                
                new_img.paste(img, (x, y))
                new_img.save(image_path, quality=95)
            
            return image_path
            
        except Exception as e:
            logger.error(f"Failed to resize image: {str(e)}")
            return image_path
    
    @staticmethod
    def enhance_image(image_path: str, 
                     brightness: float = 1.0,
                     contrast: float = 1.0,
                     saturation: float = 1.0,
                     sharpness: float = 1.0) -> str:
        """Enhance image quality"""
        try:
            with Image.open(image_path) as img:
                # Brightness
                if brightness != 1.0:
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(brightness)
                
                # Contrast
                if contrast != 1.0:
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(contrast)
                
                # Color (Saturation)
                if saturation != 1.0:
                    enhancer = ImageEnhance.Color(img)
                    img = enhancer.enhance(saturation)
                
                # Sharpness
                if sharpness != 1.0:
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(sharpness)
                
                img.save(image_path, quality=95)
            
            return image_path
            
        except Exception as e:
            logger.error(f"Failed to enhance image: {str(e)}")
            return image_path
    
    @staticmethod
    def remove_noise(image_path: str) -> str:
        """Remove noise from image using OpenCV"""
        try:
            # Read image
            img = cv2.imread(image_path)
            
            # Apply bilateral filter to reduce noise while preserving edges
            denoised = cv2.bilateralFilter(img, 9, 75, 75)
            
            # Save denoised image
            cv2.imwrite(image_path, denoised)
            
            return image_path
            
        except Exception as e:
            logger.error(f"Failed to remove noise: {str(e)}")
            return image_path
    
    @staticmethod
    def adjust_lighting(image_path: str) -> str:
        """Adjust image lighting using histogram equalization"""
        try:
            # Read image
            img = cv2.imread(image_path)
            
            # Convert to LAB color space
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            
            # Split channels
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels
            lab = cv2.merge([l, a, b])
            
            # Convert back to BGR
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            # Save result
            cv2.imwrite(image_path, result)
            
            return image_path
            
        except Exception as e:
            logger.error(f"Failed to adjust lighting: {str(e)}")
            return image_path
    
    @staticmethod
    def crop_center(image_path: str, crop_size: Tuple[int, int] = (224, 224)) -> str:
        """Crop image from center"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                crop_width, crop_height = crop_size
                
                # Calculate crop coordinates
                left = (width - crop_width) // 2
                top = (height - crop_height) // 2
                right = left + crop_width
                bottom = top + crop_height
                
                # Crop image
                cropped = img.crop((left, top, right, bottom))
                cropped.save(image_path, quality=95)
            
            return image_path
            
        except Exception as e:
            logger.error(f"Failed to crop image: {str(e)}")
            return image_path
    
    @staticmethod
    def preprocess_for_ml(image_path: str, target_size: Tuple[int, int] = (224, 224)) -> str:
        """Complete preprocessing pipeline for ML model"""
        try:
            # Fix orientation
            image_path = ImageProcessor.fix_image_orientation(image_path)
            
            # Resize image
            image_path = ImageProcessor.resize_image(image_path, target_size)
            
            # Enhance image quality
            image_path = ImageProcessor.enhance_image(
                image_path, 
                brightness=1.1, 
                contrast=1.1, 
                saturation=1.05
            )
            
            # Remove noise
            image_path = ImageProcessor.remove_noise(image_path)
            
            # Adjust lighting
            image_path = ImageProcessor.adjust_lighting(image_path)
            
            return image_path
            
        except Exception as e:
            logger.error(f"Failed to preprocess image for ML: {str(e)}")
            return image_path
    
    @staticmethod
    def create_thumbnail(image_path: str, thumb_size: Tuple[int, int] = (150, 150)) -> Optional[str]:
        """Create thumbnail version of image"""
        try:
            # Create thumbnail filename
            base_path, ext = os.path.splitext(image_path)
            thumb_path = f"{base_path}_thumb{ext}"
            
            with Image.open(image_path) as img:
                # Create thumbnail
                img.thumbnail(thumb_size, Image.Resampling.LANCZOS)
                
                # Save thumbnail
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.save(thumb_path, quality=85)
            
            return thumb_path
            
        except Exception as e:
            logger.error(f"Failed to create thumbnail: {str(e)}")
            return None
    
    @staticmethod
    def compress_image(image_path: str, quality: int = 85, max_size_mb: float = 2.0) -> str:
        """Compress image to reduce file size"""
        try:
            file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
            
            if file_size_mb <= max_size_mb:
                return image_path
            
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Start with specified quality
                current_quality = quality
                
                while current_quality > 10:
                    # Save with current quality to temporary file
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    img.save(temp_path, 'JPEG', quality=current_quality)
                    
                    # Check file size
                    temp_size_mb = os.path.getsize(temp_path) / (1024 * 1024)
                    
                    if temp_size_mb <= max_size_mb:
                        # Replace original with compressed version
                        os.replace(temp_path, image_path)
                        break
                    else:
                        # Remove temp file and reduce quality
                        os.unlink(temp_path)
                        current_quality -= 10
            
            return image_path
            
        except Exception as e:
            logger.error(f"Failed to compress image: {str(e)}")
            return image_path