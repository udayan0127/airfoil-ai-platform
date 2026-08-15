from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from aerodynamics import analyze_drone
from matcher import recommend_airfoils
from sarvam_integration import generate_airfoil_explanation
from polar_data import generate_polar, generate_ld_vs_airspeed
from reynolds_sweep import generate_reynolds_sweep

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://airfoil-ai-platform.vercel.app",
    ],
    allow_origin_regex=r"https://airfoil-ai-platform.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "Airfoil AI Platform running - Sarvam AI integration active"}


@app.post("/recommend-airfoil")
async def recommend_airfoil(weight: float, max_speed: float, payload: float,
                            wingspan: float = 1.01, aspect_ratio: float = 5.18):
    """
    Takes aircraft specs + wing geometry, runs physics analysis, matches airfoils,
    and generates AI explanations using Sarvam.
    """
    # Step 1: Physics analysis using wingspan + AR (with validation)
    try:
        physics = analyze_drone(
            weight_g=weight,
            max_speed_kmh=max_speed,
            payload_g=payload,
            wingspan_m=wingspan,
            aspect_ratio=aspect_ratio
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Step 2: Match against airfoil database
    top_airfoils = recommend_airfoils(
        reynolds=physics["reynolds_number"],
        required_cl=physics["required_cl"],
        flight_regime=physics["flight_regime"],
        top_n=3
    )

    # Guard: no matches found for these specs
    if not top_airfoils:
        raise HTTPException(
            status_code=404,
            detail="No suitable airfoils found for these specifications. Try adjusting weight, speed, or wing geometry."
        )

    # Wing area from wingspan + aspect ratio: AR = b^2 / S  =>  S = b^2 / AR
    wing_area_m2 = (wingspan ** 2) / aspect_ratio

    # Step 3: Generate Sarvam explanations + polar + Reynolds sweep + L/D vs airspeed for each airfoil
    airfoils_with_explanations = []
    for af in top_airfoils:
        explanation = generate_airfoil_explanation(af["name"], af, physics)
        airfoils_with_explanations.append({
            "name": af["name"],
            "description": af["description"],
            "match_score": af["match_score"],
            "cl_max": af["cl_max"],
            "cd_min": af["cd_min"],
            "best_cl_cd": af["best_cl_cd"],
            "use_case": af["use_case"],
            "ai_explanation": explanation,
            "polar": generate_polar(af),
            "reynolds_sweep": generate_reynolds_sweep(af),
            "ld_vs_airspeed": generate_ld_vs_airspeed(af, weight, wing_area_m2)
        })

    # Step 4: Format response
    return {
        "input": {
            "weight_g": weight,
            "max_speed_kmh": max_speed,
            "payload_g": payload,
            "wingspan_m": wingspan,
            "aspect_ratio": aspect_ratio
        },
        "physics": physics,
        "airfoils": airfoils_with_explanations,
        "recommendation": f"Based on your specs, we recommend {top_airfoils[0]['name']} for your build. See the AI explanation below."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)