import base64
import random
from typing import List

# Mock Qwen-VL integration
# In a real scenario, you would call the Alibaba Cloud Model Studio API here.

def analyze_image(image_base64: str):
    """
    Mock function to analyze image using Qwen-VL.
    Returns generated tags and a mock cropped image url.
    """
    # Simulate processing delay? No need for mock.
    
    # Mock Tags
    possible_tags = ["Park", "Family", "Sunset", "Beach", "Food", "Travel", "2024", "Memory", "Happy"]
    generated_tags = random.sample(possible_tags, 3)
    
    # Mock Cropped Image URL (just return the original or a placeholder)
    # In reality, this would be a URL to the processed image stored in Object Storage (OSS/S3)
    # For this simplified local version, we assume the frontend handles the display or we return a static placeholder.
    cropped_image_url = "https://via.placeholder.com/300x300?text=Smart+Crop"
    
    return {
        "tags": generated_tags,
        "cropped_image_url": cropped_image_url
    }
