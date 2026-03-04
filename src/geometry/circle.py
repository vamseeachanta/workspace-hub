"""Circle geometry calculations."""
import math


def calculate_circle(radius: float) -> dict:
    """Return area and circumference for a circle of given radius."""
    return {
        "area": math.pi * radius ** 2,
        "circumference": 2 * math.pi * radius,
    }
