"""
Newspaper Generator.
Renders articles into a high-fidelity newspaper HTML page using Jinja2,
matching the layout and styling from the reference images.
"""
import shutil
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from config import (
    TEMPLATES_DIR,
    OUTPUT_DIR,
    NEWSPAPER_NAME,
    NEWSPAPER_EDITION,
    NEWSPAPER_PUBLISHER
)

KST = timezone(timedelta(hours=9))


class NewspaperGenerator:
    def __init__(self, template_dir: Path = TEMPLATES_DIR, output_dir: Path = OUTPUT_DIR):
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=True)

    def balance_remaining_into_columns(self, remaining: List[Dict[str, Any]]):
        """Groups remaining articles by category and balances into left and right columns."""
        if not remaining:
            return [], []

        category_map: Dict[str, List[Dict[str, Any]]] = {}
        preferred_order = ["AI/ML", "데이터", "보안", "기타"]

        for item in remaining:
            cat = item.get("category", "기타")
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append(item)

        total_remaining = len(remaining)
        target_half = (total_remaining + 1) // 2

        left_groups: List[Dict[str, Any]] = []
        right_groups: List[Dict[str, Any]] = []

        all_cats = list(category_map.keys())
        all_cats.sort(key=lambda c: preferred_order.index(c) if c in preferred_order else 99)

        current_left_count = 0

        for cat in all_cats:
            items = category_map[cat]
            if current_left_count < target_half:
                needed = target_half - current_left_count
                if len(items) <= needed or (len(items) - needed) < 2:
                    left_groups.append({"category": cat, "articles": items})
                    current_left_count += len(items)
                else:
                    # Split this large category across both columns
                    left_items = items[:needed]
                    right_items = items[needed:]
                    left_groups.append({"category": cat, "articles": left_items})
                    current_left_count += len(left_items)
                    right_groups.append({"category": None, "articles": right_items})  # continuation
            else:
                right_groups.append({"category": cat, "articles": items})

        return left_groups, right_groups

    def organize_articles(self, articles: List[Dict[str, Any]]):
        """Fallback organizer if pre-curation was not used."""
        if not articles:
            return None, [], [], []

        with_images = [a for a in articles if a.get("image_url")]
        without_images = [a for a in articles if not a.get("image_url")]
        sorted_articles = with_images + without_images

        hero_article = sorted_articles[0]
        remaining = sorted_articles[1:]

        featured_articles = remaining[:2]
        remaining = remaining[2:]

        left_groups, right_groups = self.balance_remaining_into_columns(remaining)
        return hero_article, featured_articles, left_groups, right_groups

    def generate(
        self,
        articles: Optional[List[Dict[str, Any]]] = None,
        hero_article: Optional[Dict[str, Any]] = None,
        featured_articles: Optional[List[Dict[str, Any]]] = None,
        remaining_articles: Optional[List[Dict[str, Any]]] = None,
        target_date: Optional[datetime] = None,
        custom_name: Optional[str] = None,
        custom_edition: Optional[str] = None,
        custom_publisher: Optional[str] = None
    ) -> Path:
        """
        Generates the newspaper HTML file and returns the output path.
        Accepts either pre-curated (hero, featured, remaining) or a flat articles list.
        """
        if target_date is None:
            now_kst = datetime.now(KST)
        else:
            now_kst = target_date.astimezone(KST) if target_date.tzinfo else target_date.replace(tzinfo=KST)

        date_str = now_kst.strftime("%Y-%m-%d")
        newspaper_name = custom_name or NEWSPAPER_NAME
        newspaper_edition = custom_edition or NEWSPAPER_EDITION
        newspaper_publisher = custom_publisher or NEWSPAPER_PUBLISHER

        # If curated parts are provided
        if hero_article is not None:
            hero = hero_article
            featured = featured_articles or []
            remaining = remaining_articles or []
            left_groups, right_groups = self.balance_remaining_into_columns(remaining)
            total_count = (1 if hero else 0) + len(featured) + len(remaining)
        elif articles:
            hero, featured, left_groups, right_groups = self.organize_articles(articles)
            total_count = len(articles)
        else:
            hero, featured, left_groups, right_groups = None, [], [], []
            total_count = 0

        template = self.env.get_template("newspaper.html")
        rendered_html = template.render(
            newspaper_name=newspaper_name,
            newspaper_edition=newspaper_edition,
            newspaper_publisher=newspaper_publisher,
            date_str=date_str,
            generated_at=now_kst.strftime("%Y-%m-%d %H:%M:%S"),
            total_articles=total_count,
            hero_article=hero,
            featured_articles=featured,
            left_groups=left_groups,
            right_groups=right_groups
        )

        # Primary Output: Output/YYYY-MM-DD.html (e.g. Output/2026-10-19.html)
        primary_filename = f"{date_str}.html"
        primary_output_path = self.output_dir / primary_filename
        with open(primary_output_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        # Compatibility files: Output/newspaper_YYYY-MM-DD.html and Output/index.html
        compat_path = self.output_dir / f"newspaper_{date_str}.html"
        with open(compat_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        index_path = self.output_dir / "index.html"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        return primary_output_path
