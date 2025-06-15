#!/usr/bin/env python3
"""
Candidate Email Manager
A Python application to manage sequential email campaigns for candidates
Uses DuckDB for data persistence and SMTP for email delivery
"""

import duckdb
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import time
from dataclasses import dataclass


@dataclass
class Candidate:
    id: int
    name: str
    email: str
    position: str
    status: str = "active"
    created_at: str = None


@dataclass
class EmailTemplate:
    id: int
    sequence_number: int
    subject: str
    body: str
    delay_days: int = 0


class CandidateEmailManager:
    def __init__(self, db_path: str = "candidates.db"):
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self.setup_database()
        self.email_templates = self.load_email_templates()
    
    def setup_database(self):
        """Initialize database tables"""
        # Candidates table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY,
                name VARCHAR,
                email VARCHAR UNIQUE,
                position VARCHAR,
                status VARCHAR DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Email logs table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY,
                candidate_id INTEGER,
                email_sequence INTEGER,
                subject VARCHAR,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR DEFAULT 'sent',
                error_message VARCHAR,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            )
        """)
        
        # Email queue table for scheduled sends
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS email_queue (
                id INTEGER PRIMARY KEY,
                candidate_id INTEGER,
                email_sequence INTEGER,
                scheduled_for TIMESTAMP,
                status VARCHAR DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            )
        """)
        
        self.conn.commit()
    
    def load_email_templates(self) -> List[EmailTemplate]:
        """Load predefined email templates"""
        templates = [
            EmailTemplate(
                id=1,
                sequence_number=1,
                subject="Welcome to Our Recruitment Process - {candidate_name}",
                body="""Hi {candidate_name},

Thank you for your interest in the {position} position at our company!

We're excited to move forward with your application. This email confirms that we've received your application and our team will be reviewing it shortly.

What's next:
- Our hiring team will review your application
- We'll reach out within the next few days with updates
- Please feel free to reply if you have any questions

Best regards,
The Hiring Team""",
                delay_days=0
            ),
            EmailTemplate(
                id=2,
                sequence_number=2,
                subject="Application Update - Next Steps for {candidate_name}",
                body="""Hi {candidate_name},

I hope this email finds you well!

We've completed our initial review of your application for the {position} role, and we're impressed with your background.

Next steps:
- We'd like to schedule a brief phone screening
- Please reply with your availability for this week
- The call will take approximately 30 minutes

We're looking forward to learning more about you and discussing how you might fit into our team.

Best regards,
The Hiring Team""",
                delay_days=2
            ),
            EmailTemplate(
                id=3,
                sequence_number=3,
                subject="Final Steps - {position} Opportunity",
                body="""Hi {candidate_name},

Thank you for the great conversation during our phone screening!

We're moving to the final stages of our process for the {position} role. Based on our discussion, we believe you could be a great fit for our team.

Final steps:
- Technical interview/presentation (1 hour)
- Meet with team members (30 minutes)
- Final decision within 48 hours after the interview

Please let us know your availability for next week, and we'll coordinate the schedule.

Excited to continue this process with you!

Best regards,
The Hiring Team""",
                delay_days=5
            )
        ]
        return templates
    
    def add_candidate(self, name: str, email: str, position: str) -> int:
        """Add a new candidate to the database"""
        try:
            result = self.conn.execute("""
                INSERT INTO candidates (name, email, position)
                VALUES (?, ?, ?)
                RETURNING id
            """, [name, email, position]).fetchone()
            
            candidate_id = result[0]
            self.conn.commit()
            print(f"✅ Added candidate: {name} ({email}) - ID: {candidate_id}")
            return candidate_id
        except Exception as e:
            print(f"❌ Error adding candidate: {e}")
            return None
    
    def get_candidates(self) -> List[Dict]:
        """Get all candidates"""
        result = self.conn.execute("""
            SELECT id, name, email, position, status, created_at
            FROM candidates
            ORDER BY created_at DESC
        """).fetchall()
        
        candidates = []
        for row in result:
            candidates.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'position': row[3],
                'status': row[4],
                'created_at': row[5]
            })
        return candidates
    
    def trigger_email_sequence(self, candidate_id: int):
        """Trigger the 3-email sequence for a candidate"""
        # Check if candidate exists
        candidate = self.conn.execute("""
            SELECT name, email, position FROM candidates WHERE id = ?
        """, [candidate_id]).fetchone()
        
        if not candidate:
            print(f"❌ Candidate with ID {candidate_id} not found")
            return
        
        name, email, position = candidate
        print(f"🚀 Triggering email sequence for {name} ({email})")
        
        # Schedule all three emails
        base_date = datetime.now()
        for template in self.email_templates:
            scheduled_for = base_date + timedelta(days=template.delay_days)
            
            self.conn.execute("""
                INSERT INTO email_queue (candidate_id, email_sequence, scheduled_for)
                VALUES (?, ?, ?)
            """, [candidate_id, template.sequence_number, scheduled_for])
        
        self.conn.commit()
        print(f"📅 Scheduled {len(self.email_templates)} emails for {name}")
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP (configure your SMTP settings)"""
        try:
            # Get SMTP configuration from environment variables
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            from_email = os.getenv('FROM_EMAIL', smtp_user)
            
            if not all([smtp_user, smtp_password]):
                print("⚠️  SMTP credentials not configured. Email simulation mode.")
                print(f"📧 SIMULATED EMAIL:")
                print(f"   To: {to_email}")
                print(f"   Subject: {subject}")
                print(f"   Body: {body[:100]}...")
                return True
            
            # Create message
            msg = MimeMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    def process_email_queue(self):
        """Process pending emails in the queue"""
        pending_emails = self.conn.execute("""
            SELECT eq.id, eq.candidate_id, eq.email_sequence, c.name, c.email, c.position
            FROM email_queue eq
            JOIN candidates c ON eq.candidate_id = c.id
            WHERE eq.status = 'pending' 
            AND eq.scheduled_for <= CURRENT_TIMESTAMP
            ORDER BY eq.scheduled_for
        """).fetchall()
        
        if not pending_emails:
            print("📭 No pending emails to process")
            return
        
        print(f"📤 Processing {len(pending_emails)} pending emails...")
        
        for queue_id, candidate_id, sequence, name, email, position in pending_emails:
            # Get the email template
            template = next((t for t in self.email_templates if t.sequence_number == sequence), None)
            if not template:
                continue
            
            # Format the email content
            subject = template.subject.format(candidate_name=name, position=position)
            body = template.body.format(candidate_name=name, position=position)
            
            # Send the email
            success = self.send_email(email, subject, body)
            
            # Update queue status
            self.conn.execute("""
                UPDATE email_queue 
                SET status = ? 
                WHERE id = ?
            """, ['sent' if success else 'failed', queue_id])
            
            # Log the email
            self.conn.execute("""
                INSERT INTO email_logs (candidate_id, email_sequence, subject, status, error_message)
                VALUES (?, ?, ?, ?, ?)
            """, [candidate_id, sequence, subject, 'sent' if success else 'failed', 
                  None if success else 'SMTP Error'])
        
        self.conn.commit()
        print("✅ Email processing completed")
    
    def get_email_history(self, candidate_id: Optional[int] = None) -> List[Dict]:
        """Get email history for all candidates or specific candidate"""
        if candidate_id:
            query = """
                SELECT el.*, c.name, c.email 
                FROM email_logs el
                JOIN candidates c ON el.candidate_id = c.id
                WHERE el.candidate_id = ?
                ORDER BY el.sent_at DESC
            """
            params = [candidate_id]
        else:
            query = """
                SELECT el.*, c.name, c.email 
                FROM email_logs el
                JOIN candidates c ON el.candidate_id = c.id
                ORDER BY el.sent_at DESC
            """
            params = []
        
        result = self.conn.execute(query, params).fetchall()
        
        history = []
        for row in result:
            history.append({
                'log_id': row[0],
                'candidate_id': row[1],
                'email_sequence': row[2],
                'subject': row[3],
                'sent_at': row[4],
                'status': row[5],
                'error_message': row[6],
                'candidate_name': row[7],
                'candidate_email': row[8]
            })
        return history
    
    def show_dashboard(self):
        """Display a simple dashboard"""
        print("\n" + "="*60)
        print("📊 CANDIDATE EMAIL MANAGER DASHBOARD")
        print("="*60)
        
        # Candidate stats
        stats = self.conn.execute("""
            SELECT 
                COUNT(*) as total_candidates,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_candidates
            FROM candidates
        """).fetchone()
        
        print(f"👥 Total Candidates: {stats[0]}")
        print(f"✅ Active Candidates: {stats[1]}")
        
        # Email stats
        email_stats = self.conn.execute("""
            SELECT 
                COUNT(*) as total_emails,
                COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent_emails,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_emails
            FROM email_logs
        """).fetchone()
        
        print(f"📧 Total Emails Sent: {email_stats[0]}")
        print(f"✅ Successful: {email_stats[1]}")
        print(f"❌ Failed: {email_stats[2]}")
        
        # Pending emails
        pending = self.conn.execute("""
            SELECT COUNT(*) FROM email_queue WHERE status = 'pending'
        """).fetchone()[0]
        
        print(f"⏳ Pending Emails: {pending}")
        print("="*60)


def main():
    """Main application entry point"""
    print("🚀 Candidate Email Manager")
    print("Perfect for GitHub Codespaces!")
    
    # Initialize the manager
    manager = CandidateEmailManager()
    
    while True:
        print("\n📋 MENU:")
        print("1. Add Candidate")
        print("2. View Candidates")
        print("3. Trigger Email Sequence")
        print("4. Process Email Queue")
        print("5. View Email History")
        print("6. Dashboard")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            name = input("Candidate Name: ").strip()
            email = input("Candidate Email: ").strip()
            position = input("Position: ").strip()
            manager.add_candidate(name, email, position)
        
        elif choice == '2':
            candidates = manager.get_candidates()
            print(f"\n👥 CANDIDATES ({len(candidates)} total):")
            print("-" * 60)
            for c in candidates:
                print(f"ID: {c['id']} | {c['name']} | {c['email']} | {c['position']}")
        
        elif choice == '3':
            candidates = manager.get_candidates()
            if not candidates:
                print("No candidates found. Add some candidates first!")
                continue
            
            print("\nSelect candidate:")
            for c in candidates:
                print(f"{c['id']}: {c['name']} ({c['email']})")
            
            try:
                candidate_id = int(input("Enter candidate ID: "))
                manager.trigger_email_sequence(candidate_id)
            except ValueError:
                print("Invalid candidate ID")
        
        elif choice == '4':
            manager.process_email_queue()
        
        elif choice == '5':
            history = manager.get_email_history()
            print(f"\n📧 EMAIL HISTORY ({len(history)} emails):")
            print("-" * 80)
            for h in history:
                print(f"{h['sent_at']} | {h['candidate_name']} | Seq {h['email_sequence']} | {h['status']}")
        
        elif choice == '6':
            manager.show_dashboard()
        
        elif choice == '7':
            print("👋 Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()