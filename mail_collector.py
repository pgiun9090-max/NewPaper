"""
IMAP Mail Collector for Gmail.
Connects to Gmail via IMAP (SSL), navigates to the 'News' label,
and fetches emails within the 24-hour window from 08:00 yesterday to 08:00 today.
"""
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import re
import logging
from config import IMAP_SERVER, IMAP_PORT, GMAIL_USER, GMAIL_APP_PASSWORD, GMAIL_LABEL

logger = logging.getLogger(__name__)

# KST Timezone (UTC+9)
KST = timezone(timedelta(hours=9))


def decode_str(header_value: Optional[str]) -> str:
    """Decodes MIME encoded header strings safely."""
    if not header_value:
        return ""
    try:
        decoded_parts = decode_header(header_value)
        result = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    result.append(part.decode(encoding or "utf-8", errors="replace"))
                except Exception:
                    result.append(part.decode("utf-8", errors="replace"))
            else:
                result.append(str(part))
        return "".join(result).strip()
    except Exception as e:
        logger.warning(f"Failed to decode header '{header_value}': {e}")
        return str(header_value)


def get_target_time_window(reference_dt: Optional[datetime] = None, use_exact_today_run: bool = False):
    """
    Computes the target time window:
    - Standard 8 AM run: From yesterday 08:00 KST to today 08:00 KST.
    - If executed in the afternoon (manual/test run) and use_exact_today_run is False:
      Covers from yesterday 08:00 KST up to current time (or today 08:00 if morning),
      ensuring newly arrived test emails are also captured!
    """
    if reference_dt is None:
        now_kst = datetime.now(KST)
    else:
        if reference_dt.tzinfo is None:
            now_kst = reference_dt.replace(tzinfo=KST)
        else:
            now_kst = reference_dt.astimezone(KST)

    today_8am = now_kst.replace(hour=8, minute=0, second=0, microsecond=0)
    
    if use_exact_today_run:
        # Strict 8 AM to 8 AM window
        end_time = today_8am
        start_time = end_time - timedelta(days=1)
    else:
        # If currently after 8 AM, include emails up to now (from yesterday 8 AM)
        # so manual test runs don't miss afternoon emails!
        if now_kst > today_8am:
            start_time = today_8am - timedelta(days=1)
            end_time = now_kst
        else:
            end_time = today_8am
            start_time = end_time - timedelta(days=1)
    
    return start_time, end_time


