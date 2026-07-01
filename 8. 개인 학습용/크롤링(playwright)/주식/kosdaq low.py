import os
import sys
import time
import re
import webbrowser
from playwright.sync_api import sync_playwright
# 필수 라이브러리
# python -m pip install flask playwright
# python -m playwright install chromium
# python -m pip install flask playwright

# --- [환경 설정] ---
MIN_PRICE = 0              # 가격 제한 없음
DROP_THRESHOLD = -1.5      # -1.5% 이하로 하락한 종목 (예: -2.0%, -3.5% 등)
REPORT_FILE = "kosdaq_drop_report.html"

def collect_kosdaq_drop_stocks():
    results = []
    try:
        with sync_playwright() as p:
            print(f"📊 코스닥 하락주(등락률 {DROP_THRESHOLD}% 이하) 분석 중...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0")
            page = context.new_page()
            
            # 네이버 증권 코스닥 시가총액 페이지 (sosok=1: 코스닥)
            url = "https://finance.naver.com/sise/sise_market_sum.naver?sosok=1&page=1"
            page.goto(url, wait_until="domcontentloaded")
            
            rows = page.query_selector_all("table.type_2 tbody tr")
            
            for row in rows:
                try:
                    tds = row.query_selector_all("td")
                    if len(tds) < 10: continue 
                    
                    # 1. 종목명 및 링크
                    name_el = tds[1].query_selector("a.tltle")
                    if not name_el: continue
                    name = name_el.inner_text().strip()
                    
                    # 2. 현재가
                    price_raw = tds[2].inner_text().strip()
                    price = int(re.sub(r'[^0-9]', '', price_raw))
                    
                    # 3. 등락률 추출 및 숫자 변환
                    change_raw = tds[4].inner_text().strip()
                    change_val = float(re.sub(r'[^0-9.-]', '', change_raw)) 
                    
                    # --- [하락 필터링 로직] ---
                    # -1.5보다 더 작거나 같은(더 많이 떨어진) 경우
                    if change_val <= DROP_THRESHOLD:
                        link = "https://finance.naver.com" + name_el.get_attribute("href")
                        results.append({
                            "name": name,
                            "price": f"{price:,}원",
                            "change": f"{change_val:.2f}%",
                            "link": link
                        })
                except Exception: continue
            
            browser.close()
            generate_html(results)
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def generate_html(data):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>코스닥 하락 종목 리포트</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; background-color: #f4f7f9; padding: 30px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(26,115,232,0.1); }}
            h1 {{ color: #1a73e8; border-bottom: 3px solid #1a73e8; padding-bottom: 10px; margin-bottom: 5px; }}
            .subtitle {{ color: #666; margin-bottom: 25px; font-size: 0.9rem; }}
            .stock-card {{ display: flex; justify-content: space-between; align-items: center; border: 1px solid #e1e8ed; padding: 15px; margin-bottom: 10px; border-radius: 10px; transition: 0.2s; }}
            .stock-card:hover {{ background-color: #f0f7ff; border-color: #adc6ff; }}
            .name {{ font-size: 1.15rem; font-weight: bold; color: #222; }}
            .price {{ font-size: 1.3rem; font-weight: 800; color: #1a73e8; }}
            .drop-badge {{ display: inline-block; padding: 4px 10px; background: #1a73e8; color: white; border-radius: 20px; font-size: 0.85rem; font-weight: bold; margin-top: 5px; }}
            .link-btn {{ text-decoration: none; color: #555; font-size: 0.8rem; border: 1px solid #ccc; padding: 3px 8px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📉 KOSDAQ 하락 종목</h1>
            <div class="subtitle">등락률 {DROP_THRESHOLD}% 이하 종목 리스트</div>
    """
    if not data:
        html_content += "<p style='text-align:center; padding: 50px; color:#888;'>해당 조건만큼 하락한 종목이 없습니다. ☁️</p>"
    else:
        for item in data:
            html_content += f"""
                <div class="stock-card">
                    <div>
                        <div class="name">{item['name']}</div>
                        <a href="{item['link']}" class="link-btn" target="_blank">종목 분석 보기</a>
                    </div>
                    <div style="text-align: right;">
                        <div class="price">{item['price']}</div>
                        <div class="drop-badge">{item['change']}</div>
                    </div>
                </div>
            """
    html_content += "</div></body></html>"
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    webbrowser.open("file://" + os.path.abspath(REPORT_FILE))

if __name__ == "__main__":
    collect_kosdaq_drop_stocks()