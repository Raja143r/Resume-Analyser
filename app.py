import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import os
import csv
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter


# DESIGN SYSTEM & THEME PALETTE

BG_CANVAS = "#f8fafc"
BG_SIDEBAR = "#0f172a"
BG_CARD = "#ffffff"
TEXT_MAIN = "#0f172a"
TEXT_MUTED = "#64748b"
BORDER_LIGHT = "#e2e8f0"

# Accents
PRIMARY_VIOLET = "#6366f1"
PRIMARY_HOVER = "#4f46e5"
EMERALD_SUCCESS = "#10b981"
ROSE_DANGER = "#f43f5e"
AMBER_TAG = "#f59e0b"
TAG_BG = "#e0e7ff"


# SKILL DATABASE & PRESETS

SKILLS = {
    # Languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#", 
    "php", "ruby", "go", "rust", "kotlin", "swift",
    # Frameworks & Libraries
    "react", "angular", "vue", "node.js", "express", "django", "flask", 
    "fastapi", "spring", ".net", "pandas", "numpy", "matplotlib",
    # Databases & Storage
    "sql", "mysql", "postgresql", "postgres", "mongodb", "sqlite", "oracle", "redis",
    # Cloud & Infrastructure
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "linux", "git", "github", "devops",
    # Analytics & Tools
    "tableau", "power bi", "excel", "data analysis", "data science", "machine learning",
    # Architecture & Agile
    "rest", "rest api", "graphql", "microservices", "agile", "scrum", "jira", "testing"
}

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "with", 
    "from", "for", "to", "of", "in", "on", "at", "by", "as", "is", "are", 
    "was", "were", "be", "been", "being", "this", "that", "these", "those", 
    "it", "its", "their", "they", "them", "you", "your", "we", "our", 
    "will", "can", "should", "must", "may", "have", "has", "had", "using", 
    "used", "use", "work", "working", "worked", "experience", "role", 
    "job", "candidate", "company", "organization", "position"
}

ROLE_PRESETS = {
    "🐍 Full Stack Python Dev": "Looking for a Python Developer experienced with Django, React, REST APIs, PostgreSQL, and Docker. Experience with Git, Linux, and AWS required.",
    "📊 Data Science Lead": "Seeking Data Scientist proficient in Python, SQL, Pandas, NumPy, Machine Learning, and Tableau. Strong problem solving and communication skills.",
    "⚡ Cloud DevOps Engineer": "Hiring DevOps Specialist skilled in Docker, Kubernetes, AWS, Jenkins, Linux, Terraform, Microservices, and CI/CD pipelines."
}



# PARSING ENGINE (Standard Library)


def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower()).strip()

def detect_skills(text):
    normalized = normalize_text(text)
    found = []
    for skill in SKILLS:
        escaped = re.escape(skill.lower())
        pattern = r"(?<![a-zA-Z0-9])" + escaped + r"(?![a-zA-Z0-9])"
        if re.search(pattern, normalized):
            found.append(skill)
    return sorted(set(found))

def extract_docx_text_bytes(data):
    try:
        import io
        with zipfile.ZipFile(io.BytesIO(data), "r") as doc:
            xml_data = doc.read("word/document.xml")
        root = ET.fromstring(xml_data)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs = []
        for p in root.findall(".//w:p", ns):
            words = [t.text for t in p.findall(".//w:t", ns) if t.text]
            if words:
                paragraphs.append("".join(words))
        return "\n".join(paragraphs)
    except Exception as e:
        return f"ERROR: {e}"

def extract_pdf_text_bytes(data):
    try:
        text = data.decode("latin-1", errors="ignore")
        matches = re.findall(r"\((.*?)\)", text, flags=re.DOTALL)
        extracted = []
        for item in matches:
            cleaned = item.replace(r"\)", ")").replace(r"\(", "(").replace(r"\n", "\n").strip()
            if len(cleaned) > 1 and re.search(r"[a-zA-Z0-9]", cleaned):
                extracted.append(cleaned)
        return " ".join(extracted)
    except Exception as e:
        return f"ERROR: {e}"

def parse_bytes(filename, content_bytes):
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".txt":
        return content_bytes.decode("utf-8", errors="ignore")
    elif ext == ".docx":
        return extract_docx_text_bytes(content_bytes)
    elif ext == ".pdf":
        return extract_pdf_text_bytes(content_bytes)
    return ""



# REDESIGNED MODERN GUI