class GmailCollector:
    def __init__(self, username: str = GMAIL_USER, password: str = GMAIL_APP_PASSWORD, label: str = GMAIL_LABEL):
        self.username = username
        self.password = password
        self.label = label
        self.client: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> bool:
        """Connects and logs into Gmail IMAP server."""
        if not self.password or self.password.strip() == "":
            raise ValueError(
                "Gmail App Password is not configured in .env.\n"
                "Please generate a 16-character App Password at https://myaccount.google.com/apppasswords "
                "and set GMAIL_APP_PASSWORD in the .env file."
            )
        try:
            self.client = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
            self.client.login(self.username, self.password)
            logger.info(f"Successfully connected to Gmail IMAP as {self.username}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to IMAP: {e}")
            raise

    def find_label_mailbox(self) -> str:
        """Finds the actual mailbox name corresponding to the label in Gmail."""
        if not self.client:
            raise RuntimeError("IMAP client is not connected.")

        status, mailboxes = self.client.list()
        if status != "OK":
            return self.label

        # Look for mailbox name containing self.label
        target_name = self.label.strip('"')
        for mb in mailboxes:
            decoded_mb = mb.decode("utf-8", errors="replace")
            # Format: '(\\Flags) "/" "Folder Name"'
            match = re.search(r'\"([^\"]+)\"$', decoded_mb)
            if match:
                folder_name = match.group(1)
                if folder_name.lower() == target_name.lower() or folder_name.endswith("/" + target_name):
                    return f'"{folder_name}"'

        # Fallback to quoted label name
        return f'"{target_name}"'

    def fetch_news_emails(self, start_dt: Optional[datetime] = None, end_dt: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Fetches emails from 'News' label within [start_dt, end_dt].
        Default window: yesterday 08:00 KST to today 08:00 KST.
        """
        if not self.client:
            self.connect()

        if start_dt is None or end_dt is None:
            start_dt, end_dt = get_target_time_window()

        logger.info(f"Fetching emails between {start_dt.isoformat()} and {end_dt.isoformat()} (KST)")

        mailbox_name = self.find_label_mailbox()
        status, _ = self.client.select(mailbox_name)
        if status != "OK":
            # Retry without quotes or fallback to standard label
            status, _ = self.client.select(self.label)
            if status != "OK":
                raise ValueError(f"Could not select Gmail label/mailbox: {self.label} (tried {mailbox_name})")

        # Query IMAP with SINCE date (start_dt - 1 day to be safe with timezone variations)
        imap_since_date = (start_dt - timedelta(days=1)).strftime("%d-%b-%Y")
        search_criterion = f'(SINCE "{imap_since_date}")'
        status, msg_nums = self.client.search(None, search_criterion)

        if status != "OK" or not msg_nums[0]:
            logger.info("No emails found for the given search criteria.")
            return []

        ids = msg_nums[0].split()
        logger.info(f"Found {len(ids)} potential emails since {imap_since_date}. Filtering by exact datetime...")

        fetched_emails = []

        for msg_id in reversed(ids):  # newest first
            try:
                res, data = self.client.fetch(msg_id, "(RFC822)")
                if res != "OK" or not data or not data[0]:
                    continue

                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Parse date header
                date_str = msg.get("Date")
                if not date_str:
                    continue

                try:
                    msg_dt = parsedate_to_datetime(date_str)
                    if msg_dt.tzinfo is None:
                        msg_dt = msg_dt.replace(tzinfo=KST)
                    else:
                        msg_dt = msg_dt.astimezone(KST)
                except Exception as e:
                    logger.warning(f"Failed to parse date header '{date_str}': {e}")
                    continue

                # Filter within [start_dt, end_dt]
                if not (start_dt <= msg_dt <= end_dt):
                    # Check if email is older than start_dt
                    if msg_dt < start_dt:
                        # Since we iterate newest first, if we hit older ones we can continue or break
                        pass
                    continue

                # Extract metadata
                subject = decode_str(msg.get("Subject"))
                sender = decode_str(msg.get("From"))
                message_id = msg.get("Message-ID", "")

                # Extract body
                html_body = ""
                text_body = ""

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition", ""))
                        if "attachment" in content_disposition:
                            continue

                        payload = part.get_payload(decode=True)
                        if not payload:
                            continue

                        charset = part.get_content_charset() or "utf-8"
                        try:
                            body_text = payload.decode(charset, errors="replace")
                        except Exception:
                            body_text = payload.decode("utf-8", errors="replace")

                        if content_type == "text/html":
                            html_body += body_text
                        elif content_type == "text/plain":
                            text_body += body_text
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        charset = msg.get_content_charset() or "utf-8"
                        try:
                            body_text = payload.decode(charset, errors="replace")
                        except Exception:
                            body_text = payload.decode("utf-8", errors="replace")
                        if msg.get_content_type() == "text/html":
                            html_body = body_text
                        else:
                            text_body = body_text

                fetched_emails.append({
                    "id": msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id),
                    "message_id": message_id,
                    "subject": subject,
                    "sender": sender,
                    "date": msg_dt,
                    "html": html_body,
                    "text": text_body
                })

            except Exception as e:
                logger.error(f"Error parsing email id {msg_id}: {e}")
                continue

        logger.info(f"Successfully collected {len(fetched_emails)} emails matching the 24h window.")
        return fetched_emails

    def close(self):
        """Safely closes the IMAP connection."""
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            try:
                self.client.logout()
            except Exception:
                pass
            self.client = None
