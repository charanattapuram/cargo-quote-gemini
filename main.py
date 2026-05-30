import streamlit as st
import google.generativeai as genai
import datetime
import random
from fpdf import FPDF
import tempfile

# -------------------------------------------------------------------
# Page config
# -------------------------------------------------------------------
st.set_page_config(page_title="AI Air Cargo Quotation", layout="wide")
st.title("✈️ AI Air Cargo Quotation Assistant")
st.markdown("Generate a professional air freight quotation instantly.")

# -------------------------------------------------------------------
# API Key handling – default from secrets, fallback to user input
# -------------------------------------------------------------------
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# 1) Try to load default key from Streamlit secrets (safe, not in code)
default_key = st.secrets.get("GEMINI_API_KEY", "")

# 2) If there's a default key and user hasn't entered one, use it
if default_key and not st.session_state.api_key:
    st.session_state.api_key = default_key

# 3) UI for key input (shown only if no default key, or user wants to override)
if default_key:
    # Default key is set – app works out of the box
    use_custom = st.checkbox("🔑 Use my own API key instead", value=False)
    if use_custom:
        api_key_input = st.text_input(
            "Enter your Gemini API Key",
            type="password",
            value=st.session_state.api_key if st.session_state.api_key != default_key else "",
            help="Get it free at https://aistudio.google.com/apikey"
        )
        if api_key_input:
            st.session_state.api_key = api_key_input
    else:
        st.success("✅ Using default demo API key. The app is ready to use.")
else:
    # No default key – user must paste one
    api_key_input = st.text_input(
        "🔑 Enter your Gemini API Key",
        type="password",
        value=st.session_state.api_key,
        help="Get it free at https://aistudio.google.com/apikey"
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

# Configure Gemini if we have a key
if st.session_state.api_key:
    genai.configure(api_key=st.session_state.api_key)

# -------------------------------------------------------------------
# Constants & Mock Rate Engine (unchanged)
# -------------------------------------------------------------------
VOL_DIVISOR = 6000

REGION_RATES = {
    ("Asia", "Middle East"): 2.5,
    ("Asia", "Europe"): 3.2,
    ("Asia", "North America"): 4.0,
    ("Europe", "North America"): 3.0,
    ("Middle East", "Europe"): 2.8,
    "default": 3.5
}

URGENCY_MULT = {
    "Standard": 1.0,
    "Express": 1.8,
    "Same Day": 3.2
}

CARGO_SURCHARGE = {
    "General": 0.0,
    "Pharmaceutical": 1.2,
    "Perishable": 0.8,
    "Dangerous Goods": 2.5
}

# -------------------------------------------------------------------
# Helper functions (unchanged)
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

def generate_quotation_text(calc, origin, dest, urgency, cargo_type):
    model = genai.GenerativeModel("gemini-3.5-flash")
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
- Estimated transit time: (Standard 3-5 days, Express 1-2 days, Same Day – same day)
- Note about surcharges: (explain what's included – fuel, handling, and any special requirements for {cargo_type})

Format with clean headings, bullet points, and a polite closing. Use plain text (no markdown bold/italic, use uppercase for headings).
"""
    response = model.generate_content(prompt)
    return response.text

# -------------------------------------------------------------------
# PDF generation (unchanged)
# -------------------------------------------------------------------
class QuotationPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "ORBEM Solutions Air Cargo Quotation", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def create_pdf(quotation_text, ref_number):
    pdf = QuotationPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in quotation_text.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(4)
            continue
        if line.isupper() or (len(line) < 60 and line.endswith(":")):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, line, ln=True)
            pdf.set_font("Arial", size=12)
        else:
            pdf.write(6, line)
            pdf.ln()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

# -------------------------------------------------------------------
# UI – Shipment inputs (unchanged)
# -------------------------------------------------------------------
st.divider()
st.subheader("📦 Shipment Details")

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

if st.button("Generate Quotation", type="primary"):
    if not st.session_state.api_key:
        st.error("❌ Please enter a Gemini API key!")
    elif not origin or not destination:
        st.error("❌ Please fill in both origin and destination.")
    else:
        dims = (length, width, height)
        with st.spinner("Calculating chargeable weight..."):
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

            with st.spinner("Formatting professional quotation..."):
                quotation = generate_quotation_text(calc, origin, destination, urgency, cargo_type)

            st.success("✅ Quotation Ready!")
            st.markdown(quotation)

            ref_number = f"QT-{datetime.date.today().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
            pdf_path = create_pdf(quotation, ref_number)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download as PDF",
                    data=f,
                    file_name=f"{ref_number}.pdf",
                    mime="application/pdf"
                )
