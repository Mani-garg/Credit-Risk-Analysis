# Power BI Executive Dashboard Walkthrough & Risk Findings

This document outlines the visual structure, interactive slicers, and core risk findings of the **LendingClub Credit Risk Portfolio Power BI Dashboard**.

The report is compiled from 50,000 retail lending facilities (\$787.1M funded balance) and is exported as [`dashboard/DASHBOARD.pdf`](./DASHBOARD.pdf).

---

## 1. Visual Layout & Page Structure

### Page 1: Executive C-Suite Risk & Capital Overview
* **Top Metric Cards (KPIs):**
  * **Total Loan Capital Funded:** `$787.1M`
  * **Total Defaulted Volume:** `$154.2M`
  * **Weighted Portfolio Default Rate:** `19.59%`
  * **Regulatory Expected Loss Reserve:** `$69.39M`
  * **Average Loan Facility Size:** `$15,742`
* **Visual 1 (Donut Chart):** Total Capital Exposure by Loan Status (`Fully Paid` 72.4%, `Charged Off` 17.6%, `Current` 8.2%, `Late` 1.8%).
* **Visual 2 (Clustered Column Chart):** Funded Volume vs. Default Rate by Credit Grade (Grades A through G).
* **Visual 3 (Line & Area Trend):** Monthly Loan Origination Volume & Default Rate YoY Trajectory (2021--2024).

### Page 2: Risk Drivers & Demographics
* **Visual 4 (Bar Chart):** Default Rate across Debt-to-Income (DTI) Brackets (`<15%`, `15--25%`, `25--35%`, `>35%`).
* **Visual 5 (Treemap):** Loan Capital Origination by Loan Purpose (`Debt Consolidation` 55%, `Credit Card Refinance` 22%, `Home Improvement` 8%, `Small Business` 3%).
* **Visual 6 (Stacked Bar Chart):** Home Ownership vs. Risk Segment (`MORTGAGE`, `RENT`, `OWN`).

### Page 3: Geographic Risk Distribution
* **Visual 7 (Filled Map & Matrix):** State-by-state credit default intensity across the US (California, Texas, Florida, New York leading originations).
* **Visual 8 (Decomposition Tree / Drill-Through):** Root cause decomposition from Total Defaulted Capital $\rightarrow$ Grade $\rightarrow$ Purpose $\rightarrow$ Employment Length.

---

## 2. Interactive Slicers & Filters
* **Date Hierarchy Slicer:** Year (`2021`, `2022`, `2023`, `2024`), Quarter, Month.
* **Credit Grade Slicer:** Multi-select buttons for Grades `A`, `B`, `C`, `D`, `E`, `F`, `G`.
* **Loan Purpose Dropdown:** Slices portfolio by borrowing motive.
* **Term Toggle:** `36 months` vs. `60 months`.

---

## 3. Key Risk Insights & Business Takeaways

1. **Severe Grade G Default Concentration:**
   * Grade A loans maintain a rock-solid default rate of **4.6%**, whereas Grade G loans experience a staggering **54.2% default rate**.
   * **Recommendation:** Underwriting policy must enforce automated rejections or require collateral for sub-prime Grade F/G applicants with DTI $> 25\%$.

2. **DTI as the Primary Leading Indicator:**
   * Borrowers with DTI $> 30\%$ exhibit a default rate **2.4x higher** than borrowers with DTI $< 15\%$, regardless of annual income.

3. **Debt Consolidation Vulnerability:**
   * Debt consolidation loans represent over **55% of total funded volume** and **61% of total charged-off balances**, indicating chronic borrower overleveraging.
