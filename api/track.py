# /api/track.py
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import smtplib
from email.mime.text import MIMEText
import os

# Your legitimate domain(s)
AUTHORIZED_DOMAINS = ["amanueltravelagency.com"]

# Your email configuration for alerts
EMAIL_HOST = "smtp.gmail.com"  # Using Gmail's SMTP server
EMAIL_PORT = 587
EMAIL_USER = "yisakor17@gmail.com"  # Your Gmail address
EMAIL_PASSWORD = "bnwm odus mbzf zqrw" # You need to create an App Password for this
ALERT_RECIPIENT = "amanuelysakor@gmail.com"

# The path to your log file (it will be created in /tmp on Vercel)
LOG_FILE_PATH = "/tmp/access.log"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        
        host_url = query.get('url', [''])[0]
        user_agent = query.get('userAgent', [''])[0]
        referrer = query.get('referrer', [''])[0]
        
        is_unauthorized = not any(domain in host_url for domain in AUTHORIZED_DOMAINS)
        
        log_entry = f"Timestamp: {self.date_time_string()}, IP: {self.client_address[0]}, Host: {host_url}, User-Agent: {user_agent}\n"
        
        # Log all access to a file
        with open(LOG_FILE_PATH, "a") as log_file:
            log_file.write(log_entry)
        
        if is_unauthorized:
            print(f"UNAUTHORIZED ACCESS DETECTED: {host_url}") # Prints to Vercel logs
            self.send_alert(host_url, user_agent, referrer)
            
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Tracking signal received.")

    def send_alert(self, host, user_agent, referrer):
        try:
            msg = MIMEText(
                f"Unauthorized use detected!\n\nHost: {host}\nUser-Agent: {user_agent}\nReferrer: {referrer}"
            )
            msg['Subject'] = 'Unauthorized Website Use Alert'
            msg['From'] = EMAIL_USER
            msg['To'] = ALERT_RECIPIENT
            
            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USER, [ALERT_RECIPIENT], msg.as_string())
            print("Alert email sent successfully.")
        except Exception as e:
            print(f"Failed to send email alert: {e}")
