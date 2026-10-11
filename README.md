# CloudNest SaaS Subscription Business Analysis (SQL)

## Project summary
An end-to-end, SQL-focused analysis of a fictional subscription software business. It explores signups, recurring revenue, churn, customer support, acquisition channels, cohorts, and practical decisions.

## Business problem
CloudNest needs to understand which customers and plans generate revenue, where cancellations and support friction appear, and how retention varies across signup cohorts and acquisition sources.

## Dataset
All data is synthetic and generated locally with a fixed random seed; there are no real customer records or third-party license restrictions. The observation window is January 2023 through December 2024.

| Table / CSV | Rows | Contents |
|---|---:|---|
| `customers` | 6,000 | Customer signup, country, channel, and company size |
| `plans` | 3 | Three plan names and monthly prices |
| `subscriptions` | 6,000 | Customer plan subscription, dates, status, cancellation reason |
| `payments` | 50,891 | Dated subscription payments and payment outcomes |
| `support_tickets` | 5,294 | Customer support requests, resolution time, satisfaction |

## How to run
1. Install Python 3 with `pandas` and `numpy` (`python -m pip install pandas numpy`).
2. From this folder run `python data/generate_data.py` to recreate the five CSVs using seed 42.
3. Create the database with SQLite: open `cloudnest.db` in DB Browser for SQLite, or run the provided `sql/schema.sql` and import each CSV into its matching table. Keep the CSV column order and names.
4. Execute each statement in `sql/queries.sql` in SQLite. The already generated database and result CSVs are included for review.

`scripts/build_project.py` rebuilds the database and exports the 28 result CSVs from the existing CSV data: `python scripts/build_project.py` (requires pandas and numpy). It also writes `scripts/verification.txt`.

## Note on month-0 retention
Month-0 retention counts cohort customers whose subscription is still active at the end of their signup month; a cancellation dated on or before that month-end does not count as retained. A database check found **146 subscriptions** ending in the same calendar month they started, matching the **146 customers** not retained at month 0 (5,854 of 6,000 retained, or 97.6% when weighted by customer count). The **97.9%** reported in the insights is the unweighted average of the 24 monthly cohort retention rates, so differing cohort sizes explain the difference.

## Folder structure
`data/` generator and input CSVs · `sql/` schema and 28 business questions · `results/` one CSV per query · `docs/` narrative and diagrams · `cloudnest.db` SQLite database.

## Skills demonstrated
SELECT and filtering, joins, aggregation, NULL handling, CTEs, subqueries, window functions (RANK, LAG, running totals, moving averages, percentiles), cohort retention, data quality review, and evidence-based recommendations.

## SQL dialect note
The queries use SQLite date functions (`strftime`, `date`, `julianday`) and `LIMIT`. For PostgreSQL, replace these with `DATE_TRUNC`, interval arithmetic, and `EXTRACT`; for MySQL use `DATE_FORMAT`, `DATE_ADD`, and `DATEDIFF`. SQLite's `PERCENT_RANK()` and window syntax are available in modern SQLite; check equivalents in older database versions.
