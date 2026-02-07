# AI-Server

Conversation-based risk decision support system with a deterministic pipeline.

## Run

- Install dependencies: `pip install -r requirements.txt`
- Start API: `uvicorn app.main:app --reload`

## API

- Endpoint: POST /api/analyze
- Base URL: http://ai-server:8000
- Request: JSON
- Response: JSON

### Request Rules

- `platform`: `INSTAGRAM` 또는 `TELEGRAM`만 허용
- `messages[].type`: `TEXT` 또는 `URL`
- `URL` 메시지는 OCR로 텍스트를 추출해 분석 파이프라인에 합쳐 처리

## Swagger

- http://localhost:8000/docs

## 환경변수

- `OPENAI_API_KEY` + OpenAI API 키 필요
- `OPENAI_OCR_MODEL` (기본값: `gpt-4o-mini`)
- `OCR_DOWNLOAD_TIMEOUT_SECONDS` (기본값: `10`)
- `OCR_MAX_IMAGE_BYTES` (기본값: `5000000`)
