# -*- coding: utf-8 -*-
"""
Mock review data for products
Used when creating products with initial_review_count > 0
"""

MOCK_REVIEWS = [
    {
        "reviewer_name": "Ahmet K.",
        "reviewer_email": "ahmet.k@example.com",
        "rating": 5,
        "title": "Harika bir ürün!",
        "comment": "Kalitesi gerçekten çok iyi. Kesinlikle tavsiye ederim.",
        "verified_purchase": True,
        "status": "approved"
    },
    {
        "reviewer_name": "Zeynep Y.",
        "reviewer_email": "zeynep.y@example.com",
        "rating": 4,
        "title": "Performans çok iyi",
        "comment": "Performans çok iyi ama fiyat biraz yüksek olabilir. Yine de memnunum.",
        "verified_purchase": True,
        "status": "approved"
    },
    {
        "reviewer_name": "Mehmet A.",
        "reviewer_email": "mehmet.a@example.com",
        "rating": 5,
        "title": "Mükemmel kalite",
        "comment": "Mükemmel kalite, herkese tavsiye ederim. Beklentilerimi fazlasıyla karşıladı.",
        "verified_purchase": True,
        "status": "approved"
    }
]


def get_mock_reviews(count: int) -> list:
    """
    Get specified number of mock reviews

    Args:
        count: Number of reviews to return (0-3)

    Returns:
        List of mock review dictionaries
    """
    if count < 0 or count > 3:
        raise ValueError("Review count must be between 0 and 3")

    return MOCK_REVIEWS[:count]
