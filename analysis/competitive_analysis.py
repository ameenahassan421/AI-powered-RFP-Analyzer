import numpy as np

def analyze_competitiveness(text: str, basic_info: dict) -> dict:
    """Competitive intelligence and win probability analysis"""
    # Simulate market analysis
    market_factors = {
        "estimated_competitors": np.random.randint(3, 12),
        "market_maturity": np.random.choice(["Emerging", "Growing", "Mature", "Saturated"]),
        "barriers_to_entry": ["Specialized expertise", "Existing relationships", "Regulatory requirements"],
        "our_competitive_advantages": ["Local presence", "Proven track record", "Innovative approach", "Cost effectiveness"],
        "key_differentiators": ["Technology innovation", "Implementation speed", "Customer support", "Pricing model"]
    }

    # Calculate win probability based on various factors
    base_probability = 60
    if market_factors["estimated_competitors"] < 5:
        base_probability += 15
    if len(market_factors["our_competitive_advantages"]) > 3:
        base_probability += 10

    return {
        **market_factors,
        "win_probability": min(95, base_probability),
        "confidence_level": "High" if base_probability > 70 else "Medium",
        "competitive_threats": ["Incumbent providers", "Large national firms", "Specialized boutiques"],
        "strategic_recommendations": [
            "Emphasize local expertise",
            "Highlight successful case studies",
            "Offer innovative solution approach"
        ]
    }
