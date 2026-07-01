import requests
import json
# 필수 라이브러리
# python -m pip install flask playwright
# python -m playwright install chromium
# python -m pip install flask playwright


# 카카오톡 메시지 전송 함수
def send_kakao_message(text):
    # 본인의 카카오 API 토큰 (발급 필요)
    access_token = '여기에_본인의_액세스_토큰을_넣으세요' 
    
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": "Bearer " + access_token
    }
    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text,
            "link": {
                "web_url": "https://www.google.com",
                "mobile_web_url": "https://www.google.com"
            },
            "button_title": "리포트 확인"
        })
    }
    
    response = requests.post(url, headers=headers, data=data)
    if response.json().get('result_code') == 0:
        print('✅ 카카오톡 메시지를 성공적으로 보냈습니다.')
    else:
        print('❌ 메시지 전송 실패: ' + str(response.json()))

# --- [기존 스케줄러와 합치기] ---
def run_report_and_send():
    # 1. 주식/뉴스/테니스 데이터 수집 실행 (기존 코드)
    # result_summary = collect_data() 
    
    # 2. 요약 내용 작성
    summary = "[아침 10시 리포트]\n코스피: +1.5%\n코스닥: -1.2%\n테니스 배당 수집 완료!"
    
    # 3. 카톡 발송
    send_kakao_message(summary)

# 매일 오전 10시에 실행
# schedule.every().day.at("10:00").do(run_report_and_send)