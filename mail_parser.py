"""
Email Parser.
Distinguishes between structured data (direct article content inside emails)
and unstructured data (curated links, bookmarks, notifications).
Extracts articles directly or prepares URLs for Playwright crawling.
"""
import re
import logging
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from config import NEWSPAPER_PUBLISHER

logger = logging.getLogger(__name__)

# Keywords for category auto-classification
CATEGORY_KEYWORDS = {
    "AI/ML": [
        "ai", "인공지능", "gpt", "llm", "claude", "클로드", "제미니", "gemini",
        "openai", "오픈ai", "anthropic", "앤트로픽", "프롬프트", "머신러닝", "딥러닝",
        "에이전트", "agent", "파운데이션", "트랜스포머", "라마", "llama", "엔비디아", "nvidia",
        "휴머노이드", "로봇", "사고 사슬", "cot", "생성형"
    ],
    "데이터": [
        "데이터", "database", "db", "데이터베이스", "sql", "벡터", "vector",
        "turbopuffer", "인덱스", "파이프라인", "빅데이터", "etl", "쿼리", "스토리지",
        "data lake", "lakehouse", "redshift", "snowflake"
    ],
    "보안": [
        "보안", "security", "취약점", "vulnerability", "해킹", "hacking",
        "리눅스 커널", "kernel", "악성코드", "랜섬웨어", "cve", "피싱", "인증",
        "auth", "zero-day", "제로데이", "암호화"
    ]
}


def classify_category(text: str) -> str:
    """Classifies category based on title and content text."""
    lower_text = text.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in lower_text:
                return cat
    return "기타"


def clean_text(text: str) -> str:
    """Removes extra whitespaces and newline noise."""
    if not text:
        return ""
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def is_newsletter_unsubscribe_or_ad(url: str, text: str) -> bool:
    """Filters out unsubscribe links, privacy policies, SNS buttons, etc."""
    lower_url = url.lower()
    lower_text = text.lower()
    block_patterns = [
        "unsubscribe", "수신거부", "privacy", "terms", "policy", "facebook.com",
        "twitter.com", "instagram.com", "linkedin.com", "youtube.com",
        "mailchimp", "stibee.com/api", "forms.gle", "kakao.com/share",
        "mailto:", "javascript:", "#"
    ]
    return any(bp in lower_url or bp in lower_text for bp in block_patterns)


class EmailParser:
    def __init__(self, default_publisher: str = NEWSPAPER_PUBLISHER):
        self.default_publisher = default_publisher

    def parse_email(self, email_item: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parses an email.
        Returns:
            structured_articles: List of articles directly extracted from email body
            external_urls_to_crawl: List of URLs that require Playwright crawling (unstructured)
        """
        html = email_item.get("html", "")
        text = email_item.get("text", "")
        subject = email_item.get("subject", "").strip()
        sender = email_item.get("sender", "").strip()

        # Clean publisher name from sender
        publisher_name = self.default_publisher
        if sender:
            # e.g. "GeekNews <news@geeknews.com>" -> "GeekNews"
            match = re.match(r'^([^<]+)', sender)
            if match and match.group(1).strip():
                clean_sender = match.group(1).strip().replace('"', '')
                if clean_sender:
                    publisher_name = clean_sender

        soup = BeautifulSoup(html if html else f"<p>{text}</p>", "lxml")

        # Strip scripts, styles, forms
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        structured_articles: List[Dict[str, Any]] = []
        urls_to_crawl: List[str] = []

        # 1. Check if email contains sectioned articles (h2/h3 headings or clear blocks)
        headings = soup.find_all(["h1", "h2", "h3", "h4"])
        
        # If there are multiple clear section headings with paragraphs beneath them,
        # it is a structured digest newsletter!
        if len(headings) >= 2:
            for h in headings:
                h_title = clean_text(h.get_text())
                if len(h_title) < 5 or "구독" in h_title or "뉴스레터" in h_title:
                    continue

                # Collect sibling text until next heading
                body_paras = []
                img_url = ""
                curr = h.find_next_sibling()
                while curr and curr.name not in ["h1", "h2", "h3", "h4"]:
                    if curr.name == "p" or curr.name == "div":
                        p_txt = clean_text(curr.get_text())
                        if len(p_txt) > 20:
                            body_paras.append(p_txt)
                    if not img_url:
                        img = curr.find("img")
                        if img and img.get("src") and img.get("src").startswith("http"):
                            img_url = img.get("src")
                    curr = curr.find_next_sibling()

                # If we found substantial content directly
                if body_paras:
                    full_content = " ".join(body_paras)
                    summary = full_content[:350] + ("..." if len(full_content) > 350 else "")
                    cat = classify_category(f"{h_title} {summary}")
                    structured_articles.append({
                        "title": h_title,
                        "content": summary,
                        "full_content": full_content,
                        "image_url": img_url,
                        "source": publisher_name,
                        "category": cat,
                        "is_structured": True
                    })

        # 2. Extract potential unstructured links from <a> tags
        for a in soup.find_all("a", href=True):
            href = a.get("href", "").strip()
            link_text = clean_text(a.get_text())
            if not href.startswith(("http://", "https://")):
                continue
            if is_newsletter_unsubscribe_or_ad(href, link_text):
                continue
            # Filter out duplicate URLs
            if href not in urls_to_crawl:
                urls_to_crawl.append(href)

        # 3. If no structured articles found, check if the email itself is a single structured article
        if not structured_articles:
            body_text = clean_text(soup.get_text())
            # If body has substantial text (> 150 chars) and subject exists
            if len(body_text) > 150 and len(subject) > 5:
                # Find first image
                first_img = soup.find("img")
                img_url = first_img.get("src") if first_img and first_img.get("src", "").startswith("http") else ""
                
                # Check whether it's primarily a link list or an actual article
                link_count = len(urls_to_crawl)
                # If there are many links compared to length, it's unstructured (curated link list)
                if link_count > 4 and len(body_text) / (link_count + 1) < 80:
                    logger.info(f"Email '{subject}' detected as unstructured link list with {link_count} links.")
                else:
                    # Treat as structured single article
                    summary = body_text[:350] + ("..." if len(body_text) > 350 else "")
                    cat = classify_category(f"{subject} {summary}")
                    structured_articles.append({
                        "title": subject,
                        "content": summary,
                        "full_content": body_text,
                        "image_url": img_url,
                        "source": publisher_name,
                        "category": cat,
                        "is_structured": True
                    })

        return structured_articles, urls_to_crawl
