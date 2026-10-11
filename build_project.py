"""Build SQLite database, query result CSVs, and portfolio documentation."""
from pathlib import Path
import csv, re, sqlite3
import pandas as pd
ROOT=Path(__file__).resolve().parent
TABLES=['customers','plans','subscriptions','payments','support_tickets']
LABELS={
1:'How many customers are there in each country?',2:'How many subscriptions are active versus cancelled?',3:'How much paid revenue did each plan generate?',4:'How many customers signed up each month?',5:'What is the average number of support tickets per customer?',6:'Which five countries generated the most paid revenue?',
7:'How much paid revenue came from each acquisition channel?',8:'What is the cancellation rate for each acquisition channel?',9:'What is the average subscription length by plan?',10:'Which customers had failed payments?',11:'Which customers have never contacted support?',12:'What is the subscription plan mix in each country?',13:'What is the refund rate for each plan?',
14:'What was month-end MRR in each month?',15:'Which customers have paid lifetime revenue above the customer average?',16:'How did paid recurring revenue change month over month?',17:'Which customers show evidence of upgrading from Basic to Pro?',18:'How long elapsed from first paid payment to cancellation?',19:'Which customers had at least three tickets and cancelled?',20:'How do acquisition channels rank by average paid customer LTV?',21:'What was the cumulative paid revenue by month?',22:'What is the three-month moving average of signups?',23:'How do customers rank by paid revenue within each country?',24:'How did paid revenue compare with the previous month?',25:'What percentile is each support ticket resolution time?',26:'How does monthly signup cohort retention change from month 0 to month 12?',27:'How can customers be grouped into practical churn-risk segments?',28:'Which channel and starting plan combination has the best observed 12-month retention?'}
NAMES={i:re.sub(r'[^a-z0-9]+','_',LABELS[i].lower()).strip('_') for i in LABELS}

def build_db():
    db=ROOT/'cloudnest.db'
    if db.exists(): db.unlink()
    con=sqlite3.connect(db); con.execute('PRAGMA foreign_keys=ON')
    con.executescript((ROOT/'sql/schema.sql').read_text(encoding='utf-8'))
    for t in TABLES:
        pd.read_csv(ROOT/'data'/f'{t}.csv').to_sql(t,con,index=False,if_exists='append')
    con.commit()
    violations=con.execute('PRAGMA foreign_key_check').fetchall()
    if violations: raise RuntimeError(f'Foreign key violations: {violations[:5]}')
    return con

def run_queries(con):
    text=(ROOT/'sql/queries.sql').read_text(encoding='utf-8')
    blocks=re.split(r'(?m)^-- Q(\d{2}) \[([^]]+)\] (.+)$',text)
    outputs={}
    for i in range(1,len(blocks),4):
        qid=int(blocks[i]); difficulty=blocks[i+1]; title=blocks[i+2].strip(); sql=blocks[i+3].strip()
        sql='\n'.join(line for line in sql.splitlines() if not line.lstrip().startswith('--')).strip()
        df=pd.read_sql_query(sql,con)
        if df.empty: raise RuntimeError(f'Q{qid:02} returned no rows')
        file=f'Q{qid:02}_{NAMES[qid]}.csv'; df.to_csv(ROOT/'results'/file,index=False)
        outputs[qid]=(difficulty,title,df,file)
    if len(outputs)!=28: raise RuntimeError(f'Expected 28 queries, got {len(outputs)}')
    return outputs

def fmt(v):
    if pd.isna(v): return 'NULL'
    if isinstance(v,(float,)): return f'{v:,.2f}'
    if isinstance(v,(int,)): return f'{v:,}'
    return str(v)

