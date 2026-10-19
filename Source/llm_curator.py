"""
LLM Article Curator Module.
Uses Google Gemini API to analyze daily articles, ranking importance:
1. Selects 1 Main Headline (Hero) article (1-column wide, largest emphasis).
2. Selects 2 Sub-Headline (Featured) articles (2-column, ~1/2 size of hero).
3. Summarizes remaining articles into concise 2-3 sentences with category classification.
Provides a robust heuristic fallback if Gemini API is unavailable or times out.
"""
import json
import logging
import re
import requests
from typing import List, Dict, Any, Tuple, Optional
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-3.8-flash"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

FALLBACK_CATEGORY_KEYWORDS = {
    "AI/ML": [
        "ai", "인공지능", "gpt", "llm", "claude", "클로드", "제미니", "gemini",
        "openai", "오픈ai", "anthropic", "앤트로픽", "프롬프트", "머신러닝", "딥러닝",
        "에이전트", "agent", "파운데이션", "트랜스포머", "라마", "llama", "엔비디아", "nvidia",
        "휴머노이드", "로봇", "사고 사슬", "cot", "생성형", "추론"
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


def fallback_classify_category(text: str) -> str:
    """Keyword-based category classification."""
    lower_text = text.lower()
    for cat, keywords in FALLBACK_CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in lower_text:
                return cat
    return "기타"


def score_article_heuristically(article: Dict[str, Any]) -> float:
    """Heuristic scoring based on presence of image, length, and hot keywords."""
    score = 0.0
    title = article.get("title", "")
    content = article.get("content", "") or article.get("full_content", "")
    full_text = f"{title} {content}".lower()

    # Image bonus
    if article.get("image_url"):
        score += 30.0

    # Content length bonus (adequate length means more comprehensive news)
    length = len(content)
    if length > 200:
        score += min(20.0, length / 20.0)

    # Hot topic keywords
    hot_keywords = [
        "제미니", "gpt", "클로드", "openai", "claude", "gemini",
        "공개", "출시", "발표", "돌파", "에이전트", "특화", "신규", "혁신"
    ]
    for kw in hot_keywords:
        if kw in full_text:
            score += 8.0

    return score


class LLMCurator:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key

    def curate_articles(self, articles: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Curates articles into:
        1. hero_article (1 item)
        2. featured_articles (up to 2 items)
        3. remaining_articles (summarized and categorized)
        """
        if not articles:
            return None, [], []

        # Try Gemini API if key is available
        if self.api_key:
            try:
                curated = self._curate_with_gemini(articles)
                if curated:
                    return curated
            except Exception as e:
                logger.warning(f"Gemini API curation failed: {e}. Falling back to heuristic curation.")

        if len(articles) <= 3:
            return self._curate_small_set(articles)

        # Heuristic fallback
        return self._curate_heuristically(articles)

    def _curate_small_set(self, articles: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Handles cases where total articles <= 3 with clean titles."""
        sorted_articles = sorted(articles, key=score_article_heuristically, reverse=True)
        hero = dict(sorted_articles[0])
        featured = [dict(a) for a in sorted_articles[1:]]

        for a in [hero] + featured:
            if re.search(r'\d+[\s,]*likes', a.get("title", ""), re.I):
                lines = [l.strip().lstrip("•-*\"' ") for l in a.get("content", "").splitlines() if len(l.strip()) > 5]
                if lines:
                    a["title"] = lines[0][:60]
        return hero, featured, []

    def _curate_with_gemini(self, articles: List[Dict[str, Any]]) -> Optional[Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]]:
        """Invokes Google Gemini API to evaluate and structure the newspaper edition."""
        items_summary = []
        for idx, a in enumerate(articles):
            title = a.get("title", "")
            snippet = (a.get("content", "") or a.get("full_content", ""))[:300].replace("\n", " ")
            has_img = "O" if a.get("image_url") else "X"
            items_summary.append(f"[{idx}] 원제목: {title} | 이미지유무: {has_img} | 본문일부: {snippet}")

        articles_prompt = "\n".join(items_summary)

        system_instruction = (
            "당신은 최고 권위의 IT/시사/테크 전문 일간 신문 'Mars Tech Daily'의 수석 편집국장입니다.\n"
            "오늘 수집된 기사 목록을 분석하여 신문 1면의 레이아웃 구성을 확정하세요.\n\n"
            "선정 및 편집 기준:\n"
            "1. 'hero_index': 오늘 기사 중 독자들의 주목도가 가장 높고 파급력이 가장 큰 메인 헤드라인 기사 1개의 인덱스를 선정하세요. "
            "hero_title(정갈한 신문 헤드라인 제목)과 hero_summary(핵심 요약)도 함께 작성하세요.\n"
            "2. 'featured': 메인 기사 다음으로 중요하고 트렌디한 부 헤드라인 기사(최대 2개)를 선정하세요. 각 항목은 idx, title, summary를 포함합니다.\n"
            "3. 'remaining': 나머지 모든 기사에 대해 idx, category('AI/ML', '데이터', '보안', '문화/연예', '정치/사회', '기타' 중 택1), title, summary를 작성하세요.\n"
            "4. 중요: 원제목이 '2,679 likes...' 같은 인스타그램/SNS 메타 문구이거나 어색한 경우, 본문 내용에 걸맞은 매력적인 신문 기사 제목(title)으로 반드시 수정하세요.\n\n"
            "반드시 순수한 JSON 형식으로만 응답하세요. 다른 설명 텍스트는 일체 포함하지 마세요.\n"
            "JSON 형식 예시:\n"
            "{\n"
            '  "hero_index": 0,\n'
            '  "hero_title": "제미니 4 아르곤, 차세대 벤치마크 1위 탈환",\n'
            '  "hero_summary": "본문 요약...",\n'
            '  "featured": [\n'
            '    {"idx": 1, "title": "정제된 제목", "summary": "요약..."}\n'
            '  ],\n'
            '  "remaining": [\n'
            '    {"idx": 2, "category": "AI/ML", "title": "정제된 제목", "summary": "요약..."}\n'
            '  ]\n'
            "}"
        )

        user_prompt = f"다음은 오늘 수집된 기사 {len(articles)}건의 목록입니다:\n\n{articles_prompt}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_instruction}\n\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        }

        url = f"{GEMINI_ENDPOINT}?key={self.api_key}"
        logger.info(f"Requesting Gemini API curation for {len(articles)} articles...")
        response = requests.post(url, json=payload, timeout=25)

        if response.status_code != 200:
            logger.error(f"Gemini API returned status code {response.status_code}: {response.text[:200]}")
            return None

        res_json = response.json()
        candidates = res_json.get("candidates", [])
        if not candidates:
            return None

        content_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        if not content_text:
            return None

        # Clean JSON markdown fences if any
        clean_json_str = re.sub(r'^```json\s*|\s*```$', '', content_text.strip())
        data = json.loads(clean_json_str)

        hero_idx = data.get("hero_index")
        featured_list = data.get("featured", [])
        remaining_data = data.get("remaining", [])

        if hero_idx is None or hero_idx < 0 or hero_idx >= len(articles):
            return None

        hero_article = dict(articles[hero_idx])
        if data.get("hero_title"):
            hero_article["title"] = data["hero_title"]
        if data.get("hero_summary"):
            hero_article["content"] = data["hero_summary"]

        used_indices = {hero_idx}

        featured_articles = []
        for f_item in featured_list:
            f_idx = f_item.get("idx") if isinstance(f_item, dict) else f_item
            if f_idx is not None and 0 <= f_idx < len(articles) and f_idx not in used_indices:
                feat_copy = dict(articles[f_idx])
                if isinstance(f_item, dict):
                    if f_item.get("title"):
                        feat_copy["title"] = f_item["title"]
                    if f_item.get("summary"):
                        feat_copy["content"] = f_item["summary"]
                featured_articles.append(feat_copy)
                used_indices.add(f_idx)

        # Remaining articles
        remaining_articles = []
        remaining_map = {r.get("idx"): r for r in remaining_data if "idx" in r}

        for idx, art in enumerate(articles):
            if idx in used_indices:
                continue
            art_copy = dict(art)
            if idx in remaining_map:
                rem_info = remaining_map[idx]
                if rem_info.get("title"):
                    art_copy["title"] = rem_info["title"]
                if rem_info.get("summary"):
                    art_copy["content"] = rem_info["summary"]
                if rem_info.get("category"):
                    art_copy["category"] = rem_info["category"]
            else:
                art_copy["category"] = fallback_classify_category(f"{art.get('title')} {art.get('content')}")
            remaining_articles.append(art_copy)
        logger.info(
            f"Gemini curation completed successfully: "
            f"Hero='{hero_article.get('title')[:25]}...', "
            f"Featured={len(featured_articles)}, Remaining={len(remaining_articles)}"
        )
        return hero_article, featured_articles, remaining_articles

    def _curate_heuristically(self, articles: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Heuristic rule-based fallback curation."""
        logger.info("Applying heuristic curation algorithm...")
        scored = []
        for idx, a in enumerate(articles):
            s = score_article_heuristically(a)
            scored.append((s, idx, a))

        scored.sort(key=lambda x: x[0], reverse=True)

        hero_article = dict(scored[0][2])
        featured_articles = [dict(scored[1][2]), dict(scored[2][2])]

        remaining_articles = []
        for _, _, a in scored[3:]:
            art_copy = dict(a)
            text_for_cat = f"{art_copy.get('title', '')} {art_copy.get('content', '')}"
            art_copy["category"] = fallback_classify_category(text_for_cat)
            
            # Format concise summary (2~3 sentences, max 300 chars)
            content = art_copy.get("content", "")
            if len(content) > 300:
                cut_idx = content[:280].rfind(". ")
                if cut_idx > 120:
                    art_copy["content"] = content[:cut_idx + 1]
                else:
                    art_copy["content"] = content[:280] + "..."
            remaining_articles.append(art_copy)

        return hero_article, featured_articles, remaining_articles
