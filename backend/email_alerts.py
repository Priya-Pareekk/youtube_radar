"""
Sends the "sentiment dropped" alert email via Resend. Fails silently
(logs to console) rather than crashing the cron run if email isn't
configured or a single send fails — one bad email shouldn't stop the
rest of the watch list from being checked.
"""

import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")


def send_alert_email(to: str, topic: str, old_score: float, new_score: float, drop: float):
    if not resend.api_key:
        print(f"[email skipped] RESEND_API_KEY not set — would have alerted {to} about '{topic}'")
        return

    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to,
            "subject": f'TubeRadar: sentiment on "{topic}" just dropped',
            "html": f"""
                <div style="font-family: sans-serif; max-width: 480px;">
                  <h2 style="margin-bottom: 4px;">Sentiment shift detected</h2>
                  <p style="color: #555;">Your watch on <strong>{topic}</strong> just crossed
                  its alert threshold.</p>
                  <table style="margin: 16px 0;">
                    <tr><td style="padding-right: 16px; color: #888;">Previous score</td><td>{old_score:.2f}</td></tr>
                    <tr><td style="padding-right: 16px; color: #888;">Current score</td><td>{new_score:.2f}</td></tr>
                    <tr><td style="padding-right: 16px; color: #888;">Drop</td><td>{drop:.2f}</td></tr>
                  </table>
                  <p style="color: #999; font-size: 13px;">— TubeRadar</p>
                </div>
            """,
        })
    except Exception as e:
        print(f"[email failed] {to} / {topic}: {e}")
