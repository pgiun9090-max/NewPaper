"""
Playwright Web Crawler.
Visits extracted URLs from unstructured email content, renders web pages,
and extracts article title, main body text, top representative image, and source.
"""
import re
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

# User agent string to avoid standard bot blocks
CHROME_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Common article content container selectors
CONTENT_SELECTORS = [
    "article",
    "[itemprop='articleBody']",
    "#article-body",
    ".article-body",
    ".article_body",
    ".news_body",
    ".post-content",
    ".entry-content",
    ".content_area",
    "#newsct_article",      # Naver news
    "#dic_area",            # Naver news
    ".article_view",        # Daum news
    "main",
    ".container"
]


class PlaywrightCrawler:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._pw = None
        self._browser: Optional[Browser] = None

    def start(self):
        """Starts the Playwright browser instance."""
        if self._browser is None:
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            logger.info("Playwright browser launched.")

    def close(self):
        """Closes browser and stops Playwright."""
        if self._browser:
            try:
                self._browser.close()
            except Exception:
                pass
            self._browser = None
        if self._pw:
            try:
                self._pw.stop()
            except Exception:
                pass
            self._pw = None
        logger.info("Playwright browser closed.")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def crawl_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Crawls a single URL and extracts title, body, representative image, and source.
        """
        if not self._browser:
            self.start()

        if not url or not url.startswith(("http://", "https://")):
            return None

        context = self._browser.new_context(
            user_agent=CHROME_USER_AGENT,
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page: Page = context.new_page()

        try:
            logger.info(f"Crawling URL: {url}")
            # Navigate to the page with commit event and 10s timeout for fast scraping
            try:
                response = page.goto(url, wait_until="commit", timeout=10000)
                # Wait briefly for main content
                page.wait_for_load_state("domcontentloaded", timeout=4000)
            except PlaywrightTimeoutError:
                # Even if domcontentloaded times out, the page DOM might already have loaded
                pass

            # 1. Title extraction
            title = ""
            # Try OpenGraph title
            og_title = page.locator("meta[property='og:title']").get_attribute("content")
            if og_title and og_title.strip():
                title = og_title.strip()
            
            # Try Twitter title
            if not title:
                tw_title = page.locator("meta[name='twitter:title']").get_attribute("content")
                if tw_title and tw_title.strip():
                    title = tw_title.strip()

            # Try H1
            if not title:
                h1_elements = page.locator("h1").all()
                if h1_elements:
                    title = h1_elements[0].inner_text().strip()

            # Try Document Title
            if not title:
                title = page.title().strip()

            # Clean Title (strip site suffix like " - GeekNews", " | 블로터")
            title = re.sub(r'\s*[-|]\s*[^|^-]+$', '', title).strip() or title

            # 2. Image extraction
            image_url = ""
            og_img = page.locator("meta[property='og:image']").get_attribute("content")
            if og_img and og_img.strip():
                image_url = og_img.strip()

            if not image_url:
                tw_img = page.locator("meta[name='twitter:image']").get_attribute("content")
                if tw_img and tw_img.strip():
                    image_url = tw_img.strip()

            if not image_url:
                # Find first large image inside content container
                for selector in CONTENT_SELECTORS:
                    loc = page.locator(f"{selector} img")
                    count = loc.count()
                    if count > 0:
                        src = loc.first.get_attribute("src")
                        if src and src.startswith(("http://", "https://")):
                            image_url = src
                            break

            # 3. Source extraction
            site_name = page.locator("meta[property='og:site_name']").get_attribute("content")
            if not site_name:
                domain = urlparse(url).netloc
                site_name = domain.replace("www.", "")
            else:
                site_name = site_name.strip()

            # 4. Body Content extraction
            body_text = ""
            # Check content container selectors
            for sel in CONTENT_SELECTORS:
                container = page.locator(sel)
                if container.count() > 0:
                    # Get paragraph texts inside container
                    paragraphs = container.first.locator("p").all_inner_texts()
                    if paragraphs:
                        clean_paras = [p.strip() for p in paragraphs if len(p.strip()) > 20]
                        if len(clean_paras) >= 2:
                            body_text = " ".join(clean_paras)
                            break
                    # Fallback to inner_text of the container
                    text_candidate = container.first.inner_text().strip()
                    if len(text_candidate) > 100:
                        lines = [line.strip() for line in text_candidate.splitlines() if len(line.strip()) > 20]
                        body_text = " ".join(lines)
                        break

            # If still empty, fall back to meta description or all <p>
            if not body_text or len(body_text) < 50:
                meta_desc = page.locator("meta[name='description']").get_attribute("content")
                if not meta_desc:
                    meta_desc = page.locator("meta[property='og:description']").get_attribute("content")
                if meta_desc and len(meta_desc.strip()) > 30:
                    body_text = meta_desc.strip()
                else:
                    all_p = page.locator("p").all_inner_texts()
                    clean_all_p = [p.strip() for p in all_p if len(p.strip()) > 25]
                    body_text = " ".join(clean_all_p[:6])

            # Normalize whitespace
            body_text = re.sub(r'\s+', ' ', body_text).strip()

            # Create clean summary (e.g. 200~350 chars max for newspaper presentation)
            summary = body_text
            if len(summary) > 400:
                # Find punctuation mark around 300~400 chars
                cut_idx = summary[:350].rfind(". ")
                if cut_idx > 150:
                    summary = summary[:cut_idx + 1]
                else:
                    summary = summary[:350] + "..."

            return {
                "title": title,
                "content": summary,
                "full_content": body_text,
                "url": url,
                "image_url": image_url,
                "source": site_name,
                "is_crawled": True
            }

        except PlaywrightTimeoutError:
            logger.warning(f"Timeout while crawling {url}")
            return None
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return None
        finally:
            try:
                page.close()
                context.close()
            except Exception:
                pass

    def crawl_urls_batch(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Crawls a list of URLs and returns successful article items."""
        results = []
        for url in urls:
            item = self.crawl_url(url)
            if item and item.get("title") and len(item.get("content", "")) > 20:
                results.append(item)
        return results
