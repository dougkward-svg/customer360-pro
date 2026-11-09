# Customer360 Pro
A fictional Streamlit customer-management template with customer search, customer and order CRUD, issue tracking, health scoring, analytics, reports, CSV exports, persistence, and tests.

## Launch
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest
python -m streamlit run app.py
```

## GitHub from VS Code
Create an empty repository, then run:
```powershell
git init
git config user.name "YOUR-NAME"
git config user.email "YOUR-EMAIL"
git add .
git commit -m "Initial Customer360 Pro release"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/customer360-pro.git
git push -u origin main
```

All included records are fictional. See LICENSE.