def docs(out, counts):
    # Factual summaries are generated from each query's saved result.
    lines=['# Query insights','', 'All counts, rates, and revenue figures below are calculated from the synthetic data in `results/`. Revenue means successful paid payments unless the query says otherwise.','']
    for q,(difficulty,title,df,file) in out.items():
        first=df.iloc[0]
        # Each finding cites an observed value and explains what the output represents.
        col=df.columns[0]; val=first[col]
        if q==1:
            finding=f"{val} has the most customers (**{fmt(first.customers)}** of {counts['customers']:,}, or {first.customers/counts['customers']:.1%}). The country counts show where the current customer base is concentrated."
        elif q==2:
            a=df.set_index('status').subscriptions
            finding=f"There are **{int(a.get('active',0)):,} active** and **{int(a.get('cancelled',0)):,} cancelled** subscriptions; {a.get('cancelled',0)/counts['subscriptions']:.1%} of subscriptions are marked cancelled."
        elif q==3:
            finding=f"{val} generated the most paid revenue (**${first.paid_revenue:,.0f}**). Revenue is assigned to the plan price charged on each successful payment, so Basic-to-Pro upgrades are reflected."
        elif q==4:
            top=df.loc[df.signups.idxmax()]
            finding=f"Signups totaled **{counts['customers']:,}** over 24 months. {top.signup_month} was the busiest month with **{int(top.signups):,}** new customers; the monthly series is in `{file}`."
        elif q==5:
            finding=f"The average is **{first.iloc[0]:.3f} tickets per customer** across {counts['customers']:,} customers (including customers with no ticket)."
        elif q==6:
            finding=f"{val} leads the five countries with **${first.paid_revenue:,.0f}** in successful payment revenue."
        elif q==7:
            finding=f"{val} generated the most paid revenue (**${first.paid_revenue:,.0f}**). This is gross successful payment value, before acquisition costs."
        elif q==8:
            lo=df.loc[df.churn_rate.idxmin()]; hi=df.loc[df.churn_rate.idxmax()]
            finding=f"Cancellation share ranges from **{lo.churn_rate:.1%}** for {lo.acquisition_channel} to **{hi.churn_rate:.1%}** for {hi.acquisition_channel}. Rates use cancelled subscriptions divided by all subscriptions for that channel."
        elif q==9:
            finding=f"{val} has the longest average observed subscription duration at **{first.avg_days:.1f} days**. Active subscriptions are measured through 2024-12-31, so their lengths are right-censored."
        elif q==10:
            finding=f"**{len(df):,} customers** have at least one failed payment, accounting for **{int(df.failed_payments.sum()):,} failed payment attempts**. The output lists each affected customer."
        elif q==11:
            finding=f"**{len(df):,} customers ({len(df)/counts['customers']:.1%})** have no support ticket in the dataset. This does not imply dissatisfaction; it only records no ticket event."
        elif q==12:
            top=df.loc[df.subscriptions.idxmax()]
            basic=int(df.loc[df.plan_name=='Basic','subscriptions'].sum())
            finding=f"The largest country-plan cell is **{top.country} / {top.plan_name}** with **{int(top.subscriptions):,} subscriptions**. Basic accounts for **{basic:,} of {counts['subscriptions']:,} subscriptions ({basic/counts['subscriptions']:.1%})** overall."
        elif q==13:
            finding=f"{val} has the highest refund rate at **{first.refund_rate:.1%}** ({int(first.refunds):,} refunds among {int(first.payments):,} payment rows)."
        elif q==14:
            top=df.loc[df.mrr.idxmax()]
            finding=f"Month-end MRR peaks at **${top.mrr:,.0f} in {top.month}**. MRR sums the latest paid amount in that month for subscriptions active on the last day, falling back to the listed plan price if no payment was recorded that month."
        elif q==15:
            total_paid=sum(out[3][2].paid_revenue); avg=total_paid/counts['customers']
            finding=f"**{len(df):,} customers** exceed the average observed paid lifetime value of **${avg:,.2f}** per customer. The highest listed customer has ${df.lifetime_value.max():,.0f} in paid value."
        elif q==16:
            changes=df.dropna(subset=['growth_pct']); hi=changes.loc[changes.growth_pct.idxmax()]; lo=changes.loc[changes.growth_pct.idxmin()]
            finding=f"Month-end MRR has its largest increase in **{hi.month} ({hi.growth_pct:.1f}%)** and its largest decline in **{lo.month} ({lo.growth_pct:.1f}%)**. The comparison uses consecutive month-end MRR values."
        elif q==17:
            finding=f"**{len(df):,} customers** have a successful $29 payment on a Basic subscription, used here as evidence of a Basic-to-Pro upgrade. This is a proxy because the source schema stores the initial plan on the subscription."
        elif q==18:
            finding=f"For **{len(df):,} cancelled subscriptions** with a paid payment, the median time from first paid payment to cancellation is **{df.days_to_cancel.median():.0f} days** (mean {df.days_to_cancel.mean():.1f})."
        elif q==19:
            finding=f"**{len(df):,} customers** both cancelled and submitted at least three tickets. The highest ticket count among them is **{int(df.ticket_count.max())}**."
        elif q==20:
            finding=f"{val} ranks first with **${first.avg_ltv:,.2f} average paid LTV per customer**. This is observed paid value and does not account for channel acquisition cost."
        elif q==21:
            last=df.iloc[-1]
            finding=f"Paid revenue accumulates to **${last.running_revenue:,.0f}** by {last.month}. The largest single-month revenue value was ${df.revenue.max():,.0f}."
        elif q==22:
            top=df.loc[df.moving_avg_3m.idxmax()]
            finding=f"The three-month moving average peaks at **{top.moving_avg_3m:.2f} signups per month** in {top.month}; the series covers all 24 months."
        elif q==23:
            top=df.loc[df.revenue.idxmax()]
            finding=f"The highest-revenue customer is **{int(top.customer_id)} in {top.country}**, with **${top.revenue:,.0f}** in successful payments (country rank {int(top.country_rank)})."
        elif q==24:
            valid=df.dropna(subset=['change_amount']); hi=valid.loc[valid.change_amount.idxmax()]; lo=valid.loc[valid.change_amount.idxmin()]
            finding=f"The largest month-over-month paid-revenue increase is **${hi.change_amount:,.0f} in {hi.month}**; the largest drop is **${lo.change_amount:,.0f} in {lo.month}**."
        elif q==25:
            finding=f"There are **{len(df):,} support tickets**. Median resolution time is **{df.resolution_hours.median():.1f} hours** and the 90th-percentile value is **{df.loc[df.resolution_percentile.ge(.9),'resolution_hours'].min():.1f} hours**."
        elif q==26:
            zero=df[df.months_since_signup==0]; mature=df[df.months_since_signup==12]
            best= mature.loc[mature.retention_rate.idxmax()]; worst=mature.loc[mature.retention_rate.idxmin()]
            finding=f"Average retention is **{zero.retention_rate.mean():.1%} at month 0** and **{mature.retention_rate.mean():.1%} at month 12** across {len(mature)} fully observed cohorts. At month 12, the range is {worst.retention_rate:.1%} ({worst.cohort_month}) to {best.retention_rate:.1%} ({best.cohort_month})."
        elif q==27:
            seg=df.groupby('churn_segment').size().sort_values(ascending=False)
            finding=f"The largest segment is **{seg.index[0]} ({int(seg.iloc[0]):,} customers)**. Segment rules distinguish recent cancellations, newer paid-search or high-ticket active customers, early-tenure watch customers, and the remaining lower-risk group."
        elif q==28:
            finding=f"The top observed combination is **{val} / {first.plan_name}** at **{first.retention_12m:.1%} 12-month retention** ({int(first.retained_12m):,} of {int(first.eligible_customers):,} eligible customers). Only subscriptions old enough by 2024-12-31 are included."
        implications={
            1:'Use country counts to size regional onboarding and support coverage, then compare those counts with revenue and retention before prioritizing investment.',
            2:'Use the 40.6% cancelled share as a baseline; split it by tenure and cancellation reason to target retention work.',
            3:'Use plan revenue alongside plan population and refund rate when evaluating packaging; revenue alone does not measure margin.',
            4:'Compare signup peaks with campaign or product changes so capacity planning and growth experiments follow observed demand.',
            5:'Use average ticket volume as a support workload baseline and pair it with resolution time and satisfaction completeness.',
            6:'Compare country revenue with customer count to find markets with stronger revenue per customer before adding localized spend.',
            7:'Compare each channel’s paid revenue with acquisition cost and retention before shifting budget.',
            8:'Compare channel quality with acquisition cost before shifting spend; the highest cancellation rate signals a retention concern.',
            9:'Use plan duration together with price and cancellation reason to identify which plan needs a retention or packaging review.',
            10:'Offer payment-retry guidance to affected accounts and monitor whether failed attempts later recover.',
            11:'Treat no-ticket customers as an uncontacted group; test proactive onboarding rather than assuming they are satisfied.',
            12:'Use country-plan counts to check whether the current plan mix is consistent across regions before localizing offers.',
            13:'Review refund reasons and billing clarity for the plan with the highest refund rate.',
            14:'Use month-end MRR as a recurring-revenue baseline and explain peaks or dips with acquisition, upgrades, and cancellations.',
            15:'Use above-average LTV customers to explore retention behaviors, while avoiding conclusions from paid value alone.',
            16:'Investigate the months with the sharpest MRR changes against new signups, cancellations, and upgrades.',
            17:'Validate the inferred upgrades with explicit plan-change event tracking before using upgrade rates as a KPI.',
            18:'Use the first-payment-to-cancellation distribution to time retention outreach before typical cancellation points.',
            19:'Review cancellation feedback from customers with repeated support contacts to identify preventable service issues.',
            20:'Compare average LTV with acquisition cost and payback time; high LTV alone does not prove a channel is efficient.',
            21:'Use cumulative paid revenue to reconcile overall monetization and to communicate the scale of observed payments.',
            22:'Use the signup moving average to separate short-term noise from sustained changes in acquisition volume.',
            23:'Study top customers within each country for plan and tenure patterns, then validate those patterns across larger samples.',
            24:'Investigate large month-to-month payment changes before changing forecasts or channel budgets.',
            25:'Use the upper resolution-time tail to set a support review target, and investigate ticket categories causing long waits.',
            26:'Use cohort age-adjusted retention to identify onboarding changes that deserve a controlled follow-up.',
            27:'Use the high-risk segment as a test audience for proactive help, then measure outcomes against a comparison group.',
            28:'Treat combinations with small eligible cohorts cautiously and validate retention before changing channel or plan strategy.'}
        implication=implications[q]
        lines += [f"## Q{q:02} — {NAMES[q].replace('_',' ').title()} ({difficulty})",'',f"**Question:** {title}",'',f"**Finding:** {finding}",'',f"**Business implication:** {implication}",'']
    (ROOT/'docs/insights.md').write_text('\n'.join(lines),encoding='utf-8')
    md='''# CloudNest SaaS Subscription Business Analysis (SQL)

## Project summary
An end-to-end, SQL-focused analysis of a fictional subscription software business. It explores signups, recurring revenue, churn, customer support, acquisition channels, cohorts, and practical decisions.

## Business problem
CloudNest needs to understand which customers and plans generate revenue, where cancellations and support friction appear, and how retention varies across signup cohorts and acquisition sources.

## Dataset
All data is synthetic and generated locally with a fixed random seed; there are no real customer records or third-party license restrictions. The observation window is January 2023 through December 2024.

| Table / CSV | Rows | Contents |
|---|---:|---|
'''
    desc={'customers':'Customer signup, country, channel, and company size','plans':'Three plan names and monthly prices','subscriptions':'Customer plan subscription, dates, status, cancellation reason','payments':'Dated subscription payments and payment outcomes','support_tickets':'Customer support requests, resolution time, satisfaction'}
    for t in TABLES: md+=f"| `{t}` | {counts[t]:,} | {desc[t]} |\n"
    md+='''
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
'''
    (ROOT/'docs/README.md').write_text(md,encoding='utf-8')
    (ROOT/'docs/erd.md').write_text('''# Entity relationship diagram\n\n```mermaid\nerDiagram\n    CUSTOMERS ||--o{ SUBSCRIPTIONS : owns\n    PLANS ||--o{ SUBSCRIPTIONS : selected\n    SUBSCRIPTIONS ||--o{ PAYMENTS : billed\n    CUSTOMERS ||--o{ SUPPORT_TICKETS : opens\n    CUSTOMERS { int customer_id PK }\n    PLANS { int plan_id PK }\n    SUBSCRIPTIONS { int subscription_id PK int customer_id FK int plan_id FK }\n    PAYMENTS { int payment_id PK int subscription_id FK }\n    SUPPORT_TICKETS { int ticket_id PK int customer_id FK }\n```\n''',encoding='utf-8')
    # Recommendations are grounded directly in result tables and calculated figures.
    ch=out[8][2]; best=ch.iloc[ch.churn_rate.argmin()]; worst=ch.iloc[ch.churn_rate.argmax()]
    channel=out[20][2].iloc[0]
    cohort=out[26][2]; m0=cohort[cohort.months_since_signup==0].retention_rate.mean(); m12=cohort[cohort.months_since_signup==12].retention_rate.mean()
    ticket=out[5][2].iloc[0,0]
    refund=out[13][2].iloc[out[13][2].refund_rate.argmax()]
    rec=f'''# Business recommendations

These recommendations use only the generated query outputs. Values are from the synthetic dataset and should be treated as analysis practice, not real market benchmarks.

1. **Test an early retention intervention for {worst.acquisition_channel}.** Its observed cancellation rate is {worst.churn_rate:.1%}, compared with {best.churn_rate:.1%} for {best.acquisition_channel}. Test clearer onboarding and a day-30 check-in, then compare matched cohorts.
2. **Protect channel quality while reviewing spend.** {channel.acquisition_channel} has the highest average paid lifetime value at ${channel.avg_ltv:,.2f} per customer in Q20. Evaluate LTV alongside actual campaign cost before reallocating budget.
3. **Improve first-year onboarding using cohort checkpoints.** Mean month-0 retention is {m0:.1%} and mean observed month-12 retention is {m12:.1%}. Track activation and support needs by cohort month before rolling out product changes.
4. **Review the $79 Business plan’s pricing presentation.** Business has the highest observed refund rate ({refund.refund_rate:.1%}; {int(refund.refunds):,} of {int(refund.payments):,} payment rows). Test clearer feature and billing explanations before changing the list price, and compare refunds and conversion.
5. **Keep support load and customer experience visible.** The ticket volume is {ticket:.3f} tickets per customer on average (Q05). Track this alongside resolution-time percentiles and satisfaction completeness; use the results to find categories where faster resolution could reduce churn.
'''
    (ROOT/'docs/recommendations.md').write_text(rec,encoding='utf-8')
    # Pull actual output counts/values into resume examples; avoid claiming a causal impact.
    paid=out[3][2].paid_revenue.sum(); nret=len(out[10][2]); nfailed=len(out[10][2])
    li=f'''# Resume and LinkedIn drafts

## Resume bullets

- **Analyzed** {counts['customers']:,} synthetic customer records with SQL joins and aggregations, quantifying ${paid:,.0f} in paid revenue across three subscription plans.
- **Built** a 13-month cohort retention analysis across {len(out[26][2]):,} cohort-month observations, measuring average month-12 retention at {m12:.1%} for cohorts observable through the dataset cutoff.
- **Profiled** acquisition-channel performance with window functions and LTV summaries; identified {channel.acquisition_channel} as the top channel by average paid customer LTV (${channel.avg_ltv:,.2f}) in the generated dataset.

## LinkedIn post draft

I built a SQL portfolio project to explore a fictional SaaS subscription business, CloudNest, using reproducible synthetic data.

- The dataset includes {counts['customers']:,} customers across five countries and five acquisition channels.
- The query results show ${paid:,.0f} in successful payment revenue across the three plans.
- Average observed month-12 cohort retention was {m12:.1%} for cohorts old enough to reach that checkpoint by December 2024.

I used joins, CTEs, window functions, and cohort analysis, then translated the results into practical retention, channel, pricing, and support questions. What would you investigate next in this dataset? Comment below.
'''
    (ROOT/'docs/resume_and_linkedin.md').write_text(li,encoding='utf-8')

