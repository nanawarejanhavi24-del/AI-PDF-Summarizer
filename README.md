# AI PDF Summarizer

An intelligent PDF summarization application that extracts text from PDF documents and generates concise summaries, making lengthy documents easier to understand and review.

## Features

- **PDF Upload:** Upload PDF documents for summarization.
- **Text Extraction:** Extracts text from PDF files using PyPDF.
- **Automatic Summarization:** Generates concise summaries using TF-IDF and cosine similarity.
- **Summary Download:** Export the generated summary as a PDF document.
- **Simple User Interface:** Easy-to-use frontend built with HTML, CSS, and JavaScript.

## Technologies Used

**Frontend**
- HTML
- CSS
- JavaScript

**Backend**
- Python
- Flask
- Flask-CORS

**Libraries**
- PyPDF
- Scikit-learn
- NumPy
- ReportLab

## Project Structure

```text
AI-PDF-Summarizer/
│
├── backend/
│   ├── app.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/nanawarejanhavi24-del/AI-PDF-Summarizer.git
cd AI-PDF-Summarizer
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install -r backend/requirements.txt
```

Install ReportLab separately if it is not included in the requirements file:

```bash
python -m pip install reportlab
```

### 5. Run the backend

Open a terminal in the project root and execute:

```bash
python backend/app.py
```

### 6. Run the frontend

Open a second terminal:

```bash
cd frontend
python -m http.server 5500
```

Open your browser and visit:

```text
http://localhost:5500
```

Make sure both the backend and frontend servers are running.

## How It Works

1. Upload a PDF document.
2. The backend extracts its text.
3. TF-IDF and cosine similarity are used to identify important sentences.
4. A concise summary is generated.
5. Download the summary as a PDF.

## Note

This project uses extractive text summarization. It identifies important sentences from the original document rather than generating entirely new content. Scanned image-only PDFs may require OCR support.

## Author

**Janhavi Nanaware**

