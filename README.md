#  GitHub Dev Card Generator

An AI-powered GitHub Dev Card Generator that creates beautiful personalized developer identity cards using GitHub data and Gemini AI.

##  Live Demo

🔗 https://frontend-596173884226.us-central1.run.app/

---

# Features

-  Modern Glassmorphism UI
-  Multiple Themes (Dark / Light / Neon)
-  Gemini AI Developer Personality Analysis
-  GitHub Profile Scraping
-  Download Card as PNG
-  Export Card as PDF
-  Shareable Public URL
-  QR Code Generation
-  Animated Loading Skeleton
-  Responsive Design

---

# 🛠 Tech Stack

## Frontend
- HTML
- CSS
- JavaScript

## Backend
- FastAPI
- Python

## AI Integration
- Google Gemini API

## Other Libraries
- html2canvas
- jsPDF
- QRCode.js

---

# Screenshots

## Main UI

![App Screenshot](frontend/assets/screenshot1.png)
![App Screenshot](frontend/assets/screenshot2.png)
![App Screenshot](frontend/assets/screenshot3.png)
![App Screenshot](frontend/assets/screenshot4.png)
![App Screenshot](frontend/assets/screenshot5.png)

---

# Installation

## Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/github-dev-card-generator.git
```

---

## Backend Setup

```bash
cd github-card-generator/backend
pip install -r requirements.txt
```

Create `.env`

```env
GOOGLE_API_KEY=your_api_key
```

Run backend:

```bash
python main.py
```

---

## Frontend

Open:

```text
frontend/index.html
```

or run using Live Server.

---

# Project Structure

```text
github-card-generator/
│
├── backend/
│   ├── main.py
│   ├── agent.py
│   ├── mcp_server.py
│   ├── static/
│
├── frontend/
│   ├── index.html
│
├── .env.example
├── requirements.txt
└── README.md
```

---

# Future Improvements

- GitHub contribution heatmap
- More card templates
- Social media banner export
- Authentication system
- Public profile hosting

---

# Author

S. Mohammed Ismail

GitHub:
https://github.com/S-MOHAMMED-ISMAIL