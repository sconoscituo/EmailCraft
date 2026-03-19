# EmailCraft

AI 이메일 작성 도우미 + 템플릿 관리 SaaS

## 주요 기능

- Gemini AI 기반 이메일 자동 생성 (목적/수신자/톤 입력)
- A/B 테스트용 이메일 변형 생성
- 이메일 템플릿 저장 및 재사용
- 다국어 지원 (한국어/영어/일본어)
- JWT 인증 + 프리미엄 플랜

## 빠른 시작

```bash
cp .env.example .env
# .env에 GEMINI_API_KEY 입력

pip install -r requirements.txt
uvicorn app.main:app --reload
```

API 문서: http://localhost:8000/docs

## Docker

```bash
docker-compose up -d
```

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | /api/users/register | 회원가입 |
| POST | /api/users/login | 로그인 |
| GET | /api/users/me | 내 정보 |
| POST | /api/emails/generate | 이메일 생성 |
| POST | /api/emails/variants | 변형 생성 (A/B) |
| GET | /api/emails/templates | 템플릿 목록 |
| POST | /api/emails/templates | 템플릿 저장 |
| PUT | /api/emails/templates/{id} | 템플릿 수정 |
| DELETE | /api/emails/templates/{id} | 템플릿 삭제 |
| GET | /api/emails/history | 생성 기록 |
| POST | /api/payments/subscribe | 프리미엄 구독 |

## 환경 변수

| 변수 | 설명 |
|------|------|
| GEMINI_API_KEY | Google Gemini API 키 |
| SECRET_KEY | JWT 서명 키 |
| FREE_DAILY_LIMIT | 무료 플랜 일일 생성 제한 (기본: 5) |
| PREMIUM_MONTHLY_PRICE | 프리미엄 월 요금 (기본: 9900) |
