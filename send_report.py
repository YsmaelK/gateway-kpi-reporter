import pandas as pd
import mysql.connector
import yagmail
from datetime import datetime, timedelta

# ---------- CONFIGURATION ----------

# MySQL database connection
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': 'mxls'
}

# Email config
sender_email = os.getenv('SENDER_EMAIL')
receiver_email = os.getenv('RECEIVER_EMAIL')
email_password = os.getenv('EMAIL_PASSWORD')
subject = 'Daily Gateway KPI Reports (Organic + Bundle)'

# Output filenames
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
today = datetime.now().strftime('%Y-%m-%d')
organic_filename = f'organic_kpis_{yesterday}.csv'
bundle_filename = f'bundle_kpis_{yesterday}.csv'

# ---------- QUERIES ----------

organic_query = f"""
SELECT 
    gc.title AS gateway,
    ROUND(SUM(bem.currency_amount) * 0.00165, 2) AS revenue_usd,
    COUNT(DISTINCT bem.msisdn) AS billed_users,
    ROUND(SUM(bem.currency_amount) * 0.00165 / COUNT(DISTINCT bem.msisdn), 2) AS arppu_usd
FROM mxls.billing_exchange_messages bem
JOIN channelconnections cc 
    ON bem.channel_Id = cc.channels_Id 
    AND bem.gateway_connection_id = cc.gatewayconnections_id
JOIN gatewayconnections gc 
    ON bem.gateway_connection_id = gc.id
WHERE DATE(bem.created) = '{yesterday}'
  AND gc.title IN ('MTN-CMR-Fr', 'OrangeDigiPay-CMR-Fr', 'MTN-CIV-Fr', 'OrangeDigiPay-CIV-Fr')
  AND (cc.bundledChannel = 0 OR cc.bundledChannel IS NULL)
  AND bem.currency_amount > 0
GROUP BY gc.title
ORDER BY FIELD(gc.title, 'MTN-CMR-Fr', 'OrangeDigiPay-CMR-Fr', 'MTN-CIV-Fr', 'OrangeDigiPay-CIV-Fr');
"""

bundle_query = f"""
SELECT 
    gc.title AS gateway,
    ROUND(SUM(bem.currency_amount) * 0.00165, 2) AS revenue_usd,
    COUNT(DISTINCT bem.msisdn) AS billed_users,
    ROUND(SUM(bem.currency_amount) * 0.00165 / COUNT(DISTINCT bem.msisdn), 2) AS arppu_usd
FROM mxls.billing_exchange_messages bem
JOIN channelconnections cc 
    ON bem.channel_Id = cc.channels_Id 
    AND bem.gateway_connection_id = cc.gatewayconnections_id
JOIN gatewayconnections gc 
    ON bem.gateway_connection_id = gc.id
WHERE DATE(bem.created) = '{yesterday}'
  AND gc.title IN ('MTN-CMR-Fr', 'OrangeDigiPay-CMR-Fr', 'MTN-CIV-Fr', 'OrangeDigiPay-CIV-Fr')
  AND cc.bundledChannel = 1
  AND bem.currency_amount > 0
GROUP BY gc.title
ORDER BY FIELD(gc.title, 'MTN-CMR-Fr', 'OrangeDigiPay-CMR-Fr', 'MTN-CIV-Fr', 'OrangeDigiPay-CIV-Fr');
"""

# ---------- RUN QUERIES AND SAVE TO CSV ----------

try:
    conn = mysql.connector.connect(**db_config)
    
    # Organic
    df_organic = pd.read_sql(organic_query, conn)
    df_organic.to_csv(organic_filename, index=False)
    print(f"✅ Organic CSV saved: {organic_filename}")

    # Bundle
    df_bundle = pd.read_sql(bundle_query, conn)
    df_bundle.to_csv(bundle_filename, index=False)
    print(f"✅ Bundle CSV saved: {bundle_filename}")

except Exception as e:
    print("❌ Error fetching data:", e)
finally:
    if conn.is_connected():
        conn.close()

# ---------- SEND EMAIL ----------

try:
    yag = yagmail.SMTP(sender_email, email_password)
    yag.send(
        to=receiver_email,
        subject=subject,
        contents=f"""Hello,

Attached are the Organic and Bundle KPI reports for {yesterday}.

Best regards,
Ysmael""",
        attachments=[organic_filename, bundle_filename]
    )
    print("📧 Email sent successfully!")
except Exception as e:
    print("❌ Error sending email:", e)
