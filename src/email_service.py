"""
Real email service implementation with SMTP integration
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """Production-ready email service with SMTP integration"""
    
    def __init__(self, config_file: str = "config/email_config.json"):
        self.config = self._load_email_config(config_file)
        self.smtp_server = self.config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = self.config.get('smtp_port', 587)
        self.username = self.config.get('username')
        self.password = self.config.get('password')
        self.from_email = self.config.get('from_email')
        self.from_name = self.config.get('from_name', 'Personalized Roadmap System')
        
    def _load_email_config(self, config_file: str) -> Dict[str, Any]:
        """Load email configuration from file or environment variables"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load email config file: {e}")
        
        # Fallback to environment variables
        return {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'from_email': os.getenv('FROM_EMAIL', 'noreply@roadmap-system.com'),
            'from_name': os.getenv('FROM_NAME', 'Personalized Roadmap System')
        }
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   html_body: Optional[str] = None, attachments: Optional[List[str]] = None) -> bool:
        """Send email with optional HTML content and attachments"""
        try:
            if not self.username or not self.password:
                logger.error("Email credentials not configured")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text body
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_notification_email(self, to_email: str, notification_type: str, 
                              title: str, message: str, priority: str = "medium") -> bool:
        """Send formatted notification email"""
        
        # Create HTML email template
        html_body = self._create_notification_template(
            title, message, notification_type, priority
        )
        
        # Create plain text version
        text_body = f"""
{title}

{message}

Notification Type: {notification_type}
Priority: {priority.title()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
Personalized Roadmap Generation System
        """.strip()
        
        return self.send_email(to_email, title, text_body, html_body)
    
    def send_roadmap_notification(self, to_email: str, student_name: str, 
                                 roadmap_id: str, action: str) -> bool:
        """Send roadmap-related notification"""
        subject = f"Roadmap Update - {student_name}"
        
        if action == "created":
            message = f"A new personalized roadmap has been created for {student_name}."
        elif action == "updated":
            message = f"The roadmap for {student_name} has been updated based on recent progress."
        elif action == "review_required":
            message = f"Teacher review required for {student_name}'s roadmap."
        else:
            message = f"Roadmap notification for {student_name}."
        
        return self.send_notification_email(
            to_email, "roadmap", subject, message, "high"
        )
    
    def send_progress_report(self, to_email: str, student_name: str, 
                           report_data: Dict[str, Any]) -> bool:
        """Send weekly progress report"""
        subject = f"Weekly Progress Report - {student_name}"
        
        # Create detailed progress report
        message = f"""
Weekly Progress Report for {student_name}

Performance Summary:
- Tasks Completed: {report_data.get('tasks_completed', 0)}
- Tasks Pending: {report_data.get('tasks_pending', 0)}
- Adherence Rate: {report_data.get('adherence_rate', 0):.1%}

Irregularities Detected: {len(report_data.get('irregularities', []))}
Recommendations: {len(report_data.get('recommendations', []))}

Please review the full report in the system dashboard.
        """.strip()
        
        return self.send_notification_email(
            to_email, "progress_report", subject, message, "medium"
        )
    
    def send_alert_email(self, to_email: str, alert_type: str, 
                        student_name: str, details: str) -> bool:
        """Send urgent alert email"""
        subject = f"URGENT: {alert_type} - {student_name}"
        
        message = f"""
URGENT ALERT

Student: {student_name}
Alert Type: {alert_type}
Details: {details}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please take immediate action.
        """.strip()
        
        return self.send_notification_email(
            to_email, "alert", subject, message, "critical"
        )
    
    def _create_notification_template(self, title: str, message: str, 
                                    notification_type: str, priority: str) -> str:
        """Create HTML email template"""
        
        # Color coding based on priority
        priority_colors = {
            "low": "#28a745",
            "medium": "#ffc107", 
            "high": "#fd7e14",
            "critical": "#dc3545"
        }
        
        color = priority_colors.get(priority.lower(), "#6c757d")
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: {color};
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 0 0 5px 5px;
                }}
                .priority {{
                    display: inline-block;
                    background-color: {color};
                    color: white;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                    font-weight: bold;
                    text-transform: uppercase;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    font-size: 12px;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{title}</h1>
                <span class="priority">{priority}</span>
            </div>
            <div class="content">
                <p>{message}</p>
                <p><strong>Notification Type:</strong> {notification_type}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <div class="footer">
                <p>This is an automated message from the Personalized Roadmap Generation System.</p>
                <p>Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def send_bulk_emails(self, email_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """Send bulk emails and return results"""
        results = {
            "total": len(email_list),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for email_data in email_list:
            try:
                success = self.send_email(
                    to_email=email_data['to'],
                    subject=email_data['subject'],
                    body=email_data['body'],
                    html_body=email_data.get('html_body')
                )
                
                if success:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Failed to send to {email_data['to']}")
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error sending to {email_data['to']}: {str(e)}")
        
        return results

class EmailTemplateManager:
    """Manage email templates for different notification types"""
    
    def __init__(self):
        self.templates = {
            "welcome": self._welcome_template,
            "roadmap_created": self._roadmap_created_template,
            "progress_report": self._progress_report_template,
            "teacher_feedback": self._teacher_feedback_template,
            "parent_notification": self._parent_notification_template,
            "system_alert": self._system_alert_template
        }
    
    def get_template(self, template_name: str, **kwargs) -> Dict[str, str]:
        """Get email template with variables filled"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        return self.templates[template_name](**kwargs)
    
    def _welcome_template(self, user_name: str, user_type: str) -> Dict[str, str]:
        return {
            "subject": f"Welcome to Personalized Roadmap System, {user_name}!",
            "body": f"""
Welcome {user_name}!

You have been successfully registered as a {user_type} in the Personalized Roadmap Generation System.

You can now:
- Access your personalized dashboard
- Monitor student progress (if applicable)
- Submit feedback and recommendations
- Receive real-time notifications

Please log in to the system to get started.

Best regards,
The Personalized Roadmap Team
            """.strip()
        }
    
    def _roadmap_created_template(self, student_name: str, roadmap_id: str) -> Dict[str, str]:
        return {
            "subject": f"New Roadmap Created for {student_name}",
            "body": f"""
A new personalized roadmap has been created for {student_name}.

Roadmap ID: {roadmap_id}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

The roadmap includes:
- Personalized study schedule
- Subject-specific time allocation
- Learning resource recommendations
- Progress tracking milestones

Please review the roadmap in the system dashboard.

Best regards,
The Personalized Roadmap Team
            """.strip()
        }
    
    def _progress_report_template(self, student_name: str, week: int, data: Dict) -> Dict[str, str]:
        return {
            "subject": f"Weekly Progress Report - {student_name} (Week {week})",
            "body": f"""
Weekly Progress Report for {student_name} - Week {week}

Performance Summary:
- Tasks Completed: {data.get('tasks_completed', 0)}
- Tasks Pending: {data.get('tasks_pending', 0)}
- Adherence Rate: {data.get('adherence_rate', 0):.1%}

Key Insights:
- Irregularities: {len(data.get('irregularities', []))}
- Recommendations: {len(data.get('recommendations', []))}

Please review the full report in the system dashboard for detailed analysis.

Best regards,
The Personalized Roadmap Team
            """.strip()
        }
    
    def _teacher_feedback_template(self, teacher_name: str, student_name: str) -> Dict[str, str]:
        return {
            "subject": f"Feedback Required - {student_name}",
            "body": f"""
Dear {teacher_name},

Your feedback is required for {student_name}'s personalized roadmap.

Please review the current roadmap and provide your professional assessment:
- Academic accuracy of the study plan
- Feasibility of the timeline
- Resource recommendations
- Any adjustments needed

You can submit your feedback through the teacher interface.

Best regards,
The Personalized Roadmap Team
            """.strip()
        }
    
    def _parent_notification_template(self, parent_name: str, student_name: str, update_type: str) -> Dict[str, str]:
        return {
            "subject": f"Update on {student_name}'s Progress",
            "body": f"""
Dear {parent_name},

This is an update regarding {student_name}'s progress in the Personalized Roadmap System.

Update Type: {update_type}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

You can view detailed progress information in the parent dashboard.

Best regards,
The Personalized Roadmap Team
            """.strip()
        }
    
    def _system_alert_template(self, alert_type: str, details: str) -> Dict[str, str]:
        return {
            "subject": f"SYSTEM ALERT: {alert_type}",
            "body": f"""
SYSTEM ALERT

Alert Type: {alert_type}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Details: {details}

This is an automated system alert. Please investigate if necessary.

Best regards,
The Personalized Roadmap System
            """.strip()
        }