class ModernScreeningApp:

    def __init__(self, root):
        self.root = root
        self.root.title("TalentScreen Pro — AI-Free Candidate Evaluator")
        self.root.geometry("1300x850")
        self.root.configure(bg=BG_CANVAS)

        self.loaded_files = {}  # {filename: text_content}
        self.results = []

        self.setup_styles()
        self.build_layout()

    def setup_styles(self):
        self.style = ttk.Style()
        for t in ("clamp", "alt", "default"):
            if t in self.style.theme_names():
                self.style.theme_use(t)
                break

        # Treeview Dashboard Table
        self.style.configure(
            "Dashboard.Treeview",
            background=BG_CARD,
            foreground=TEXT_MAIN,
            fieldbackground=BG_CARD,
            rowheight=40,
            font=("Segoe UI", 10),
            borderwidth=1,
            relief="solid"
        )
        self.style.map("Dashboard.Treeview", background=[("selected", "#e0e7ff")], foreground=[("selected", PRIMARY_VIOLET)])

        self.style.configure(
            "Dashboard.Treeview.Heading",
            background="#f1f5f9",
            foreground=TEXT_MAIN,
            font=("Segoe UI", 9, "bold"),
            padding=8
        )

    def build_layout(self):
        # ----------------------------------------------------
        # TOP NAVIGATION BAR
        # ----------------------------------------------------
        navbar = tk.Frame(self.root, bg=BG_SIDEBAR, height=60)
        navbar.pack(side="top", fill="x")
        navbar.pack_propagate(False)

        # Brand / Logo
        logo_frame = tk.Frame(navbar, bg=BG_SIDEBAR)
        logo_frame.pack(side="left", padx=20)

        badge = tk.Label(logo_frame, text="TS", font=("Segoe UI", 11, "bold"), bg=PRIMARY_VIOLET, fg="#ffffff", width=3, height=1)
        badge.pack(side="left", padx=(0, 10))

        title = tk.Label(logo_frame, text="TalentScreen Pro", font=("Segoe UI", 14, "bold"), bg=BG_SIDEBAR, fg="#ffffff")
        title.pack(side="left")

        subtitle = tk.Label(logo_frame, text="— Deterministic JD Engine", font=("Segoe UI", 9), bg=BG_SIDEBAR, fg="#94a3b8")
        subtitle.pack(side="left", padx=(5, 0))

        # Status Tag
        status_pill = tk.Label(navbar, text="● NO EXTERNAL APIs", font=("Segoe UI", 8, "bold"), bg="#1e293b", fg=EMERALD_SUCCESS, padx=12, pady=4)
        status_pill.pack(side="right", padx=20)

        # ----------------------------------------------------
        # MAIN SPLIT CANVAS
        # ----------------------------------------------------
        canvas = tk.Frame(self.root, bg=BG_CANVAS)
        canvas.pack(fill="both", expand=True, padx=20, pady=20)

        # LEFT COLUMN (Job Description & Skill Cloud)
        left_col = tk.Frame(canvas, bg=BG_CANVAS, width=580)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Card 1: Job Description Input
        jd_card = self.create_card(left_col, "1. TARGET JOB DESCRIPTION", "Paste requirements or pick a preset template")
        jd_card.pack(fill="both", expand=True, pady=(0, 15))

        # Preset Buttons
        preset_bar = tk.Frame(jd_card, bg=BG_CARD)
        preset_bar.pack(fill="x", pady=(0, 8))

        for name, text in ROLE_PRESETS.items():
            btn = tk.Button(
                preset_bar, text=name, command=lambda t=text: self.load_preset(t),
                bg="#f1f5f9", fg=TEXT_MAIN, activebackground="#e2e8f0", font=("Segoe UI", 8), relief="flat", padx=8, pady=3, cursor="hand2"
            )
            btn.pack(side="left", padx=(0, 5))

        # Text Area
        self.jd_text_box = tk.Text(
            jd_card, wrap="word", font=("Consolas", 10), bg="#f8fafc", fg=TEXT_MAIN,
            highlightbackground=BORDER_LIGHT, highlightthickness=1, relief="flat", padx=10, pady=10
        )
        self.jd_text_box.pack(fill="both", expand=True)
        self.jd_text_box.bind("<KeyRelease>", lambda e: self.update_skill_cloud())

        # Card 2: Interactive Skill Cloud
        cloud_card = self.create_card(left_col, "EXTRACTED SKILL MATRIX", "Detected automatically from Job Description above")
        cloud_card.pack(fill="x")

        self.cloud_frame = tk.Frame(cloud_card, bg=BG_CARD)
        self.cloud_frame.pack(fill="x", pady=(5, 0))

        self.cloud_empty_lbl = tk.Label(self.cloud_frame, text="Type or paste a job description above to parse skill tags...", font=("Segoe UI", 9, "italic"), bg=BG_CARD, fg=TEXT_MUTED)
        self.cloud_empty_lbl.pack(anchor="w")

        # RIGHT COLUMN (Candidate Queue & Action Panel)
        right_col = tk.Frame(canvas, bg=BG_CANVAS, width=640)
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Card 3: File Dropzone / Queue
        queue_card = self.create_card(right_col, "2. CANDIDATE RESUMES", "Upload TXT, DOCX, PDF, or ZIP bundles")
        queue_card.pack(fill="both", expand=True, pady=(0, 15))

        drop_zone = tk.Frame(queue_card, bg="#f1f5f9", highlightbackground=PRIMARY_VIOLET, highlightthickness=1, padx=15, pady=12)
        drop_zone.pack(fill="x", pady=(0, 10))

        tk.Label(drop_zone, text="📁 Batch Resume Importer", font=("Segoe UI", 10, "bold"), bg="#f1f5f9", fg=TEXT_MAIN).pack(side="left")

        browse_btn = tk.Button(
            drop_zone, text="Browse Files / ZIP", command=self.browse_files,
            bg=PRIMARY_VIOLET, fg="#ffffff", activebackground=PRIMARY_HOVER, activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"), relief="flat", padx=14, pady=5, cursor="hand2"
        )
        browse_btn.pack(side="right")

        # File Queue Listbox
        self.file_listbox = tk.Listbox(
            queue_card, font=("Consolas", 9), bg="#f8fafc", fg=TEXT_MAIN,
            selectbackground=PRIMARY_VIOLET, selectforeground="#ffffff", relief="flat", highlightbackground=BORDER_LIGHT, highlightthickness=1
        )
        self.file_listbox.pack(fill="both", expand=True, pady=(0, 8))

        clear_btn = tk.Button(
            queue_card, text="Clear Queue", command=self.clear_queue,
            bg=BG_CARD, fg=ROSE_DANGER, font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2"
        )
        clear_btn.pack(anchor="e")

        # Execute Button
        run_btn = tk.Button(
            right_col, text="RUN EVALUATION ENGINE →", command=self.run_evaluation,
            bg=EMERALD_SUCCESS, fg="#ffffff", activebackground="#059669", activeforeground="#ffffff",
            font=("Segoe UI", 11, "bold"), relief="flat", pady=12, cursor="hand2"
        )
        run_btn.pack(fill="x")

        # ----------------------------------------------------
        # BOTTOM DASHBOARD PANEL (Results View)
        # ----------------------------------------------------
        self.results_card = self.create_card(self.root, "3. SCREENING MATRIX RESULTS", "Candidates matching 50%+ of required skills are marked SELECTED")
        self.results_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        cols = ("Rank", "Candidate Name", "Match %", "Skills Matched", "Status Decision")
        self.tree = ttk.Treeview(self.results_card, columns=cols, show="headings", style="Dashboard.Treeview", height=6)

        self.tree.heading("Rank", text="RANK")
        self.tree.heading("Candidate Name", text="CANDIDATE FILE")
        self.tree.heading("Match %", text="MATCH %")
        self.tree.heading("Skills Matched", text="MATCHED / REQUIRED SKILLS")
        self.tree.heading("Status Decision", text="DECISION")

        self.tree.column("Rank", width=70, anchor="center")
        self.tree.column("Candidate Name", width=320, anchor="w")
        self.tree.column("Match %", width=110, anchor="center")
        self.tree.column("Skills Matched", width=420, anchor="w")
        self.tree.column("Status Decision", width=140, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=(0, 10))

        # Bottom Bar Export Button
        bottom_bar = tk.Frame(self.results_card, bg=BG_CARD)
        bottom_bar.pack(fill="x")

        export_btn = tk.Button(
            bottom_bar, text="Export CSV Matrix Report", command=self.export_csv,
            bg=BG_SIDEBAR, fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=15, pady=6, cursor="hand2"
        )
        export_btn.pack(side="right")

    def create_card(self, parent, title, desc):
        card = tk.Frame(parent, bg=BG_CARD, highlightbackground=BORDER_LIGHT, highlightthickness=1, padx=15, pady=12)
        
        t_lbl = tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), bg=BG_CARD, fg=TEXT_MAIN)
        t_lbl.pack(anchor="w")

        d_lbl = tk.Label(card, text=desc, font=("Segoe UI", 8), bg=BG_CARD, fg=TEXT_MUTED)
        d_lbl.pack(anchor="w", pady=(0, 8))

        return card

    # ========================================================
    # INTERACTIVE EVENTS & SKILL CLOUD
    # ========================================================

    def load_preset(self, text):
        self.jd_text_box.delete("1.0", tk.END)
        self.jd_text_box.insert(tk.END, text)
        self.update_skill_cloud()

    def update_skill_cloud(self):
        # Clear existing skill pills
        for widget in self.cloud_frame.winfo_children():
            widget.destroy()

        jd_text = self.jd_text_box.get("1.0", tk.END).strip()
        skills = detect_skills(jd_text)

        if not skills:
            lbl = tk.Label(self.cloud_frame, text="Type or paste a job description above to parse skill tags...", font=("Segoe UI", 9, "italic"), bg=BG_CARD, fg=TEXT_MUTED)
            lbl.pack(anchor="w")
            return

        # Render Pill Badges
        row_frame = tk.Frame(self.cloud_frame, bg=BG_CARD)
        row_frame.pack(fill="x", anchor="w")

        for skill in skills:
            pill = tk.Label(
                row_frame, text=f"  {skill.upper()}  ", font=("Segoe UI", 8, "bold"),
                bg=TAG_BG, fg=PRIMARY_VIOLET, padx=4, pady=2
            )
            pill.pack(side="left", padx=2, pady=2)

    def browse_files(self):
        files = filedialog.askopenfilenames(
            title="Select Candidates or Archives",
            filetypes=[("Supported Documents", "*.txt *.docx *.pdf *.zip"), ("ZIP Files", "*.zip"), ("Word Files", "*.docx"), ("PDF Files", "*.pdf"), ("Text Files", "*.txt")]
        )
        if not files:
            return

        for path in files:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".zip":
                try:
                    with zipfile.ZipFile(path, "r") as z:
                        for name in z.namelist():
                            if name.startswith("__MACOSX") or name.endswith("/"):
                                continue
                            sub_ext = os.path.splitext(name)[1].lower()
                            if sub_ext in (".txt", ".docx", ".pdf"):
                                data = z.read(name)
                                self.loaded_files[os.path.basename(name)] = parse_bytes(name, data)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to unzip: {e}")
            else:
                try:
                    with open(path, "rb") as f:
                        data = f.read()
                    filename = os.path.basename(path)
                    self.loaded_files[filename] = parse_bytes(filename, data)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read file: {e}")

        # Update Listbox View
        self.file_listbox.delete(0, tk.END)
        for fname in self.loaded_files.keys():
            ext = os.path.splitext(fname)[1].upper()
            self.file_listbox.insert(tk.END, f" [{ext[1:]}]  {fname}")

    def clear_queue(self):
        self.loaded_files.clear()
        self.file_listbox.delete(0, tk.END)

    # ========================================================
    # EVALUATION ENGINE
    # ========================================================

    def run_evaluation(self):
        jd_text = self.jd_text_box.get("1.0", tk.END).strip()

        if not jd_text:
            messagebox.showwarning("Input Needed", "Please provide a Job Description.")
            return

        if not self.loaded_files:
            messagebox.showwarning("Input Needed", "Please upload candidate resume files.")
            return

        jd_skills = set(detect_skills(jd_text))

        self.results = []
        for filename, content in self.loaded_files.items():
            res_skills = set(detect_skills(content))
            matched = jd_skills & res_skills
            missing = jd_skills - res_skills

            score = round((len(matched) / len(jd_skills)) * 100) if jd_skills else 0
            decision = "SELECTED" if score >= 50 else "REJECTED"

            self.results.append({
                "candidate": filename,
                "score": score,
                "matched": sorted(matched),
                "missing": sorted(missing),
                "total_required": len(jd_skills),
                "decision": decision
            })

        self.results.sort(key=lambda x: x["score"], reverse=True)

        # Populate Results Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        for idx, res in enumerate(self.results, start=1):
            matched_str = ", ".join(res["matched"]) if res["matched"] else "None"
            self.tree.insert(
                "", tk.END,
                values=(
                    f"#{idx}",
                    res["candidate"],
                    f"{res['score']}%",
                    f"({len(res['matched'])}/{res['total_required']}) {matched_str}",
                    res["decision"]
                )
            )

        messagebox.showinfo("Analysis Complete", f"Evaluated {len(self.results)} candidate profile(s) successfully.")

    def export_csv(self):
        if not self.results:
            messagebox.showwarning("No Data", "Run an evaluation prior to exporting.")
            return

        path = filedialog.asksaveasfilename(title="Save Matrix Report", defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Rank", "Candidate Name", "Match %", "Status Decision", "Matched Skills", "Missing Skills"])
                for rank, res in enumerate(self.results, start=1):
                    writer.writerow([
                        rank, res["candidate"], f"{res['score']}%", res["decision"],
                        ", ".join(res["matched"]), ", ".join(res["missing"])
                    ])
            messagebox.showinfo("Saved", "CSV Matrix report generated successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))



# ENTRY POINT


def main():
    root = tk.Tk()
    app = ModernScreeningApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
