import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import os
import csv
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter


# APPLICATION CONFIGURATION & THEMING


APP_TITLE = "Resume Screening System"
APP_WIDTH = 1200
APP_HEIGHT = 800

# Dark Modern Palette
BG_DARK = "#0f172a"          
CARD_BG = "#1e293b"         
CARD_BORDER = "#334155"      
TEXT_MAIN = "#f8fafc"        
TEXT_MUTED = "#94a3b8"       
ACCENT_BLUE = "#38bdf8"      
ACCENT_GREEN = "#22c55e"     
ACCENT_PURPLE = "#a855f7"    
ACCENT_RED = "#ef4444"      
INPUT_BG = "#0f172a"        



# BUILT-IN SKILL DATABASE


SKILLS = {
    # Programming
    "python", "java", "javascript", "typescript", "c", "c++", "c#", 
    "php", "ruby", "go", "rust", "kotlin", "swift",

    # Web
    "html", "css", "react", "angular", "vue", "node.js", "node", 
    "express", "django", "flask", "fastapi", "spring", ".net",

    # Database
    "sql", "mysql", "postgresql", "postgres", "mongodb", "sqlite", 
    "oracle", "redis",

    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", 
    "linux", "git", "github", "gitlab", "devops",

    # Data
    "pandas", "numpy", "matplotlib", "seaborn", "tableau", "power bi", 
    "excel", "data analysis", "data science", "machine learning",

    # APIs / Architecture
    "rest", "rest api", "graphql", "microservices",

    # Soft skills
    "communication", "leadership", "teamwork", "problem solving", 
    "time management", "project management", "presentation", "critical thinking",

    # General
    "testing", "debugging", "agile", "scrum", "jira"
}



# STOP WORDS


STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "with", 
    "from", "for", "to", "of", "in", "on", "at", "by", "as", "is", "are", 
    "was", "were", "be", "been", "being", "this", "that", "these", "those", 
    "it", "its", "their", "they", "them", "you", "your", "we", "our", 
    "will", "can", "should", "must", "may", "have", "has", "had", "using", 
    "used", "use", "work", "working", "worked", "experience", "role", 
    "job", "candidate", "company", "organization", "position", 
    "responsibilities", "requirements", "skills", "required", 
    "preferred", "ability"
}



# TEXT UTILITIES & ANALYSIS ENGINE


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text):
    text = text.lower()
    words = re.findall(r"[a-zA-Z0-9+#.-]+", text)
    return words


def get_frequency(text):
    words = tokenize(text)
    filtered = [
        word for word in words 
        if word not in STOP_WORDS and len(word) >= 3
    ]
    return Counter(filtered)


def detect_skills(text):
    normalized = normalize_text(text)
    found = []

    for skill in SKILLS:
        skill_lower = skill.lower()
        escaped_skill = re.escape(skill_lower)
        pattern = r"(?<![a-zA-Z0-9])" + escaped_skill + r"(?![a-zA-Z0-9])"
        if re.search(pattern, normalized):
            found.append(skill)

    return sorted(set(found))


def extract_keywords(text, limit=30):
    frequency = get_frequency(text)
    return [word for word, count in frequency.most_common(limit)]


def extract_docx_text(filename):
    try:
        with zipfile.ZipFile(filename, "r") as document:
            xml_data = document.read("word/document.xml")

        root = ET.fromstring(xml_data)
        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs = []

        for paragraph in root.findall(".//w:p", namespace):
            words = []
            for text_node in paragraph.findall(".//w:t", namespace):
                if text_node.text:
                    words.append(text_node.text)
            if words:
                paragraphs.append("".join(words))

        return "\n".join(paragraphs)

    except Exception as error:
        return f"ERROR: Could not read DOCX file.\n{error}"


def extract_pdf_text(filename):
    try:
        with open(filename, "rb") as file:
            data = file.read()

        text = data.decode("latin-1", errors="ignore")
        matches = re.findall(r"\((.*?)\)", text, flags=re.DOTALL)
        extracted = []

        for item in matches:
            item = item.replace(r"\)", ")").replace(r"\(", "(").replace(r"\n", "\n")
            cleaned = item.strip()
            if len(cleaned) > 1 and re.search(r"[a-zA-Z0-9]", cleaned):
                extracted.append(cleaned)

        return " ".join(extracted)

    except Exception as error:
        return f"ERROR: Could not read PDF file.\n{error}"


