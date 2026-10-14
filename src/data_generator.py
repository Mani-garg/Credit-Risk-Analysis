"""
Synthetic LendingClub Loan Data Generator
Generates realistic retail credit lending portfolio data for 25,000+ borrower records.
Reflects Basel-II banking risk characteristics (Default rates by Grade A through G).
"""

import os
import random
import numpy as np
import pandas as pd

def generate_lendingclub_data(base_dir=".", num_records=25000):
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, "lending_club_loans.csv")

    print(f"[1/2] Generating {num_records:,} authentic LendingClub loan records...")
    random.seed(42)
    np.random.seed(42)

    grades = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    grade_weights = [0.22, 0.28, 0.24, 0.14, 0.08, 0.03, 0.01]
    
    # Basel baseline default probabilities per credit grade
    grade_default_probs = {
        'A': 0.05,
        'B': 0.12,
        'C': 0.19,
        'D': 0.28,
        'E': 0.38,
        'F': 0.46,
        'G': 0.55
    }

    purposes = ['debt_consolidation', 'credit_card', 'home_improvement', 'major_purchase', 'small_business', 'medical']
    purpose_weights = [0.50, 0.22, 0.10, 0.08, 0.06, 0.04]

    terms = ['36 months', '60 months']

    records = []
    for i in range(1, num_records + 1):
        loan_id = f"LN_{i:06d}"
        grade = random.choices(grades, weights=grade_weights, k=1)[0]
        sub_grade = f"{grade}{random.randint(1, 5)}"
        term = random.choices(terms, weights=[0.72, 0.28], k=1)[0]

        # Loan amount: higher grades borrow larger or prime amounts
        if grade in ['A', 'B']:
            loan_amnt = round(random.choice(range(5000, 35000, 500)), 2)
            annual_inc = round(float(np.random.lognormal(mean=11.2, sigma=0.45)), 2)
            dti = round(float(np.random.normal(loc=15.0, scale=5.0)), 2)
            int_rate = round(random.uniform(5.5, 11.5), 2)
            revol_util = round(float(np.random.beta(a=2.0, b=5.0) * 100), 1)
            delinq_2yrs = int(np.random.poisson(lam=0.08))
        elif grade in ['C', 'D']:
            loan_amnt = round(random.choice(range(3000, 25000, 500)), 2)
            annual_inc = round(float(np.random.lognormal(mean=10.9, sigma=0.50)), 2)
            dti = round(float(np.random.normal(loc=22.0, scale=6.5)), 2)
            int_rate = round(random.uniform(12.0, 18.5), 2)
            revol_util = round(float(np.random.beta(a=3.5, b=3.5) * 100), 1)
            delinq_2yrs = int(np.random.poisson(lam=0.25))
        else:
            loan_amnt = round(random.choice(range(2000, 20000, 500)), 2)
            annual_inc = round(float(np.random.lognormal(mean=10.6, sigma=0.55)), 2)
            dti = round(float(np.random.normal(loc=28.0, scale=8.0)), 2)
            int_rate = round(random.uniform(19.0, 29.5), 2)
            revol_util = round(float(np.random.beta(a=5.0, b=2.0) * 100), 1)
            delinq_2yrs = int(np.random.poisson(lam=0.65))

        # Boundaries & sanity
        dti = max(2.0, min(50.0, dti))
        annual_inc = max(18000.0, min(350000.0, annual_inc))
        revol_util = max(1.0, min(99.5, revol_util))

        # Monthly installment calculation: M = P * (r*(1+r)^n) / ((1+r)^n - 1)
        months = 36 if '36' in term else 60
        r = (int_rate / 100.0) / 12.0
        installment = round(loan_amnt * (r * (1 + r)**months) / ((1 + r)**months - 1), 2)

        emp_length_years = random.randint(1, 10)
        total_acc = random.randint(6, 45)
        purpose = random.choices(purposes, weights=purpose_weights, k=1)[0]

        # Multi-factor Default probability calculation
        base_prob = grade_default_probs[grade]
        dti_impact = (dti - 20.0) * 0.008
        util_impact = (revol_util - 50.0) * 0.003
        delinq_impact = delinq_2yrs * 0.08
        
        final_prob = np.clip(base_prob + dti_impact + util_impact + delinq_impact, 0.02, 0.92)
        defaulted = 1 if random.random() < final_prob else 0

        records.append({
            "loan_id": loan_id,
            "loan_amnt": loan_amnt,
            "term": term,
            "int_rate": int_rate,
            "installment": installment,
            "grade": grade,
            "sub_grade": sub_grade,
            "emp_length_years": emp_length_years,
            "annual_inc": annual_inc,
            "dti": dti,
            "delinq_2yrs": delinq_2yrs,
            "revol_util": revol_util,
            "total_acc": total_acc,
            "purpose": purpose,
            "defaulted": defaulted
        })

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"[2/2] Saved {len(df):,} records to {output_path}")
    print(f"      Overall Portfolio Default Rate: {df['defaulted'].mean()*100:.2f}%\n")
    return output_path

if __name__ == "__main__":
    generate_lendingclub_data(".")
