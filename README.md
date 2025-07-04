
# Gateway KPI Reporter 📊

This Python project automates the extraction of daily KPI metrics from a MySQL database and sends reports via email as CSV attachments. It separates metrics by **Organic** and **Bundle** users across four telecom gateways: `MTN-CMR`, `Orange-CMR`, `MTN-CIV`, and `Orange-CIV`.

## 📌 Features

- Connects to a MySQL database using credentials stored in environment variables
- Runs two queries daily:
  - **Organic KPIs**: non-bundled subscribers
  - **Bundle KPIs**: bundled subscribers
- Calculates:
  - Total revenue (converted to USD)
  - Billed users
  - ARPPU (Average Revenue Per Paying User)
- Outputs two CSV files (`organic_kpis_YYYY-MM-DD.csv`, `bundle_kpis_YYYY-MM-DD.csv`)
- Emails both CSVs using Gmail and Yagmail

## ⚙️ Technologies Used

- Python
- MySQL
- Pandas
- Yagmail
- Environment Variables for security
