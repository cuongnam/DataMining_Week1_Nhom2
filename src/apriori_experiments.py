# -*- coding: utf-8 -*-
"""
Run Apriori experiments with different support/confidence/lift settings

Generates a summary CSV with counts of rules for each parameter combination
and saves top rules for manual inspection.
"""
import os
import sys
import itertools
import pandas as pd

sys.path.append(os.path.dirname(__file__))

from apriori_library import BasketPreparer, AssociationRulesMiner


def load_cleaned_data(project_root: str):
    path = os.path.normpath(os.path.join(project_root, "data/processed/cleaned_uk_data.csv"))
    if not os.path.exists(path):
        raise FileNotFoundError(f"Cleaned data not found: {path}")
    return pd.read_csv(path, parse_dates=["InvoiceDate"])


def run_experiments(
    df, output_dir: str, supports, confidences, lifts, threshold_for_generation=0.0
):
    os.makedirs(output_dir, exist_ok=True)
    bp = BasketPreparer(df)
    basket = bp.create_basket()
    basket_bool = bp.encode_basket()

    miner = AssociationRulesMiner(basket_bool)

    results = []

    for min_support, min_conf, min_lift in itertools.product(supports, confidences, lifts):
        fi = miner.mine_frequent_itemsets(min_support=min_support)
        # generate all rules with low threshold, we'll filter afterwards
        try:
            miner.generate_rules(metric="lift", min_threshold=threshold_for_generation)
        except Exception:
            # no rules generated
            rules_df = pd.DataFrame()
            miner.rules = rules_df

        filtered = miner.filter_rules(min_support=min_support, min_confidence=min_conf, min_lift=min_lift)

        count_rules = 0 if filtered is None else len(filtered)

        results.append(
            {
                "min_support": min_support,
                "min_confidence": min_conf,
                "min_lift": min_lift,
                "frequent_itemsets": len(fi) if fi is not None else 0,
                "rules_after_filter": count_rules,
            }
        )

        # save top rules for this combo (if any)
        combo_dir = os.path.join(output_dir, "rules")
        os.makedirs(combo_dir, exist_ok=True)
        combo_name = f"s{min_support}_c{min_conf}_l{min_lift}".replace(".", "p")
        out_path = os.path.join(combo_dir, f"top_rules_{combo_name}.csv")

        if count_rules > 0:
            top_n = filtered.sort_values(["lift", "confidence"], ascending=False).head(20)
            # add readable strings if missing
            if "rule_str" not in top_n.columns:
                top_n = miner.add_readable_rule_str()
                top_n = top_n.head(20)
            top_n.to_csv(out_path, index=False)
        else:
            # write an empty file with header
            pd.DataFrame().to_csv(out_path, index=False)

    summary_df = pd.DataFrame(results)
    summary_path = os.path.join(output_dir, "apriori_experiment_summary.csv")
    summary_df.to_csv(summary_path, index=False)
    return summary_df


def main():
    project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
    df = load_cleaned_data(project_root)

    supports = [0.025, 0.03, 0.02]
    confidences = [0.2, 0.4, 0.6]
    lifts = [1.0, 1.5, 2.0]

    out = run_experiments(
        df,
        output_dir=os.path.join(project_root, "data/processed/apriori_experiments"),
        supports=supports,
        confidences=confidences,
        lifts=lifts,
    )

    print("Experiment summary:")
    print(out)


if __name__ == "__main__":
    main()
