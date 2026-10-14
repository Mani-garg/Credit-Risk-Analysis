# LendingClub Credit Risk & Loan Portfolio Power BI Analytics

An enterprise **Business Intelligence & Credit Risk Dashboard** developed in **Microsoft Power BI** on **50,000+ LendingClub retail loan agreements ($787.1M total funded exposure)**. Designed with a robust **Star Schema data architecture**, advanced **DAX measures**, and executive drill-through pages for portfolio risk management, capital loss provisioning, and underwriting yield analysis.

---

## 1. Executive Portfolio Highlights & KPIs

| Metric | Portfolio Value | Significance & Banking Context |
| :--- | :---: | :--- |
| **Total Funded Capital** | **$787.1M** | Total retail debt facilities originated across 2021--2024. |
| **Total Loan Agreements** | **50,000** | Diversified personal loan accounts across 30 US states. |
| **Portfolio Default Rate** | **19.59%** | Capital-weighted default rate across standard retail facilities. |
| **Expected Credit Loss (EL)** | **$69.39M** | Regulatory loss reserve provision under the **Basel-II Standardized Framework** (assuming 45% Loss Given Default). |
| **Average Loan Facility** | **$15,742** | Average principal balance per originated borrower. |
| **Weighted Average Yield** | **14.09%** | Capital-weighted annual interest rate yield across the portfolio. |

---

## 2. Data Architecture & Star Schema Model

The data model is engineered following enterprise data warehousing standards, segregating transactions into a high-density **Fact Table** joined with four optimized **Dimension Tables** via one-to-many (`1:*`) relationships:

```
                            ┌────────────────────────────────────┐
                            │              Dim_Date              │
                            │  date_key (PK) | Year | Quarter    │
                            │  MonthName | MonthNum | YearMonth  │
                            └─────────────────┬──────────────────┘
                                              │ 1
                                              │
                                              │ *
┌─────────────────────────────┐               ▼               ┌─────────────────────────────┐
│          Dim_Grade          │  1       ┌─────────┐       1  │        Dim_Geography        │
│ grade (PK) | sub_grade      ├─────────►│  Fact_  │◄─────────┤ state_code (PK) | state_name│
│ credit_tier | risk_level    │ *        │  Loans  │        * │ region (Midwest, South...)  │
└─────────────────────────────┘          └────▲────┘          └─────────────────────────────┘
                                              │ *
                                              │
                                              │ 1
                            ┌─────────────────┴──────────────────┐
                            │            Dim_Purpose             │
                            │ purpose_code (PK) | purpose_name   │
                            │ category (Refinance, Consumer...)  │
                            └────────────────────────────────────┘
```

### Table Specifications:
* **`Fact_Loans` (50,000 rows):** Primary transaction table containing loan amounts, funded capital, interest rates, installment terms, borrower DTI, revolving utilization, and default status.
* **`Dim_Date`:** Comprehensive calendar dimension supporting time-intelligence DAX functions (`TOTALYTD`, `SAMEPERIODLASTYEAR`, `DATEADD`).
* **`Dim_Grade`:** Ordinal credit grade hierarchy from Prime (`A1-A5`) to Distressed Speculative (`G1-G5`).
* **`Dim_Geography`:** Geographic regional hierarchy for spatial risk mapping across US territories.
* **`Dim_Purpose`:** Clean categorical segmentation of loan motives (Debt Consolidation, Credit Card Refinance, etc.).

---

## 3. Core DAX Calculations & Formulas

All business logic is implemented using optimized DAX formulas stored in [`dax/DAX_Measures.dax`](./dax/DAX_Measures.dax).

### 1. Default Rate & Risk Provisioning
```dax
Default Rate % = 
DIVIDE(
    CALCULATE(SUM('Fact_Loans'[funded_amount]), 'Fact_Loans'[is_default] = 1),
    SUM('Fact_Loans'[funded_amount]),
    0
)

Expected Credit Loss (EL) = 
[Total Defaulted Amount] * 0.45 // Basel-II Retail LGD Benchmark (45%)
```

