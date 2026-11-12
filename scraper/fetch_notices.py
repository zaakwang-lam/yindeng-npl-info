#!/usr/bin/env python3
"""抓取银登中心资产招商专区公告标题，并尽量抽出个人不良转让 PDF 链接。

只使用公开页面。默认慢速、只取前几页。字段抽取依赖可选的 pypdf，
抽不到就留空，不要手填。
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

LIST_URL = "https://www.yindeng.com.cn/ywzq/ywzq_bldkzr/bldkzr_zczszq/"
USER_AGENT = "digao-yindeng-scraper/0.1 (public notices; contact local operator)"

ITEM_RE = re.compile(
    r"href='(https://www\.yindeng\.com\.cn/ywzq/[^']+\.html)'"
    r"[\s\S]{0,500}?title='([^']+)'"
    r"[\s\S]{0,600}?rightListTime data-time\">\s*(\d{4}-\d{2}-\d{2})",
    re.I,
)
PDF_RE = re.compile(r"href='(https://www\.yindeng\.com\.cn/[^']+\.pdf)'", re.I)
PAGE_COUNT_RE = re.compile(r"createPageHTMLApp\(\s*(\d+)\s*,")

FIELD_RES = {
    "principal_yuan": r"未偿本金总额[（(]元[）)]\s*[：:]?\s*([0-9,，\.]+)",
    "interest_yuan": r"未偿利息总额[（(]元[）)]\s*[：:]?\s*([0-9,，\.]+)",
    "total_yuan": r"未偿本息总额[（(]元[）)]\s*[：:]?\s*([0-9,，\.]+)",
    "asset_count": r"资产笔数[（(]笔[）)]\s*[：:]?\s*([0-9,，]+)",
    "borrowers": r"借款人(?:户数|数量|数)?[（(]户[）)]\s*[：:]?\s*([0-9,，]+)",
    "overdue_days": r"加权平均逾期天数\s*[：:]?\s*([0-9,，\.]+)",
    "benchmark": r"交易基准日\s*[：:]?\s*([0-9]{4}[-年/][0-9]{1,2}[-月/][0-9]{1,2}日?)",
}


def fetch(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return raw.decode("utf-8", "replace")


def list_page_url(page: int, page_count: int) -> str:
    if page <= 1:
        return LIST_URL if LIST_URL.endswith("/") else LIST_URL + "/"
    index = page_count - page + 1
    return f"{LIST_URL}index_{index}.html"


def parse_list(html: str) -> list[dict]:
    items = []
    seen = set()
    for url, title, date in ITEM_RE.findall(html):
        title = unescape(re.sub(r"\s+", " ", title)).strip()
        if url in seen:
            continue
        seen.add(url)
        items.append({"date": date, "title": title, "url": url, "personal": "个人" in title})
    return items


def page_count_of(html: str) -> int:
    match = PAGE_COUNT_RE.search(html)
    return int(match.group(1)) if match else 1


def pdf_links(html: str) -> list[str]:
    return list(dict.fromkeys(PDF_RE.findall(html)))


def pdf_text(url: str) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=40) as resp:
        data = resp.read()
    reader = PdfReader(stream=__import__("io").BytesIO(data))
    parts = []
    for page in reader.pages[:8]:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def extract_fields(text: str) -> dict:
    found = {}
    if not text:
        return found
    compact = text.replace(" ", "").replace("\n", "")
    for key, pattern in FIELD_RES.items():
        match = re.search(pattern, compact)
        if match:
            found[key] = match.group(1).replace("，", "").replace(",", "")
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description="抓取银登个人不良转让公开公告")
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--sleep", type=float, default=1.2)
    parser.add_argument("--details", type=int, default=8)
    parser.add_argument("--all-types", action="store_true")
    parser.add_argument("--out", default="data/notices.json")
    args = parser.parse_args()

    first = fetch(LIST_URL)
    total_pages = page_count_of(first)
    pages = max(1, min(args.pages, total_pages))
    collected = parse_list(first)
    for page in range(2, pages + 1):
        time.sleep(args.sleep)
        url = list_page_url(page, total_pages)
        try:
            html = fetch(url)
        except urllib.error.URLError as exc:
            print(f"skip {url}: {exc}")
            continue
        collected.extend(parse_list(html))

    dedup = []
    seen = set()
    for item in collected:
        if item["url"] in seen:
            continue
        seen.add(item["url"])
        if not args.all_types and not item["personal"]:
            continue
        dedup.append(item)

    detailed = 0
    for item in dedup:
        if detailed >= args.details:
            item["pdfs"] = []
            item["fields"] = {}
            continue
        time.sleep(args.sleep)
        try:
            detail = fetch(item["url"])
        except urllib.error.URLError as exc:
            print(f"detail fail {item['url']}: {exc}")
            item["pdfs"] = []
            item["fields"] = {}
            continue
        item["pdfs"] = pdf_links(detail)
        fields = {}
        if item["pdfs"]:
            try:
                fields = extract_fields(pdf_text(item["pdfs"][0]))
            except Exception as exc:
                print(f"pdf fail {item['pdfs'][0]}: {exc}")
        item["fields"] = fields
        detailed += 1

    payload = {
        "source": LIST_URL,
        "page_count": total_pages,
        "note": "标题和链接来自公开列表。fields 只有 pypdf 抽到才有值，空对象表示未抽取。",
        "items": dedup,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out} count={len(dedup)}")


if __name__ == "__main__":
    main()
