# API Documentation

This directory contains the OpenAPI specification for the Review Analysis API.

## Files

- `openapi.yml` - Main OpenAPI 3.0.3 specification
- `README.md` - This file with description
- `examples/` - Request and response examples

## API Endpoints

- `POST /api/v1/task/result/single` - Get last single task result
- `POST /api/v1/task/result/batch` - Get last batch task result
- `POST /api/v1/task/run/single` - Send task for analysis single text
- `POST /api/v1/task/run/batch` - Send task for batch (file) analysis

## Data Schemas

### POST /api/v1/task/result/single

Body payload:
```json
{
  "user_id": "some cookies id"
}
```

Response:
```json
{
  "task_id": "uuid",
  "type": "single",
  "status": "accepted|queued|ready|error",
  "start": "unix timestamp",
  "end": "unix timestamp (optional)",
  "result": {
    "sentiment": "positive|negative|neutral",
    "confidence": 0.0-1.0,  
    "text": "Analyzed text (optional)"
  },
  "error": {
    "code": "01|02|03",
    "description": "Some backend original description (optional)"
  }
}
```

### POST /api/v1/task/result/batch

Body payload:
```json
{
  "user_id": "some cookies id"
}
```

Response:
```json
{
  "task_id": "uuid",
  "type": "batch",
  "status": "accepted|queued|ready|error",
  "start": "unix timestamp",
  "end": "unix timestamp (optional)",
  "result": {
    "total_reviews": 150,
    "positive": 90,
    "negative": 35,
    "neutral": 25,
    "positive_percentage": 60.0,
    "negative_percentage": 23.3,
    "neutral_percentage": 16.7
  },
  "error": {
    "code": "01|02|03",
    "description": "Some backend original description (optional)"
  }
}
```

### POST /api/v1/task/run/single

Body payload:
```json
{
  "user_id": "some cookies id",
  "text": "Text to check (max up to 512)"
}
```

Response:
```json
{
  "task_id": "uuid",
  "type": "single",
  "status": "accepted|queued|ready|error",
  "start": "unix timestamp",
  "end": "unix timestamp (optional)",
  "result": {
    "sentiment": "positive|negative|neutral",
    "confidence": 0.0-1.0,  
    "text": "Analyzed text (optional)"
  },
  "error": {
    "code": "01|02|03",
    "description": "Some backend original description (optional)"
  }
}
```

### POST /api/v1/task/run/batch

Body payload:
```json
{
  "user_id": "some cookies id"
}
```

Media:
File CSV/TXT/JSON max size 10MB

Response:
```json
{
  "task_id": "uuid",
  "type": "batch",
  "status": "accepted|queued|ready|error",
  "start": "unix timestamp",
  "end": "unix timestamp (optional)",
  "result": {
    "total_reviews": 150,
    "positive": 90,
    "negative": 35,
    "neutral": 25,
    "positive_percentage": 60.0,
    "negative_percentage": 23.3,
    "neutral_percentage": 16.7
  },
  "error": {
    "code": "01|02|03",
    "description": "Some backend original description (optional)"
  }
}
```

## Usage

1. **View specification**: Open `openapi.yml` in Swagger UI or other OpenAPI tools
2. **Generate clients**: Use OpenAPI Generator to create clients for various languages
3. **Testing**: Use examples from the specification to test the API

## Tools for Working

- [Swagger UI](https://swagger.io/tools/swagger-ui/) - for interactive viewing
- [Swagger Editor](https://editor.swagger.io/) - for editing specification
- [OpenAPI Generator](https://openapi-generator.tech/) - for code generation
- [Postman](https://www.postman.com/) - import OpenAPI for testing

## Validation

The specification follows OpenAPI 3.0.3 standard and can be validated using:
```bash
swagger-codegen validate -i openapi.yml
```

## CONTEXT.MD Compliance

The specification was created according to requirements from `frontend/CONTEXT.MD`:
- Using service layer for API calls
- TypeScript typing (schemas match types in `src/types/index.ts`)
- Error handling at various levels
- Logging of all API operations
- Following RESTful API principles
