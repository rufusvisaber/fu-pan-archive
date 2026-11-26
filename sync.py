#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短线复盘 GitHub Pages 同步脚本
用法：
  python sync.py            # 复制复盘 + 重建列表页 + git 提交推送
  python sync.py --no-push  # 只更新本地文件，不推送
"""
import os
import re
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parent / "work"
POSTS = HERE / "posts"
INDEX = HERE / "index.html"
PATTERN = re.compile(r"^duanxian-fupan-(\d{8})\.html$")
WEEKDAYS = ["一", "二", "三", "四", "五", "六", "日"]

PUSH = "--no-push" not in sys.argv


def extract_meta(path):
    """从复盘 HTML 提取 title 与 subtitle"""
    html = path.read_text(encoding="utf-8", errors="ignore")
    title_m = re.search(r"<title>(.*?)</title>", html, re.S)
    sub_m = re.search(r'<div class="subtitle">(.*?)</div>', html, re.S)
    title = title_m.group(1).strip() if title_m else "短线交易复盘"
    subtitle = ""
    if sub_m:
        subtitle = re.sub(r"<[^>]+>", "", sub_m.group(1))
        subtitle = re.sub(r"\s+", " ", subtitle).strip()
    return title, subtitle


def copy_posts():
    copied = []
    for src in sorted(WORK.glob("duanxian-fupan-*.html")):
        m = PATTERN.match(src.name)
        if not m:
            continue
        dst = POSTS / src.name
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dst)
        copied.append((m.group(1), dst))
    return copied


def build_index(entries):
    """entries: list of (date_str, path)"""
    items = []
    for date_str, path in entries:
        try:
            dt = datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            continue
        title, subtitle = extract_meta(path)
        items.append({
            "date": date_str,
            "dt": dt,
            "weekday": WEEKDAYS[dt.weekday()],
            "ym": dt.strftime("%Y 年 %m 月"),
            "display": dt.strftime("%m.%d"),
            "year": dt.strftime("%Y"),
            "title": title,
            "subtitle": subtitle,
            "href": "posts/" + path.name,
        })
    items.sort(key=lambda x: x["date"], reverse=True)

    groups = {}
    for it in items:
        groups.setdefault(it["ym"], []).append(it)

    total = len(items)
    first = items[-1]["display"] if items else "-"
    last = items[0]["display"] if items else "-"
    latest = items[0] if items else None

    group_html = []
    for ym, rows in groups.items():
        cards = []
        for r in rows:
            is_latest = latest and r["date"] == latest["date"]
            badge = '<span class="tag tag-danger">最新</span>' if is_latest else ""
            sub = r["subtitle"] or "A 股短线复盘"
            if len(sub) > 90:
                sub = sub[:90] + "…"
            cards.append(f'''      <a class="card" href="{r['href']}" target="_blank" rel="noopener">
        <div class="card-date">
          <span class="day">{r['display']}</span>
          <span class="week">周{r['weekday']}</span>
        </div>
        <div class="card-body">
          <div class="card-title">{r['title']} {badge}</div>
          <div class="card-sub">{sub}</div>
        </div>
        <div class="card-arrow">→</div>
      </a>''')
        group_html.append(f'''    <section class="group">
      <h2 class="group-title"><span class="group-dot"></span>{ym}<span class="group-count">{len(rows)} 篇</span></h2>
      <div class="cards">
{chr(10).join(cards)}
      </div>
    </section>''')

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>短线交易复盘 · 归档</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, "Microsoft YaHei", "PingFang SC", sans-serif;
    background: #f0f2f5; color: #1a1a2e; line-height: 1.6; padding-bottom: 60px;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 0 20px; }}
  .header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: #fff; padding: 40px 36px; border-radius: 0 0 20px 20px;
    position: relative; overflow: hidden;
  }}
  .header::after {{
    content: ''; position: absolute; top: 0; right: 0; width: 320px; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(230,57,70,0.18));
  }}
  .header h1 {{ font-size: 30px; font-weight: 800; letter-spacing: 1px; position: relative; z-index: 1; }}
  .header .subtitle {{ font-size: 14px; color: #a0aec0; margin-top: 8px; position: relative; z-index: 1; }}
  .header .meta {{ display: flex; gap: 10px; margin-top: 18px; flex-wrap: wrap; position: relative; z-index: 1; }}
  .meta-item {{
    background: rgba(255,255,255,0.08); padding: 6px 16px; border-radius: 20px;
    font-size: 13px; color: #cbd5e0;
  }}
  .meta-item span {{ color: #e63946; font-weight: 700; }}

  .toolbar {{
    background: #fff; margin: 24px 0 8px; padding: 16px 20px; border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); display: flex; gap: 14px;
    align-items: center; flex-wrap: wrap;
  }}
  .search {{
    flex: 1; min-width: 240px; padding: 10px 16px; border: 2px solid #eef0f3;
    border-radius: 10px; font-size: 14px; outline: none; transition: border-color .2s;
  }}
  .search:focus {{ border-color: #e63946; }}
  .filter-btns {{ display: flex; gap: 8px; flex-wrap: wrap; }}
  .filter-btn {{
    padding: 8px 16px; border: 1.5px solid #e2e8f0; border-radius: 8px;
    background: #fff; color: #4a5568; font-size: 13px; cursor: pointer;
    font-weight: 600; transition: all .2s;
  }}
  .filter-btn:hover {{ border-color: #e63946; color: #e63946; }}
  .filter-btn.active {{ background: #e63946; color: #fff; border-color: #e63946; }}

  .group {{ margin-top: 28px; }}
  .group-title {{
    font-size: 17px; font-weight: 700; color: #2c3e50; margin-bottom: 12px;
    display: flex; align-items: center; gap: 10px;
  }}
  .group-dot {{ width: 6px; height: 20px; background: #e63946; border-radius: 3px; }}
  .group-count {{ font-size: 12px; color: #999; font-weight: 400; margin-left: 6px; }}
  .cards {{ display: flex; flex-direction: column; gap: 10px; }}

  .card {{
    background: #fff; border-radius: 12px; padding: 16px 20px;
    display: flex; align-items: center; gap: 18px; text-decoration: none;
    color: inherit; box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    border-left: 4px solid #e63946; transition: transform .15s, box-shadow .15s;
  }}
  .card:hover {{ transform: translateX(4px); box-shadow: 0 4px 18px rgba(230,57,70,0.15); }}
  .card-date {{ min-width: 76px; text-align: center; }}
  .card-date .day {{ display: block; font-size: 20px; font-weight: 800; color: #1a1a2e; }}
  .card-date .week {{ display: block; font-size: 12px; color: #999; margin-top: 2px; }}
  .card-body {{ flex: 1; min-width: 0; }}
  .card-title {{ font-size: 15px; font-weight: 700; color: #1a1a2e; margin-bottom: 4px; }}
  .card-sub {{
    font-size: 12px; color: #718096;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }}
  .card-arrow {{ font-size: 22px; color: #e63946; font-weight: 700; }}
  .tag {{
    display: inline-block; padding: 1px 8px; border-radius: 8px; font-size: 11px;
    font-weight: 600; vertical-align: middle;
  }}
  .tag-danger {{ background: #c0392b; color: #fff; }}

  .empty {{ text-align: center; padding: 60px 20px; color: #999; display: none; }}
  .footer {{ text-align: center; color: #a0aec0; font-size: 12px; margin-top: 40px; }}

  @media (max-width: 640px) {{
    .header {{ padding: 28px 22px; border-radius: 0 0 16px 16px; }}
    .header h1 {{ font-size: 23px; }}
    .card {{ padding: 14px; gap: 12px; }}
    .card-date {{ min-width: 58px; }}
    .card-date .day {{ font-size: 17px; }}
    .card-sub {{ white-space: normal; }}
  }}
</style>
</head>
<body>
  <div class="header">
    <div class="container" style="padding:0">
      <h1>短线交易复盘 · 归档</h1>
      <div class="subtitle">每日复盘按日期归档，点击任意一条查看完整内容</div>
      <div class="meta">
        <div class="meta-item">共 <span>{total}</span> 篇</div>
        <div class="meta-item">跨度 <span>{first} — {last}</span></div>
        <div class="meta-item">更新于 <span>{datetime.now().strftime('%Y-%m-%d %H:%M')}</span></div>
      </div>
    </div>
  </div>

  <div class="container">
    <div class="toolbar">
      <input class="search" id="search" type="text" placeholder="搜索日期或关键词，如 2026.11.26 或 机器人…">
      <div class="filter-btns">
        <button class="filter-btn active" data-year="all">全部</button>
        <button class="filter-btn" data-year="2026">2026</button>
      </div>
    </div>

    <div id="content">
{chr(10).join(group_html)}
    </div>
    <div class="empty" id="empty">没有匹配的复盘</div>
    <div class="footer">短线交易复盘框架 · 自动生成于每日收盘后</div>
  </div>

<script>
(function() {{
  var search = document.getElementById('search');
  var cards = Array.prototype.slice.call(document.querySelectorAll('.card'));
  var groups = Array.prototype.slice.call(document.querySelectorAll('.group'));
  var empty = document.getElementById('empty');
  var buttons = Array.prototype.slice.call(document.querySelectorAll('.filter-btn'));
  var activeYear = 'all';

  function apply() {{
    var q = search.value.trim().toLowerCase();
    var shown = 0;
    cards.forEach(function(c) {{
      var text = c.textContent.toLowerCase();
      var href = c.getAttribute('href');
      var yearOk = activeYear === 'all' || href.indexOf(activeYear) !== -1;
      var ok = yearOk && (q === '' || text.indexOf(q) !== -1);
      c.style.display = ok ? '' : 'none';
      if (ok) shown++;
    }});
    groups.forEach(function(g) {{
      var any = Array.prototype.slice.call(g.querySelectorAll('.card')).some(function(c) {{
        return c.style.display !== 'none';
      }});
      g.style.display = any ? '' : 'none';
    }});
    empty.style.display = shown === 0 ? 'block' : 'none';
  }}

  search.addEventListener('input', apply);
  buttons.forEach(function(b) {{
    b.addEventListener('click', function() {{
      buttons.forEach(function(x) {{ x.classList.remove('active'); }});
      b.classList.add('active');
      activeYear = b.getAttribute('data-year');
      apply();
    }});
  }});
}})();
</script>
</body>
</html>
'''
    INDEX.write_text(html, encoding="utf-8")


def git(*args):
    return subprocess.run(["git", *args], cwd=HERE, check=True,
                          capture_output=True, text=True).stdout.strip()


def main():
    POSTS.mkdir(parents=True, exist_ok=True)
    entries = copy_posts()
    build_index(entries)
    print(f"[sync] 站点已更新：{len(entries)} 篇复盘 -> {INDEX}")

    if not PUSH:
        print("[sync] --no-push，跳过 git 操作")
        return

    git("add", "-A")
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=HERE)
    if diff.returncode == 0:
        print("[sync] 无变更，跳过提交")
        return
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    git("commit", "-m", f"同步复盘归档 {stamp}")
    print("[sync] 已提交")
    out = git("push", "origin", "HEAD")
    if out:
        print(out)
    print("[sync] 已推送到 GitHub")


if __name__ == "__main__":
    main()
