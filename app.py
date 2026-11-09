from pathlib import Path
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from logic import VALID_STATUSES, validate_customer, validate_order, health_score

BASE=Path(__file__).parent; DATA=BASE/'data'
st.set_page_config(page_title='Customer360 Pro',page_icon='📊',layout='wide')

def load(name, dates=()):
    df=pd.read_csv(DATA/name, dtype={'postal_code':str})
    for c in dates: df[c]=pd.to_datetime(df[c])
    return df

def save(df,name):
    out=df.copy()
    for c in ['date_acquired','last_activity','order_date','delivery_date','opened_date']:
        if c in out: out[c]=pd.to_datetime(out[c]).dt.strftime('%Y-%m-%d')
    out.to_csv(DATA/name,index=False)

customers=load('customers.csv',['date_acquired','last_activity']); orders=load('orders.csv',['order_date','delivery_date']); issues=load('issues.csv',['opened_date'])
st.session_state.setdefault('page','Dashboard'); st.session_state.setdefault('selected',customers.iloc[0].customer_id)

st.sidebar.title('📊 Customer360 Pro')
page=st.sidebar.radio('Navigation',['Dashboard','Customers','Orders','Issues','Reports'])
st.sidebar.caption('Fictional demo data only')

if page=='Dashboard':
 st.title('Customer Dashboard')
 names=dict(zip(customers.customer_name,customers.customer_id)); pre=list(names.values()).index(st.session_state.selected) if st.session_state.selected in names.values() else 0
 with st.form('search'):
  name=st.selectbox('Select customer',list(names),index=pre); go=st.form_submit_button('Search Customer',type='primary')
 if go: st.session_state.selected=names[name]
 cid=st.session_state.selected; c=customers[customers.customer_id==cid].iloc[0]; co=orders[orders.customer_id==cid].copy(); ci=issues[issues.customer_id==cid].copy(); co['sales']=co.quantity*co.unit_price
 score=health_score(co,ci); color='Green' if score>=80 else 'Amber' if score>=60 else 'Red'
 m1,m2,m3,m4=st.columns(4); m1.metric('Orders',len(co)); m2.metric('Sales',f"${co.sales.sum():,.0f}"); m3.metric('Open Issues',len(ci)); m4.metric('Health',f'{score} ({color})')
 left,right=st.columns([1,2],gap='large')
 with left:
  st.subheader(c.customer_name); st.write(f"**Industry:** {c.industry}"); st.write(f"**Tier:** {c.account_tier}"); st.write(f"**Acquired:** {c.date_acquired.date()}"); st.write(f"**Contact:** {c.contact_name}, {c.contact_role}"); st.write(c.contact_email); st.write(f"**Address:** {c.address}, {c.city}, {c.state} {c.postal_code}")
  st.subheader('Open Issues')
  if ci.empty: st.success('No open issues')
  else: st.dataframe(ci[['issue_id','title','severity','status']],hide_index=True,use_container_width=True)
 with right:
  monthly=co.assign(month=co.order_date.dt.to_period('M').astype(str)).groupby('month',as_index=False).sales.sum()
  st.plotly_chart(px.bar(monthly,x='month',y='sales',title='Sales per Month'),use_container_width=True)
  mix=co.groupby('product_family',as_index=False).sales.sum(); st.plotly_chart(px.pie(mix,names='product_family',values='sales',title='Sales Product Mix',hole=.35),use_container_width=True)
 st.subheader('Customer Orders'); st.dataframe(co[['order_id','order_date','delivery_date','product_family','quantity','unit_price','status','notes']],hide_index=True,use_container_width=True)

elif page=='Customers':
 st.title('Customer Management')
 tab1,tab2=st.tabs(['Add Customer','Edit Customer'])
 with tab1:
  with st.form('add_customer'):
   cid=st.text_input('Customer ID'); name=st.text_input('Company name'); industry=st.text_input('Industry'); acquired=st.date_input('Date acquired'); tier=st.selectbox('Tier',['Growth','Strategic','Enterprise']); value=st.number_input('Annual value',min_value=0.0); address=st.text_input('Address'); city=st.text_input('City'); state=st.text_input('State'); postal=st.text_input('Postal code'); contact=st.text_input('Primary contact'); role=st.text_input('Contact role'); email=st.text_input('Contact email'); submit=st.form_submit_button('Add Customer',type='primary')
  if submit:
   errs=validate_customer(cid,name,customers.customer_id.tolist())
   if errs:
    for e in errs: st.error(e)
   else:
    row={'customer_id':cid.upper().strip(),'customer_name':name.strip(),'industry':industry,'date_acquired':pd.Timestamp(acquired),'account_tier':tier,'annual_value':value,'address':address,'city':city,'state':state,'postal_code':postal,'contact_name':contact,'contact_role':role,'contact_email':email,'last_activity':pd.Timestamp(date.today())}; customers=pd.concat([customers,pd.DataFrame([row])],ignore_index=True); save(customers,'customers.csv'); st.success('Customer added.'); st.rerun()
 with tab2:
  cid=st.selectbox('Customer to edit',customers.customer_id,key='edit_customer'); idx=customers.index[customers.customer_id==cid][0]
  with st.form('edit_customer_form'):
   name=st.text_input('Company name',customers.loc[idx,'customer_name']); tier=st.selectbox('Tier',['Growth','Strategic','Enterprise'],index=['Growth','Strategic','Enterprise'].index(customers.loc[idx,'account_tier'])); value=st.number_input('Annual value',min_value=0.0,value=float(customers.loc[idx,'annual_value'])); contact=st.text_input('Primary contact',customers.loc[idx,'contact_name']); save_edit=st.form_submit_button('Save Changes')
  if save_edit:
   customers.loc[idx,['customer_name','account_tier','annual_value','contact_name']]=[name,tier,value,contact]; save(customers,'customers.csv'); st.success('Customer updated.'); st.rerun()

