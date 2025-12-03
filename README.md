
# H-001 | The Automated Insight Engine

> **Tagline:** An event-driven strategic intelligence tool that converts raw CSV logs into executive-ready PDF reports with AI-generated narratives in under 30 seconds.

-----

## 1\. The Problem (Real World Scenario)

**Context:** During my research into AdTech and Retail workflows, I identified a major inefficiency: Account Managers waste 4-6 hours every week manually downloading CSVs, cleaning data, and taking screenshots to build "Weekly Performance Reports."

**The Pain Point:** This manual process is slow, boring, and error-prone. If a product category is bleeding money, the client might not know for days because the reporting lag is too high.

**My Solution:** I built **TrendSpotter**, a standalone desktop automation tool. A user simply selects a raw dataset, and seconds later, the system mathematically diagnoses profit leaks and generates a fully analyzed, executive-ready PDF report saved directly to their machine.

-----

## 2\. Expected End Result

**For the User:**

  * **Input:** A simplified pop-up window asks to select a raw CSV file.
  * **Processing:** The system identifies anomalies (e.g., "Furniture discounts \> 15%") in the background.
  * **Output:** A downloadable PDF containing:
      * **Visual Evidence:** Charts highlighting the profit/loss distribution.
      * **Strategic Narrative:** An AI-written executive summary that explains *why* the loss happened and prescribes specific actions (e.g., "Cap discounts at 10%").

-----

## 3\. Technical Approach & Architecture

I challenged myself to build a tool that bridges the gap between **Hard Data Analysis** and **Generative AI Reasoning**, moving beyond simple scripts to a robust pipeline.

###  1. The "Strict Context" Pipeline

Instead of asking the AI to "analyze the CSV" (which leads to hallucinations), I built a decoupled architecture:

  * **Step 1: Python Data Engine (The Truth Source):** Pandas performs all mathematical aggregations (Sum, Mean, weighted averages). It identifies the *exact* worst-performing category and calculates the specific loss.
  * **Step 2: The Context Injection:** These hard numbers are injected into a structured JSON payload.
  * **Step 3: The AI Analyst (Gemini):** The AI is strictly constrained to *only* explain the provided numbers, preventing it from inventing data.

### 2. AI Guardrails & Prompt Engineering

To ensure production-grade reliability, I implemented several techniques:

  * **Chain-of-Thought Prompting:** The prompt forces the AI to first "Diagnose" the root cause before prescribing a "Solution," ensuring logical consistency.
  * **Hallucination Guardrails:** The system uses a "Refusal Token" strategy. If the data is inconclusive, the AI is instructed to output "Data Inconclusive" rather than guessing.
  * **Self-Healing Model Discovery:** Hardcoding API model names often causes crashes. My system dynamically queries the user's API key permissions to auto-select the best available model (`Gemini 1.5 Pro` vs `Flash`).

-----

## 4\. Tech Stack

  * **Language:** Python 3.10+
  * **Data Engine:** Pandas (High-performance aggregation)
  * **AI Model:** Google Gemini (via `google-generativeai`)
  * **Prompt Engineering:** Few-Shot & Chain-of-Thought techniques
  * **GUI:** Tkinter (Native OS file dialogs for UX)
  * **Reporting:** Matplotlib (Vector-quality PDF rendering)

-----

## 5\. Challenges & Learnings

**Challenge 1: Text Overflow & PDF Formatting**

  * **Issue:** Generating PDFs programmatically is difficult; text often runs off the page or overlaps with charts when the AI generates a long response.
  * **Solution:** I implemented a dynamic text-wrapping algorithm (`textwrap` library) that calculates the character width of the AI's insight and adjusts the layout line-by-line, ensuring a pixel-perfect document every time.

**Challenge 2: Model Availability Errors**

  * **Issue:** The application crashed when testing on different keys due to `404 Model Not Found` errors (some keys allow `Pro`, others only `Flash`).
  * **Solution:** I built a **Discovery Algorithm** that iterates through available models in the user's account and selects the most capable one automatically at runtime.

-----

## 6\. Visual Proof

### 1\. The Input (No Code Required)

*The user selects their dataset via a native file dialog.*

### 2\. The Analysis (Real-Time Feedback)

*The system auto-detects the best AI model and runs the aggregation logic.*

### 3\. The Output (Executive PDF)

*A professional report with AI-generated strategy and vector charts.*

-----

## 7\. How to Run

### Prerequisites

  * Python 3.x installed
  * A Google Gemini API Key (Free tier works)

### Quick Start Commands

```bash
# 1. Clone the repository
git clone https://github.com/your-username/trendspotter.git
cd trendspotter

# 2. Install dependencies
pip install pandas matplotlib google-generativeai

# 3. Run the Insight Engine
python insight_tool_final.py
```

### Usage Steps

1.  **Launch:** Run the script. A pop-up will ask for your **Gemini API Key**.
2.  **Select Data:** A file picker will appear. Select `Sample - Superstore.csv`.
3.  **Processing:** Watch the terminal as the script connects to the AI and runs the "Chain of Thought" prompt.
4.  **Save:** A "Save As" dialog will appear. Save your report as `Strategy_Report.pdf`.
