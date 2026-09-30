# Vireo Ticket Tool

Does not just use the bot's Tag to classify each ticket. It is used to determine which team is responsible for owning the ticket and generates monthly charts, tables and a business case for ticket misrouting.

## Run (Python 3.10+)

Install the required libraries:

```bash
pip install pandas matplotlib
```

Put the input files in the `data/` folder (required):

* `tickets.csv`
* `agents.csv`
* `orders.csv`
* `customers.csv`
* `products.csv`

Install from project root:

```bash
python src/run.py --data data --out out
```

### Outputs

The tool creates the following files in out/:

Monthly CSV tables by category/team.
* Monthly charts (`chart_monthly_*.png`)
* `team_volume.csv`
* `metrics.json`
* `business_case.json`
* `tickets_classified.csv`

The tool does not require API keys, network access or paid API calls.

## What It Does

Loads ticket data; corrects timezone for legacy helpdesk ticket resolved_at date, that is stored in UTC. If this wasn't applied, 2,379 tickets would seem to have been solved before they were opened.
2. Classifies tickets: applies ordered regular-expression rules found in src/classify.py to the `customer_message`, then the agent notes, then the bot tag. Maps 17 intents to Section 6's owning teams.
3. **Analyses routing and costs.** Carries out analyses of team volumes based on team as originally routed and estimates misrouting costs based on the policy figures of ₹350 per occurrence of SLA breach and ₹305 per occurrence of internal routing.

**Analysis period:** January 2025 – June 2026. The legacy records of 139 stray records from 2024 are not included.

## Validation and Checks

Validation materials are available in the `eval/` folder.

One person hand labelled 50 Billing-tagged samples of the tickets. The rules matched 49 out of 50 labels (98%); the original bot tag matched 27 out of 50 (54%).
For the 9,199 tickets that both agents were able to classify, the assigned team agreed with agent_notes in 89% of them.

The results are limited as they are based on only the Billing-tagged category, and one person is responsible for the checking of the labels. These results are not intended to be used as independent human verification of each ticket.

## Known Limitations

Rules, not a machine-learning model, are used by the classifier. If the words or language in a ticket is not recognized, it may revert to a note or the bot tag; this is the case for about 1.5% of tickets.
Small sample and nested categories (the hand-labelled sample only includes one category). Other categories are verified by Agent notes.
Only records from the helpdesk period (approx. September 2025) are available. Thus, the period of the transfer data is used for transfer-cost estimates.