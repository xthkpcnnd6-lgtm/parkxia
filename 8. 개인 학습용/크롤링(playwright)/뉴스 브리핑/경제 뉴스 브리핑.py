import os
import webbrowser
from playwright.sync_api import sync_playwright

# --- [환경 설정] ---
# 네이버 경제 뉴스 홈 (헤드라인 중심)
NEWS_URL = "https://news.naver.com/section/101" 
REPORT_FILE = "economy_news_report.html"
MAX_NEWS_COUNT = 12

def collect_economy_news():
    results = []
    try:
        with sync_playwright() as p:
            print(f"📰 최신 경제 뉴스 수집 중...")
            # 브라우저 실행 (새로운 구조 대응을 위해 설정 보강)
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # 페이지 접속 및 대기
            page.goto(NEWS_URL, wait_until="networkidle")
            
            # 최신 네이버 뉴스 섹션의 카드 구조 선택자
            # .sa_item_inner 는 뉴스 리스트의 개별 단위입니다.
            news_items = page.query_selector_all(".sa_item_inner")
            
            if not news_items:
                # 다른 구조(.as_headline_item) 시도 (네이버의 A/B 테스트 대응)
                news_items = page.query_selector_all(".as_headline_item")

            for item in news_items[:MAX_NEWS_COUNT]:
                try:
                    # 1. 제목 및 링크 (.sa_text_title 또는 a 태그)
                    title_el = item.query_selector(".sa_text_title") or item.query_selector("a")
                    if not title_el: continue
                    
                    title = title_el.inner_text().strip()
                    link = title_el.get_attribute("href")
                    
                    # 2. 언론사
                    press_el = item.query_selector(".sa_text_press")
                    press = press_el.inner_text().strip() if press_el else "경제 뉴스"
                    
                    # 3. 요약 (내용이 없을 경우 대비)
                    summary_el = item.query_selector(".sa_text_lede")
                    summary = summary_el.inner_text().strip() if summary_el else "클릭하여 상세 내용을 확인하세요."
                    
                    if title and link:
                        results.append({
                            "title": title,
                            "press": press,
                            "summary": summary,
                            "link": link
                        })
                except Exception as e:
                    continue
            
            browser.close()
            
            if results:
                generate_news_html(results)
            else:
                print("❌ 뉴스 데이터를 찾지 못했습니다. 선택자를 점검해야 합니다.")
                # 디버깅용: 현재 페이지 소스 일부 출력 가능
                
                
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def generate_news_html(data):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>경제 뉴스 리포트</title>
        <style>
            body {{ font-family: 'Pretendard', 'Malgun Gothic', sans-serif; background-color: #f8f9fa; padding: 20px; line-height: 1.6; }}
            .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 40px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            h1 {{ color: #111; font-size: 24px; font-weight: 800; border-left: 5px solid #0055fb; padding-left: 15px; margin-bottom: 30px; }}
            .news-item {{ margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid #f1f3f5; }}
            .news-item:last-child {{ border-bottom: none; }}
            .press {{ font-size: 13px; color: #0055fb; font-weight: bold; margin-bottom: 8px; display: block; }}
            .title {{ font-size: 18px; font-weight: bold; color: #222; text-decoration: none; display: block; margin-bottom: 10px; transition: 0.2s; }}
            .title:hover {{ color: #0055fb; }}
            .summary {{ font-size: 14px; color: #666; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
            .btn-box {{ margin-top: 40px; text-align: center; }}
            .date {{ font-size: 12px; color: #adb5bd; margin-top: 50px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>오늘의 경제 주요 브리핑</h1>
    """
    
    for item in data:
        html_content += f"""
            <div class="news-item">
                <span class="press">{item['press']}</span>
                <a href="{item['link']}" class="title" target="_blank">{item['title']}</a>
                <p class="summary">{item['summary']}</p>
            </div>
        """
            
    html_content += f"""
            <div class="date">수집 시각: {time_stamp()}</div>
        </div>
    </body>
    </html>
    """
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ 리포트가 성공적으로 생성되었습니다: {REPORT_FILE}")
    webbrowser.open("file://" + os.path.abspath(REPORT_FILE))

def time_stamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    collect_economy_news()