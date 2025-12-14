# -*- coding: utf-8 -*-
"""
Parameter sensitivity analysis for Apriori `min_support`.

Produces a summary CSV with, for each min_support:
- number of frequent itemsets
- number of rules after filtering
- statistics for support/confidence/lift
- product cluster counts and largest cluster size

Saves top rules per support in `data/processed/apriori_experiments/rules/`.
"""
import os
import math
import pandas as pd
import networkx as nx

from apriori_library import BasketPreparer, AssociationRulesMiner


def run_sensitivity(df, output_dir, supports, min_confidence=0.3, min_lift=1.2):
    os.makedirs(output_dir, exist_ok=True)
    bp = BasketPreparer(df)
    basket = bp.create_basket()
    basket_bool = bp.encode_basket()

    miner = AssociationRulesMiner(basket_bool)

    records = []

    rules_dir = os.path.join(output_dir, "rules")
    os.makedirs(rules_dir, exist_ok=True)

    for s in supports:
        print(f"Running support={s}")
        fi = miner.mine_frequent_itemsets(min_support=s)
        fi_count = 0 if fi is None else len(fi)

        # generate all rules first (low threshold)
        try:
            miner.generate_rules(metric="lift", min_threshold=0.0)
        except Exception:
            miner.rules = pd.DataFrame()

        filtered = miner.filter_rules(min_support=s, min_confidence=min_confidence, min_lift=min_lift)

        rules_count = 0 if filtered is None else len(filtered)

        # rule stats
        if rules_count > 0:
            supp_stats = filtered["support"].describe().to_dict()
            conf_stats = filtered["confidence"].describe().to_dict()
            lift_stats = filtered["lift"].describe().to_dict()
        else:
            supp_stats = conf_stats = lift_stats = {k: float("nan") for k in ["mean","50%","std","min","max"]}

        # product clusters via undirected graph of rules (items as nodes)
        num_clusters = 0
        largest_cluster = 0
        if rules_count > 0:
            G = nx.Graph()
            for _, row in filtered.iterrows():
                ants = list(row["antecedents"]) if "antecedents" in row else []
                cons = list(row["consequents"]) if "consequents" in row else []
                for a in ants:
                    for c in cons:
                        G.add_edge(str(a), str(c))

            comps = list(nx.connected_components(G)) if G.number_of_nodes() > 0 else []
            num_clusters = len(comps)
            largest_cluster = max((len(c) for c in comps), default=0)

        # save top rules for this support
        combo_name = f"s{s}".replace(".", "p")
        out_path = os.path.join(rules_dir, f"top_rules_{combo_name}.csv")
        if rules_count > 0:
            df_top = filtered.copy()
            if "rule_str" not in df_top.columns:
                df_top = miner.add_readable_rule_str()
            df_top.sort_values(["lift","confidence"], ascending=False).head(50).to_csv(out_path, index=False)
        else:
            pd.DataFrame().to_csv(out_path, index=False)

        records.append({
            "min_support": s,
            "frequent_itemsets": fi_count,
            "rules_after_filter": rules_count,
            "rules_num_clusters": num_clusters,
            "rules_largest_cluster_size": largest_cluster,
            "support_mean": supp_stats.get("mean", float("nan")),
            "support_median": supp_stats.get("50%", float("nan")),
            "confidence_mean": conf_stats.get("mean", float("nan")),
            "confidence_median": conf_stats.get("50%", float("nan")),
            "lift_mean": lift_stats.get("mean", float("nan")),
            "lift_median": lift_stats.get("50%", float("nan")),
        })

    summary = pd.DataFrame(records).sort_values("min_support")
    summary_path = os.path.join(output_dir, "parameter_sensitivity_summary.csv")
    summary.to_csv(summary_path, index=False)
    return summary


def main():
    project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
    data_path = os.path.join(project_root, "data/processed/cleaned_uk_data.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Cleaned data not found: {data_path}")

    df = pd.read_csv(data_path, parse_dates=["InvoiceDate"]) 

    supports = [0.015, 0.02, 0.025, 0.03, 0.04, 0.05]

    out_dir = os.path.join(project_root, "data/processed/apriori_experiments")

    summary = run_sensitivity(df, out_dir, supports=supports, min_confidence=0.3, min_lift=1.2)

    print("Parameter sensitivity summary:")
    print(summary)


if __name__ == "__main__":
    main()
