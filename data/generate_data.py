"""Generate the seeded, synthetic CloudNest SaaS dataset."""
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
SEED = 42
AS_OF = pd.Timestamp("2024-12-31")

def main():
    rng = np.random.default_rng(SEED)
    n = 6000
    days = pd.date_range("2023-01-01", AS_OF, freq="D")
    weights = np.linspace(.7, 1.3, len(days)); weights /= weights.sum()
    signup_dates = pd.to_datetime(rng.choice(days.to_numpy(), n, p=weights))
    customers = pd.DataFrame({
        "customer_id": np.arange(1,n+1), "signup_date": signup_dates.strftime("%Y-%m-%d"),
        "country": rng.choice(["US","UK","Canada","Australia","Germany"],n,p=[.43,.23,.14,.11,.09]),
        "acquisition_channel": rng.choice(["Organic","Paid Search","Social","Referral","Email"],n,p=[.27,.25,.18,.17,.13]),
        "company_size": rng.choice(["Solo","Small","Medium","Large"],n,p=[.30,.38,.23,.09])})
    plans = pd.DataFrame({"plan_id":[1,2,3],"plan_name":["Basic","Pro","Business"],"monthly_price":[9,29,79]})
    subscriptions=[]; payments=[]; tickets=[]
    for i,c in customers.iterrows():
        start=pd.Timestamp(c.signup_date); age=(AS_OF-start).days
        plan=int(rng.choice([1,2,3],p=[.61,.29,.10]))
        factor=1.55 if c.acquisition_channel=="Paid Search" else (.78 if c.acquisition_channel=="Referral" else 1.0)
        p_cancel=min(.78,.23*factor+(.16*factor if age>90 else 0))
        cancelled=rng.random()<p_cancel
        if cancelled:
            maxd=max(1,age)
            if maxd<20: tenure=maxd
            elif rng.random()<.62: tenure=int(rng.integers(20,min(90,maxd)+1))
            else: tenure=int(rng.integers(min(91,maxd),maxd+1))
            end=min(AS_OF,start+pd.Timedelta(days=tenure)); status="cancelled"
            reason=rng.choice(["Price","Missing features","No longer needed","Poor experience","Other"],p=[.28,.24,.20,.16,.12])
        else: end=None; status="active"; reason=None
        upgrade=None
        if plan==1 and (end is None or (end-start).days>=100) and rng.random()<.14:
            upper=max(61,min(180,age+1)); upgrade=start+pd.Timedelta(days=int(rng.integers(60,upper)))
        sid=i+1
        subscriptions.append([sid,i+1,plan,start.strftime("%Y-%m-%d"),end.strftime("%Y-%m-%d") if end is not None else None,status,reason])
        last=end if end is not None else AS_OF
        month=start.replace(day=1)
        while month<=last:
            pdte=max(start,month)+pd.Timedelta(days=int(rng.integers(0,5)))
            if pdte<=last:
                active_plan=2 if upgrade is not None and pdte>=upgrade else plan
                price={1:9,2:29,3:79}[active_plan]; x=rng.random()
                pstatus="failed" if x<.025 else ("refunded" if x<.035 else "paid")
                payments.append([len(payments)+1,sid,pdte.strftime("%Y-%m-%d"),price,pstatus])
            month+=pd.offsets.MonthBegin(1)
        nt=int(rng.choice([0,1,2,3,5,8],p=[.44,.34,.15,.05,.018,.002]))
        for _ in range(nt):
            td=start+pd.Timedelta(days=int(rng.integers(0,max(1,age+1))))
            cat=rng.choice(["Billing","Technical","How-to","Account","Feature request"],p=[.22,.30,.25,.13,.10])
            hours=round(float(np.clip(rng.lognormal(2.25,.75),.2,120)),1)
            score=int(np.clip(round(rng.normal(4.0-.25*(hours>24),.9)),1,5))
            if rng.random()<.01: score=None
            tickets.append([len(tickets)+1,i+1,td.strftime("%Y-%m-%d"),cat,hours,score])
    subs=pd.DataFrame(subscriptions,columns=["subscription_id","customer_id","plan_id","start_date","end_date","status","cancel_reason"])
    pays=pd.DataFrame(payments,columns=["payment_id","subscription_id","payment_date","amount","status"])
    support=pd.DataFrame(tickets,columns=["ticket_id","customer_id","created_date","category","resolution_hours","satisfaction_score"])
    if len(support):
        ids=rng.choice(support.index,size=max(1,round(len(support)*.004)),replace=False)
        dup=support.loc[ids].copy(); dup["ticket_id"]=np.arange(len(support)+1,len(support)+len(dup)+1)
        support=pd.concat([support,dup],ignore_index=True)
    for name,df in [("customers",customers),("plans",plans),("subscriptions",subs),("payments",pays),("support_tickets",support)]: df.to_csv(OUT/f"{name}.csv",index=False)
    print("Generated:", {p.name:sum(1 for _ in p.open(encoding="utf-8"))-1 for p in OUT.glob("*.csv")})

if __name__=="__main__": main()
