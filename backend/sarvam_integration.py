"""
Sarvam AI integration - generates personalized aerodynamic explanations
for airfoil recommendations using the Sarvam chat completion API.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_ENDPOINT = "https://api.sarvam.ai/v1/chat/completions"
SARVAM_MODEL = "sarvam-105b"


def generate_airfoil_explanation(airfoil_name: str, airfoil_data: dict, 
                                 physics: dict) -> str:
    """
    Generates a personalized explanation for why this airfoil is recommended.
    
    Args:
        airfoil_name: e.g., "NACA 2412"
        airfoil_data: dict with cl_max, cd_min, best_cl_cd, use_case, etc.
        physics: dict with reynolds_number, required_cl, wing_loading_n_m2, etc.
    
    Returns:
        Natural language explanation (2-3 sentences)
    """
    
    if not SARVAM_API_KEY:
        return f"[Sarvam API key not configured. {airfoil_name} is recommended for your specs.]"
    
    # Build context for the prompt
    re_number = physics["reynolds_number"]
    required_cl = physics["required_cl"]
    wing_loading = physics["wing_loading_n_m2"]
    flight_regime = physics["flight_regime"]
    
    cl_max = airfoil_data["cl_max"]
    cd_min = airfoil_data["cd_min"]
    ld_ratio = airfoil_data["best_cl_cd"]
    use_case = airfoil_data["use_case"]
    
    # Construct the prompt - be specific about what to explain
    prompt = f"""You are an aerospace engineer explaining airfoil selection to a drone designer.

AIRCRAFT SPECS:
- Reynolds Number: {re_number:,.0f}
- Required Lift Coefficient: {required_cl:.3f}
- Wing Loading: {wing_loading:.2f} N/m²
- Flight Regime: {flight_regime}

SELECTED AIRFOIL: {airfoil_name}
- Max Lift Coefficient (Cl max): {cl_max}
- Min Drag Coefficient (Cd min): {cd_min}
- Best Lift-to-Drag Ratio: {ld_ratio}
- Best Use Case: {use_case}

Write a 2-3 sentence technical explanation (100 words max) for why {airfoil_name} is recommended for these specs. 
Focus on:
1. How it matches the Reynolds number
2. Whether it can produce the required lift safely
3. Its efficiency for this flight regime

Be specific and use only the numbers provided above. No speculation."""

    try:
        # Call Sarvam API
        headers = {
            "api-subscription-key": SARVAM_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": SARVAM_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 400,  # High enough to avoid thinking mode eating all tokens
            "temperature": 0.3

        }
        
        response = requests.post(SARVAM_ENDPOINT, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Extract the text from the response
        result = response.json()
        explanation = result["choices"][0]["message"]["content"].strip()
        
        return explanation
    
    except requests.exceptions.Timeout:
        return f"{airfoil_name} is recommended. (API timeout - explanation unavailable)"
    except requests.exceptions.ConnectionError:
        return f"{airfoil_name} is recommended. (Connection error - explanation unavailable)"
    except requests.exceptions.HTTPError as e:
        try:
            body = e.response.text[:300]
        except Exception:
            body = str(e)
        print(f"SARVAM API ERROR (status {e.response.status_code}): {body}")
        return f"{airfoil_name} is recommended for your {flight_regime} flight regime. (API error: {body[:100]})"
    except Exception as e:
        # Graceful fallback if Sarvam is down
        return f"{airfoil_name} is recommended for your {flight_regime} flight regime. (Details unavailable: {str(e)[:30]})"


# Test function - run this file directly to test
if __name__ == "__main__":
    # Sample physics and airfoil data
    test_physics = {
        "reynolds_number": 154295.0,
        "required_cl": 0.661,
        "wing_loading_n_m2": 49.99,
        "flight_regime": "general",
        "total_weight_g": 1090,
        "estimated_wing_area_m2": 0.2139,
        "estimated_chord_m": 0.2028
    }
    
    test_airfoil = {
        "name": "NACA 2412",
        "cl_max": 1.4,
        "cd_min": 0.0075,
        "best_cl_cd": 65,
        "use_case": "general",
        "match_score": 100.0
    }
    
    print("Testing Sarvam integration...")
    explanation = generate_airfoil_explanation(test_airfoil["name"], test_airfoil, test_physics)
    print(f"\nGenerated explanation:\n{explanation}")