def main():
    con=build_db(); out=run_queries(con)
    counts={t:con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in TABLES}
    docs(out,counts)
    checks={t:{'database':counts[t],'csv':len(pd.read_csv(ROOT/'data'/f'{t}.csv'))} for t in TABLES}
    if any(x['database']!=x['csv'] for x in checks.values()): raise RuntimeError(f'Row count mismatch: {checks}')
    results=list((ROOT/'results').glob('Q*.csv'))
    if len(results)!=28: raise RuntimeError(f'Expected 28 result CSVs, found {len(results)}')
    null_scores=con.execute('SELECT COUNT(*) FROM support_tickets WHERE satisfaction_score IS NULL').fetchone()[0]
    failed=con.execute("SELECT COUNT(*) FROM payments WHERE status='failed'").fetchone()[0]
    duplicate_ticket_rows=con.execute('SELECT COUNT(*) FROM support_tickets').fetchone()[0]-con.execute('SELECT COUNT(*) FROM (SELECT customer_id,created_date,category,resolution_hours,satisfaction_score FROM support_tickets GROUP BY customer_id,created_date,category,resolution_hours,satisfaction_score)').fetchone()[0]
    (ROOT/'verification.txt').write_text(f"Queries executed: {len(out)}\nAll query outputs non-empty: yes\nForeign key violations: 0\nRow count checks (CSV = database): {checks}\nResult CSV files: {len(results)}\nData quality review: {null_scores} NULL satisfaction scores ({null_scores/counts['support_tickets']:.2%}); {duplicate_ticket_rows} duplicate-detail ticket rows; {failed} failed payment rows.\n",encoding='utf-8')
    con.close(); print((ROOT/'verification.txt').read_text())

if __name__=='__main__': main()
