from datetime import date
VALID_STATUSES = ["Open", "In Production", "On Hold", "Shipped", "Complete"]

def validate_customer(customer_id, name, existing_ids):
    errors=[]
    if not customer_id.strip(): errors.append("Customer ID is required.")
    if not name.strip(): errors.append("Company name is required.")
    if customer_id.strip().upper() in {x.upper() for x in existing_ids}: errors.append("Customer ID already exists.")
    return errors

def validate_order(order_id, customer_id, order_date, delivery_date, quantity, status, existing_order_ids, valid_customer_ids):
    errors=[]
    if not order_id.strip(): errors.append("Order ID is required.")
    if order_id.strip().upper() in {x.upper() for x in existing_order_ids}: errors.append("Order ID already exists.")
    if customer_id not in valid_customer_ids: errors.append("Customer does not exist.")
    if int(quantity) <= 0: errors.append("Quantity must be a positive whole number.")
    if delivery_date < order_date: errors.append("Delivery date cannot be before order date.")
    if status not in VALID_STATUSES: errors.append("Invalid order status.")
    return errors

def health_score(customer_orders, customer_issues):
    score=100
    open_orders=customer_orders[~customer_orders["status"].isin(["Complete","Shipped"])]
    score -= min(len(open_orders)*2,20)
    severity_penalty={"Low":2,"Medium":5,"High":10,"Critical":20}
    score -= sum(severity_penalty.get(x,0) for x in customer_issues["severity"].tolist())
    return max(0,min(100,int(score)))