def read_file(filename):
    extension = os.path.splitext(filename)[1].lower()

    if extension == ".txt":
        try:
            with open(filename, "r", encoding="utf-8", errors="ignore") as file:
                return file.read()
        except Exception as error:
            return str(error)

    if extension == ".docx":
        return extract_docx_text(filename)

    if extension == ".pdf":
        return extract_pdf_text(filename)

    return f"Unsupported file type: {extension}"


def detect_email(text):
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    return re.findall(pattern, text)


def detect_phone(text):
    pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    return re.findall(pattern, text)


def calculate_match(jd_text, resume_text):
    jd_skills = set(detect_skills(jd_text))
    resume_skills = set(detect_skills(resume_text))

    matched_skills = jd_skills & resume_skills
    missing_skills = jd_skills - resume_skills

    jd_keywords = set(extract_keywords(jd_text, 30))
    resume_keywords = set(extract_keywords(resume_text, 50))

    matched_keywords = jd_keywords & resume_keywords
    missing_keywords = jd_keywords - resume_keywords

    skill_score = (len(matched_skills) / len(jd_skills) * 60) if jd_skills else 0
    keyword_score = (len(matched_keywords) / len(jd_keywords) * 25) if jd_keywords else 0

    contact_score = 0
    if detect_email(resume_text):
        contact_score += 3
    if detect_phone(resume_text):
        contact_score += 2

    content_score = 0
    if len(resume_text) > 500:
        content_score += 5
    if len(resume_text) > 1000:
        content_score += 5

    total_score = min(100, round(skill_score + keyword_score + contact_score + content_score))

    if total_score >= 80:
        level = "Excellent Match"
    elif total_score >= 65:
        level = "Good Match"
    elif total_score >= 50:
        level = "Moderate Match"
    else:
        level = "Low Match"

    return {
        "score": total_score,
        "level": level,
        "jd_skills": sorted(jd_skills),
        "resume_skills": sorted(resume_skills),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "matched_keywords": sorted(matched_keywords),
        "missing_keywords": sorted(missing_keywords),
    }


def generate_recommendations(result):
    recommendations = []

    if result["missing_skills"]:
        recommendations.append(
            f"Candidate missing {len(result['missing_skills'])} key skill(s): "
            + ", ".join(result["missing_skills"][:4])
        )

    if len(result["matched_skills"]) >= 5:
        recommendations.append("Strong technical skill alignment demonstrated.")

    if result["score"] < 50:
        recommendations.append("Low overall alignment with job requirements.")
    elif result["score"] < 70:
        recommendations.append("Moderate alignment - manual review suggested.")
    else:
        recommendations.append("High match profile for shortlist consideration.")

    return recommendations



# MODERN GUI CLASS


