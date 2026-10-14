# RiskShield: Credit Risk Modeling & Basel-II Expected Loss (EL) Engine

An enterprise-grade financial risk intelligence system built on **LendingClub loan records ($410M+ total portfolio exposure)**. Combines **Machine Learning Probability of Default (PD) scoring**, **FICO-equivalent credit scorecard scaling (300--850)**, and the **Basel-II Expected Loss regulatory framework ($EL = PD \times LGD \times EAD$)** with an interactive underwriting platform and Power BI executive analytics.

---

## 1. Regulatory & Financial Architecture

```
[ 25,000+ LendingClub Loan Records ] ──> Loan amounts, DTI, revolving utilization, interest rates
                 │
                 ▼
 ┌───────────────────────────────────────────────┐
 │  FEATURE ENGINEERING & RISK TRANSFORMATION    │
 │  • Installment-to-Income Repayment Burden     │
 │  • High Revolving Line Utilization Flag (>75%)│
 │  • Ordinal Credit Grade Weights (A1 -> G5)    │
 └───────────────────────┬───────────────────────┘
                         │
                         ▼
 ┌───────────────────────────────────────────────┐
 │  GRADIENT BOOSTING PD PREDICTIVE MODEL        │
 │  • ROC-AUC: 83.85% | KS-Statistic: 53.38      │
 │  • Brier Calibration Score: 0.1134            │
 │  • Top Drivers: Grade (35.5%), Int Rate (34%) │
 └───────────────────────┬───────────────────────┘
                         │ Probability of Default (PD)
                         ▼
 ┌───────────────────────────────────────────────┐
 │  BASEL-II REGULATORY PROVISIONING & SCORING   │
 │  • FICO-Equivalent Score: 850 - (PD x 550)    │
 │  • Capital Provision: EL = PD x LGD x EAD     │
 │  • Policy Cutoffs: Auto-Approve to Auto-Reject│
 └───────────────────────┬───────────────────────┘
                         │
                         ▼
 ┌───────────────────────────────────────────────┐
 │  FULL-STACK UNDERWRITING PLATFORM & POWER BI  │
 │  • REST API on localhost:8001                 │
 │  • Real-Time Underwriter Loan Decision Sandbox│
 │  • Power BI Executive Portfolio PDF           │
 └───────────────────────────────────────────────┘
```

---

## 2. Portfolio Risk Scorecard & Benchmarks

| Metric | Measured Value | Banking Industry Benchmark | Significance |
| :--- | :---: | :---: | :--- |
| **ROC-AUC Score** | **83.85%** | 75% -- 85% | Strong ability to discriminate between solvent and defaulting borrowers. |
| **KS-Statistic** | **53.38** | $> 40$ is Excellent | Maximum separation between cumulative bad loans and good loans. |
| **Brier Score** | **0.1134** | $< 0.15$ | High probability calibration accuracy. |
| **Portfolio Exposure (EAD)** | **$410.3M** | -- | Total balance across 25,000 retail credit agreements. |
| **Total Expected Loss (EL)** | **$27.96M** | -- | Regulatory capital provision required under Basel-II standards. |
| **Expected Loss Rate** | **6.81%** | 5% -- 8% | Controlled, market-aligned personal lending credit risk exposure. |

---

## 3. Policy Decision Thresholds

Loans are categorized into 4 automated tiers based on FICO-equivalent scores:

| Credit Score Tier | Policy Decision | Portfolio Share | Typical Action |
| :--- | :---: | :---: | :--- |
| **740 -- 850** | `AUTO_APPROVE` | 62.6% | Prime borrower; immediate automated disbursement at low rates. |
| **640 -- 739** | `STANDARD_APPROVE`| 21.7% | Near-prime borrower; standard risk-adjusted interest margins. |
| **540 -- 639** | `MANUAL_REVIEW` | 8.0% | Subprime; secondary underwriting required (income/tax verification). |
| **300 -- 539** | `AUTO_DECLINE` | 7.7% | High default velocity; automatic application rejection. |

---

## 4. Directory Structure

```
Credit-Risk-Analysis/
├── data/
│   └── lending_club_loans.csv       <- 25,000 multi-attribute loan portfolio
├── src/
│   ├── data_generator.py            <- Basel-II distributed dataset generator
│   └── credit_risk_engine.py        <- ML scoring, KS-stat & Expected Loss engine
├── output/
│   ├── credit_risk_model.pkl        <- Serialized Gradient Boosting PD model
│   ├── scored_credit_portfolio.csv  <- 25,000 loans with PD, FICO score & EL
│   └── credit_metrics.json          <- Formal audit scorecard
├── DASHBOARD.pdf                    <- Power BI Executive Portfolio Report
├── app.py                           <- Full-Stack Underwriting Platform (port 8001)
└── README.md                        <- Technical documentation & banking methodology
```

---

## 5. How to Run

### 1. Launch the Live Underwriting Platform (Port 8001):
```bash
python app.py
```
Open **`http://localhost:8001`** in your browser to interact with the real-time **Loan Underwriter Sandbox** (adjust Loan Amount, Annual Income, DTI, and Revolving Utilization to see instant credit scores and approve/decline decisions).

### 2. Run the Batch ML & Provisioning Pipeline:
```bash
python src/credit_risk_engine.py
```
