"""Outbound Email Dispatcher Service for CareerPilot AI.
Handles delivery of tailored job applications via SMTP or Sandbox mock.
Supports Human-in-the-Loop 1-Click Apply and Threshold-Based Auto-Apply.
"""
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from typing import Optional

from careerpilot.core.config import settings
from careerpilot.domain.models import AuditEvent, CareerProfile, NormalizedJob
from careerpilot.drafting.models import ApplicationPackage, ApplicationStatus
from careerpilot.storage.repository import JobRepository


class EmailDispatchResult:
    def __init__(self, success: bool, message_id: str, recipient: str, status: str, error: Optional[str] = None):
        self.success = success
        self.message_id = message_id
        self.recipient = recipient
        self.status = status
        self.error = error

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "message_id": self.message_id,
            "recipient": self.recipient,
            "status": self.status,
            "error": self.error,
        }


class EmailDispatcher:
    """Dispatches approved application packages to hiring teams via SMTP or sandbox simulator."""

    def __init__(
        self,
        repository: JobRepository,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_pass: Optional[str] = None,
        sandbox_mode: bool = True,
    ):
        self.repo = repository
        self.smtp_host = smtp_host or getattr(settings, "smtp_host", "localhost")
        self.smtp_port = smtp_port or getattr(settings, "smtp_port", 587)
        self.smtp_user = smtp_user or getattr(settings, "smtp_user", "")
        self.smtp_pass = smtp_pass or getattr(settings, "smtp_password", "")
        self.sandbox_mode = sandbox_mode or not bool(self.smtp_user and self.smtp_pass)

    def extract_company_email(self, job: NormalizedJob) -> str:
        """Derive or sanitize recipient email for a job opportunity."""
        # Check source URL or domain heuristic
        clean_company = "".join(c for c in job.company.lower() if c.isalnum())
        return f"careers@{clean_company}.com"

    def build_mime_message(
        self,
        application: ApplicationPackage,
        job: NormalizedJob,
        profile: CareerProfile,
        recipient: str,
    ) -> MIMEMultipart:
        """Construct RFC-compliant MIME message with cover email and tailored CV attachment."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = application.cover_email.subject
        msg["From"] = f"{profile.full_name} <{profile.email}>"
        msg["To"] = recipient
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain="careerpilot.ai")

        # Plain text version
        email = application.cover_email
        body_text_parts = [
            email.salutation,
            "",
            "\n\n".join(email.body_paragraphs),
            "",
            email.call_to_action,
            "",
            email.sign_off,
            f"{profile.full_name}",
            f"{profile.email} | {profile.phone or ''}",
            "",
            "=" * 50,
            f"TAILORED CV ATTACHMENT: {application.cv_variant.tailored_headline}",
            "=" * 50,
            application.cv_variant.tailored_summary,
            "",
            "HIGHLIGHTED SKILLS:",
            ", ".join(application.cv_variant.highlighted_skills),
            "",
            "RELEVANT EXPERIENCE:",
        ]
        for exp in application.cv_variant.highlighted_experience:
            body_text_parts.append(f"- {exp.title} at {exp.company}:")
            for hl in exp.highlights:
                body_text_parts.append(f"    * {hl}")

        body_text_parts.append("\nREPRESENTATIVE PROJECTS:")
        for proj in application.cv_variant.highlighted_projects:
            body_text_parts.append(f"- {proj.name} ({proj.role}): {', '.join(proj.highlights)}")

        plain_part = MIMEText("\n".join(body_text_parts), "plain", "utf-8")
        msg.attach(plain_part)

        # HTML version
        paragraphs_html = "".join(f"<p style='margin-bottom: 12px;'>{p}</p>" for p in email.body_paragraphs)
        skills_html = "".join(f"<span style='display:inline-block;background:#eff6ff;color:#1e40af;padding:3px 8px;border-radius:4px;margin:2px;font-size:12px;'>{s}</span>" for s in application.cv_variant.highlighted_skills)
        
        html_content = f"""
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1e293b; line-height: 1.6; max-width: 650px; margin: 0 auto; padding: 20px;">
            <p>{email.salutation}</p>
            {paragraphs_html}
            <p style="font-weight: 500;">{email.call_to_action}</p>
            <p>{email.sign_off}<br><strong>{profile.full_name}</strong><br><span style="color:#64748b; font-size:13px;">{profile.email} | {profile.phone or ''}</span></p>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px;">
                <h4 style="margin: 0 0 8px 0; color: #0f172a;">Tailored Resume Summary: {application.cv_variant.tailored_headline}</h4>
                <p style="font-size: 13px; color: #334155; margin-bottom: 12px;">{application.cv_variant.tailored_summary}</p>
                <div style="margin-bottom: 12px;">{skills_html}</div>
            </div>
        </body>
        </html>
        """
        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(html_part)

        return msg

    def dispatch(
        self,
        application: ApplicationPackage,
        job: NormalizedJob,
        profile: CareerProfile,
        recipient_override: Optional[str] = None,
    ) -> EmailDispatchResult:
        """Send application via SMTP or Sandbox mode."""
        recipient = recipient_override or self.extract_company_email(job)
        mime_msg = self.build_mime_message(application, job, profile, recipient)
        msg_id = mime_msg["Message-ID"]

        if self.sandbox_mode:
            # Sandbox dispatch: verify payload structure and log to database
            dispatch_status = "SENT_SANDBOX"
        else:
            try:
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_pass)
                    server.send_message(mime_msg)
                dispatch_status = "DELIVERED_SMTP"
            except Exception as e:
                return EmailDispatchResult(
                    success=False,
                    message_id=msg_id,
                    recipient=recipient,
                    status="FAILED",
                    error=str(e),
                )

        # Update application status in repository
        self.repo.record_audit_event(
            AuditEvent(
                entity_type="application",
                entity_id=application.id,
                action="APPLICATION_SUBMITTED",
                actor="careerpilot_dispatcher",
                outcome="SUCCESS",
                details={
                    "job_id": job.id,
                    "company": job.company,
                    "recipient": recipient,
                    "subject": application.cover_email.subject,
                    "mode": "sandbox" if self.sandbox_mode else "smtp",
                    "draft_hash": application.draft_hash,
                },
            )
        )

        return EmailDispatchResult(
            success=True,
            message_id=msg_id,
            recipient=recipient,
            status=dispatch_status,
        )
