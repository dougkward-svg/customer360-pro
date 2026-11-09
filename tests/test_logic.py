import pandas as pd
from datetime import date
from logic import validate_customer, validate_order, health_score

def test_duplicate_customer_rejected(): assert "Customer ID already exists." in validate_customer("C1","Acme",["C1"])
def test_valid_customer(): assert validate_customer("C2","Acme",["C1"]) == []
def test_invalid_order_rules():
 e=validate_order("O1","C1",date(2026,2,1),date(2026,1,1),0,"Bad",[],["C1"])
 assert len(e)==3
def test_health_score_range():
 o=pd.DataFrame({'status':['Open','Complete']}); i=pd.DataFrame({'severity':['High']})
 assert health_score(o,i)==88
