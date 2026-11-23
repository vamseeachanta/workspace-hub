#!/usr/bin/env python3

"""
Email Notification System for Baseline Testing
Supports SMTP, template-based emails, and comprehensive error handling
"""

import smtplib
import ssl
import os
import json
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Template
from datetime import datetime
from typing import List, Dict, Optional, Any
import argparse


class EmailNotifier:
    """Email notification system with SMTP support and template rendering"""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize email notifier with configuration"""
        self.config = config or {}
        self.setup_logging()

        # SMTP Configuration
        self.smtp_host = self.config.get('smtp_host', os.getenv('SMTP_HOST', 'localhost'))
        self.smtp_port = self.config.get('smtp_port', int(os.getenv('SMTP_PORT', '587')))
        self.smtp_user = self.config.get('smtp_user', os.getenv('SMTP_USER', ''))
        self.smtp_pass = self.config.get('smtp_pass', os.getenv('SMTP_PASS', ''))
        self.use_tls = self.config.get('use_tls', os.getenv('SMTP_TLS', 'true').lower() == 'true')

        # Email defaults
        self.from_email = self.config.get('from_email', os.getenv('FROM_EMAIL', 'baseline-tests@example.com'))
        self.from_name = self.config.get('from_name', 'Baseline Testing System')

        # Retry configuration
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 5)

    def setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config.get('log_level', 'INFO')
        log_file = self.config.get('log_file', '.baseline-cache/logs/email.log')

        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def send_email(self, to_emails: List[str], subject: str, content: str,
                   html_content: str = None, attachments: List[str] = None) -> Dict[str, Any]:
        """Send email with retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.info(f"Sending email attempt {attempt + 1}/{self.max_retries + 1}")
                result = self._send_email_attempt(to_emails, subject, content, html_content, attachments)
                self.logger.info("Email sent successfully")
                return {
                    'success': True,
                    'attempt': attempt + 1,
                    'result': result
                }
            except Exception as e:
                self.logger.warning(f"Email attempt {attempt + 1} failed: {str(e)}")

                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"Failed to send email after {self.max_retries + 1} attempts")
                    return {
                        'success': False,
                        'attempts': self.max_retries + 1,
                        'error': str(e)
                    }

    def _send_email_attempt(self, to_emails: List[str], subject: str, content: str,
                            html_content: str = None, attachments: List[str] = None) -> str:
        """Single email sending attempt"""
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{self.from_name} <{self.from_email}>"
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject

        # Add text content
        text_part = MIMEText(content, 'plain')
        msg.attach(text_part)

        # Add HTML content if provided
        if html_content:
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

        # Add attachments if provided
        if attachments:
            for attachment_path in attachments:
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())

                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)
                else:
                    self.logger.warning(f"Attachment not found: {attachment_path}")

        # Send email
        context = ssl.create_default_context()

        if self.smtp_port == 465:  # SSL
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context) as server:
                if self.smtp_user and self.smtp_pass:
                    server.login(self.smtp_user, self.smtp_pass)
                result = server.send_message(msg)
        else:  # STARTTLS or plain
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                if self.smtp_user and self.smtp_pass:
                    server.login(self.smtp_user, self.smtp_pass)
                result = server.send_message(msg)

        return f"Email sent to {len(to_emails)} recipients"

    def send_baseline_notification(self, payload: Dict[str, Any], recipients: List[str]) -> Dict[str, Any]:
        """Send baseline test notification email"""
        # Determine email type based on status
        status = payload.get('status', 'UNKNOWN')
        score = payload.get('score', 0)

        if status == 'FAIL' or score < 50:
            return self.send_failure_notification(payload, recipients)
        elif status == 'UNSTABLE' or score < 85:
            return self.send_warning_notification(payload, recipients)
        else:
            return self.send_success_notification(payload, recipients)

    def send_failure_notification(self, payload: Dict[str, Any], recipients: List[str]) -> Dict[str, Any]:
        """Send failure notification email"""
        subject = f"🚨 Baseline Tests FAILED - Score: {payload.get('score', 0)}%"

        text_content = self.render_text_template('failure', payload)
        html_content = self.render_html_template('failure', payload)

        return self.send_email(recipients, subject, text_content, html_content)

    def send_warning_notification(self, payload: Dict[str, Any], recipients: List[str]) -> Dict[str, Any]:
        """Send warning notification email"""
        subject = f"⚠️ Baseline Tests UNSTABLE - Score: {payload.get('score', 0)}%"

        text_content = self.render_text_template('warning', payload)
        html_content = self.render_html_template('warning', payload)

        return self.send_email(recipients, subject, text_content, html_content)

    def send_success_notification(self, payload: Dict[str, Any], recipients: List[str]) -> Dict[str, Any]:
        """Send success notification email"""
        subject = f"✅ Baseline Tests PASSED - Score: {payload.get('score', 0)}%"

        text_content = self.render_text_template('success', payload)
        html_content = self.render_html_template('success', payload)

        return self.send_email(recipients, subject, text_content, html_content)

    def render_text_template(self, template_type: str, payload: Dict[str, Any]) -> str:
        """Render text email template"""
        templates = {
            'failure': """
BASELINE TESTS FAILED

Status: {{ status }}
Score: {{ score }}%
Test Suite: {{ test_suite }}
Build: {{ build_number }}
Branch: {{ branch }}
Commit: {{ commit_hash }}

Failed Tests: {{ failed_tests }}

{% if issues %}
Critical Issues:
{% for issue in issues %}
- {{ issue }}
{% endfor %}
{% endif %}

{% if build_url %}
View Build: {{ build_url }}
{% endif %}

This is an automated message from the Baseline Testing System.
Timestamp: {{ timestamp }}
            """,
            'warning': """
BASELINE TESTS UNSTABLE

Status: {{ status }}
Score: {{ score }}%
Test Suite: {{ test_suite }}
Build: {{ build_number }}
Branch: {{ branch }}
Commit: {{ commit_hash }}

Some tests may have failed or performance degraded.

{% if build_url %}
View Build: {{ build_url }}
{% endif %}

This is an automated message from the Baseline Testing System.
Timestamp: {{ timestamp }}
            """,
            'success': """
BASELINE TESTS PASSED

Status: {{ status }}
Score: {{ score }}%
Test Suite: {{ test_suite }}
Build: {{ build_number }}
Branch: {{ branch }}
Commit: {{ commit_hash }}

All tests passed successfully!

{% if build_url %}
View Build: {{ build_url }}
{% endif %}

This is an automated message from the Baseline Testing System.
Timestamp: {{ timestamp }}
            """
        }

        template_str = templates.get(template_type, templates['failure'])
        template = Template(template_str)

        context = {
            'timestamp': datetime.now().isoformat(),
            'status': payload.get('status', 'UNKNOWN'),
            'score': payload.get('score', 0),
            'test_suite': payload.get('testSuite', 'all'),
            'build_number': payload.get('buildNumber', 'N/A'),
            'branch': payload.get('branch', 'unknown'),
            'commit_hash': payload.get('commitHash', 'N/A'),
            'failed_tests': payload.get('failedTests', 0),
            'issues': payload.get('issues', []),
            'build_url': payload.get('buildUrl', ''),
        }

        return template.render(**context).strip()

    def render_html_template(self, template_type: str, payload: Dict[str, Any]) -> str:
        """Render HTML email template"""
        color_map = {
            'failure': '#dc3545',
            'warning': '#ffc107',
            'success': '#28a745'
        }

        icon_map = {
            'failure': '🚨',
            'warning': '⚠️',
            'success': '✅'
        }

        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baseline Test Results</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: {{ color }};
            color: white;
            padding: 20px;
            border-radius: 5px 5px 0 0;
            text-align: center;
        }
        .content {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 0 0 5px 5px;
            border: 1px solid #ddd;
        }
        .metric {
            display: inline-block;
            margin: 10px;
            padding: 10px;
            background-color: white;
            border-radius: 5px;
            border: 1px solid #ddd;
            min-width: 120px;
            text-align: center;
        }
        .metric-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }
        .metric-value {
            font-size: 18px;
            font-weight: bold;
            color: {{ color }};
        }
        .issues {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
        }
        .footer {
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
        .button {
            display: inline-block;
            background-color: {{ color }};
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 0;
        }
        .button:hover {
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ icon }} Baseline Tests {{ status }}</h1>
    </div>

    <div class="content">
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Score</div>
                <div class="metric-value">{{ score }}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Test Suite</div>
                <div class="metric-value">{{ test_suite }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Build</div>
                <div class="metric-value">{{ build_number }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Branch</div>
                <div class="metric-value">{{ branch }}</div>
            </div>
        </div>

        {% if issues %}
        <div class="issues">
            <h3>Issues Detected:</h3>
            <ul>
            {% for issue in issues %}
                <li>{{ issue }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}

        {% if build_url %}
        <div style="text-align: center; margin: 20px 0;">
            <a href="{{ build_url }}" class="button">View Full Build Report</a>
        </div>
        {% endif %}

        <div style="margin-top: 20px;">
            <strong>Commit:</strong> {{ commit_hash }}<br>
            <strong>Timestamp:</strong> {{ timestamp }}
        </div>
    </div>

    <div class="footer">
        This is an automated message from the Baseline Testing System.<br>
        Generated at {{ timestamp }}
    </div>
</body>
</html>
        """

        template = Template(html_template)
        context = {
            'color': color_map.get(template_type, color_map['failure']),
            'icon': icon_map.get(template_type, icon_map['failure']),
            'timestamp': datetime.now().isoformat(),
            'status': payload.get('status', 'UNKNOWN'),
            'score': payload.get('score', 0),
            'test_suite': payload.get('testSuite', 'all'),
            'build_number': payload.get('buildNumber', 'N/A'),
            'branch': payload.get('branch', 'unknown'),
            'commit_hash': payload.get('commitHash', 'N/A'),
            'failed_tests': payload.get('failedTests', 0),
            'issues': payload.get('issues', []),
            'build_url': payload.get('buildUrl', ''),
        }

        return template.render(**context)

    def test_email_configuration(self) -> Dict[str, Any]:
        """Test email configuration by sending a test email"""
        test_payload = {
            'status': 'PASS',
            'score': 95,
            'testSuite': 'test',
            'buildNumber': 'TEST-001',
            'branch': 'main',
            'commitHash': 'abc123def456'
        }

        # Send to a test recipient (could be the from_email for testing)
        test_recipient = self.config.get('test_recipient', self.from_email)

        subject = "🧪 Baseline Testing Email Configuration Test"
        content = self.render_text_template('success', test_payload)
        html_content = self.render_html_template('success', test_payload)

        return self.send_email([test_recipient], subject, content, html_content)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Failed to load config: {e}")
    return {}


def main():
    """CLI interface for email notifier"""
    parser = argparse.ArgumentParser(description='Email notification system for baseline testing')
    parser.add_argument('command', choices=['send', 'test'], help='Command to execute')
    parser.add_argument('--payload', help='JSON payload file for notification')
    parser.add_argument('--recipients', nargs='+', help='Email recipients')
    parser.add_argument('--config', default='email-config.json', help='Configuration file')
    parser.add_argument('--log-level', default='INFO', help='Log level')

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    config['log_level'] = args.log_level

    notifier = EmailNotifier(config)

    if args.command == 'test':
        print("Testing email configuration...")
        result = notifier.test_email_configuration()
        print(f"Test result: {json.dumps(result, indent=2)}")

    elif args.command == 'send':
        if not args.payload or not os.path.exists(args.payload):
            print("Payload file required and must exist")
            return 1

        if not args.recipients:
            print("Recipients required")
            return 1

        # Load payload
        with open(args.payload, 'r') as f:
            payload = json.load(f)

        print(f"Sending notification to {len(args.recipients)} recipients...")
        result = notifier.send_baseline_notification(payload, args.recipients)
        print(f"Send result: {json.dumps(result, indent=2)}")

        return 0 if result.get('success', False) else 1

    return 0


if __name__ == '__main__':
    exit(main())