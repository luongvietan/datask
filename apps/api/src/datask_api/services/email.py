# -*- coding: utf-8 -*-
"""
Email notification service.
Stub: log to console in development; use Resend in production.
"""
import os
import structlog

logger = structlog.get_logger()


async def send_quota_alert(account_id: str, email: str, pct: int, tier: str) -> None:
    """
    Gửi email cảnh báo khi quota đạt 80% hoặc 100%.
    pct = 80 hoặc 100.
    """
    subject = f"[Datask] You've used {pct}% of your monthly quota"
    body = (
        f"Hi,\n\n"
        f"You've used {pct}% of your monthly Datask quota ({tier} tier).\n\n"
        f"{'Upgrade now to avoid interruptions: https://datask.run/pricing' if pct >= 100 else 'Consider upgrading: https://datask.run/pricing'}\n\n"
        f"— The Datask Team"
    )

    resend_api_key = os.environ.get("RESEND_API_KEY", "")

    if resend_api_key:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {resend_api_key}"},
                    json={
                        "from": "Datask <noreply@datask.run>",
                        "to": [email],
                        "subject": subject,
                        "text": body,
                    },
                )
                if response.is_success:
                    logger.info("quota_alert_sent", account_id=account_id, pct=pct)
                else:
                    logger.warning("quota_alert_failed", account_id=account_id, status=response.status_code)
        except Exception as e:
            logger.error("quota_alert_error", account_id=account_id, error=str(e))
    else:
        # Development: log thay vì gửi email
        logger.info("quota_alert_console", account_id=account_id, email=email, pct=pct, subject=subject)
