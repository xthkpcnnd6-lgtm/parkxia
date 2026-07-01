# 🖼️ 올리브영 사진 포함 로컬 분석 리포터
# Project: OliveYoung Visual Report v1.0
# Feature: 상품 이미지 수집 -> HTML 파일 저장 -> 웹 브라우저로 즉시 실행

# 필수 라이브러리
# python -m pip install flask playwright
# python -m playwright install chromium
# python -m pip install flask playwright


import os
import sys
import time
import re
import webbrowser
from playwright.sync_api import sync_playwright

# --- [환경 설정] ---
SEARCH_KEYWORD = "넘버즈인"
MIN_PRICE = 15000
REPORT_FILE = "oliveyoung_visual_report.html"

def collect_and_save_visual():
    results = []
    try:
        with sync_playwright() as p:
            print(f"🔍 '{SEARCH_KEYWORD}' 이미지 및 데이터 수집 중...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # 1. 접속 및 검색
            page.goto("https://www.oliveyoung.co.kr/store/main/main.do", wait_until="domcontentloaded")
            page.fill("#query", SEARCH_KEYWORD)
            page.keyboard.press("Enter")
            
            # 2. 로딩 및 스크롤
            page.wait_for_selector(".prd_info", timeout=10000)
            page.mouse.wheel(0, 4000) # 이미지가 로드되도록 충분히 스크롤
            time.sleep(3)
            
            items = page.query_selector_all(".prd_info")
            
            for item in items:
                try:
                    # 가격 체크
                    price_el = item.query_selector(".tx_cur > .tx_num")
                    if not price_el: continue
                    price = int(re.sub(r'[^0-9]', '', price_text := price_el.inner_text().strip()))
                    
                    if price >= MIN_PRICE:
                        # 이미지 주소 추출 (Lazy loading 대응)
                        img_el = item.query_selector("img.thumb_img") or item.query_selector("img")
                        img_url = img_el.get_attribute("src") if img_el else ""
                        
                        brand = item.query_selector(".tx_brand").inner_text().strip() if item.query_selector(".tx_brand") else "BRAND"
                        name = item.query_selector(".tx_name").inner_text().strip() if item.query_selector(".tx_name") else "상품명"
                        
                        link_el = item.query_selector("a")
                        link = link_el.get_attribute("href") if link_el else ""
                        full_url = link if link.startswith("http") else f"https://www.oliveyoung.co.kr{link}"
                        
                        results.append({
                            "img": img_url,
                            "brand": brand,
                            "name": name,
                            "price": f"{price:,}원",
                            "link": full_url
                        })
                except Exception: continue
            
            browser.close()
            
            # 3. HTML 파일 생성
            generate_html(results)
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def generate_html(data):
    # HTML 템플릿 작성 (CSS 포함)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>{SEARCH_KEYWORD} 리포트</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            h1 {{ border-bottom: 3px solid #2ecc71; padding-bottom: 10px; color: #333; }}
            .item-box {{ display: flex; align-items: center; border-bottom: 1px solid #eee; padding: 15px 0; }}
            .item-img {{ width: 120px; height: 120px; border-radius: 10px; object-fit: cover; margin-right: 20px; border: 1px solid #ddd; }}
            .item-info {{ flex: 1; }}
            .brand {{ font-size: 0.85rem; color: #888; font-weight: bold; }}
            .name {{ font-size: 1.1rem; color: #222; margin: 5px 0; font-weight: 600; }}
            .price {{ font-size: 1.2rem; color: #e74c3c; font-weight: 800; }}
            .link-btn {{ display: inline-block; margin-top: 10px; padding: 5px 15px; background: #24292f; color: white; text-decoration: none; border-radius: 5px; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌿 '{SEARCH_KEYWORD}' 분석 결과</h1>
            <p>기준: {MIN_PRICE:,}원 이상 | 생성일: {time.strftime('%Y-%m-%d %H:%M')}</p>
    """
    
    for item in data:
        html_content += f"""
            <div class="item-box">
                <img src="{item['img']}" class="item-img" alt="상품이미지">
                <div class="item-info">
                    <div class="brand">{item['brand']}</div>
                    <div class="name">{item['name']}</div>
                    <div class="price">{item['price']}</div>
                    <a href="{item['link']}" class="link-btn" target="_blank">상품 보기</a>
                </div>
            </div>
        """
        
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # 파일 저장
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ 리포트 생성 완료: {REPORT_FILE}")
    
    # 파일 자동 실행
    file_path = "file://" + os.path.abspath(REPORT_FILE)
    webbrowser.open(file_path)

if __name__ == "__main__":
    collect_and_save_visual()