elif page=='Orders':
 st.title('Order Management')
 tab1,tab2=st.tabs(['Add Order','Edit Order'])
 with tab1:
  with st.form('add_order'):
   oid=st.text_input('Order ID'); cid=st.selectbox('Customer',customers.customer_id); od=st.date_input('Order date'); dd=st.date_input('Delivery date'); product=st.selectbox('Product family',['Controls','Assemblies','Services']); qty=st.number_input('Quantity',min_value=1,step=1); price=st.number_input('Unit price',min_value=0.0); status=st.selectbox('Status',VALID_STATUSES); notes=st.text_area('Notes'); submit=st.form_submit_button('Add Order',type='primary')
  if submit:
   errs=validate_order(oid,cid,od,dd,qty,status,orders.order_id.tolist(),customers.customer_id.tolist())
   if errs:
    for e in errs: st.error(e)
   else:
    row={'order_id':oid.upper().strip(),'customer_id':cid,'order_date':pd.Timestamp(od),'delivery_date':pd.Timestamp(dd),'product_family':product,'quantity':int(qty),'unit_price':price,'status':status,'notes':notes}; orders=pd.concat([orders,pd.DataFrame([row])],ignore_index=True); save(orders,'orders.csv'); st.success('Order added.'); st.rerun()
 with tab2:
  oid=st.selectbox('Order to edit',orders.order_id); idx=orders.index[orders.order_id==oid][0]
  with st.form('edit_order'):
   dd=st.date_input('Delivery date',orders.loc[idx,'delivery_date'].date()); qty=st.number_input('Quantity',min_value=1,step=1,value=int(orders.loc[idx,'quantity'])); status=st.selectbox('Status',VALID_STATUSES,index=VALID_STATUSES.index(orders.loc[idx,'status'])); notes=st.text_area('Notes',orders.loc[idx,'notes']); submit=st.form_submit_button('Save Order')
  if submit:
   if dd < orders.loc[idx,'order_date'].date(): st.error('Delivery date cannot be before order date.')
   else:
    orders.loc[idx,['delivery_date','quantity','status','notes']]=[pd.Timestamp(dd),int(qty),status,notes]; save(orders,'orders.csv'); st.success('Order updated.'); st.rerun()

elif page=='Issues':
 st.title('Issue Management')
 st.dataframe(issues,hide_index=True,use_container_width=True)
 with st.form('add_issue'):
  iid=st.text_input('Issue ID'); cid=st.selectbox('Customer',customers.customer_id); title=st.text_input('Title'); severity=st.selectbox('Severity',['Low','Medium','High','Critical']); status=st.selectbox('Status',['Open','In Progress','Waiting','Escalated']); submit=st.form_submit_button('Add Issue')
 if submit:
  if not iid or iid.upper() in issues.issue_id.str.upper().tolist() or not title: st.error('Provide a unique issue ID and title.')
  else:
   row={'issue_id':iid.upper(),'customer_id':cid,'title':title,'severity':severity,'status':status,'opened_date':pd.Timestamp(date.today())}; issues=pd.concat([issues,pd.DataFrame([row])],ignore_index=True); save(issues,'issues.csv'); st.success('Issue added.'); st.rerun()

else:
 st.title('Reports and Exports')
 merged=orders.merge(customers[['customer_id','customer_name']],on='customer_id'); merged['sales']=merged.quantity*merged.unit_price
 summary=merged.groupby('customer_name',as_index=False).agg(orders=('order_id','count'),sales=('sales','sum'))
 st.dataframe(summary,hide_index=True,use_container_width=True)
 st.download_button('Download customer summary',summary.to_csv(index=False).encode(),'customer_summary.csv','text/csv')
 st.download_button('Download all orders',merged.to_csv(index=False).encode(),'orders_export.csv','text/csv')
