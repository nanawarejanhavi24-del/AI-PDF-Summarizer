const uploadForm = document.getElementById("uploadForm");

const pdfFile = document.getElementById("pdfFile");

const summaryLength = document.getElementById(
    "summaryLength"
);

const summarizeBtn = document.getElementById(
    "summarizeBtn"
);

const statusText = document.getElementById(
    "status"
);

const resultSection = document.getElementById(
    "resultSection"
);

const pageCount = document.getElementById(
    "pageCount"
);

const originalWords = document.getElementById(
    "originalWords"
);

const summaryWords = document.getElementById(
    "summaryWords"
);

const summaryText = document.getElementById(
    "summaryText"
);

const keyPoints = document.getElementById(
    "keyPoints"
);

const downloadBtn = document.getElementById(
    "downloadBtn"
);

let latestSummary = "";


// ==================================================
// SUMMARIZE PDF
// ==================================================

uploadForm.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();

        const file = pdfFile.files[0];

        if (!file) {

            statusText.textContent =
                "Please select a PDF.";

            return;
        }

        if (
            !file.name
                .toLowerCase()
                .endsWith(".pdf")
        ) {

            statusText.textContent =
                "Only PDF files are allowed.";

            return;
        }


        const formData = new FormData();

        formData.append(
            "pdf",
            file
        );

        formData.append(
            "summary_length",
            summaryLength.value
        );


        summarizeBtn.disabled = true;

        summarizeBtn.textContent =
            "Summarizing...";

        statusText.textContent =
            "Processing your PDF...";

        resultSection.classList.add(
            "hidden"
        );


        try {

            const response = await fetch(
                "http://127.0.0.1:5000/api/summarize",
                {
                    method: "POST",
                    body: formData
                }
            );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Something went wrong."
                );

            }


            // --------------------------------------
            // DISPLAY STATISTICS
            // --------------------------------------

            pageCount.textContent =
                data.total_pages;

            originalWords.textContent =
                data.original_word_count;

            summaryWords.textContent =
                data.summary_word_count;


            // --------------------------------------
            // DISPLAY SUMMARY
            // --------------------------------------

            summaryText.innerHTML = "";

            const sentences =
                data.summary.split(
                    /(?<=[.!?])\s+/
                );


            let currentParagraph = "";


            sentences.forEach(
                function(sentence, index) {

                    currentParagraph +=
                        sentence + " ";


                    // Put two sentences in
                    // one paragraph
                    if (
                        (index + 1) % 2 === 0 ||
                        index ===
                            sentences.length - 1
                    ) {

                        const paragraph =
                            document.createElement(
                                "p"
                            );


                        paragraph.textContent =
                            currentParagraph.trim();


                        summaryText.appendChild(
                            paragraph
                        );


                        currentParagraph = "";

                    }

                }
            );


            // --------------------------------------
            // DISPLAY KEY POINTS
            // --------------------------------------

            keyPoints.innerHTML = "";


            data.key_points.forEach(
                function(point) {

                    const li =
                        document.createElement(
                            "li"
                        );


                    li.textContent =
                        point;


                    keyPoints.appendChild(
                        li
                    );

                }
            );


            // --------------------------------------
            // SAVE SUMMARY
            // --------------------------------------

            latestSummary =
                data.summary;


            // --------------------------------------
            // SHOW RESULT
            // --------------------------------------

            resultSection.classList.remove(
                "hidden"
            );


            statusText.textContent =
                "Summary generated successfully!";


        } catch (error) {

            statusText.textContent =
                "Error: " +
                error.message;


        } finally {

            summarizeBtn.disabled =
                false;

            summarizeBtn.textContent =
                "Generate Summary";

        }

    }
);


// ==================================================
// DOWNLOAD SUMMARY
// ==================================================

downloadBtn.addEventListener(
    "click",
    async function() {

        if (!latestSummary) {

            alert(
                "Please generate a summary first."
            );

            return;
        }


        downloadBtn.disabled = true;

        downloadBtn.textContent =
            "Creating PDF...";


        try {

            const response = await fetch(
                "http://127.0.0.1:5000/api/download-summary",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        summary:
                            latestSummary
                    })
                }
            );


            if (!response.ok) {

                const errorData =
                    await response.json();

                throw new Error(
                    errorData.error ||
                    "Could not create PDF."
                );

            }


            const blob =
                await response.blob();


            const url =
                URL.createObjectURL(
                    blob
                );


            const link =
                document.createElement(
                    "a"
                );


            link.href = url;

            link.download =
                "AI_PDF_Summary.pdf";


            document.body.appendChild(
                link
            );


            link.click();


            link.remove();


            URL.revokeObjectURL(
                url
            );


        } catch (error) {

            alert(
                "Error: " +
                error.message
            );


        } finally {

            downloadBtn.disabled =
                false;

            downloadBtn.textContent =
                "Download Summary";

        }

    }
);