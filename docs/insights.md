# Query insights

All counts, rates, and revenue figures below are calculated from the synthetic data in `results/`. Revenue means successful paid payments unless the query says otherwise.

## Q01 — How Many Customers Are There In Each Country (Basic)

**Question:** Customers by country

**Finding:** US has the most customers (**2583** of 6,000, or 43.0%). The country counts show where the current customer base is concentrated.

**Business implication:** Use country counts to size regional onboarding and support coverage, then compare those counts with revenue and retention before prioritizing investment.

## Q02 — How Many Subscriptions Are Active Versus Cancelled (Basic)

**Question:** Active vs cancelled subscriptions

**Finding:** There are **3,564 active** and **2,436 cancelled** subscriptions; 40.6% of subscriptions are marked cancelled.

**Business implication:** Use the 40.6% cancelled share as a baseline; split it by tenure and cancellation reason to target retention work.

## Q03 — How Much Paid Revenue Did Each Plan Generate (Basic)

**Question:** Revenue by plan (paid payments)

**Finding:** Pro generated the most paid revenue (**$465,102**). Revenue is assigned to the plan price charged on each successful payment, so Basic-to-Pro upgrades are reflected.

**Business implication:** Use plan revenue alongside plan population and refund rate when evaluating packaging; revenue alone does not measure margin.

## Q04 — How Many Customers Signed Up Each Month (Basic)

**Question:** Monthly signups

**Finding:** Signups totaled **6,000** over 24 months. 2024-10 was the busiest month with **325** new customers; the monthly series is in `Q04_how_many_customers_signed_up_each_month.csv`.

**Business implication:** Compare signup peaks with campaign or product changes so capacity planning and growth experiments follow observed demand.

## Q05 — What Is The Average Number Of Support Tickets Per Customer (Basic)

**Question:** Average tickets per customer

**Finding:** The average is **0.882 tickets per customer** across 6,000 customers (including customers with no ticket).

**Business implication:** Use average ticket volume as a support workload baseline and pair it with resolution time and satisfaction completeness.

## Q06 — Which Five Countries Generated The Most Paid Revenue (Basic)

**Question:** Top 5 countries by paid revenue

**Finding:** US leads the five countries with **$468,544** in successful payment revenue.

**Business implication:** Compare country revenue with customer count to find markets with stronger revenue per customer before adding localized spend.

## Q07 — How Much Paid Revenue Came From Each Acquisition Channel (Joins)

**Question:** Paid revenue by acquisition channel

**Finding:** Organic generated the most paid revenue (**$298,953**). This is gross successful payment value, before acquisition costs.

**Business implication:** Compare each channel’s paid revenue with acquisition cost and retention before shifting budget.

## Q08 — What Is The Cancellation Rate For Each Acquisition Channel (Joins)

**Question:** Churn rate by channel (cancelled subscriptions / subscriptions)

**Finding:** Cancellation share ranges from **29.6%** for Referral to **56.0%** for Paid Search. Rates use cancelled subscriptions divided by all subscriptions for that channel.

**Business implication:** Compare channel quality with acquisition cost before shifting spend; the highest cancellation rate signals a retention concern.

## Q09 — What Is The Average Subscription Length By Plan (Joins)

**Question:** Average subscription length by plan (days)

**Finding:** Basic has the longest average observed subscription duration at **240.9 days**. Active subscriptions are measured through 2024-12-31, so their lengths are right-censored.

**Business implication:** Use plan duration together with price and cancellation reason to identify which plan needs a retention or packaging review.

## Q10 — Which Customers Had Failed Payments (Joins)

**Question:** Customers with failed payments

**Finding:** **1,109 customers** have at least one failed payment, accounting for **1,284 failed payment attempts**. The output lists each affected customer.

**Business implication:** Offer payment-retry guidance to affected accounts and monitor whether failed attempts later recover.

## Q11 — Which Customers Have Never Contacted Support (Joins)

**Question:** Customers with no support tickets

**Finding:** **2,645 customers (44.1%)** have no support ticket in the dataset. This does not imply dissatisfaction; it only records no ticket event.

**Business implication:** Treat no-ticket customers as an uncontacted group; test proactive onboarding rather than assuming they are satisfied.

## Q12 — What Is The Subscription Plan Mix In Each Country (Joins)

**Question:** Plan mix by country

**Finding:** The largest country-plan cell is **US / Basic** with **1,550 subscriptions**. Basic accounts for **3,696 of 6,000 subscriptions (61.6%)** overall.

**Business implication:** Use country-plan counts to check whether the current plan mix is consistent across regions before localizing offers.

## Q13 — What Is The Refund Rate For Each Plan (Joins)

**Question:** Refund rate by plan (refunds / all payment rows)

**Finding:** Business has the highest refund rate at **1.1%** (51 refunds among 4,703 payment rows).

**Business implication:** Review refund reasons and billing clarity for the plan with the highest refund rate.

## Q14 — What Was Month End Mrr In Each Month (CTE)

**Question:** MRR by month-end from active subscriptions and latest paid amount that month

**Finding:** Month-end MRR peaks at **$81,844 in 2024-11**. MRR sums the latest paid amount in that month for subscriptions active on the last day, falling back to the listed plan price if no payment was recorded that month.

**Business implication:** Use month-end MRR as a recurring-revenue baseline and explain peaks or dips with acquisition, upgrades, and cancellations.

## Q15 — Which Customers Have Paid Lifetime Revenue Above The Customer Average (CTE)

**Question:** Customers above average observed paid lifetime value

**Finding:** **1,655 customers** exceed the average observed paid lifetime value of **$180.02** per customer. The highest listed customer has $1,896 in paid value.

