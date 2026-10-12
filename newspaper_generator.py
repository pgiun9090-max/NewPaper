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

    def organize_articles(self, articles: List[Dict[str, Any]]):
        """
        Organizes articles into:
        1. hero_article (1 item)
        2. featured_articles (up to 2 items)
        3. left_column_groups & right_column_groups (balanced columns)
        """
        if not articles:
            return None, [], [], []

        # Prioritize articles with images for Hero and Featured
        with_images = [a for a in articles if a.get("image_url")]
        without_images = [a for a in articles if not a.get("image_url")]
        sorted_articles = with_images + without_images

        # 1. Hero
        hero_article = sorted_articles[0]
        remaining = sorted_articles[1:]

        # 2. Featured (up to 2 items)
        featured_articles = remaining[:2]
        remaining = remaining[2:]

        # 3. Group remaining by category
        category_map: Dict[str, List[Dict[str, Any]]] = {}
        preferred_order = ["AI/ML", "데이터", "보안", "기타"]

        for item in remaining:
            cat = item.get("category", "기타")
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append(item)

        # Build list of sections/groups
        # If a category has many items (e.g. > 4), we can split it to balance columns
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

        return hero_article, featured_articles, left_groups, right_groups

    def generate(
        self,
        articles: List[Dict[str, Any]],
        target_date: Optional[datetime] = None,
        custom_name: Optional[str] = None,
        custom_edition: Optional[str] = None,
        custom_publisher: Optional[str] = None
    ) -> Path:
        """
        Generates the newspaper HTML file and returns the output path.
        """
        if target_date is None:
            now_kst = datetime.now(KST)
        else:
            now_kst = target_date.astimezone(KST) if target_date.tzinfo else target_date.replace(tzinfo=KST)

        date_str = now_kst.strftime("%Y-%m-%d")
        newspaper_name = custom_name or NEWSPAPER_NAME
        newspaper_edition = custom_edition or NEWSPAPER_EDITION
        newspaper_publisher = custom_publisher or NEWSPAPER_PUBLISHER

        hero, featured, left_groups, right_groups = self.organize_articles(articles)

        template = self.env.get_template("newspaper.html")
        rendered_html = template.render(
            newspaper_name=newspaper_name,
            newspaper_edition=newspaper_edition,
            newspaper_publisher=newspaper_publisher,
            date_str=date_str,
            generated_at=now_kst.strftime("%Y-%m-%d %H:%M:%S"),
            total_articles=len(articles),
            hero_article=hero,
            featured_articles=featured,
            left_groups=left_groups,
            right_groups=right_groups
        )

        # Save to dated output file
        filename = f"newspaper_{date_str}.html"
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        # Also copy/save to index.html for quick browsing
        index_path = self.output_dir / "index.html"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        return output_path
