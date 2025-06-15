# Candidate-Email-Manager_VIBECODING_Experiment
Candidate Email Manager_VIBECODING_Experiment_CLAUDE
---
 Candidate Email Manager
A Python application designed for managing sequential email campaigns for job candidates. Built with DuckDB for data persistence and perfect for running in GitHub Codespaces!

🚀 Features

Candidate Management: Add and track candidates with their details
Sequential Email Campaigns: Send 3 automated emails per candidate with configurable delays
Email Templates: Pre-built professional email templates for recruitment
Queue System: Schedule and process emails automatically
Email Logging: Track all sent emails with timestamps and status
Dashboard: View statistics and campaign performance
SMTP Integration: Send real emails or run in simulation mode

🛠️ Setup
For GitHub Codespaces

Create a new repository with these files
Open in Codespaces - everything will be automatically configured!
Install dependencies:
bashpip install -r requirements.txt

Configure email settings (optional):
bashcp .env.example .env
# Edit .env with your SMTP credentials

Run the application:
bashpython candidate_email_manager.py


Email Configuration
The app works in two modes:
1. Simulation Mode (Default)

No SMTP configuration needed
Emails are printed to console instead of being sent
Perfect for testing and development

2. Real Email Mode

Configure SMTP settings in .env file
Supports Gmail, Outlook, Yahoo, and custom SMTP servers
For Gmail: Use App Passwords (not regular password)

📋 Usage
1. Add Candidates
Menu Option 1: Add Candidate
- Enter candidate name, email, and position
- Candidate is stored in DuckDB database
2. Trigger Email Sequence
Menu Option 3: Trigger Email Sequence
- Select a candidate from the list
- Schedules 3 emails with delays:
  - Email 1: Immediate (Welcome)
  - Email 2: After 2 days (Update)
  - Email 3: After 5 days (Final Steps)
3. Process Email Queue
Menu Option 4: Process Email Queue
- Sends all scheduled emails that are due
- Updates email status and logs
4. Monitor Progress
Menu Option 6: Dashboard
- View candidate statistics
- Email sending statistics
- Pending email count
📊 Database Schema
The application uses DuckDB with three main tables:
Candidates

id: Primary key
name: Candidate name
email: Email address (unique)
position: Job position
status: Active/Inactive
created_at: Timestamp

Email Logs

id: Primary key
candidate_id: Foreign key to candidates
email_sequence: Which email in sequence (1, 2, or 3)
subject: Email subject line
sent_at: When email was sent
status: Sent/Failed
error_message: Error details if failed

Email Queue

id: Primary key
candidate_id: Foreign key to candidates
email_sequence: Which email to send
scheduled_for: When to send the email
status: Pending/Sent/Failed

🎯 Email Templates
Email 1: Welcome (Immediate)

Confirms application received
Sets expectations for next steps
Professional and welcoming tone

Email 2: Update (2 days later)

Application review update
Requests phone screening availability
Maintains engagement

Email 3: Final Steps (5 days later)

Technical interview invitation
Final process details
Closing the loop

🔧 Customization
Modify Email Templates
Edit the load_email_templates() method in the CandidateEmailManager class:

Change subject lines
Update email content
Adjust delay timings
Add more email sequences

Add New Features
The modular design makes it easy to extend:

Add candidate scoring
Integrate with job boards
Add email analytics
Connect to CRM systems

📁 Project Structure
candidate-email-manager/
├── candidate_email_manager.py  # Main application
├── requirements.txt           # Python dependencies
├── .env.example              # Email configuration template
├── README.md                 # This file
└── candidates.db            # DuckDB database (created automatically)
🚨 GitHub Codespaces Tips

Persistent Storage: The DuckDB file persists between Codespace sessions
Environment Variables: Store sensitive SMTP credentials in Codespace secrets
Port Forwarding: Not needed for this CLI application
Extensions: Consider installing Python and SQLite extensions for better development experience

🔒 Security Notes

Never commit SMTP credentials to version control
Use environment variables for sensitive configuration
Consider using app passwords for Gmail
Test with simulation mode first

🐛 Troubleshooting
Common Issues

SMTP Authentication Failed

Check if 2FA is enabled (use app passwords)
Verify SMTP server settings
Test with a simple SMTP client first


Database Locked

Only one instance should run at a time
Check for other Python processes using the database


Email Not Sending

Run in simulation mode to test logic
Check email queue status
Verify network connectivity



🎉 Getting Started

Open this project in GitHub Codespaces
Run: python candidate_email_manager.py
Add a few test candidates
Trigger email sequences
Process the queue to see emails in action!

Perfect for recruitment teams, HR departments, or anyone managing candidate communications! 🚀
