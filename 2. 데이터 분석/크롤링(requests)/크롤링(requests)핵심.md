# 🌐 requests 기반 정적 크롤링 핵심 정리

---

## 1️⃣ 정적 크롤링이란?

> 👉 서버에서 **이미 완성된 HTML**을 가져와 파싱하는 방식

* JavaScript 실행 ❌ (동적 X)
* 빠르고 가벼움
* 대부분의 기본 웹페이지에 적용 가능

---

## 2️⃣ requests 모듈 역할

> 👉 웹 서버에 요청(Request)을 보내고 응답(Response)을 받는 라이브러리

```python
import requests

res = requests.get("https://example.com")
print(res.status_code)  # 응답 상태 코드
print(res.text)         # HTML 원문
```

---

## 3️⃣ HTTP 요청 기본 구조

### ✔ GET 요청 (가장 기본)

```python
requests.get(url)
```

### ✔ POST 요청

```python
requests.post(url, data={"key": "value"})
```

---

## 4️⃣ 응답(Response) 핵심 요소

```python
res.status_code  # 상태 코드 (200 = 성공)
res.text         # HTML 문자열
res.content      # 바이너리 데이터
```

### ✔ 주요 상태 코드

* 200 → 성공
* 404 → 페이지 없음
* 403 → 접근 거부

---

## 5️⃣ HTML 파싱 (BeautifulSoup)

> 👉 HTML에서 원하는 데이터 추출

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(res.text, "html.parser")
title = soup.find("title").text

print(title)
```

---

## 6️⃣ 데이터 추출 방법

### ✔ 단일 요소

```python
soup.find("태그")
```

### ✔ 여러 요소

```python
soup.find_all("태그")
```

### ✔ CSS 선택자

```python
soup.select("div.class")
```

---

## 7️⃣ 요청 시 헤더 설정 (중요)

> 👉 서버가 봇을 차단하는 것을 방지

```python
headers = {
    "User-Agent": "Mozilla/5.0"
}

requests.get(url, headers=headers)
```

---

## 8️⃣ 쿼리 파라미터 처리

```python
params = {"q": "python"}

requests.get(url, params=params)
```

👉 URL에 자동으로 `?q=python` 붙음

---

## 9️⃣ 크롤링 기본 흐름

```python
import requests
from bs4 import BeautifulSoup

url = "https://example.com"

res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")

data = soup.find_all("a")

for i in data:
    print(i.text)
```

---

## 🔟 주의사항 (중요)

* robots.txt 확인
* 너무 많은 요청 ❌ (서버 부하)
* 사이트 이용약관 준수
* 로그인 / JS 페이지 → Selenium 필요

---

## 📌 한눈에 핵심 정리

* requests → **페이지 가져오기**
* BeautifulSoup → **데이터 추출**
* headers → **차단 방지**
* select/find → **데이터 찾기**

---

## 💡 한 줄 요약

> 👉 **정적 크롤링 = "HTML 가져오기 + 파싱해서 데이터 뽑기"**