**Business implication:** Use above-average LTV customers to explore retention behaviors, while avoiding conclusions from paid value alone.

## Q16 — How Did Paid Recurring Revenue Change Month Over Month (CTE)

**Question:** Month-over-month MRR growth

**Finding:** Month-end MRR has its largest increase in **2023-02 (92.4%)** and its largest decline in **2024-12 (-4.1%)**. The comparison uses consecutive month-end MRR values.

**Business implication:** Investigate the months with the sharpest MRR changes against new signups, cancellations, and upgrades.

## Q17 — Which Customers Show Evidence Of Upgrading From Basic To Pro (CTE)

**Question:** Customers with Basic-to-Pro upgrade evidence

**Finding:** **254 customers** have a successful $29 payment on a Basic subscription, used here as evidence of a Basic-to-Pro upgrade. This is a proxy because the source schema stores the initial plan on the subscription.

**Business implication:** Validate the inferred upgrades with explicit plan-change event tracking before using upgrade rates as a KPI.

## Q18 — How Long Elapsed From First Paid Payment To Cancellation (CTE)

**Question:** Days from first paid payment to cancellation

**Finding:** For **2,418 cancelled subscriptions** with a paid payment, the median time from first paid payment to cancellation is **69 days** (mean 113.7).

**Business implication:** Use the first-payment-to-cancellation distribution to time retention outreach before typical cancellation points.

## Q19 — Which Customers Had At Least Three Tickets And Cancelled (CTE)

**Question:** High-ticket customers (3+) who churned

**Finding:** **174 customers** both cancelled and submitted at least three tickets. The highest ticket count among them is **8**.

**Business implication:** Review cancellation feedback from customers with repeated support contacts to identify preventable service issues.

## Q20 — How Do Acquisition Channels Rank By Average Paid Customer Ltv (Window)

**Question:** Rank acquisition channels by average paid LTV

**Finding:** Referral ranks first with **$203.44 average paid LTV per customer**. This is observed paid value and does not account for channel acquisition cost.

**Business implication:** Compare average LTV with acquisition cost and payback time; high LTV alone does not prove a channel is efficient.

## Q21 — What Was The Cumulative Paid Revenue By Month (Window)

**Question:** Running total of paid revenue by month

**Finding:** Paid revenue accumulates to **$1,080,113** by 2024-12. The largest single-month revenue value was $85,740.

**Business implication:** Use cumulative paid revenue to reconcile overall monetization and to communicate the scale of observed payments.

## Q22 — What Is The Three Month Moving Average Of Signups (Window)

**Question:** Three-month moving average of signups

**Finding:** The three-month moving average peaks at **311.00 signups per month** in 2024-10; the series covers all 24 months.

**Business implication:** Use the signup moving average to separate short-term noise from sustained changes in acquisition volume.

## Q23 — How Do Customers Rank By Paid Revenue Within Each Country (Window)

**Question:** Rank customers within country by paid revenue

**Finding:** The highest-revenue customer is **3321 in Canada**, with **$1,896** in successful payments (country rank 1).

**Business implication:** Study top customers within each country for plan and tenure patterns, then validate those patterns across larger samples.

## Q24 — How Did Paid Revenue Compare With The Previous Month (Window)

**Question:** Previous-month paid payment comparison

**Finding:** The largest month-over-month paid-revenue increase is **$4,179 in 2024-10**; the largest drop is **$1,638 in 2024-11**.

**Business implication:** Investigate large month-to-month payment changes before changing forecasts or channel budgets.

## Q25 — What Percentile Is Each Support Ticket Resolution Time (Window)

**Question:** Percentile rank of ticket resolution time

**Finding:** There are **5,294 support tickets**. Median resolution time is **9.5 hours** and the 90th-percentile value is **25.3 hours**.

**Business implication:** Use the upper resolution-time tail to set a support review target, and investigate ticket categories causing long waits.

## Q26 — How Does Monthly Signup Cohort Retention Change From Month 0 To Month 12 (Advanced)

**Question:** Signup cohort retention months 0 through 12 (active subs at month end)

**Finding:** Average retention is **97.9% at month 0** and **63.3% at month 12** across 12 fully observed cohorts. At month 12, the range is 55.3% (2023-10) to 72.8% (2023-01).

**Business implication:** Use cohort age-adjusted retention to identify onboarding changes that deserve a controlled follow-up.

**Note:** Month 0 counts customers active at signup-month end; 146 same-month cancellations account for all 146 customers not retained across the 24 cohorts. The reported 97.9% is the unweighted average of cohort rates (the customer-weighted rate is 97.6%).

## Q27 — How Can Customers Be Grouped Into Practical Churn Risk Segments (Advanced)

**Question:** Churn-risk segment using tenure, channel, and ticket volume

**Finding:** The largest segment is **Lower risk (3,245 customers)**. Segment rules distinguish recent cancellations, newer paid-search or high-ticket active customers, early-tenure watch customers, and the remaining lower-risk group.

**Business implication:** Use the high-risk segment as a test audience for proactive help, then measure outcomes against a comparison group.

## Q28 — Which Channel And Starting Plan Combination Has The Best Observed 12 Month Retention (Advanced)

**Question:** Best acquisition channel and starting plan for 12-month retention among observable cohorts

**Finding:** The top observed combination is **Referral / Pro** at **78.3% 12-month retention** (94 of 120 eligible customers). Only subscriptions old enough by 2024-12-31 are included.

**Business implication:** Treat combinations with small eligible cohorts cautiously and validate retention before changing channel or plan strategy.
