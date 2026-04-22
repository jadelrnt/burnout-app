# Burnout Self-Assessment App

Interactive web application to estimate professional burnout risk, based on a logistic regression model trained on the French Working Conditions Survey (CT-RPS 2016).

**[Try the app → burnout-app.streamlit.app](https://burnout-app.streamlit.app)**  
**[View the full analysis → jadelrnt/burnout-prediction](https://github.com/jadelrnt/burnout-prediction)**

---

## What it does

The app asks a series of questions about your work conditions, relationships, and well-being — then applies a logistic regression model in the background to estimate your probability of severe professional burnout.

**Output:**
- Estimated burnout probability (%)
- Risk level (low / high)
- Personalized prevention advice

---

## Model

The underlying model is a **binary logistic regression** trained on 11,213 French workers.

| Metric | Value |
|--------|-------|
| AUC (ROC) | 0.81 |
| Accuracy | 81% |
| Recall | 63.5% |
| F1-score | 0.51 |

> Classification threshold set at 0.20 to maximize recall — the app is designed for prevention, so it favors sensitivity over precision.

Key predictors include: degrading tasks, boredom, out-of-hours contact, work-life balance, social support, and income level.

---

## Stack

Python · Streamlit · statsmodels · pandas · numpy

---

## Run locally

```bash
git clone https://github.com/jadelrnt/burnout-app
cd burnout-app
pip install -r requirements.txt
streamlit run app.py
```

---

## Project context

This app was developed as part of a Master 1 thesis in Data Science at Université Paris-Est Créteil (2024–2025), supervised by Sylvain Chareyron.

The goal is to make burnout risk estimation accessible and actionable — bridging statistical rigor with practical prevention.
