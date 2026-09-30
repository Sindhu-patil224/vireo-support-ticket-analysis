
import os
import pandas as pd

# Run this from the vireo project root
os.makedirs("eval", exist_ok=True)

tickets = pd.read_csv("data/tickets.csv")
classified = pd.read_csv("out/tickets_classified.csv")

# Select tickets originally routed to Billing
billing = classified[classified["assigned_team"] == "Billing"].copy()

# Keep a reproducible random sample of up to 50 tickets
sample = billing.sample(
    n=min(50, len(billing)),
    random_state=42
)

# Add the original customer text and agent notes
sample = sample.merge(
    tickets[["ticket_id", "customer_message", "agent_notes"]],
    on="ticket_id",
    how="left"
)

# Create blank columns for your manual validation
sample["manual_intent"] = ""
sample["manual_team"] = ""
sample["notes_for_review"] = ""

columns = [
    "ticket_id",
    "customer_message",
    "agent_notes",
    "category",
    "assigned_team",
    "intent",
    "true_team",
    "manual_intent",
    "manual_team",
    "notes_for_review",
]

sample[columns].to_csv(
    "eval/billing_validation_sample.csv",
    index=False
)

print(f"Created validation sample: {len(sample)} tickets")
print("File: eval/billing_validation_sample.csv")
print("Fill in manual_intent and manual_team after reviewing each ticket.")