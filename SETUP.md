# EmailCraft - 프로젝트 설정 가이드

## 프로젝트 소개

EmailCraft는 Google Gemini AI를 활용하여 비즈니스 이메일, 마케팅 이메일, 뉴스레터 등 다양한 용도의 이메일을 자동 생성하는 SaaS 서비스입니다. 무료 플랜(일 5회)과 프리미엄 플랜을 지원합니다.

- **기술 스택**: FastAPI, SQLAlchemy (asyncio), SQLite, Google Gemini AI
- **인증**: JWT (python-jose)
- **무료 한도**: 일 5회 생성

---

## 필요한 API 키 / 환경변수

| 환경변수 | 설명 | 발급 URL |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini AI API 키 | [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| `SECRET_KEY` | JWT 서명용 비밀 키 (임의의 긴 문자열) | 직접 생성 (`openssl rand -hex 32`) |
| `DATABASE_URL` | DB 연결 URL (기본: SQLite) | - |
| `DEBUG` | 디버그 모드 (`true`/`false`, 기본: `false`) | - |
| `FREE_DAILY_LIMIT` | 무료 사용자 일일 생성 한도 (기본: `5`) | - |
| `PREMIUM_MONTHLY_PRICE` | 프리미엄 월 가격 원화 (기본: `9900`) | - |

---

## GitHub Secrets 설정 방법

저장소의 **Settings > Secrets and variables > Actions** 에서 아래 Secrets를 등록합니다.

```
GEMINI_API_KEY     = <Google AI Studio에서 발급한 키>
SECRET_KEY         = <openssl rand -hex 32 으로 생성한 값>
```

---

## 로컬 개발 환경 설정

### 1. 저장소 클론

```bash
git clone https://github.com/sconoscituo/EmailCraft.git
cd EmailCraft
```

### 2. Python 가상환경 생성 및 의존성 설치

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 환경변수 파일 생성

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite+aiosqlite:///./emailcraft.db
DEBUG=true
FREE_DAILY_LIMIT=5
PREMIUM_MONTHLY_PRICE=9900
```

---

## 실행 방법

### 로컬 실행 (uvicorn)

```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 문서 확인: [http://localhost:8000/docs](http://localhost:8000/docs)

### Docker Compose로 실행

```bash
docker-compose up --build
```

### 테스트 실행

```bash
pytest tests/
```
