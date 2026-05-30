✈️ AI Air Cargo Quotation Assistant

Automates air freight pricing with IATA standard chargeable weight calculation, dynamic surcharges, and professional quotation generation using Google Gemini.

---

📌 Overview

The AI Air Cargo Quotation Assistant is a Streamlit based web application designed to streamline the air freight quotation process.

The system automatically calculates chargeable weight, applies freight rates and surcharges, and generates professional quotations in seconds.

Built as a Gen AI internship prototype project.

---

🚀 Features

Chargeable Weight Calculation

Automatically compares:

* Gross Weight
* Volumetric Weight (IATA Standard)

and selects the higher value as the chargeable weight.

Dynamic Pricing Engine

Supports:

* Region based freight rates
* Standard shipments
* Express shipments
* Same Day shipments
* Cargo specific surcharges

AI Generated Quotations

Uses Google Gemini to create:

* Professional quotation format
* Shipment summary
* Pricing breakdown
* Terms and conditions

PDF Export

Generate and download quotations as PDF files ready to send to customers.

Easy Setup

Users simply provide their own Gemini API key.

No backend configuration required.

---

🛠️ Technology Stack

Technology| Purpose
Python| Core application logic
Streamlit| Web interface
Google Gemini| AI quotation generation
FPDF2| PDF creation
Streamlit Cloud| Deployment

---

📊 How It Works

1. User enters shipment details.
2. Application calculates volumetric weight.
3. Chargeable weight is determined.
4. Freight charges are calculated.
5. Shipment data is sent to Google Gemini.
6. Gemini generates a professional quotation.
7. User downloads the quotation as a PDF.

Formula Used

Volumetric Weight

Length × Width × Height ÷ 6000

Chargeable Weight

Max(Gross Weight, Volumetric Weight)

Freight Charge

Chargeable Weight × Effective Rate

---

📦 Installation

Clone Repository

git clone https://github.com/charanattapuram/cargo-quote-gemini.git
cd cargo-quote-gemini

Install Dependencies

pip install -r requirements.txt

Run Application

streamlit run main.py

Open:

http://localhost:8501

in your browser.

---

🔑 Gemini API Key

Get a free Gemini API key from:

https://aistudio.google.com/apikey

Paste the API key into the application and start generating quotations.

---

📁 Project Structure

cargo-quote-gemini/
│
├── main.py
├── requirements.txt
└── README.md

---

📄 Sample Output

AIR FREIGHT QUOTATION

Quotation Reference: QT-20260530-6179

Origin: Mumbai
Destination: Dubai

Cargo Type: General Cargo
Urgency: Standard

Gross Weight: 100 kg
Volumetric Weight: 120 kg
Chargeable Weight: 120 kg

Rate per KG: $2.50

Total Freight Charge: $300.00

---

🔮 Future Improvements

* Real time airline rate integration
* Multi currency support
* Email quotation delivery
* WhatsApp sharing
* CRM integration
* Customer database
* Admin dashboard

---

👨‍💻 Author

Charan Attapuram Reddy

GitHub: https://github.com/charanattapuram

---

📜 License

This project was developed as an internship prototype submission.

For educational and demonstration purposes only.

---

🙏 Acknowledgements

* Streamlit
* Google Gemini
* Python Community
* Open Source Contributors
