
"""Vireo ticket analysis. Usage: python src/run.py [--data data] [--out out]"""

import argparse
import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from classify import classify_row


# SLA targets in minutes, from the support policy
TGT = {
    "chat": 15,
    "voice": 120,
    "social": 240,
    "email": 480,
}

# Policy costs in rupees
CREDIT = 350
XFER = 305


def load(data_dir):
    """Load tickets and correct legacy UTC resolution timestamps."""
    path = os.path.join(data_dir, "tickets.csv")

    tickets = pd.read_csv(
        path,
        parse_dates=[
            "created_at",
            "first_response_at",
            "resolved_at",
        ],
    )

    legacy = tickets["source_system"] == "legacy_fd"

    # Legacy resolved_at timestamps are UTC; helpdesk timestamps are IST.
    tickets.loc[legacy, "resolved_at"] += pd.Timedelta(
        hours=5, minutes=30
    )

    return tickets


def enrich(tickets):
    """Classify ticket intent, owner, SLA breach and routing accuracy."""

    results = tickets.apply(
        lambda row: classify_row(
            row.customer_message,
            row.agent_notes,
        ),
        axis=1,
        result_type="expand",
    )

    tickets[["intent", "true_team", "label_src"]] = results

    # Assign frontline tickets to the relevant channel team.
    frontline_teams = {
        "chat": "Chat Frontline",
        "email": "Email Frontline",
        "voice": "Voice Frontline",
        "social": "Chat Frontline",
    }

    tickets["true_team"] = np.where(
        tickets["true_team"] == "Frontline",
        tickets["channel"].map(frontline_teams),
        tickets["true_team"],
    )

    # For unclassified tickets, retain the original assigned team.
    unclassified = tickets["intent"] == "Unclassified"

    tickets.loc[unclassified, "true_team"] = (
        tickets.loc[unclassified, "assigned_team"]
    )

    tickets["month"] = (
        tickets["created_at"].dt.to_period("M").astype(str)
    )

    tickets["frm_min"] = (
        tickets["first_response_at"] - tickets["created_at"]
    ).dt.total_seconds() / 60

    tickets["breach"] = (
        tickets["frm_min"] > tickets["channel"].map(TGT)
    )

    tickets["misrouted"] = (
        tickets["assigned_team"] != tickets["true_team"]
    )

    return tickets


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--data", default="data")
    parser.add_argument("--out", default="out")

    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    tickets = enrich(load(args.data))

    # Save ticket-level classification results.
    classified_columns = [
        "ticket_id",
        "month",
        "channel",
        "category",
        "assigned_team",
        "intent",
        "true_team",
        "label_src",
        "misrouted",
        "breach",
        "transfers",
        "source_system",
    ]

    tickets[classified_columns].to_csv(
        os.path.join(args.out, "tickets_classified.csv"),
        index=False,
    )

    # Analyse the requested period: January 2025 to June 2026.
    tickets["ym"] = tickets["month"]

    full = tickets[
        tickets["created_at"] >= "2025-01-01"
    ].copy()

    # Save monthly breakdowns.
    pd.crosstab(
        full["ym"], full["category"]
    ).to_csv(
        os.path.join(args.out, "monthly_by_bot_category.csv")
    )

    pd.crosstab(
        full["ym"], full["intent"]
    ).to_csv(
        os.path.join(args.out, "monthly_by_intent.csv")
    )

    pd.crosstab(
        full["ym"], full["assigned_team"]
    ).to_csv(
        os.path.join(args.out, "monthly_by_team_as_routed.csv")
    )

    pd.crosstab(
        full["ym"], full["true_team"]
    ).to_csv(
        os.path.join(args.out, "monthly_by_team_true.csv")
    )

    # Compare team volumes before and after content-based classification.
    volume = pd.DataFrame({
        "as_routed": full["assigned_team"].value_counts(),
        "by_content": full["true_team"].value_counts(),
    }).fillna(0).astype(int)

    volume["share_routed_%"] = (
        volume["as_routed"] / len(full) * 100
    ).round(1)

    volume["share_content_%"] = (
        volume["by_content"] / len(full) * 100
    ).round(1)

    volume = volume.sort_values(
        "by_content", ascending=False
    )

    volume.to_csv(
        os.path.join(args.out, "team_volume.csv")
    )

    print("\nTeam volume comparison:")
    print(volume)

    # Calculate business metrics.
    helpdesk = tickets[
        tickets["source_system"] == "helpdesk"
    ]

    billing = full[
        full["assigned_team"] == "Billing"
    ]

    misrouted_delivery = billing[
        billing["intent"].isin([
            "Delivery not received",
            "Wrong / damaged item",
        ])
    ]

    genuine_billing = billing[
        ~billing.index.isin(misrouted_delivery.index)
    ]

    metrics = {
        "tickets_window": int(len(full)),

        "billing_share_routed_%": round(
            (full["assigned_team"] == "Billing").mean() * 100, 1
        ),

        "logistics_share_routed_%": round(
            (full["assigned_team"] == "Logistics").mean() * 100, 1
        ),

        "billing_true_share_%": round(
            (full["true_team"] == "Billing").mean() * 100, 1
        ),

        "logistics_true_share_%": round(
            (full["true_team"] == "Logistics").mean() * 100, 1
        ),

        "billing_tagged_that_are_delivery": int(
            len(misrouted_delivery)
        ),

        "billing_tagged_delivery_share_%": round(
            len(misrouted_delivery) / len(billing) * 100, 1
        ) if len(billing) else 0,

        "billing_breach_rate_true_billing_%": round(
            genuine_billing["breach"].mean() * 100, 1
        ),

        "billing_breach_rate_misrouted_%": round(
            misrouted_delivery["breach"].mean() * 100, 1
        ),

        "overall_breach_rate_%": round(
            full["breach"].mean() * 100, 1
        ),

        "breach_credit_rs_18m": int(
            full["breach"].sum() * CREDIT
        ),

        "billing_breach_credit_rs_18m": int(
            billing["breach"].sum() * CREDIT
        ),
    }

    # Transfer data is available for helpdesk-era tickets.
    billing_helpdesk = helpdesk[
        helpdesk["assigned_team"] == "Billing"
    ]

    other_helpdesk = helpdesk[
        helpdesk["assigned_team"] != "Billing"
    ]

    misrouted_helpdesk = billing_helpdesk[
        billing_helpdesk["intent"].isin([
            "Delivery not received",
            "Wrong / damaged item",
        ])
    ]

    genuine_helpdesk = billing_helpdesk[
        ~billing_helpdesk.index.isin(
            misrouted_helpdesk.index
        )
    ]

    metrics["xfer_per_ticket_billing_helpdesk"] = round(
        billing_helpdesk["transfers"].mean(), 3
    )

    metrics["xfer_per_ticket_other_helpdesk"] = round(
        other_helpdesk["transfers"].mean(), 3
    )

    metrics["xfer_per_ticket_billing_misrouted"] = round(
        misrouted_helpdesk["transfers"].mean(), 3
    )

    metrics["xfer_per_ticket_billing_true"] = round(
        genuine_helpdesk["transfers"].mean(), 3
    )

    # Save metrics.json.
    metrics_path = os.path.join(args.out, "metrics.json")

    with open(metrics_path, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    print("\nBusiness metrics:")
    print(json.dumps(metrics, indent=2))

    # Create the business case using observed differences.
    breach_difference = (
        metrics["billing_breach_rate_misrouted_%"]
        - metrics["billing_breach_rate_true_billing_%"]
    ) / 100

    transfer_difference = (
        metrics["xfer_per_ticket_billing_misrouted"]
        - metrics["xfer_per_ticket_billing_true"]
    )

    extra_breach_cost = breach_difference * CREDIT
    extra_transfer_cost = transfer_difference * XFER

    extra_cost = extra_breach_cost + extra_transfer_cost

    misrouted_share = (
        metrics["billing_tagged_that_are_delivery"]
        / metrics["tickets_window"]
        if metrics["tickets_window"] else 0
    )

    business_case = {
        "tickets_analysed": metrics["tickets_window"],

        "misrouted_delivery_tickets": (
            metrics["billing_tagged_that_are_delivery"]
        ),

        "extra_breach_cost_per_ticket_rs": round(
            extra_breach_cost, 2
        ),

        "extra_transfer_cost_per_ticket_rs": round(
            extra_transfer_cost, 2
        ),

        "estimated_extra_cost_per_misrouted_ticket_rs": round(
            extra_cost, 2
        ),

        "annual_estimate_at_650_tickets_per_week_rs": round(
            650 * misrouted_share * extra_cost * 52, 2
        ),

        "annual_estimate_at_150_tickets_per_week_rs": round(
            150 * misrouted_share * extra_cost * 52, 2
        ),

        "note": (
            "These are estimates based on observed rate differences. "
            "Transfer figures use helpdesk-era data. Confirm actual "
            "weekly ticket volume before relying on annual estimates."
        ),
    }

    business_case_path = os.path.join(
        args.out, "business_case.json"
    )

    with open(
        business_case_path, "w", encoding="utf-8"
    ) as file:
        json.dump(business_case, file, indent=2)

    print("\nBusiness case saved:")
    print(json.dumps(business_case, indent=2))

    # Generate monthly charts.
    charts = [
        (
            "chart_monthly_by_category",
            "category",
            "Monthly tickets by bot category tag",
        ),
        (
            "chart_monthly_by_team",
            "assigned_team",
            "Monthly tickets by team as routed",
        ),
        (
            "chart_monthly_by_true_team",
            "true_team",
            "Monthly tickets by team based on message content",
        ),
    ]

    for filename, column, title in charts:
        chart_data = pd.crosstab(
            full["ym"], full[column]
        )

        ax = chart_data.plot(
            kind="bar",
            stacked=True,
            figsize=(12, 5.5),
            colormap="tab20",
            width=0.85,
        )

        ax.set_title(title)
        ax.set_xlabel("")
        ax.set_ylabel("Tickets")

        ax.legend(
            fontsize=7,
            ncol=2,
            bbox_to_anchor=(1.01, 1),
            loc="upper left",
        )

        plt.xticks(
            rotation=60,
            ha="right",
            fontsize=8,
        )

        plt.tight_layout()

        plt.savefig(
            os.path.join(args.out, filename + ".png"),
            dpi=130,
        )

        plt.close()

    print("\nAll outputs saved in:", args.out)


if __name__ == "__main__":
    main()