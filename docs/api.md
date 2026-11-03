# CreatorFlow API Reference

Base URL: `http://127.0.0.1:8000`

All endpoints under `/api/*` require an `X-API-Key` header.
Current dev key: `creatorflow_dev_key` (configurable via `.env`).

## Endpoints

### GET /health
Returns service status. No auth required.

**Response (200):**
```json
{
  "status": "ok",
  "app": "CreatorFlow",
  "env": "development"
}