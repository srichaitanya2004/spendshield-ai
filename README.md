# 🛡️ SpendShield AI

> **AI-powered personal finance intelligence that finds where your money is going — and shows you how to take it back.**

<p align="center">

🚀 **[Live Demo](https://spendshield-ai-n4pvqhsxqoeyjvd7djg9vn.streamlit.app/)**  
💻 **[GitHub Repository](https://github.com/srichaitanya2004/spendshield-ai)**  
🔗 **[LinkedIn Post](https://lnkd.in/p/d7XdCrCV)**

</p>

SpendShield AI is an interactive personal finance analysis application built with **Streamlit, Pandas, Plotly, and Google Gemini AI**.

It transforms raw expense data into meaningful financial insights through spending analytics, AI-powered financial diagnosis, interactive budget simulation, and AI-based receipt scanning.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Key Features](#key-features)
- [Application Workflow](#application-workflow)
- [Architecture](#architecture)
- [AI Architecture](#ai-architecture)
- [Prompt Engineering Strategy](#prompt-engineering-strategy)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Local Setup](#local-setup)
- [Environment Variables](#environment-variables)
- [Gemini Integration](#gemini-integration)
- [Receipt Scanner Architecture](#receipt-scanner-architecture)
- [Data Processing](#data-processing)
- [Budget Simulation Logic](#budget-simulation-logic)
- [Deployment](#deployment)
- [Screenshots](#screenshots)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Privacy & Security](#privacy--security)
- [Demo Dataset](#demo-dataset)
- [Author](#author)

---

## 🎯 Overview

**SpendShield AI** is a personal finance intelligence dashboard designed to help users understand their spending behavior and identify opportunities to reduce unnecessary expenses.

Instead of simply displaying transaction records, the application combines:

- 📊 Data analytics
- 📈 Interactive visualizations
- 🤖 Generative AI
- 💰 Budget simulation
- 📸 Receipt image analysis
- ✏️ Editable expense data

The goal is to convert raw financial data into **clear, actionable insights**.

---

## 📌 Problem Statement

Managing personal expenses can be difficult when transaction data is scattered across different sources.

Traditional expense trackers often show:

> "You spent ₹52,448."

But they don't necessarily explain:

- Where most of the money went
- How much spending was essential
- How much was discretionary
- Which categories have optimization potential
- How much could potentially be saved
- What behavioral changes could improve spending

SpendShield AI addresses this by combining **data analysis with AI-generated financial guidance**.

---

## 💡 Solution

SpendShield AI follows a simple workflow:

```text
Raw Expense Data
       ↓
Data Processing
       ↓
Spending Analysis
       ↓
Interactive Dashboard
       ↓
AI Financial Diagnosis
       ↓
Budget Simulation
       ↓
Potential Savings

The basic calculation is:

Projected Amount
=
Current Amount × (1 - Reduction Percentage)

Potential savings are calculated as:

Potential Savings
=
Current Spending - Projected Spending

The application also provides an annualized savings estimate.

These numbers represent hypothetical scenarios, not guaranteed future savings.

📸 4. Receipt Scanner

The Receipt Scanner allows users to upload a receipt image.

The image is processed using Gemini's multimodal capabilities.

The workflow is:

Receipt Image
     ↓
Image Processing
     ↓
Gemini Vision Analysis
     ↓
Structured Receipt Data
     ↓
Receipt Validation
     ↓
User Review

The receipt extraction functionality is implemented separately from the main Streamlit interface.

The service can extract useful information such as:

Merchant
Date
Amount
Receipt information

Extracted information is validated before being used by the application.

✏️ 5. Data Editor

The application includes an editable expense dataset interface.

Users can review and modify transaction information.

This allows users to correct or update:

Dates
Descriptions
Categories
Amounts
Transaction types

Updated information can then be used for further analysis.

📤 6. CSV Expense Import

Users can upload their own expense CSV file.

The application:

Upload CSV
    ↓
Read Dataset
    ↓
Normalize Column Names
    ↓
Check Required Columns
    ↓
Validate Data
    ↓
Clean Data
    ↓
Generate Analysis

The required expense schema is:

date
description
category
amount
type
🔄 Application Workflow

The overall application workflow is:

                 ┌───────────────────┐
                 │    User Input     │
                 └─────────┬─────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
       CSV Expense Data            Receipt Image
             │                           │
             ▼                           ▼
       Data Validation             Gemini Vision
             │                           │
             ▼                           ▼
       Data Cleaning              Receipt Data
             │                           │
             └─────────────┬─────────────┘
                           │
                           ▼
                  Expense Data Model
                           │
                           ▼
                 Financial Analytics
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
          Dashboard      Gemini     Simulator
              │            │            │
              │            ▼            │
              │       AI Diagnosis      │
              │                         │
              └────────────┬────────────┘
                           │
                           ▼
                    User Insights
🏗️ Architecture

SpendShield AI follows a modular Python architecture.

The main application is responsible for coordinating the interface while dedicated modules handle specific functionality.

SpendShield AI
│
├── Streamlit UI
│
├── Components
│   ├── Dashboard
│   ├── Charts
│   ├── Sidebar
│   └── Budget Simulator
│
├── Services
│   ├── Expense Service
│   ├── Gemini Service
│   └── Receipt Service
│
├── Utilities
│   ├── Calculations
│   ├── Data Cleaning
│   └── Prompts
│
└── Sample Data

This separation helps keep the application maintainable and makes individual functionality easier to modify.

🤖 AI Architecture

Gemini functionality is separated into a dedicated service layer.

The main AI service is:

services/gemini_service.py

Prompt definitions are maintained separately in:

utils/prompts.py

Receipt-specific processing is handled by:

services/receipt_service.py

This separation prevents AI-specific functionality from being tightly coupled to the Streamlit UI.

🎯 Prompt Engineering Strategy

SpendShield AI uses structured prompts to provide the AI with relevant information about the user's expense data.

1. Role-Based Prompting

Different AI responsibilities are separated conceptually.

Financial Analyst

Analyzes the user's spending patterns and identifies important trends.

Financial Roaster

Provides a humorous but relevant critique of spending behavior.

Recovery Strategist

Creates practical actions for reducing unnecessary spending.

Receipt Extraction Agent

Extracts structured information from receipt images.

2. Dynamic Context

The AI receives information derived from the user's actual dataset.

Relevant context can include:

Total spending
Category spending
Essential spending
Discretionary spending
Large transactions
Spending patterns
Other calculated financial metrics

This allows the generated response to be based on the user's data rather than generic financial advice.

3. Structured Output

Where structured information is required, prompts are designed to produce predictable output that can be processed by the application.

This is particularly useful for financial recovery planning and receipt extraction.

4. Multimodal Prompting

Receipt processing uses image input together with instructions so that Gemini can analyze the visual contents of a receipt.

The extracted information is then validated before being used.

📊 Data Processing

Expense processing is implemented primarily through Pandas.

The main service is:

services/expense_service.py

Data-cleaning utilities are located in:

utils/data_cleaning.py

Financial calculations are located in:

utils/calculations.py

The general processing pipeline is:

Input CSV
    ↓
Column Normalization
    ↓
Required Column Validation
    ↓
Data Validation
    ↓
Duplicate Removal
    ↓
Amount Cleaning
    ↓
Date Cleaning
    ↓
Description Cleaning
    ↓
Category Cleaning
    ↓
Transaction Type Cleaning
    ↓
Missing Value Handling
    ↓
Date Features
    ↓
Anomaly Detection
    ↓
Sorted Clean Dataset
💰 Expense Data Validation

The application expects the following columns:

Column	Description
date	Transaction date
description	Description of the transaction
category	Expense category
amount	Transaction amount
type	Transaction classification

Column names are normalized before validation.

For example:

"Date" → "date"
"Description" → "description"
"Amount" → "amount"

This makes the CSV import process more tolerant of common column-format differences.

💹 Budget Simulator

The Budget Simulator is implemented in:

components/budget_simulator.py

It allows users to explore hypothetical spending reductions.

For example:

Food
Current Spending: ₹10,000
Reduction: 20%

Projected Spending:
₹10,000 × (1 - 0.20)

= ₹8,000

Potential Savings:
₹10,000 - ₹8,000

= ₹2,000

The simulator can then estimate the corresponding annualized savings.

The simulator is intended for scenario planning.

It does not guarantee that a user will achieve the projected savings.

📸 Receipt Scanner Architecture

Receipt scanning is implemented using:

services/receipt_service.py

The workflow is:

User uploads receipt
        ↓
Receipt image received
        ↓
Gemini multimodal analysis
        ↓
Structured receipt information
        ↓
Receipt validation
        ↓
User review
        ↓
Expense data update

The application checks whether the extracted information contains useful transaction data before accepting it.

🧠 Gemini Integration

SpendShield AI uses Google's Gemini API through the Gemini service layer.

The main integration is located in:

services/gemini_service.py

Prompt definitions are located in:

utils/prompts.py

Receipt processing uses:

services/receipt_service.py

The AI layer is separated from the UI so that prompt logic and API functionality can be modified without restructuring the entire application.

🛠️ Tech Stack
Technology	Purpose
Python	Core programming language
Streamlit	Web application framework
Pandas	Data processing and analysis
Plotly	Interactive visualizations
Google Gemini	Generative AI and multimodal receipt analysis
Pillow	Image processing
python-dotenv	Local environment configuration
📁 Project Structure

The repository is organized as follows:

spendshield-ai/
│
├── app.py
│
├── components/
│   ├── __init__.py
│   ├── budget_simulator.py
│   ├── charts.py
│   ├── dashboard.py
│   └── sidebar.py
│
├── services/
│   ├── __init__.py
│   ├── expense_service.py
│   ├── gemini_service.py
│   └── receipt_service.py
│
├── utils/
│   ├── __init__.py
│   ├── calculations.py
│   ├── data_cleaning.py
│   └── prompts.py
│
├── sample_data/
│   └── expenses.csv
│
├── .env.example
├── .gitignore
├── README.md
├── TECHNICAL_DESIGN.md
└── requirements.txt
📄 Important Files
app.py

Main Streamlit application controller.

It coordinates:

Application layout
Sidebar
Navigation
Dashboard
Data editor
Budget simulator
Receipt scanner
Application state
services/expense_service.py

Handles:

CSV loading
Required-column validation
Data cleaning
Sample data
Dataset summaries
services/gemini_service.py

Handles communication with Gemini for AI-powered functionality.

services/receipt_service.py

Handles receipt extraction and validation.

components/dashboard.py

Contains dashboard-related UI functionality.

components/charts.py

Contains interactive visualization functionality.

components/budget_simulator.py

Contains the interactive budget simulation functionality.

utils/data_cleaning.py

Contains reusable data cleaning and validation functions.

utils/calculations.py

Contains financial calculations used by the application.

utils/prompts.py

Contains prompt definitions used by the AI layer.

📑 CSV Data Format

SpendShield AI expects CSV files containing these columns:

date,description,category,amount,type
2026-01-01,Groceries,Food,3200,Essential
2026-01-02,Coffee,Food,150,Discretionary
2026-01-03,Uber,Transport,450,Discretionary
2026-01-04,Rent,Housing,15000,Essential
Required Columns
date
description
category
amount
type
Example
date	description	category	amount	type
2026-01-01	Groceries	Food	3200	Essential
2026-01-02	Coffee	Food	150	Discretionary
2026-01-03	Uber	Transport	450	Discretionary
2026-01-04	Rent	Housing	15000	Essential
💻 Local Setup
Prerequisites

Before running SpendShield AI locally, install:

Python
pip
Git
A Gemini API key
1. Clone the Repository
git clone https://github.com/srichaitanya2004/spendshield-ai.git

Move into the project directory:

cd spendshield-ai
2. Create a Virtual Environment

On Windows:

python -m venv venv

Activate it:

venv\Scripts\activate

On macOS/Linux:

python -m venv venv
source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
4. Configure the Gemini API Key

Create a .env file in the project root.

GEMINI_API_KEY=your_actual_gemini_api_key

Do not commit the .env file to GitHub.

The repository contains:

.env.example

as a template.

5. Run the Application

Start Streamlit:

streamlit run app.py

The application will then be available through the local Streamlit URL shown in the terminal.

🔐 Environment Variables

The application requires a Gemini API key for AI functionality.

Example:

GEMINI_API_KEY=your_actual_gemini_api_key

The repository intentionally does not include the real API key.

The .gitignore file excludes:

.env
.env.local

This helps prevent accidental exposure of API credentials.

🚀 Deployment

SpendShield AI is deployed using Streamlit Community Cloud.

Live Application

🚀 Open SpendShield AI

Deployment Architecture
GitHub Repository
        ↓
Streamlit Community Cloud
        ↓
Install requirements.txt
        ↓
Configure Application Secrets
        ↓
Run app.py
        ↓
Live Streamlit Application
🔑 Streamlit Cloud Configuration

The Gemini API key should be configured using Streamlit Cloud secrets.

The secret should contain:

GEMINI_API_KEY = "your_actual_gemini_api_key"

The actual API key should never be committed to GitHub.

🧪 Testing

The application was tested locally and through the deployed Streamlit application.

Testing areas include:

CSV Upload
Valid CSV upload
Required-column validation
Data cleaning
Invalid data handling
Dashboard
Spending metrics
Category analysis
Charts
Transaction summaries
Data Editor
Viewing expense records
Editing expense information
Recalculation after data changes
Budget Simulator
Category reduction controls
Projected spending
Potential savings
Annualized savings
Receipt Scanner
Receipt image upload
Gemini extraction
Extracted-data validation
Handling extraction failures
Deployment
Streamlit Cloud startup
Dependency installation
Gemini configuration
Live application testing
🖼️ Screenshots

Screenshots can be added here to demonstrate the major parts of the application.

Recommended screenshots:

Dashboard

Show:

KPI metrics
Spending charts
Category breakdown
Financial insights
Data Editor

Show:

Uploaded transactions
Editable data table
Budget Simulator

Show:

Category controls
Reduction percentages
Projected savings
Receipt Scanner

Show:

Receipt upload
Extracted information
AI Financial Diagnosis

Show:

AI spending analysis
Financial roast
Recovery recommendations

Add screenshots to the repository and reference them here using relative Markdown paths.

Example:

![Dashboard](screenshots/dashboard.png)
⚠️ Limitations

SpendShield AI is a prototype and educational project.

Important limitations include:

AI-generated financial insights may not always be correct.
Receipt extraction can fail on unclear or low-quality images.
Budget projections are hypothetical scenarios.
The application should not be treated as professional financial advice.
Users should review AI-generated recommendations before acting on them.
The current application focuses on expense analysis rather than direct banking integration.
The application does not guarantee financial savings.
🔒 Security and Privacy

SpendShield AI is designed as a demonstration and educational application.

Users should avoid uploading highly sensitive financial information.

Do not upload:

Banking passwords
Card PINs
Authentication credentials
Full payment-card information
Other highly sensitive information

API credentials should never be committed to GitHub.

The .env file is excluded through .gitignore.

🧾 Demo Dataset

A sample dataset is included in:

sample_data/expenses.csv

The demo dataset allows users to explore the application without preparing their own expense data.

The application can also generate demo expense data through the application's demo-data functionality.

📚 Technical Documentation

Additional technical documentation is available in:

TECHNICAL_DESIGN.md

The technical design document provides additional information about the project's architecture and implementation decisions.

🔮 Future Improvements

Potential future improvements include:

🔐 User authentication
🗄️ Persistent database storage
🏦 Bank account/API integration
📱 Improved mobile experience
📅 Monthly and yearly financial reports
🔔 Spending alerts
🎯 Personalized financial goals
📈 Long-term spending trend analysis
🧾 Improved receipt extraction
💱 Multi-currency support
📊 More advanced financial forecasting
🤖 More personalized AI financial coaching
☁️ Persistent cloud-based user profiles
🎓 Internship Project Context

SpendShield AI was developed as part of the MirAI School of Technology AI Builder Track Internship.

The project demonstrates the practical integration of:

Python application development
Data processing
Generative AI
Multimodal AI
Prompt engineering
Interactive visualization
Modular software architecture
Streamlit deployment

The project focuses on building a usable AI-powered application rather than only demonstrating an isolated AI API call.

🧠 Architectural Decisions
Modular Service Layer

AI and expense-processing functionality are separated into services.

This makes it easier to:

Maintain the application
Test individual components
Replace implementation details
Keep UI code manageable
Utility Layer

Common calculations, data-cleaning logic, and prompts are separated into reusable utility modules.

This reduces duplication and keeps the main application controller focused on orchestration.

Component-Based UI

Major UI sections are separated into components.

For example:

Dashboard
Charts
Sidebar
Budget Simulator

This allows individual sections to evolve independently.

🔄 Data Flow

The general data flow through the application is:

                 User
                  │
                  ▼
          ┌───────────────┐
          │ CSV / Receipt │
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────┐
          │   Validation  │
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────┐
          │ Data Cleaning │
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────┐
          │  Data Model   │
          └───────┬───────┘
                  │
          ┌───────┼────────┐
          │       │        │
          ▼       ▼        ▼
      Dashboard   AI    Simulator
          │       │        │
          └───────┼────────┘
                  │
                  ▼
          Financial Insights
📈 Example Analysis

A simplified example of how the application can interpret expense information:

Total Spending
      ↓
Category Breakdown
      ↓
Essential vs Discretionary
      ↓
Identify High-Spending Categories
      ↓
AI Financial Diagnosis
      ↓
Potential Reduction Scenarios

This allows the user to move from:

"What did I spend?"

to:

"Where did I spend it?"

and finally:

"What could I potentially change?"

🤖 AI Design Philosophy

The AI layer is designed around the principle that financial analysis should be:

Data-Grounded

AI responses should be based on the expense information supplied to the application.

Actionable

Insights should ideally lead to specific actions rather than generic statements.

Understandable

Financial information should be presented in a way that is easy for a normal user to understand.

Engaging

The financial roast concept provides a more engaging way to communicate spending problems while keeping the focus on the user's data.

🧩 Separation of Responsibilities

The project follows a separation-of-concerns approach.

app.py
   │
   ├── Application Control
   │
   ├── UI Navigation
   │
   └── Session State
        │
        ├── components/
        │      ├── Dashboard
        │      ├── Charts
        │      ├── Sidebar
        │      └── Budget Simulator
        │
        ├── services/
        │      ├── Expense Service
        │      ├── Gemini Service
        │      └── Receipt Service
        │
        └── utils/
               ├── Calculations
               ├── Data Cleaning
               └── Prompts
📦 Dependencies

Project dependencies are maintained in:

requirements.txt

The application uses the required Python packages specified there rather than relying on globally installed packages.

For local installation:

pip install -r requirements.txt
🛡️ Error Handling

The application includes validation and error handling for several common situations.

Examples include:

Invalid CSV files
Missing required columns
Empty datasets
Invalid expense values
Invalid dates
Failed AI requests
Receipt extraction failures
Empty AI responses

The objective is to prevent invalid input from silently propagating through the application.

🧪 Demo Workflow

A simple demonstration workflow is:

1. Open the Live Demo
          ↓
2. Load Demo Expenses
          ↓
3. Explore Dashboard
          ↓
4. Open Data Editor
          ↓
5. Try Budget Simulator
          ↓
6. Open AI Financial Diagnosis
          ↓
7. Try Receipt Scanner

The included sample dataset can also be uploaded manually.

🌐 Live Application
🚀 Try SpendShield AI

Live Demo:

https://spendshield-ai-n4pvqhsxqoeyjvd7djg9vn.streamlit.app/

The application is hosted using Streamlit Community Cloud.

💻 Source Code
GitHub Repository

https://github.com/srichaitanya2004/spendshield-ai

The complete source code, requirements, documentation, sample data, and project structure are available in the repository.

👤 Author
SRI CHAITANYA

GitHub Profile:

https://github.com/srichaitanya2004

GitHub Repository:

https://github.com/srichaitanya2004/spendshield-ai

LinkedIn Submission:

YOUR_LINKEDIN_POST_URL

💼 LinkedIn Submission

The project submission post is available here:

View LinkedIn Project Post

The LinkedIn post should contain the project demonstration and tag:

MirAI School of Technology

Replace YOUR_LINKEDIN_POST_URL with the actual LinkedIn post URL after publishing.

⭐ Project Highlights

SpendShield AI demonstrates the practical integration of:

🐍 Python
📊 Data Analytics
📈 Interactive Data Visualization
🤖 Generative AI
👁️ Multimodal AI
🎯 Prompt Engineering
🧹 Data Cleaning
💰 Financial Scenario Simulation
📸 Receipt Analysis
🧩 Modular Software Architecture
🌐 Streamlit Application Development
☁️ Cloud Deployment
🏁 Conclusion

SpendShield AI demonstrates how raw expense data can be transformed into an interactive financial intelligence experience.

Instead of stopping at:

"You spent ₹X."

the application attempts to answer:

Where did the money go?
          ↓
Why does it matter?
          ↓
What spending patterns stand out?
          ↓
What could potentially be reduced?
          ↓
What could those reductions mean?

The combination of data analytics, interactive visualization, generative AI, receipt analysis, and budget simulation creates a complete prototype for AI-assisted personal finance analysis.

🛡️ SpendShield AI

Your money has a problem. We found it.

🚀 Live Demo

https://spendshield-ai-n4pvqhsxqoeyjvd7djg9vn.streamlit.app/

💻 GitHub

https://github.com/srichaitanya2004/spendshield-ai

👤 Developer

https://github.com/srichaitanya2004

💼 LinkedIn

YOUR_LINKEDIN_POST_URL