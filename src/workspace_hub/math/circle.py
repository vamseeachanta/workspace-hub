import math
from typing import Dict

def calculate_circle(radius: float) -> Dict[str, float]:
    """Calculate area and circumference of a circle.
    
    Args:
        radius: The radius of the circle
        
    Returns:
        Dict with keys 'area' and 'circumference'
    """
    if radius < 0:
        raise ValueError("Radius cannot be negative")
        
    return {
        "area": math.pi * radius ** 2,
        "circumference": 2 * math.pi * radius
    }
