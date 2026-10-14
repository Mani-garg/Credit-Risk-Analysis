"""
=============================================================================
CREDIT RISK MODELING & BASEL-II EXPECTED LOSS (EL) ENGINE
-----------------------------------------------------------------------------
1. Advanced Feature Engineering (Debt-to-Income, Installment-to-Income, Utilization)
2. Gradient Boosting Classifier for Probability of Default (PD) Modeling
3. Banking Risk Evaluation: ROC-AUC, PR-AUC, Kolmogorov-Smirnov (KS-Statistic)
4. Basel-II Regulatory Framework: EL = PD * LGD * EAD
5. Credit Score Scaling: Translates PD into 300-850 FICO-Equivalent Credit Score
=============================================================================
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, brier_score_loss

def calculate_ks_statistic(y_true, y_prob):
    """Calculates Kolmogorov-Smirnov (KS) statistic - the gold standard in retail credit banking."""
    df_eval = pd.DataFrame({'y': y_true, 'prob': y_prob})
    df_eval = df_eval.sort_values(by='prob', ascending=False)
    df_eval['cum_bads'] = (df_eval['y'] == 1).cumsum() / (df_eval['y'] == 1).sum()
    df_eval['cum_goods'] = (df_eval['y'] == 0).cumsum() / (df_eval['y'] == 0).sum()
    ks_stat = max(abs(df_eval['cum_bads'] - df_eval['cum_goods']))
    return round(float(ks_stat) * 100, 2)

def run_credit_risk_pipeline(base_dir="."):
    data_path = os.path.join(base_dir, "data", "lending_club_loans.csv")
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(data_path):
        from data_generator import generate_lendingclub_data
        generate_lendingclub_data(base_dir)

    print("=" * 75)
    print("      LENDINGCLUB CREDIT RISK & BASEL-II EXPECTED LOSS ENGINE")
    print("=" * 75)

    df = pd.read_csv(data_path)
    print(f"\n--> Loaded {len(df):,} LendingClub loan records.")
    print(f"--> Baseline Default Distribution: {df['defaulted'].value_counts(normalize=True).to_dict()}")

    # 1. Feature Engineering
    print("--> Engineering Financial Risk Features:")
    print("    * Installment-to-Income Ratio (Repayment burden)")
    print("    * High Revolving Utilization Flag (>75%)")
    print("    * Ordinal Grade Mapping (A=1 -> G=7)")

    grade_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7}
    df['grade_num'] = df['grade'].map(grade_map)
    df['term_num'] = df['term'].apply(lambda x: 36 if '36' in str(x) else 60)
    df['installment_to_inc'] = ((df['installment'] * 12) / df['annual_inc']).round(4)
    df['high_util_flag'] = (df['revol_util'] > 75.0).astype(int)

    feature_cols = [
        'loan_amnt', 'int_rate', 'installment', 'grade_num', 'term_num',
        'emp_length_years', 'annual_inc', 'dti', 'delinq_2yrs',
        'revol_util', 'total_acc', 'installment_to_inc', 'high_util_flag'
    ]

    X = df[feature_cols]
    y = df['defaulted']

    # 2. Stratified Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"--> Training Set: {len(X_train):,} loans | Test Set: {len(X_test):,} loans")

    # 3. Model Training (Gradient Boosting for Credit Risk)
    print("--> Training Gradient Boosting Probability of Default (PD) Model...")
    model = GradientBoostingClassifier(
        n_estimators=140,
        learning_rate=0.07,
        max_depth=4,
        subsample=0.85,
        random_state=42
    )
    model.fit(X_train, y_train)

    # 4. Evaluation & Banking Metrics
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.30).astype(int) # Optimal financial cutoff for risk aversion

    roc_auc = round(float(roc_auc_score(y_test, y_prob)), 4)
    ks_stat = calculate_ks_statistic(y_test.values, y_prob)
    brier = round(float(brier_score_loss(y_test, y_prob)), 4)
    prec = round(float(precision_score(y_test, y_pred)), 4)
    rec = round(float(recall_score(y_test, y_pred)), 4)
    f1 = round(float(f1_score(y_test, y_pred)), 4)

    print("\n" + "-"*50)
    print("[METRICS] CREDIT RISK SCORECARD & BASEL-II BENCHMARKS:")
    print(f"  * ROC-AUC Score:          {roc_auc * 100:.2f}%  (Discriminatory power)")
    print(f"  * KS-Statistic:           {ks_stat:.2f}         (Banking Standard: >40 is Excellent)")
    print(f"  * Brier Score:            {brier:.4f}         (Calibration accuracy)")
    print(f"  * Precision @ 0.30 Cut:   {prec * 100:.2f}%")
    print(f"  * Recall @ 0.30 Cut:      {rec * 100:.2f}%")
    print("-" * 50)

    # 5. Full Portfolio Scoring & Basel-II Expected Loss (EL)
    full_pd = model.predict_proba(X)[:, 1]
    df['pd_score'] = full_pd.round(4)

    # Credit Score Scaling: 850 - (PD * 550)
    df['credit_score'] = (850 - (df['pd_score'] * 550)).astype(int)

    def assign_underwriting_decision(row):
        score = row['credit_score']
        if score >= 740:
            return "AUTO_APPROVE"
        elif score >= 640:
            return "STANDARD_APPROVE"
        elif score >= 540:
            return "MANUAL_REVIEW"
        else:
            return "AUTO_DECLINE"

    df['underwriting_decision'] = df.apply(assign_underwriting_decision, axis=1)

    # Basel-II Expected Loss: EL = PD * LGD * EAD
    # LGD = 45% (Unsecured Personal Loans standard), EAD = loan_amnt
    LGD = 0.45
    df['ead_amount'] = df['loan_amnt']
    df['expected_loss'] = (df['pd_score'] * LGD * df['ead_amount']).round(2)

    total_portfolio_exposure = df['ead_amount'].sum()
    total_expected_loss = df['expected_loss'].sum()
    expected_loss_rate = (total_expected_loss / total_portfolio_exposure) * 100

    print("\n[CAPITAL] BASEL-II PORTFOLIO CAPITAL PROVISIONING:")
    print(f"  * Total Exposure at Default (EAD): ${total_portfolio_exposure:,.2f}")
    print(f"  * Total Expected Loss (EL):        ${total_expected_loss:,.2f}")
    print(f"  * Expected Loss Rate:              {expected_loss_rate:.2f}%")

    # 6. Top Risk Drivers (Feature Importance)
    feat_imp = pd.DataFrame({
        'Feature': feature_cols,
        'Importance': model.feature_importances_
    }).sort_values(by='Importance', ascending=False)

    print("\n[DRIVERS] TOP RISK FACTORS DRIVING DEFAULT:")
    for _, row in feat_imp.head(5).iterrows():
        print(f"  {row['Feature']:<22}: {row['Importance']*100:.1f}%")

    # 7. Save Models and Scored Database
    model_save_path = os.path.join(output_dir, "credit_risk_model.pkl")
    joblib.dump(model, model_save_path)

    scored_csv_path = os.path.join(output_dir, "scored_credit_portfolio.csv")
    df.to_csv(scored_csv_path, index=False)

    metrics_save_path = os.path.join(output_dir, "credit_metrics.json")
    metrics_payload = {
        "roc_auc": float(roc_auc),
        "ks_statistic": float(ks_stat),
        "brier_score": float(brier),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "total_exposure": float(total_portfolio_exposure),
        "total_expected_loss": float(total_expected_loss),
        "expected_loss_rate": float(expected_loss_rate),
        "top_features": [{'Feature': str(r['Feature']), 'Importance': float(r['Importance'])} for _, r in feat_imp.head(6).iterrows()],
        "decision_counts": {str(k): int(v) for k, v in df['underwriting_decision'].value_counts().items()}
    }
    with open(metrics_save_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    print(f"\n[OK] Model successfully serialized to: {model_save_path}")
    print(f"[OK] Scored portfolio dataset saved to: {scored_csv_path}")
    print("=" * 75)
    return scored_csv_path

if __name__ == "__main__":
    run_credit_risk_pipeline(".")
