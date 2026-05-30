# ✈️ AI Air Cargo Quotation Assistant

> Automates air freight pricing with IATA-standard chargeable weight calculation, dynamic surcharges, and professional quotation generation using Google Gemini.

---

## 📌 Overview

The **AI Air Cargo Quotation Assistant** is a Streamlit web application that streamlines the air freight quotation process. It eliminates manual rate lookups, volumetric weight calculation errors, and formatting inconsistencies — reducing quote turnaround time from hours to seconds.

Built for **ORBEM Solutions Private Limited** as part of the NIAT Gen AI Internship prototype submission.

---

## 🚀 Features

- **Chargeable Weight Calculation** — Automatically compares gross weight vs volumetric weight using the IATA standard (1 kg = 6,000 cm³)
- **Dynamic Rate Engine** — Applies region-based base rates, urgency multipliers (Standard/Express/Same Day), and cargo-type surcharges (General, Pharmaceutical, Perishable, Dangerous Goods)
- **AI-Powered Quotation Formatting** — Uses Google Gemini 3.1 Pro to generate clean, structured, and professional quotation text
- **One-Click PDF Download** — Exports the quotation as a ready-to-send PDF with proper formatting
- **No Backend Configuration Required** — Users paste their own Gemini API key directly in the app

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python** | Core logic & calculations |
| **Streamlit** | Web UI framework |
| **Google Gemini 3.1 Pro** | AI-powered quotation formatting |
| **fpdf2** | PDF generation |
| **Streamlit Cloud** | Free deployment |

---

## 📸 Demo

![App Screenshot](https://via.placeholder.com/800x400?text=AI+Cargo+Quotation+Assistant+Demo)

---

## 🧪 How It Works

