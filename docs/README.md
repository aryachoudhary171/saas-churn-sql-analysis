# CloudNest SaaS Subscription Business Analysis (SQL)

## Project summary
An end-to-end, SQL-focused analysis of a fictional subscription software business. It explores signups, recurring revenue, churn, customer support, acquisition channels, cohorts, and practical decisions.

## Business problem
CloudNest needs to understand which customers and plans generate revenue, where cancellations and support friction appear, and how retention varies across signup cohorts and acquisition sources.

## Dataset
All data is synthetic and generated locally with a fixed random seed; there are no real customer records or third-party license restrictions. The observation window is January 2023 through December 2024.

The generator intentionally includes **63 missing satisfaction scores (1.19%)**, **21 duplicate-detail ticket rows**, and **1,284 failed payment rows**. Duplicate tickets have distinct primary keys so referential integrity stays intact; inspect the customer/date/category/details to identify them during data cleaning.

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

`build_project.py` is included to rebuild the database and export the 28 result CSVs with the bundled analysis workflow: `python build_project.py` (requires pandas and numpy).

## Folder structure
`data/` generator and input CSVs · `sql/` schema and 28 business questions · `results/` one CSV per query · `docs/` narrative and diagrams · `cloudnest.db` SQLite database.

## Skills demonstrated
SELECT and filtering, joins, aggregation, NULL handling, CTEs, subqueries, window functions (RANK, LAG, running totals, moving averages, percentiles), cohort retention, data quality review, and evidence-based recommendations.

## SQL dialect note
The queries use SQLite date functions (`strftime`, `date`, `julianday`) and `LIMIT`. For PostgreSQL, replace these with `DATE_TRUNC`, interval arithmetic, and `EXTRACT`; for MySQL use `DATE_FORMAT`, `DATE_ADD`, and `DATEDIFF`. SQLite's `PERCENT_RANK()` and window syntax are available in modern SQLite; check equivalents in older database versions.
