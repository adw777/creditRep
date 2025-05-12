from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from parse_image import DocumentParsingTool
from genResponses import generate_response

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Document Parser and Chat API")

# Initialize document parsing tool
doc_parser = DocumentParsingTool()

# Model for chat request
class ChatRequest(BaseModel):
    query: str
    document_path: str

@app.post("/parse")
async def parse_document(file: UploadFile = File(...)):
    """
    Endpoint to parse a PDF document using OCR and extract content
    """
    try:
        # Verify file is PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save the uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse the PDF using OCR
        result = doc_parser.parse_pdf_as_images(temp_file_path)
        
        # Clean up temporary file
        os.remove(temp_file_path)
        
        return {"status": "success", "result": result}
    
    except Exception as e:
        # Clean up temporary file in case of error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Endpoint to generate responses based on document content
    """
    try:
        # Check if document exists
        if not os.path.exists(request.document_path):
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not found")
        
        # Read document content
        with open(request.document_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate response
        response = generate_response(content, request.query, api_key)
        
        if response is None:
            raise HTTPException(status_code=500, detail="Failed to generate response")
        
        return {"status": "success", "response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)