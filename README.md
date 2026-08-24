# 🛡️ SpendShield AI

## 📋 Table of Contents
- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [AI Architecture](#ai-architecture)
- [Prompt Engineering Strategy](#prompt-engineering-strategy)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Local Setup](#local-setup)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Gemini Integration](#gemini-integration)
- [Future Improvements](#future-improvements)
- [Author](#author)
- [Live Deployment](#live-deployment)

## 🎯 Overview

**SpendShield AI** is an AI-powered personal finance analysis and recovery dashboard that transforms your expense data into actionable insights. Using Google's Gemini AI, it provides a humorous but brutally honest analysis of your spending habits and creates a strict recovery plan to help you save money.

## 📌 Problem Statement

People struggle with understanding their spending patterns and making meaningful changes. Traditional budgeting apps provide data but don't offer personalized, actionable insights or the emotional engagement needed to drive behavior change.

**The Expense Roaster** concept: Users upload their monthly expenses, and AI analyzes the data to brutally roast their discretionary spending while providing a strict budget recovery plan.

## 💡 Solution

SpendShield AI turns this concept into a polished, professional product that:

1. **Analyzes** your spending patterns with advanced AI
2. **Roasts** your bad habits in an entertaining way
3. **Recovers** your finances with a strict action plan
4. **Simulates** potential savings with interactive tools
5. **Scans** receipts using computer vision

## ✨ Key Features

### 📊 Financial Dashboard
- Real-time KPI metrics (total spending, discretionary, savings potential)
- Interactive Plotly visualizations
- Category breakdown and trends
- Essential vs. discretionary analysis

### 🤖 AI Financial Diagnosis
- **Brutal Roast**: Humorous but helpful critique of spending habits
- **Recovery Plan**: Structured, actionable savings strategy
- **Intelligent Analysis**: Uses dynamic context from your actual data

### 💹 Budget Simulator
- Interactive sliders for each spending category
- Real-time savings projections
- Annual savings estimates
- Comparison visualizations

### 📸 Receipt Scanner
- Upload or take photo of receipts
- Gemini Vision extracts merchant, date, amount, and items
- One-click addition to your expense data

### ✏️ Data Editor
- Edit any expense in the dataset
- Update categories, amounts, or descriptions
- Automatic recalculation of metrics

## 🏗️ Architecture

## 🤖 AI Architecture

### Role-Based Prompting
SpendShield uses specialized AI roles for different tasks:

1. **Financial Analyst**: Analyzes spending patterns and identifies trends
2. **Brutal Roaster**: Delivers humorous but helpful critiques
3. **Recovery Strategist**: Creates strict, actionable recovery plans
4. **Receipt Agent**: Extracts structured data from receipt images

### Context Engineering
The AI receives dynamic context built from user data:
- Total and discretionary spending
- Category breakdown
- Largest transactions
- Recurring expenses
- Spending trends

## 🎯 Prompt Engineering Strategy

### 1. System-Level Instructions
Each AI role has specific system instructions that define its personality and output format.

### 2. Dynamic Context
F-strings populate the context with actual user data, making the AI response personalized.

### 3. Structured Output
Recovery plans use JSON format for consistent, parsable results.

### 4. Multi-Modal
Gemini Vision processes receipt images for expense extraction.

## 📸 Screenshots

*Screenshots to be added after deployment*

## 🛠️ Tech Stack

- **Python** 3.9+
- **Streamlit** - UI Framework
- **Pandas** - Data Processing
- **Plotly** - Interactive Visualizations
- **Google Gemini** - AI Engine
- **Pillow** - Image Processing

## 💻 Local Setup

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Gemini API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/spendshield-ai.git
cd spendshield-ai
