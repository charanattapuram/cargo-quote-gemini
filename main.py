import streamlit as st
import google.generativeai as genai
import datetime
import random
import os

# -------------------------------------------------------------------
# 1. Page config
# -------------------------------------------------------------------
st.set_page_config(page_title="AI Air Cargo Quotation", layout="wide")
st.title("✈️ AI Air Cargo Quotation Assistant")
st.markdown("Enter shipment details – we calculate the chargeable weight and generate a professional quotation instantly.")

# -------------------------------------------------------------------
# 2. Constants & Mock Rate Engine
# -------------------------------------------------------------------
# Volumetric divisor (IATA standard: 1 kg = 6000 cm³)
VOL_DIVISOR = 6000

# Base freight rates per kg by region pair (simplified)
REGION_RATES = {
    ("Asia", "Middle East"): 2.5,
    ("Asia", "Europe"): 3.2,
    ("Asia", "North America"): 4.0,
    ("Europe", "North America"): 3.0,
    ("Middle East", "Europe"): 2.8,
    "default": 3.5
}

# Urgency multiplier
URGENCY_MULT = {
    "Standard": 1.0,
    "Express": 1.8,
    "Same Day": 3.2
}

# Cargo type surcharge per kg
CARGO_SURCHARGE = {
    "General": 0.0,
    "Pharmaceutical": 1.2,
    "Perishable": 0.8,
    "Dangerous Goods": 2.5
}

# -------------------------------------------------------------------
# 3. Helper: determine region from city (simple mapping)
# -------------------------------------------------------------------
def get_region(city):
    city = city.lower()
    if any(c in city for c in ["mumbai", "delhi", "bangalore", "india", "bom", "del"]):
        return "Asia"
    if any(c in city for c in ["dubai", "dxb", "sharjah", "uae"]):
        return "Middle East"
    if any(c in city for c in ["london", "lhr", "frankfurt", "fra", "paris", "cdg", "amsterdam", "ams"]):
        return "Europe"
    if any(c in city for c in ["new york", "jfk", "los angeles", "lax", "chicago", "usa"]):
        return "North America"
    return "default"

# -------------------------------------------------------------------
# 4. Core calculation
# -------------------------------------------------------------------
def calculate_quote(weight, dims, origin_city, dest_city, urgency, cargo_type):
    l, w, h = dims
    gross_weight = weight
    vol_weight = (l * w * h) / VOL_DIVISOR
    chargeable_weight = max(gross_weight, vol_weight)

    origin_region = get_region(origin_city)
    dest_region = get_region(dest_city)

    base_rate = REGION_RATES.get((origin_region, dest_region),
                                 REGION_RATES.get((dest_region, origin_region), REGION_RATES["default"]))

    urgency_factor = URGENCY_MULT.get(urgency, 1.0)
    cargo_surcharge_kg = CARGO_SURCHARGE.get(cargo_type, 0.0)

    effective_rate = (base_rate * urgency_factor) + cargo_surcharge_kg
    freight_charge = round(chargeable_weight * effective_rate, 2)

    return {
        "gross_weight": gross_weight,
        "vol_weight": round(vol_weight, 2),
        "chargeable_weight": round(chargeable_weight, 2),
        "base_rate_per_kg": base_rate,
        "urgency_multiplier": urgency_factor,
        "cargo_surcharge_per_kg": cargo_surcharge_kg,
        "effective_rate_per_kg": round(effective_rate, 2),
        "freight_charge": freight_charge,
        "currency": "USD"
    }

# -------------------------------------------------------------------
# 5. Gemini setup
# -------------------------------------------------------------------
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro")
else:
    model = None

def generate_quotation_text(calc, origin, dest, urgency, cargo_type):
    prompt = f"""
You are a professional air cargo quotation writer for ORBEM Solutions.
Create a formal, structured freight quotation using the precise numbers provided.
Do NOT recalculate anything – only format the data.

Include:
- Quotation Reference: QT-{datetime.date.today().strftime('%Y%m%d')}-{random.randint(1000,9999)}
- Date: {datetime.date.today().strftime('%B %d, %Y')}
- Customer name: [To be filled]
- Origin: {origin}
- Destination: {dest}
- Cargo type: {cargo_type}
- Urgency: {urgency}
- Gross weight: {calc['gross_weight']} kg
- Volumetric weight (L×W×H ÷ {VOL_DIVISOR}): {calc['vol_weight']} kg
- Chargeable weight: {calc['chargeable_weight']} kg
- Rate per kg: ${calc['effective_rate_per_kg']}
- Total freight charge: ${calc['freight_charge']}
- Payment terms: 100% advance
- Validity: 7 days
- Estimated transit time: (based on urgency: Standard 3-5 days, Express 1-2 days, Same Day – same day)
- Note about surcharges: (explain what is included – fuel, handling, and any special requirements for {cargo_type})

Format with clean headings, bullet points, and a polite closing.
"""
    response = model.generate_content(prompt)
    return response.text

# -------------------------------------------------------------------
# 6. UI
# -------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    weight = st.number_input("Gross Weight (kg)", min_value=0.1, step=0.1, value=100.0)
    length = st.number_input("Length (cm)", min_value=1, value=120)
    width = st.number_input("Width (cm)", min_value=1, value=80)
    height = st.number_input("Height (cm)", min_value=1, value=75)

with col2:
    origin = st.text_input("Origin City/Airport", value="Mumbai (BOM)")
    destination = st.text_input("Destination City/Airport", value="Dubai (DXB)")
    urgency = st.selectbox("Urgency", ["Standard", "Express", "Same Day"])
    cargo_type = st.selectbox("Cargo Type", ["General", "Pharmaceutical", "Perishable", "Dangerous Goods"])

if not api_key:
    st.warning("⚠️ **GEMINI_API_KEY not set.** Add your Gemini API key in Replit Secrets (key: `GEMINI_API_KEY`) to enable AI quotation generation.")

if st.button("Generate Quotation", type="primary"):
    if not origin or not destination:
        st.error("Please fill in origin and destination.")
    elif not api_key:
        st.error("Please add your GEMINI_API_KEY in Replit Secrets before generating a quotation.")
    else:
        dims = (length, width, height)
        with st.spinner("Calculating chargeable weight and generating quotation..."):
            calc = calculate_quote(weight, dims, origin, destination, urgency, cargo_type)

            st.subheader("📊 Chargeable Weight Breakdown")
            c1, c2, c3 = st.columns(3)
            c1.metric("Gross Weight", f"{calc['gross_weight']} kg")
            c2.metric("Volumetric Weight", f"{calc['vol_weight']} kg")
            c3.metric("Chargeable Weight", f"{calc['chargeable_weight']} kg",
                      delta=f"{(calc['chargeable_weight'] - calc['gross_weight']):.2f} kg")

            st.subheader("💰 Rate Calculation")
            r1, r2, r3 = st.columns(3)
            r1.metric("Base Rate", f"${calc['base_rate_per_kg']}/kg")
            r2.metric("After Urgency & Cargo Surcharge", f"${calc['effective_rate_per_kg']}/kg")
            r3.metric("Total Freight", f"${calc['freight_charge']}")

            with st.spinner("Formatting professional quotation via Gemini AI..."):
                try:
                    quotation = generate_quotation_text(calc, origin, destination, urgency, cargo_type)
                    st.success("Quotation Ready!")
                    st.markdown(quotation)
                    st.text_area("Copy-ready version", value=quotation, height=300)
                except Exception as e:
                    st.error(f"Gemini API error: {e}")