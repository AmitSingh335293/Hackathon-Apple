"""
Email Route
API endpoint for sending query results as CSV email attachments.
SMTP credentials are read from .env via app settings — callers only need to supply recipients.
Uses Python's built-in smtplib — no extra dependencies required.
"""

import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

from fastapi import APIRouter, HTTPException, status, Depends

from app.models import EmailRequest
from app.config import get_settings
from app.routes.auth import get_current_user
from app.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["email"])


@router.post(
    "/send-email",
    summary="Send query results via email",
    description=(
        "Accepts recipient emails and CSV content. "
        "SMTP credentials (host, port, username, password, sender) are read from server .env — "
        "callers do NOT need to supply SMTP config."
    ),
    responses={
        200: {"description": "Email sent successfully"},
        400: {"description": "Bad request or SMTP auth failure"},
        500: {"description": "SMTP delivery failure"},
        503: {"description": "SMTP not configured on server"},
    },
)
async def send_email(
    request: EmailRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Send query result CSV as an email attachment.
    SMTP config is loaded from server-side environment variables.
    """
    settings = get_settings()

    # ------------------------------------------------------------------ #
    # Guard — ensure SMTP is configured in .env                           #
    # ------------------------------------------------------------------ #
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD or not settings.SMTP_SENDER_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "SMTP is not configured on the server. "
                "Please set SMTP_USERNAME, SMTP_PASSWORD, and SMTP_SENDER_EMAIL in the .env file."
            ),
        )

    logger.info(
        "Email send requested",
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        sender=settings.SMTP_SENDER_EMAIL,
        recipients=request.recipient_emails,
    )

    # ------------------------------------------------------------------ #
    # Build the email message                                              #
    # ------------------------------------------------------------------ #
    msg = EmailMessage()
    msg["Subject"] = request.subject
    msg["From"] = formataddr((settings.SMTP_SENDER_NAME, settings.SMTP_SENDER_EMAIL))
    msg["To"] = ", ".join(request.recipient_emails)
    msg.set_content(request.body)

    # Attach CSV
    msg.add_attachment(
        request.csv_content.encode("utf-8"),
        maintype="text",
        subtype="csv",
        filename=request.csv_filename,
    )

    # ------------------------------------------------------------------ #
    # Send via SMTP                                                        #
    # ------------------------------------------------------------------ #
    try:
        if settings.SMTP_USE_TLS:
            # STARTTLS — most common (port 587)
            context = ssl.create_default_context()
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # Try SSL first (port 465), fallback to plain (port 25)
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=context, timeout=30) as server:
                    server.ehlo()
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                    server.send_message(msg)
            except Exception:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as server:
                    server.ehlo()
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                    server.send_message(msg)

        logger.info("Email sent successfully", recipients=request.recipient_emails, filename=request.csv_filename)
        return {
            "success": True,
            "message": f"Email sent successfully to {', '.join(request.recipient_emails)}",
            "recipients": request.recipient_emails,
            "sender": settings.SMTP_SENDER_EMAIL,
            "attachment": request.csv_filename,
        }

    except smtplib.SMTPAuthenticationError as e:
        logger.error("SMTP authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SMTP authentication failed. Check SMTP_USERNAME / SMTP_PASSWORD in .env. Error: {e}",
        )
    except smtplib.SMTPConnectError as e:
        logger.error("SMTP connection failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not connect to SMTP server '{settings.SMTP_HOST}:{settings.SMTP_PORT}'. Error: {e}",
        )
    except smtplib.SMTPRecipientsRefused as e:
        logger.error("SMTP recipients refused", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"One or more recipient addresses were refused: {e}",
        )
    except smtplib.SMTPException as e:
        logger.error("SMTP error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SMTP error: {e}",
        )
    except TimeoutError:
        logger.error("SMTP connection timed out")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection to SMTP server timed out ({settings.SMTP_HOST}:{settings.SMTP_PORT}).",
        )
    except Exception as e:
        logger.error("Unexpected error sending email", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}",
        )
