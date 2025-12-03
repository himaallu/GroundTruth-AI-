import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import sys
import io
import warnings

# --- REPORTING ENGINE UPDATE ---
# NOTE: As mentioned in the README 'Challenges' section, we migrated from 
# Matplotlib-only PDFs to ReportLab. Matplotlib is great for charts, but 
# ReportLab provides the "Executive-Ready" typography and layout control 
# required for client-facing documents.
from reportlab.lib import colors  
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# 🚀 TRENDSPOTTER: THE AUTOMATED INSIGHT ENGINE
# Tagline: Event-driven strategic intelligence tool.
# ---------------------------------------------------------
class DesktopInsightApp:
    def __init__(self):
        # Application State Management
        self.df = None
        self.client_reports = {} 
        self.api_key = None
        self.model = None
        self.model_name = "Unknown"
        self.reporting_period = "Unknown"
        
        # Initialize Tkinter (Hidden)
        # We use Tkinter for native OS file dialogs (User Experience upgrade)
        # instead of forcing users to type file paths in a terminal.
        self.root = tk.Tk()
        self.root.withdraw() 

    # --- 1. AI ARCHITECTURE: SELF-HEALING DISCOVERY ---
    # CHALLENGE SOLVED: "Model Availability Errors" from README.
    # Instead of hardcoding a model name that might crash (e.g., Gemini 1.5 Pro),
    # this function queries the API Key's permissions dynamically to find
    # the best available reasoning engine.
    def find_working_model(self):
        print("\n🔍 Scanning for available AI models...")
        try:
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            # Priority Logic: Best Reasoning -> Fastest -> Legacy
            priorities = ['models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
            for p in priorities:
                if p in available_models: return p
            for m in available_models:
                if 'gemini' in m: return m
            return None
        except: return None

    def get_api_key(self):
        # UX: Secure pop-up for API Key entry (No hardcoding in source)
        self.api_key = simpledialog.askstring("Configuration", "Enter Google Gemini API Key:", show='*')
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                found_name = self.find_working_model()
                if found_name:
                    self.model_name = found_name
                    # Config: Temperature 0.7 balances creativity with professional consistency
                    config = genai.types.GenerationConfig(temperature=0.7, top_k=40)
                    self.model = genai.GenerativeModel(found_name, generation_config=config)
                    return True
                messagebox.showerror("Error", "No compatible models found.")
            except Exception as e:
                messagebox.showerror("API Error", f"Invalid Key: {e}")
        return False

    def select_file(self):
        return filedialog.askopenfilename(title="Select Marketing Dataset (CSV)", filetypes=[("CSV Files", "*.csv")])

    def load_data(self, file_path):
        if not file_path: sys.exit()
        try:
            self.df = pd.read_csv(file_path)
            
            # --- ROBUST DATA CLEANING ---
            # Handles raw currency strings (e.g., "$1,200.00") often found in AdTech exports
            for col in ['Acquisition_Cost']:
                if col in self.df.columns and self.df[col].dtype == 'object':
                    self.df[col] = self.df[col].replace(r'[$,]', '', regex=True).astype(float)
            
            if 'ROI' in self.df.columns:
                 self.df['ROI'] = pd.to_numeric(self.df['ROI'], errors='coerce')
            
            # Date Parsing is critical for the Period-over-Period logic
            if 'Date' in self.df.columns:
                self.df['Date'] = pd.to_datetime(self.df['Date'])
            else:
                messagebox.showerror("Error", "Dataset must have a 'Date' column.")
                sys.exit()

            print("✅ Data Ingested & Cleaned.")
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not read file: {e}")
            sys.exit()

    # --- 2. THE "STRICT CONTEXT" PIPELINE ---
    # ARCHITECTURE NOTE: This is the "Truth Source."
    # We calculate hard metrics (Spend, ROI, Delta %) in Python using Pandas.
    # We DO NOT ask the AI to do math. This prevents Hallucinations.
    def analyze(self):
        print("Running Month-over-Month Analysis...")
        df = self.df
        
        # Automatic Period Detection (Current Month vs Previous Month)
        last_date = df['Date'].max()
        current_month_start = last_date.replace(day=1)
        prev_month_end = current_month_start - pd.Timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)
        
        self.reporting_period = current_month_start.strftime("%B %Y")
        
        companies = df['Company'].unique()
        
        for company in companies:
            print(f"  > Auditing {company}...")
            
            # Isolate Client Data
            c_df = df[df['Company'] == company]
            curr_df = c_df[(c_df['Date'] >= current_month_start) & (c_df['Date'] <= last_date)]
            prev_df = c_df[(c_df['Date'] >= prev_month_start) & (c_df['Date'] <= prev_month_end)]
            
            if curr_df.empty: continue 

            # Aggregation Logic
            def get_metrics(d):
                return {
                    'spend': d['Acquisition_Cost'].sum(),
                    'roi': d['ROI'].mean(),
                    'conv': d['Conversion_Rate'].mean() * 100
                }
            
            curr = get_metrics(curr_df)
            prev = get_metrics(prev_df) if not prev_df.empty else {'spend':1, 'roi':1, 'conv':1}
            
            # Trend Calculation (Delta %)
            # These exact numbers are fed to the AI to ground the narrative.
            delta = {
                'spend_pct': ((curr['spend'] - prev['spend']) / prev['spend']) * 100,
                'roi_pct': ((curr['roi'] - prev['roi']) / prev['roi']) * 100,
                'conv_pct': ((curr['conv'] - prev['conv']) / prev['conv']) * 100
            }
            
            # Insight Extraction: Identifying the "Winner" channel
            if not curr_df.empty:
                best_chan_stats = curr_df.groupby('Channel_Used')['ROI'].mean().sort_values(ascending=False)
                best_channel = best_chan_stats.index[0]
                best_channel_roi = best_chan_stats.iloc[0]
            else:
                best_channel = "N/A"
                best_channel_roi = 0

            self.client_reports[company] = {
                'current': curr,
                'prev': prev,
                'delta': delta,
                'best_channel': best_channel,
                'best_channel_roi': best_channel_roi,
                'trend_data': curr_df.set_index('Date').resample('D')['ROI'].mean(), # For Charting
                'narrative': "Pending..."
            }

    # --- 3. PROMPT ENGINEERING & GUARDRAILS ---
    # TECHNIQUE: "Role Prompting" (Senior Account Manager)
    # TECHNIQUE: "Chain of Thought" (Analyze Performance -> Explain Why -> Propose Optimization)
    def generate_report_text(self):
        for company, data in self.client_reports.items():
            print(f"Writing Executive Summary for {company}...")
            
            # Context Variables determine the Tone (Celebratory vs Corrective)
            roi_arrow = "UP" if data['delta']['roi_pct'] > 0 else "DOWN"
            spend_arrow = "INCREASED" if data['delta']['spend_pct'] > 0 else "DECREASED"
            
            prompt = f"""
            ACT AS: A Senior Account Manager at a premium Ad Agency.
            CLIENT: "{company}"
            PERIOD: {self.reporting_period}
            
            ### PERFORMANCE DATA (STRICT TRUTH):
            - Spend: ${data['current']['spend']:,.0f} ({spend_arrow} {abs(data['delta']['spend_pct']):.1f}%).
            - ROI: {data['current']['roi']:.2f}x (Trending {roi_arrow} {abs(data['delta']['roi_pct']):.1f}%).
            - Top Channel: {data['best_channel']} ({data['best_channel_roi']:.2f}x ROI).

            ### YOUR TASK:
            Write a short, professional Executive Recap (1 paragraph).
            1. HIGHLIGHT: The ROI trend.
            2. EXPLAIN: Connect the result to the Spend or Channel performance.
            3. OPTIMIZE: Suggest doubling down on the Top Channel.
            """
            
            if self.api_key and self.model:
                try:
                    response = self.model.generate_content(prompt)
                    # Cleaning Markdown for PDF compatibility
                    data['narrative'] = response.text.replace('**', '').replace('##', '')
                except:
                    data['narrative'] = "AI Unavailable."
            else:
                data['narrative'] = "Demo Mode: AI analysis skipped."

    # --- 4. EXECUTIVE REPORT RENDERING ---
    # TECH STACK: ReportLab + Matplotlib
    # Using 'TableStyle' for conditional formatting (Green/Red text for KPIs)
    def save_pdf(self):
        save_path = filedialog.asksaveasfilename(
            title="Save Monthly Reports", 
            defaultextension=".pdf", 
            initialfile=f"Client_Reports_{self.reporting_period.replace(' ', '_')}.pdf"
        )
        if not save_path: return

        print(f"Rendering PDF Bundle to {save_path}...")
        
        doc = SimpleDocTemplate(save_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Professional Styles matching Agency Branding
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, textColor=HexColor('#2C3E50'), spaceAfter=5)
        sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=12, textColor=HexColor('#7F8C8D'), spaceAfter=20)
        h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, textColor=HexColor('#2980B9'), spaceBefore=15, spaceAfter=10)
        body_style = ParagraphStyle('Body', parent=styles['BodyText'], fontSize=11, leading=15, spaceAfter=10)
        
        for company, data in self.client_reports.items():
            story.append(Paragraph(f"MONTHLY PERFORMANCE REPORT", sub_style))
            story.append(Paragraph(f"{company.upper()}", title_style))
            story.append(Paragraph(f"Period: {self.reporting_period}", sub_style))
            story.append(Spacer(1, 10))
            
            # Logic for Dynamic KPI Colors (Visual Proof of Performance)
            roi_color = colors.green if data['delta']['roi_pct'] >= 0 else colors.red
            roi_sign = "+" if data['delta']['roi_pct'] >= 0 else ""
            spend_sign = "+" if data['delta']['spend_pct'] >= 0 else ""
            
            # KPI Table Construction
            table_data = [
                ['METRIC', 'THIS MONTH', 'LAST MONTH', '% CHANGE'],
                ['Total Ad Spend', f"${data['current']['spend']:,.0f}", f"${data['prev']['spend']:,.0f}", f"{spend_sign}{data['delta']['spend_pct']:.1f}%"],
                ['ROAS (ROI)', f"{data['current']['roi']:.2f}x", f"{data['prev']['roi']:.2f}x", f"{roi_sign}{data['delta']['roi_pct']:.1f}%"],
                ['Conversion Rate', f"{data['current']['conv']:.1f}%", f"{data['prev']['conv']:.1f}%", f"{roi_sign}{data['delta']['conv_pct']:.1f}%"]
            ]
            
            t = Table(table_data, colWidths=[150, 100, 100, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ECF0F1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#2C3E50')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#BDC3C7')),
                ('TEXTCOLOR', (3, 2), (3, 2), roi_color), # Conditional Coloring logic
            ]))
            story.append(t)
            
            story.append(Spacer(1, 20))
            story.append(Paragraph("EXECUTIVE SUMMARY", h2_style))
            story.append(Paragraph(data['narrative'], body_style))
            
            # Embedding High-Res Matplotlib Chart
            chart_buffer = io.BytesIO()
            fig, ax = plt.subplots(figsize=(7, 3))
            data['trend_data'].plot(kind='line', ax=ax, color='#8E44AD', linewidth=2)
            ax.set_title(f"Daily ROI Trend ({self.reporting_period})")
            ax.set_ylabel("ROI")
            plt.grid(True, linestyle=':', alpha=0.6)
            plt.tight_layout()
            plt.savefig(chart_buffer, format='png', dpi=120)
            chart_buffer.seek(0)
            plt.close()
            
            story.append(Spacer(1, 10))
            story.append(RLImage(chart_buffer, width=450, height=200))
            story.append(PageBreak())

        doc.build(story)
        messagebox.showinfo("Success", f"Client Reports Generated!\n{save_path}")

if __name__ == "__main__":
    app = DesktopInsightApp()
    if app.get_api_key():
        path = app.select_file()
        if path:
            app.load_data(path)
            app.analyze()
            app.generate_report_text()
            app.save_pdf()