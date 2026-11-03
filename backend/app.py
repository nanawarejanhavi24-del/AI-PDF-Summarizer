import re
import io
import numpy as np

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pypdf import PdfReader

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# ==================================================
# CLEAN PDF TEXT
# ==================================================

def clean_text(text):

    # Remove common PDF bullet symbols
    text = text.replace("•", " ")
    text = text.replace("▪", " ")
    text = text.replace("●", " ")
    text = text.replace("◦", " ")

    # Replace multiple spaces/newlines with one space
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==================================================
# SPLIT TEXT INTO SENTENCES
# ==================================================

def split_into_sentences(text):

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) > 20
    ]


# ==================================================
# AI EXTRACTIVE SUMMARIZATION
# TF-IDF + COSINE SIMILARITY
# ==================================================

def summarize_text(text, sentence_count=5):

    text = clean_text(text)

    if not text:
        return []

    sentences = split_into_sentences(text)

    if not sentences:
        return []

    if len(sentences) <= sentence_count:
        return sentences

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    try:

        matrix = vectorizer.fit_transform(
            sentences
        )

    except ValueError:

        return sentences[:sentence_count]

    document_vector = np.asarray(
        matrix.mean(axis=0)
    )

    scores = cosine_similarity(
        matrix,
        document_vector
    ).flatten()

    ranked_indices = scores.argsort()[::-1]

    selected_indices = []

    for index in ranked_indices:

        duplicate = False

        for selected_index in selected_indices:

            similarity = cosine_similarity(
                matrix[index],
                matrix[selected_index]
            )[0][0]

            if similarity > 0.75:

                duplicate = True
                break

        if not duplicate:

            selected_indices.append(index)

        if len(selected_indices) >= sentence_count:

            break

    # Restore original document order
    selected_indices.sort()

    return [
        sentences[index]
        for index in selected_indices
    ]


# ==================================================
# GENERATE SEPARATE KEY POINTS
# ==================================================

def generate_key_points(
    text,
    summary_sentences,
    point_count=5
):

    sentences = split_into_sentences(text)

    if not sentences:
        return []

    # Remove sentences already used in summary
    summary_set = set(
        sentence.lower().strip()
        for sentence in summary_sentences
    )

    remaining_sentences = [
        sentence
        for sentence in sentences
        if sentence.lower().strip() not in summary_set
    ]

    # If there are not enough remaining sentences,
    # use the complete sentence list.
    if len(remaining_sentences) < point_count:

        remaining_sentences = sentences

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    try:

        matrix = vectorizer.fit_transform(
            remaining_sentences
        )

    except ValueError:

        return remaining_sentences[:point_count]

    document_vector = np.asarray(
        matrix.mean(axis=0)
    )

    scores = cosine_similarity(
        matrix,
        document_vector
    ).flatten()

    ranked_indices = scores.argsort()[::-1]

    selected_indices = []

    for index in ranked_indices:

        duplicate = False

        for selected_index in selected_indices:

            similarity = cosine_similarity(
                matrix[index],
                matrix[selected_index]
            )[0][0]

            if similarity > 0.65:

                duplicate = True
                break

        if not duplicate:

            selected_indices.append(index)

        if len(selected_indices) >= point_count:

            break

    # Restore document order
    selected_indices.sort()

    key_points = []

    for index in selected_indices:

        sentence = remaining_sentences[index]

        sentence = re.sub(
            r"\s+",
            " ",
            sentence
        ).strip()

        # Remove unnecessary bullet characters
        sentence = re.sub(
            r"^[•▪●◦\-]+\s*",
            "",
            sentence
        )

        key_points.append(sentence)

    return key_points


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    return jsonify({
        "message": "AI PDF Summarizer Backend is Running!"
    })


# ==================================================
# SUMMARIZE PDF
# ==================================================

@app.route("/api/summarize", methods=["POST"])
def summarize_pdf():

    if "pdf" not in request.files:

        return jsonify({
            "error": "Please upload a PDF file."
        }), 400

    pdf_file = request.files["pdf"]

    if pdf_file.filename == "":

        return jsonify({
            "error": "No file selected."
        }), 400

    if not pdf_file.filename.lower().endswith(".pdf"):

        return jsonify({
            "error": "Only PDF files are allowed."
        }), 400

    try:

        # Read PDF
        reader = PdfReader(pdf_file)

        extracted_text = ""

        # Extract text from every page
        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                extracted_text += page_text + "\n"

        # Clean extracted text
        extracted_text = clean_text(
            extracted_text
        )

        if not extracted_text:

            return jsonify({
                "error": "No readable text found in this PDF."
            }), 400

        # ------------------------------------------
        # SUMMARY LENGTH
        # ------------------------------------------

        summary_length = request.form.get(
            "summary_length",
            "medium"
        )

        if summary_length == "short":

            sentence_count = 3

        elif summary_length == "long":

            sentence_count = 10

        else:

            sentence_count = 5

        # ------------------------------------------
        # GENERATE SUMMARY
        # ------------------------------------------

        summary_sentences = summarize_text(
            extracted_text,
            sentence_count
        )

        summary = " ".join(
            summary_sentences
        )

        # ------------------------------------------
        # GENERATE KEY POINTS
        # ------------------------------------------

        key_points = generate_key_points(
            extracted_text,
            summary_sentences,
            5
        )

        # ------------------------------------------
        # SEND RESPONSE
        # ------------------------------------------

        return jsonify({

            "success": True,

            "filename": pdf_file.filename,

            "total_pages": len(reader.pages),

            "original_word_count": len(
                extracted_text.split()
            ),

            "summary_word_count": len(
                summary.split()
            ),

            "summary": summary,

            "key_points": key_points
        })

    except Exception as error:

        return jsonify({
            "error": f"Could not process PDF: {str(error)}"
        }), 500


# ==================================================
# DOWNLOAD SUMMARY AS PDF
# ==================================================

@app.route("/api/download-summary", methods=["POST"])
def download_summary():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "No summary data received."
        }), 400

    summary = data.get(
        "summary",
        ""
    )

    if not summary:

        return jsonify({
            "error": "No summary available."
        }), 400

    pdf_buffer = io.BytesIO()

    pdf = canvas.Canvas(
        pdf_buffer,
        pagesize=A4
    )

    width, height = A4

    # Title
    pdf.setFont(
        "Helvetica-Bold",
        18
    )

    pdf.drawString(
        50,
        height - 50,
        "AI PDF Summarizer"
    )

    # Subtitle
    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawString(
        50,
        height - 85,
        "Generated Summary"
    )

    # Summary text
    pdf.setFont(
        "Helvetica",
        10
    )

    y = height - 115

    line_height = 15

    words = summary.split()

    line = ""

    for word in words:

        test_line = line + " " + word

        if pdf.stringWidth(
            test_line,
            "Helvetica",
            10
        ) < 500:

            line = test_line

        else:

            pdf.drawString(
                50,
                y,
                line.strip()
            )

            y -= line_height

            line = word

            if y < 50:

                pdf.showPage()

                pdf.setFont(
                    "Helvetica",
                    10
                )

                y = height - 50

    if line:

        pdf.drawString(
            50,
            y,
            line.strip()
        )

    pdf.save()

    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="AI_PDF_Summary.pdf",
        mimetype="application/pdf"
    )


# ==================================================
# START SERVER
# ==================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )