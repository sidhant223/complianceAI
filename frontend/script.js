const pdfFile = document.getElementById("pdfFile");
const fileText = document.getElementById("fileText");
const givenTag = document.getElementById("givenTag");
const jsonBtn = document.getElementById("jsonBtn");
const pdfBtn = document.getElementById("pdfBtn");
const statusBox = document.getElementById("statusBox");
const outputBox = document.getElementById("outputBox");
const clearBtn = document.getElementById("clearBtn");
const downloadArea = document.getElementById("downloadArea");

pdfFile.addEventListener("change", () => {
  if (pdfFile.files.length > 0) {
    fileText.textContent = pdfFile.files[0].name;
    statusBox.textContent = "File selected. Ready to audit.";
  }
});

function getFormData() {
  if (!pdfFile.files.length) {
    alert("Please select a PDF file first.");
    return null;
  }

  const formData = new FormData();

  // These names must match your FastAPI endpoint:
  // given_tag: str = Form(...)
  // file: UploadFile = File(...)
  formData.append("given_tag", givenTag.value);
  formData.append("file", pdfFile.files[0]);

  return formData;
}

jsonBtn.addEventListener("click", async () => {
  const formData = getFormData();
  if (!formData) return;

  statusBox.textContent = "Generating JSON audit report...";
  outputBox.textContent = "Processing...";
  downloadArea.innerHTML = "";

  try {
    const response = await fetch("/final-audit-json-llm", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || "Server returned an error while generating JSON.");
    }

    const data = await response.json();
    outputBox.textContent = JSON.stringify(data, null, 2);
    statusBox.textContent = "JSON audit generated successfully.";
  } catch (error) {
    statusBox.textContent = "Failed to generate JSON audit.";
    outputBox.textContent = error.message;
  }
});

pdfBtn.addEventListener("click", async () => {
  const formData = getFormData();
  if (!formData) return;

  statusBox.textContent = "Generating PDF audit report...";
  outputBox.textContent = "Processing PDF report...";
  downloadArea.innerHTML = "";

  try {
    const response = await fetch("/final-audit-pdf-llm", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || "Server returned an error while generating PDF.");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    outputBox.textContent = "PDF audit report generated successfully.";

    downloadArea.innerHTML = `
      <a class="download-link" href="${url}" download="ComplianceAI_Audit_Report.pdf">
        Download Audit PDF
      </a>
    `;

    statusBox.textContent = "PDF audit generated successfully.";
  } catch (error) {
    statusBox.textContent = "Failed to generate PDF audit.";
    outputBox.textContent = error.message;
  }
});

clearBtn.addEventListener("click", () => {
  outputBox.textContent = "No output generated yet.";
  statusBox.textContent = "Waiting for file upload...";
  downloadArea.innerHTML = "";
  pdfFile.value = "";
  givenTag.value = "TPMR";
  fileText.textContent = "Choose PDF file";
});