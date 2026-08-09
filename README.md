# ⚡ Resume Screening System

An offline, zero-dependency desktop application designed to automate candidate resume evaluation. Built entirely using the **Python Standard Library**, it natively parses resumes, extracts technical skills using regular expression word boundaries, and ranks candidates against Job Descriptions (JDs) in real time—all through a modern, dark-mode GUI.

---

## 🌟 Key Features

* **Zero Third-Party Dependencies:** Runs out of the box on any standard Python 3.x installation. No `pip install` required.
* **100% Privacy-First & Offline:** All processing occurs locally on your machine. Candidate data is never sent to external APIs or cloud servers.
* **Multi-Format Document Parsing:**
* **Plain Text (`.txt`):** Direct stream reading.
* **Word Documents (`.docx`):** Unpacks OpenXML ZIP archives natively and parses `word/document.xml` using `xml.etree.ElementTree`.
* **PDF Documents (`.pdf`):** Lightweight pattern extraction from PDF text streams.


* **Regex Skill & Keyword Engine:** Uses exact word boundaries `(?<![a-zA-Z0-9])` and `(?![a-zA-Z0-9])` to accurately detect programming languages and tools (e.g., `c`, `c++`, `c#`, `python`, `gcp`, `node.js`) without triggering false substring matches.
* **4-Tier Scoring Model:** Normalizes candidates on a **0–100%** scale based on:
1. **Required Skill Match (60%):** Direct set intersection of JD skills vs. candidate skills.
2. **Keyword Relevance (25%):** Non-stopword term frequency matching via `collections.Counter`.
3. **Document Depth (10%):** Evaluation of resume length and detail.
4. **Contact Information (5%):** Regex verification for email and phone number presence.


* **Modern Dark-Mode UI:** Built with Tkinter and `ttk`, featuring card-based containers, real-time candidate ranking tables, candidate detail modals, and CSV export capabilities.

---

## 📸 Interface Preview

The application provides a clean workflow split into two main sections:

1. **Input Panel:** Paste the Job Description on the left and load candidate resume files on the right.
2. **Rankings Table:** Click **ANALYZE CANDIDATES** to process all files and view ranked results sorted by match score.
3. **Candidate Breakdown:** Double-click any row to view matched/missing skills and tailored hiring recommendations.

---

## 📐 Scoring Formula

$$\text{Total Score} = \text{Skill Match (60\%)} + \text{Keyword Match (25\%)} + \text{Document Depth (10\%)} + \text{Contact Details (5\%)}$$

| Criteria | Weight | Logic / Method |
| --- | --- | --- |
| **Skill Match** | **60 Points** | $(\frac{\text{Matched Skills}}{\text{Total JD Skills}}) \times 60$ using regex boundary lookarounds. |
| **Keyword Match** | **25 Points** | $(\frac{\text{Matched Keywords}}{\text{Total JD Keywords}}) \times 25$ using `collections.Counter`. |
| **Document Depth** | **10 Points** | Character/word count checks to ensure sufficient resume detail. |
| **Contact Info** | **5 Points** | Regex search for valid email address (+3 pts) and phone number (+2 pts). |

---

## 🚀 Getting Started

### Prerequisites

* **Python 3.8 or higher** (Python's built-in `tkinter` package is required).

> **Linux Users:** If `tkinter` is not installed by default with Python, install it via your package manager:
> ```bash
> # Ubuntu / Debian
> sudo apt-get install python3-tk
> 
> # Fedora
> sudo dnf install python3-tkinter
> 
> ```
> 
> 

### Installation & Execution

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/resume-screening-system.git
cd resume-screening-system

```


2. **Run the application:**
```bash
python main.py

```



---

## 📂 Project Structure

```text
resume-screening-system/
├── main.py              # Self-contained application code
├── README.md            # Project documentation
└── sample_resumes/      # Sample files for testing (optional)
    ├── candidate_1.docx
    ├── candidate_2.pdf
    └── sample_jd.txt

```

---

## 🛠️ Built With

| Module | Purpose |
| --- | --- |
| `tkinter` / `tkinter.ttk` | Graphical User Interface layout and styling |
| `re` | Regex pattern matching for skill boundaries, emails, and phone numbers |
| `zipfile` & `xml.etree.ElementTree` | Native DOCX archive decompression and XML content parsing |
| `collections.Counter` | Keyword frequency analysis |
| `csv` | Exporting evaluation metrics to CSV files |

---
