"""
File upload endpoints
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import csv
import json
import io
from typing import List

from app.core.database import get_db
from app.services.review_service import ReviewService
from app.services.ml_service import MLService
from app.schemas.review import ReviewCreate

router = APIRouter()


@router.post("/file")
async def upload_reviews_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and analyze reviews from a file (CSV, TXT, or JSON)."""
    
    # Check file extension
    if not file.filename.lower().endswith(('.csv', '.txt', '.json')):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload CSV, TXT, or JSON files."
        )
    
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Parse reviews based on file type
        reviews_texts = []
        
        if file.filename.lower().endswith('.csv'):
            reviews_texts = parse_csv_content(content_str)
        elif file.filename.lower().endswith('.json'):
            reviews_texts = parse_json_content(content_str)
        elif file.filename.lower().endswith('.txt'):
            reviews_texts = parse_txt_content(content_str)
        
        if not reviews_texts:
            raise HTTPException(status_code=400, detail="No valid review texts found in the file.")
        
        # Analyze sentiments
        ml_service = MLService()
        review_service = ReviewService(db)
        
        analyzed_reviews = []
        for text in reviews_texts:
            if text.strip():  # Skip empty texts
                sentiment_result = ml_service.analyze_sentiment(text)
                
                review_data = ReviewCreate(
                    text=text,
                    sentiment=sentiment_result["sentiment"],
                    confidence=sentiment_result["confidence"],
                    source=file.filename
                )
                
                review = review_service.create_review(review_data)
                analyzed_reviews.append({
                    "id": review.id,
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "sentiment": sentiment_result["sentiment"],
                    "confidence": sentiment_result["confidence"]
                })
        
        return {
            "message": f"Successfully analyzed {len(analyzed_reviews)} reviews",
            "filename": file.filename,
            "total_reviews": len(analyzed_reviews),
            "results": analyzed_reviews[:10]  # Return first 10 results as preview
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


def parse_csv_content(content: str) -> List[str]:
    """Parse CSV content and extract review texts."""
    reviews = []
    csv_reader = csv.reader(io.StringIO(content))
    
    # Try to detect if first row is header
    rows = list(csv_reader)
    if not rows:
        return reviews
    
    # Assume first column contains review text
    # Skip header if it looks like one
    start_row = 1 if len(rows) > 1 and not any(char.isdigit() for char in rows[0][0][:50]) else 0
    
    for row in rows[start_row:]:
        if row and len(row) > 0:
            reviews.append(row[0])
    
    return reviews


def parse_json_content(content: str) -> List[str]:
    """Parse JSON content and extract review texts."""
    try:
        data = json.loads(content)
        reviews = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    reviews.append(item)
                elif isinstance(item, dict):
                    # Try common field names for review text
                    for field in ['text', 'review', 'comment', 'content', 'message']:
                        if field in item:
                            reviews.append(str(item[field]))
                            break
        elif isinstance(data, dict):
            # Single review object
            for field in ['text', 'review', 'comment', 'content', 'message']:
                if field in data:
                    reviews.append(str(data[field]))
                    break
        
        return reviews
    except json.JSONDecodeError:
        return []


def parse_txt_content(content: str) -> List[str]:
    """Parse TXT content - assume each line is a review."""
    return [line.strip() for line in content.split('\n') if line.strip()]
