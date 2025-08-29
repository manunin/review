# cURL Examples for Review Analysis API

## Task Results

### Get last single task result
```bash
curl -X POST "http://localhost:8000/api/v1/task/result/single" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "user_id": "some cookies id"
  }'
```

### Get last batch task result
```bash
curl -X POST "http://localhost:8000/api/v1/task/result/batch" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "user_id": "some cookies id"
  }'
```

## Task Execution

### Send task for single text analysis
```bash
curl -X POST "http://localhost:8000/api/v1/task/run/single" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "user_id": "some cookies id",
    "text": "Text to check (max up to 512)"
  }'
```

### Send task for batch analysis (CSV file)
```bash
curl -X POST "http://localhost:8000/api/v1/task/run/batch" \
  -H "Accept: application/json" \
  -F "user_id=some cookies id" \
  -F "file=@reviews.csv"
```

### Send task for batch analysis (TXT file)
```bash
curl -X POST "http://localhost:8000/api/v1/task/run/batch" \
  -H "Accept: application/json" \
  -F "user_id=some cookies id" \
  -F "file=@reviews.txt"
```

### Send task for batch analysis (JSON file)
```bash
curl -X POST "http://localhost:8000/api/v1/task/run/batch" \
  -H "Accept: application/json" \
  -F "user_id=some cookies id" \
  -F "file=@reviews.json"
```

## Example files for batch upload

### CSV format (reviews.csv)
```csv
text
"Excellent product, very satisfied with the purchase!"
"Quality leaves much to be desired"
"Average product, nothing special"
"Outstanding quality and fast delivery"
"Not recommended for purchase"
```

### TXT format (reviews.txt)
```
Excellent product, very satisfied with the purchase!
Quality leaves much to be desired
Average product, nothing special
Outstanding quality and fast delivery
Not recommended for purchase
```

### JSON format (reviews.json)
```json
[
  {"text": "Excellent product, very satisfied with the purchase!"},
  {"text": "Quality leaves much to be desired"},
  {"text": "Average product, nothing special"},
  {"text": "Outstanding quality and fast delivery"},
  {"text": "Not recommended for purchase"}
]
```

## Example responses

### Successful single task result
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "single",
  "status": "ready",
  "start": 1640995200,
  "end": 1640995205,
  "result": {
    "sentiment": "positive",
    "confidence": 0.95,
    "text": "Excellent product, very satisfied!"
  }
}
```

### Successful batch task result
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174001",
  "type": "batch",
  "status": "ready",
  "start": 1640995200,
  "end": 1640995300,
  "result": {
    "total_reviews": 150,
    "positive": 90,
    "negative": 35,
    "neutral": 25,
    "positive_percentage": 60.0,
    "negative_percentage": 23.3,
    "neutral_percentage": 16.7
  }
}
```

### Task in progress (queued)
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "single",
  "status": "queued",
  "start": 1640995200
}
```

### Task with error
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "single",
  "status": "error",
  "start": 1640995200,
  "end": 1640995205,
  "error": {
    "code": "01",
    "description": "Some backend original description"
  }
}
```

## Error handling examples

### Missing user_id
```bash
curl -X POST "http://localhost:8000/api/v1/task/result/single" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{}'

# Expected response: 422 Validation Error
```

### Text too long
```bash
curl -X POST "http://localhost:8000/api/v1/task/run/single" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "user_id": "some cookies id",
    "text": "'$(head -c 600 < /dev/zero | tr '\0' 'a')'"
  }'

# Expected response: 422 Validation Error
```

### No task found
```bash
curl -X POST "http://localhost:8000/api/v1/task/result/single" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "user_id": "nonexistent_user_id"
  }'

# Expected response: 404 Not Found
```

### File too large
```bash
# Create a large file (> 10MB)
curl -X POST "http://localhost:8000/api/v1/task/run/batch" \
  -H "Accept: application/json" \
  -F "user_id=some cookies id" \
  -F "file=@large_file.csv"

# Expected response: 413 File Too Large
```

### Invalid file format
```bash
curl -X POST "http://localhost:8000/api/v1/task/run/batch" \
  -H "Accept: application/json" \
  -F "user_id=some cookies id" \
  -F "file=@document.pdf"

# Expected response: 415 Unsupported File Format
```
