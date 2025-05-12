# from fastapi import FastAPI, UploadFile, File, HTTPException
# from pydantic import BaseModel
# from typing import Optional
# import os
# from dotenv import load_dotenv
# from parse_image import DocumentParsingTool
# from genResponses import generate_response

# # Load environment variables
# load_dotenv()

# # Initialize FastAPI app
# app = FastAPI(title="Document Parser and Chat API")

# # Initialize document parsing tool
# doc_parser = DocumentParsingTool()

# # Model for chat request
# class ChatRequest(BaseModel):
#     query: str
#     document_path: str

# @app.post("/parse")
# async def parse_document(file: UploadFile = File(...)):
#     """
#     Endpoint to parse a PDF document using OCR and extract content
#     """
#     try:
#         # Verify file is PDF
#         if not file.filename.lower().endswith('.pdf'):
#             raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
#         # Save the uploaded file temporarily
#         temp_file_path = f"temp_{file.filename}"
#         with open(temp_file_path, "wb") as buffer:
#             content = await file.read()
#             buffer.write(content)
        
#         # Parse the PDF using OCR
#         result = doc_parser.parse_pdf_as_images(temp_file_path)
        
#         # Clean up temporary file
#         os.remove(temp_file_path)
        
#         return {"status": "success", "result": result}
    
#     except Exception as e:
#         # Clean up temporary file in case of error
#         if os.path.exists(temp_file_path):
#             os.remove(temp_file_path)
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/chat")
# async def chat(request: ChatRequest):
#     """
#     Endpoint to generate responses based on document content
#     """
#     try:
#         # Check if document exists
#         if not os.path.exists(request.document_path):
#             raise HTTPException(status_code=404, detail="Document not found")
        
#         # Get API key from environment
#         api_key = os.getenv("OPENAI_API_KEY")
#         if not api_key:
#             raise HTTPException(status_code=500, detail="OpenAI API key not found")
        
#         # Read document content
#         with open(request.document_path, 'r', encoding='utf-8') as f:
#             content = f.read()
        
#         # Generate response
#         response = generate_response(content, request.query, api_key)
        
#         if response is None:
#             raise HTTPException(status_code=500, detail="Failed to generate response")
        
#         return {"status": "success", "response": response}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001)


from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
from dotenv import load_dotenv
from parse_image import DocumentParsingTool
from genResponses import generate_response
from emailTool import send_email

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

# Model for email request
class EmailRequest(BaseModel):
    sender_email: EmailStr
    receiver_email: EmailStr
    subject: str
    body: str
    attachment_path: Optional[str] = None

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

@app.post("/sendEmail")
async def send_email_endpoint(request: EmailRequest):
    """
    Endpoint to send emails with optional attachments
    """
    try:
        # Get email password from environment variables
        email_password = os.getenv("EMAIL_PASSWORD")
        if not email_password:
            raise HTTPException(status_code=500, detail="Email password not found in environment variables")

        # Verify attachment path if provided
        if request.attachment_path and not os.path.exists(request.attachment_path):
            raise HTTPException(status_code=400, detail="Attachment file not found")

        # Send email
        success = send_email(
            sender_email=request.sender_email,
            receiver_email=request.receiver_email,
            subject=request.subject,
            body=request.body,
            password=email_password,
            attachment_path=request.attachment_path
        )

        if success:
            return {
                "status": "success",
                "message": "Email sent successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)