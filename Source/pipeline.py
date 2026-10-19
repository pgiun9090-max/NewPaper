"""
Main Pipeline orchestrating Mail Collection, Parsing, Crawling,
Deduplication, and Newspaper Generation.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from config import (
    GMAIL_USER,
    GMAIL_APP_PASSWORD,
    GMAIL_LABEL,
    NEWSPAPER_NAME,
    NEWSPAPER_EDITION,
    NEWSPAPER_PUBLISHER
)
from mail_collector import GmailCollector, get_target_time_window
from mail_parser import EmailParser
from crawler import PlaywrightCrawler
from deduplicator import ArticleDeduplicator
from llm_curator import LLMCurator
from newspaper_generator import NewspaperGenerator
from demo_data import DEMO_ARTICLES

logger = logging.getLogger(__name__)
KST = timezone(timedelta(hours=9))


def run_pipeline(
    reference_dt: Optional[datetime] = None,
    use_demo_data: bool = False,
    headless_crawler: bool = True,
    use_exact_8am_window: bool = False
) -> Optional[Path]:
    """
    Executes the full newspaper generation pipeline:
    1. Collects emails from Gmail 'News' label within the 24h window (yesterday 08:00 ~ today 08:00).
    2. Parses structured content vs unstructured links.
    3. Crawls unstructured links with Playwright.
    4. Deduplicates all articles.
    5. Curates via LLM (Gemini 3.8 Flash):
       - 1 Main Headline (Hero, 1-column wide)
       - 2 Sub-Headlines (Featured, 2-column)
       - Summaries & Categories for remaining articles (2-column balanced)
    6. Renders newspaper HTML in Output/YYYY-MM-DD.html.
    """
    if reference_dt is None:
        target_dt = datetime.now(KST)
    else:
        target_dt = reference_dt.astimezone(KST) if reference_dt.tzinfo else reference_dt.replace(tzinfo=KST)

    generator = NewspaperGenerator()
    curator = LLMCurator()

    if use_demo_data:
        logger.info("Generating newspaper using demo dataset with LLM Curation...")
        hero, featured, remaining = curator.curate_articles(DEMO_ARTICLES)
        output_file = generator.generate(
            hero_article=hero,
            featured_articles=featured,
            remaining_articles=remaining,
            target_date=target_dt
        )
        logger.info(f"Demo newspaper generated successfully at: {output_file}")
        return output_file

    # 1. IMAP Mail Collection
    start_dt, end_dt = get_target_time_window(target_dt, use_exact_today_run=use_exact_8am_window)
    logger.info(f"Target window: {start_dt.strftime('%Y-%m-%d %H:%M')} ~ {end_dt.strftime('%Y-%m-%d %H:%M')} (KST)")

    if not GMAIL_APP_PASSWORD:
        logger.error(
            "GMAIL_APP_PASSWORD is not set in .env! "
            "Please configure your Google App Password to fetch live emails, "
            "or run with --demo to preview the layout."
        )
        return None

    collector = GmailCollector(username=GMAIL_USER, password=GMAIL_APP_PASSWORD, label=GMAIL_LABEL)
    try:
        raw_emails = collector.fetch_news_emails(start_dt=start_dt, end_dt=end_dt)
    except Exception as e:
        logger.error(f"Failed to fetch emails via IMAP: {e}")
        return None
    finally:
        collector.close()

    if not raw_emails:
        logger.warning("No emails found within the 24h window. Nothing to produce.")
        return None

    # 2. Email Parsing (Structured vs Unstructured)
    parser = EmailParser(default_publisher=NEWSPAPER_PUBLISHER)
    all_structured_articles: List[Dict[str, Any]] = []
    all_urls_to_crawl: List[str] = []

    for mail in raw_emails:
        struct_arts, crawl_urls = parser.parse_email(mail)
        all_structured_articles.extend(struct_arts)
        for u in crawl_urls:
            if u not in all_urls_to_crawl:
                all_urls_to_crawl.append(u)

    logger.info(
        f"Extracted {len(all_structured_articles)} structured articles and "
        f"{len(all_urls_to_crawl)} unstructured URLs to crawl."
    )

    # 3. Playwright Crawling for Unstructured URLs
    all_crawled_articles: List[Dict[str, Any]] = []
    if all_urls_to_crawl:
        logger.info(f"Starting Playwright crawler for {len(all_urls_to_crawl)} URLs...")
        with PlaywrightCrawler(headless=headless_crawler) as crawler:
            all_crawled_articles = crawler.crawl_urls_batch(all_urls_to_crawl)
        logger.info(f"Finished crawling. Retrieved {len(all_crawled_articles)} valid articles.")

    # Combine all articles
    combined_articles = all_structured_articles + all_crawled_articles

    if not combined_articles:
        logger.warning("No valid articles could be extracted or crawled.")
        return None

    # 4. Deduplication
    deduplicator = ArticleDeduplicator(title_threshold=0.65)
    unique_articles = deduplicator.deduplicate(combined_articles)

    # 5. LLM Curation (Gemini 3.8 Flash)
    logger.info("Executing LLM Curation for article ranking and summarization...")
    hero, featured, remaining = curator.curate_articles(unique_articles)

    # 6. Newspaper HTML Generation
    output_file = generator.generate(
        hero_article=hero,
        featured_articles=featured,
        remaining_articles=remaining,
        target_date=target_dt
    )

    logger.info(f"Newspaper generated successfully: {output_file}")
    return output_file
