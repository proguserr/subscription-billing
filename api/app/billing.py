from datetime import date, timedelta
PLAN_PRICES={'basic':9900,'pro':19900,'ent':49900}
def next_period(start:date): end=start+timedelta(days=30); return start,end
def price_for_plan(plan_code:str)->int: return PLAN_PRICES.get(plan_code,0)
def usage_charge(usage:int,tier:str='api_calls')->int:
  if usage<=100000: return 0
  over=usage-100000; blocks=(over+999)//1000; return blocks*20