class ResumeAnalyzerApp:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.configure(bg=BG_DARK)

        self.jd_text = ""
        self.resume_files = []
        self.results = []

        self.setup_styles()
        self.create_interface()

    def setup_styles(self):
        self.style = ttk.Style()
        
        # Try preferred themes safely; fall back to available system themes
        available_themes = self.style.theme_names()
        for theme in ("clamp", "alt", "default", "classic"):
            if theme in available_themes:
                self.style.theme_use(theme)
                break

        # Configure Treeview (Results Table)
        self.style.configure(
            "Treeview",
            background=CARD_BG,
            foreground=TEXT_MAIN,
            fieldbackground=CARD_BG,
            rowheight=38,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        self.style.map(
            "Treeview",
            background=[("selected", "#0284c7")],
            foreground=[("selected", "#ffffff")]
        )

        # Configure Treeview Header
        self.style.configure(
            "Treeview.Heading",
            background="#0f172a",
            foreground=ACCENT_BLUE,
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=8
        )
        self.style.map("Treeview.Heading", background=[("active", CARD_BORDER)])

    def create_card(self, parent, title_text):
        """Helper to create dark card sections."""
        card = tk.Frame(
            parent,
            bg=CARD_BG,
            highlightbackground=CARD_BORDER,
            highlightthickness=1,
            padx=15,
            pady=12
        )
        header = tk.Label(
            card,
            text=title_text,
            font=("Segoe UI", 12, "bold"),
            bg=CARD_BG,
            fg=TEXT_MAIN
        )
        header.pack(anchor="w", pady=(0, 8))
        return card

    def create_interface(self):
        # Header Banner
        header_frame = tk.Frame(self.root, bg=BG_DARK)
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        title = tk.Label(
            header_frame,
            text="⚡ Resume Screening System",
            font=("Segoe UI", 22, "bold"),
            bg=BG_DARK,
            fg=ACCENT_BLUE
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header_frame,
            text="Rule-based candidate match engine • Native Python Standard Library Execution",
            font=("Segoe UI", 10),
            bg=BG_DARK,
            fg=TEXT_MUTED
        )
        subtitle.pack(anchor="w")

        # Main Grid Layout Frame
        main_grid = tk.Frame(self.root, bg=BG_DARK)
        main_grid.pack(fill="both", expand=True, padx=20, pady=5)

        # Left Panel (Job Description)
        left_card = self.create_card(main_grid, "Job Description")
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.jd_box = tk.Text(
            left_card,
            wrap="word",
            font=("Consolas", 10),
            bg=INPUT_BG,
            fg=TEXT_MAIN,
            insertbackground=TEXT_MAIN,
            relief="flat",
            highlightthickness=1,
            highlightbackground=CARD_BORDER,
            padx=10,
            pady=10
        )
        self.jd_box.pack(fill="both", expand=True)

        # Right Panel (File Input)
        right_card = self.create_card(main_grid, "Selected Resumes")
        right_card.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.resume_list = tk.Listbox(
            right_card,
            font=("Segoe UI", 10),
            bg=INPUT_BG,
            fg=TEXT_MAIN,
            selectbackground=ACCENT_BLUE,
            selectforeground=BG_DARK,
            relief="flat",
            highlightthickness=1,
            highlightbackground=CARD_BORDER,
            activestyle="none"
        )
        self.resume_list.pack(fill="both", expand=True, pady=(0, 10))

        btn_container = tk.Frame(right_card, bg=CARD_BG)
        btn_container.pack(fill="x")

        select_btn = tk.Button(
            btn_container,
            text="+ Add Resumes",
            command=self.select_resumes,
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        select_btn.pack(side="left", padx=(0, 5))

        clear_btn = tk.Button(
            btn_container,
            text="Clear",
            command=self.clear_resumes,
            bg=CARD_BORDER,
            fg=TEXT_MAIN,
            activebackground="#475569",
            activeforeground="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        clear_btn.pack(side="left")

        # Action Bar (Analyze Button)
        action_frame = tk.Frame(self.root, bg=BG_DARK)
        action_frame.pack(fill="x", padx=20, pady=12)

        analyze_btn = tk.Button(
            action_frame,
            text="ANALYZE CANDIDATES",
            command=self.analyze,
            bg=ACCENT_GREEN,
            fg=BG_DARK,
            activebackground="#16a34a",
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            pady=10,
            cursor="hand2"
        )
        analyze_btn.pack(fill="x")

        # Results Section Frame
        results_card = self.create_card(self.root, "Screening Rankings (Double-click entry for breakdown)")
        results_card.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        columns = ("Rank", "Candidate File", "Match Score", "Alignment Level")
        self.tree = ttk.Treeview(results_card, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("Rank", text="RANK")
        self.tree.heading("Candidate File", text="CANDIDATE FILE")
        self.tree.heading("Match Score", text="MATCH SCORE")
        self.tree.heading("Alignment Level", text="ALIGNMENT LEVEL")

        self.tree.column("Rank", width=80, anchor="center")
        self.tree.column("Candidate File", width=400, anchor="w")
        self.tree.column("Match Score", width=150, anchor="center")
        self.tree.column("Alignment Level", width=200, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=(0, 10))
        self.tree.bind("<Double-1>", self.show_details)

        # Bottom Bar (Export Button)
        bottom_bar = tk.Frame(results_card, bg=CARD_BG)
        bottom_bar.pack(fill="x")

        export_btn = tk.Button(
            bottom_bar,
            text="Export CSV Report",
            command=self.export_results,
            bg=ACCENT_PURPLE,
            fg="white",
            activebackground="#9333ea",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=15,
            pady=6,
            cursor="hand2"
        )
        export_btn.pack(side="right")

    def select_resumes(self):
        files = filedialog.askopenfilenames(
            title="Select Resume Files",
            filetypes=[("Supported Resumes", "*.txt *.docx *.pdf"), ("All Files", "*.*")]
        )
        if files:
            self.resume_files = list(files)
            self.resume_list.delete(0, tk.END)
            for file in self.resume_files:
                self.resume_list.insert(tk.END, f"  📄 {os.path.basename(file)}")

    def clear_resumes(self):
        self.resume_files = []
        self.resume_list.delete(0, tk.END)
        self.results = []
        for item in self.tree.get_children():
            self.tree.delete(item)

    def analyze(self):
        self.jd_text = self.jd_box.get("1.0", tk.END).strip()

        if not self.jd_text:
            messagebox.showwarning("Input Required", "Please paste a Job Description first.")
            return

        if not self.resume_files:
            messagebox.showwarning("Input Required", "Please select at least one candidate resume.")
            return

        self.results = []
        for item in self.tree.get_children():
            self.tree.delete(item)

        for filename in self.resume_files:
            resume_text = read_file(filename)
            if resume_text.startswith("ERROR"):
                continue

            result = calculate_match(self.jd_text, resume_text)
            result["filename"] = filename
            result["candidate"] = os.path.basename(filename)
            result["recommendations"] = generate_recommendations(result)
            self.results.append(result)

        self.results.sort(key=lambda x: x["score"], reverse=True)

        for idx, result in enumerate(self.results, start=1):
            self.tree.insert(
                "",
                tk.END,
                values=(
                    f"#{idx}",
                    result["candidate"],
                    f"{result['score']}%",
                    result["level"]
                )
            )

        if self.results:
            messagebox.showinfo("Analysis Complete", f"Successfully evaluated {len(self.results)} candidate profile(s).")
        else:
            messagebox.showerror("Execution Error", "Failed to parse selected files.")

    def show_details(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        candidate_name = item["values"][1]

        result = next((r for r in self.results if r["candidate"] == candidate_name), None)
        if not result:
            return

        # Modern Pop-up Window
        window = tk.Toplevel(self.root)
        window.title(f"Evaluation Matrix — {candidate_name}")
        window.geometry("720x600")
        window.configure(bg=BG_DARK)

        # Candidate Title Card
        title_card = tk.Frame(window, bg=CARD_BG, padx=20, pady=15)
        title_card.pack(fill="x", padx=15, pady=15)

        tk.Label(
            title_card, text=candidate_name,
            font=("Segoe UI", 16, "bold"), bg=CARD_BG, fg=TEXT_MAIN
        ).pack(anchor="w")

        score_color = ACCENT_GREEN if result['score'] >= 70 else (ACCENT_BLUE if result['score'] >= 50 else ACCENT_RED)
        tk.Label(
            title_card, text=f"Overall Match: {result['score']}%  •  {result['level']}",
            font=("Segoe UI", 11, "bold"), bg=CARD_BG, fg=score_color
        ).pack(anchor="w", pady=(4, 0))

        # Details Content Area
        text_area = tk.Text(
            window,
            wrap="word",
            font=("Consolas", 10),
            bg=CARD_BG,
            fg=TEXT_MAIN,
            relief="flat",
            padx=15,
            pady=15
        )
        text_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        matched_skills = [f"  ✓ {s}" for s in result["matched_skills"]] or ["  None detected"]
        missing_skills = [f"  ✗ {s}" for s in result["missing_skills"]] or ["  None detected"]
        matched_keywords = [f"  ✓ {k}" for k in result["matched_keywords"]] or ["  None detected"]
        recommendations = [f"  • {r}" for r in result["recommendations"]] or ["  None"]

        report = [
            "============================================================",
            " MATCHED SKILLS",
            "============================================================",
            *matched_skills,
            "",
            "============================================================",
            " MISSING SKILLS",
            "============================================================",
            *missing_skills,
            "",
            "============================================================",
            " MATCHED KEYWORDS",
            "============================================================",
            *matched_keywords,
            "",
            "============================================================",
            " RECOMMENDATIONS & NOTES",
            "============================================================",
            *recommendations
        ]

        text_area.insert(tk.END, "\n".join(report))
        text_area.config(state="disabled")

    def export_results(self):
        if not self.results:
            messagebox.showwarning("No Data", "Perform an analysis prior to exporting.")
            return

        filename = filedialog.asksaveasfilename(
            title="Save CSV Report",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )

        if not filename:
            return

        try:
            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Rank", "Candidate", "Score", "Level", "Matched Skills", "Missing Skills"])
                for rank, res in enumerate(self.results, start=1):
                    writer.writerow([
                        rank, res["candidate"], res["score"], res["level"],
                        ", ".join(res["matched_skills"]), ", ".join(res["missing_skills"])
                    ])
            messagebox.showinfo("Export Successful", "Report exported successfully.")
        except Exception as err:
            messagebox.showerror("Export Error", str(err))



# PROGRAM ENTRY POINT


def main():
    root = tk.Tk()
    app = ResumeAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
