import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.settings import Settings

settings = Settings.load()
logger = logging.getLogger(__name__)


class EmailService:
    def __init__(
            self,
            *,
            use_tls: bool | None = None,
            smtp_host: str | None = None,
            smtp_port: str | None = None,
            smtp_user: str | None = None,
            smtp_password: str | None = None,
    ) -> None:
        self._use_tls = use_tls or settings.email_settings.USE_TLS
        self._smtp_host = smtp_host or settings.email_settings.SMTP_HOST
        self._smtp_port = smtp_port or settings.email_settings.SMTP_PORT
        self._smtp_user = smtp_user or settings.email_settings.SMTP_USER
        self._smtp_password = smtp_password or settings.email_settings.SMTP_PASSWORD

    async def send_registration_email(self, email: str, password: str) -> None:
        try:
            await self._send_email(
                to_email=email,
                subject='New account',
                body=f'Your password : "{password}"',
            )
            logger.info('Password sent to %s', email)
        except Exception:
            logger.exception('Failed to send password to %s', email)
            raise

    async def _send_email(
            self,
            to_email: str,
            subject: str,
            body: str,
    ) -> None:
        """Send an email.

        Args:
            to_email: Recipient email address.
            subject: Email subject.
            body: Email body.

        Raises:
            Exception: If email sending fails.

        """
        msg = MIMEMultipart()
        msg['From'] = self._smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            # Run synchronous SMTP operations in thread pool
            await asyncio.to_thread(self._send_sync_email, msg)
        except Exception:
            logger.exception('Failed to send email to %s', to_email)
            raise

    def _send_sync_email(self, msg: MIMEMultipart) -> None:
        """Send an email.

        Args:
            msg: Email message.

        Raises:
            Exception: If email sending fails.

        """
        with smtplib.SMTP(
                self._smtp_host,
                self._smtp_port,
        ) as server:
            if self._use_tls:
                server.starttls()

            if (
                    self._smtp_user
                    and self._smtp_password
            ):
                server.login(
                    self._smtp_user,
                    self._smtp_password,
                )

            server.send_message(msg)