### 2. Weighted Portfolio Yield & DTI
```dax
Weighted Average Interest Rate = 
DIVIDE(
    SUMX('Fact_Loans', 'Fact_Loans'[int_rate] * 'Fact_Loans'[funded_amount]),
    [Total Funded Amount],
    0
) / 100

Weighted Average DTI = 
DIVIDE(
    SUMX('Fact_Loans', 'Fact_Loans'[dti] * 'Fact_Loans'[funded_amount]),
    [Total Funded Amount],
    0
) / 100
```

### 3. Time Intelligence (MoM & YoY Growth)
```dax
Funded Amount YoY Growth % = 
VAR PriorYear = CALCULATE([Total Funded Amount], SAMEPERIODLASTYEAR('Dim_Date'[date]))
RETURN
DIVIDE([Total Funded Amount] - PriorYear, PriorYear, 0)

Default Rate MoM Change = 
VAR CurrentRate = [Default Rate %]
VAR PriorMonthRate = CALCULATE([Default Rate %], DATEADD('Dim_Date'[date], -1, MONTH))
RETURN
IF(ISBLANK(PriorMonthRate), BLANK(), CurrentRate - PriorMonthRate)
```

---

## 4. Key Business Insights & Underwriting Takeaways

1. **Exponential Risk Escalation across Sub-prime Grades:**
   * **Grade A (Prime):** Default rate of **4.6%** with an average interest rate of **7.2%**.
   * **Grade G (Distressed):** Default rate jumps to **54.2%** with interest rates exceeding **32.7%**.
   * *Business Impact:* The current 32% interest rate cap on Grade G loans is insufficient to offset the 54% loss rate; underwriting guidelines should restrict Grade G originations to secured facilities only.

2. **DTI as the Primary Debt-Burden Predictor:**
   * Borrowers with DTI $> 30\%$ default at **2.4x the rate** of borrowers with DTI $< 15\%$, irrespective of annual income level.

3. **Concentration in Debt Consolidation:**
   * Over **55% ($432.9M) of total funded capital** is concentrated in debt consolidation loans, accounting for **61% of all credit defaults**.

---

## 5. How to Explore the Dashboard

* **PDF Executive Export:** Open [`dashboard/DASHBOARD.pdf`](./dashboard/DASHBOARD.pdf) for the original Power BI report pages.
* **Interactive Web Viewer:** Double-click [`dashboard/Interactive_Dashboard_Viewer.html`](./dashboard/Interactive_Dashboard_Viewer.html) to interact with slicers (Grade, Term, Purpose) and dynamic KPI recalculations in any browser.
* **Power BI Desktop:**
  1. Open Power BI Desktop.
  2. Import the Star Schema CSV files from the `data/` folder.
  3. Relate tables as documented in the Star Schema diagram above.
  4. Paste DAX formulas from `dax/DAX_Measures.dax`.

---

## 6. Repository Structure

```
Credit-Risk-Analysis/
├── dashboard/
│   ├── DASHBOARD.pdf                      # Exported Power BI Executive Report
│   ├── Executive_Summary.md               # Visual page structure & risk takeaways
│   └── Interactive_Dashboard_Viewer.html  # Interactive offline slicer dashboard
├── data/
│   ├── Fact_Loans.csv                     # 50,000 LendingClub loan records ($787M)
│   ├── Dim_Date.csv                       # Calendar table with date hierarchy
│   ├── Dim_Grade.csv                      # Credit tier and risk benchmark mapping
│   ├── Dim_Geography.csv                  # State and US regional hierarchy
│   └── Dim_Purpose.csv                    # Loan category taxonomy
├── dax/
│   ├── DAX_Measures.dax                   # Formatted DAX calculations
│   └── DAX_Documentation.md               # Measure definitions and business logic
├── DASHBOARD.pdf                          # Root quick-access report
└── README.md                              # Project documentation
```

---

**Author:** Mani Garg  
**Focus:** Power BI &bull; DAX &bull; Data Modeling &bull; Financial Analytics  
**Institution:** Punjab Engineering College, Chandigarh
