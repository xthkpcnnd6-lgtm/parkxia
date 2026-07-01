## 코스피 등락률 3퍼센트 이상 종목 필터 크롤링

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
MIN_PRICE = 15000       # 1.5만 원 이상
MIN_CHANGE_RATE = 3.0    # +3.0% 이상
REPORT_FILE = "kospi_surging_stocks.html"

def collect_surging_stocks():
    results = []
    try:
        with sync_playwright() as p:
            print(f"📊 코스피 급등 대형주(가격 {MIN_PRICE:,}원↑, 등락 {MIN_CHANGE_RATE}%↑) 분석 중...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0")
            page = context.new_page()
            
            # 네이버 증권 코스피 시가총액 페이지 (상위 50위)
            url = "https://finance.naver.com/sise/sise_market_sum.naver?sosok=0&page=1"
            page.goto(url, wait_until="domcontentloaded")
            
            rows = page.query_selector_all("table.type_2 tbody tr")
            
            for row in rows:
                try:
                    tds = row.query_selector_all("td")
                    if len(tds) < 10: continue # 데이터가 없는 빈 줄 건너뛰기
                    
                    # 1. 종목명 및 링크 추출
                    name_el = tds[1].query_selector("a.tltle")
                    if not name_el: continue
                    name = name_el.inner_text().strip()
                    
                    # 2. 현재가 추출 및 숫자 변환
                    price_raw = tds[2].inner_text().strip()
                    price = int(re.sub(r'[^0-9]', '', price_raw))
                    
                    # 3. 등락률 추출 및 숫자 변환 (핵심!)
                    change_raw = tds[4].inner_text().strip() # 5번째 칸이 등락률
                    # '+', '-', '%' 제거하고 실수(float)로 변환
                    change_val = float(re.sub(r'[^0-9.-]', '', change_raw)) 
                    
                    # --- [복합 필터링 로직] ---
                    # 가격이 10만원 이상이고 등락률이 5.0% 이상인 경우만 수집
                    if price >= MIN_PRICE and change_val >= MIN_CHANGE_RATE:
                        link = "https://finance.naver.com" + name_el.get_attribute("href")
                        results.append({
                            "name": name,
                            "price": f"{price:,}원",
                            "change": f"{change_val:+}%", # 기호를 붙여서 표시
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
        <title>급등 대형주 리포트</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; background-color: #fff5f5; padding: 30px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(217,48,37,0.1); }}
            h1 {{ color: #d93025; border-bottom: 3px solid #d93025; padding-bottom: 10px; margin-bottom: 5px; }}
            .subtitle {{ color: #666; margin-bottom: 25px; font-size: 0.9rem; }}
            .stock-card {{ display: flex; justify-content: space-between; align-items: center; border: 1px solid #ffebeb; padding: 15px; margin-bottom: 10px; border-radius: 10px; transition: 0.2s; }}
            .stock-card:hover {{ background-color: #fff8f8; border-color: #ffcfcf; }}
            .name {{ font-size: 1.15rem; font-weight: bold; color: #222; }}
            .price {{ font-size: 1.3rem; font-weight: 800; color: #d93025; }}
            .change-badge {{ display: inline-block; padding: 4px 10px; background: #d93025; color: white; border-radius: 20px; font-size: 0.85rem; font-weight: bold; margin-top: 5px; }}
            .link-btn {{ text-decoration: none; color: #555; font-size: 0.8rem; border: 1px solid #ccc; padding: 3px 8px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔥 급등 대형주 포착</h1>
            <div class="subtitle">가격 {MIN_PRICE:,}원 ↑ & 등락률 {MIN_CHANGE_RATE}% ↑ 기준</div>
    """
    if not data:
        html_content += "<p style='text-align:center; padding: 50px; color:#888;'>현재 조건에 맞는 종목이 없습니다. 📊</p>"
    else:
        for item in data:
            html_content += f"""
                <div class="stock-card">
                    <div>
                        <div class="name">{item['name']}</div>
                        <a href="{item['link']}" class="link-btn" target="_blank">차트 보기</a>
                    </div>
                    <div style="text-align: right;">
                        <div class="price">{item['price']}</div>
                        <div class="change-badge">{item['change']}</div>
                    </div>
                </div>
            """
    html_content += "</div></body></html>"
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    webbrowser.open("file://" + os.path.abspath(REPORT_FILE))

if __name__ == "__main__":
    collect_surging_stocks()