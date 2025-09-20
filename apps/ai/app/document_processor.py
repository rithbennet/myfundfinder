"""
Document Processing Service for various file types
Extracts text from documents and analyzes with Nova Pro
"""

import PyPDF2
import io
from typing import Dict, Any, Optional
import os
import sys
from PIL import Image
import pytesseract
from docx import Document

sys.path.append('.')
from bedrock_service import BedrockService

class DocumentProcessor:
    def __init__(self):
        self.bedrock_service = BedrockService()
    
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from image (OCR may not be available): {str(e)}")
    
    def extract_text_from_docx(self, docx_bytes: bytes) -> str:
        """Extract text from Word document"""
        try:
            doc = Document(io.BytesIO(docx_bytes))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from Word document: {str(e)}")
    
    def extract_text_from_txt(self, txt_bytes: bytes) -> str:
        """Extract text from plain text file"""
        try:
            return txt_bytes.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")
    
    def extract_text_from_file(self, file_bytes: bytes, filename: str) -> str:
        """Extract text based on file type"""
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return self.extract_text_from_pdf(file_bytes)
        elif filename_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
            return self.extract_text_from_image(file_bytes)
        elif filename_lower.endswith('.docx'):
            return self.extract_text_from_docx(file_bytes)
        elif filename_lower.endswith('.txt'):
            return self.extract_text_from_txt(file_bytes)
        else:
            raise Exception(f"Unsupported file type: {filename}. Supported: PDF, images, Word (.docx), text (.txt)")
    
    def analyze_document_content(self, text: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze document content using AI"""
        try:
            if analysis_type == "company_info":
                return self.bedrock_service.extract_company_info_from_text(text)
            elif analysis_type == "funding":
                # Extract company info first, then get funding recommendations
                company_info = self.bedrock_service.extract_company_info_from_text(text)
                if company_info.get('sector') and company_info.get('company_size'):
                    funding_advice = self.bedrock_service.analyze_company_for_funding(company_info)
                    return {
                        "company_info": company_info,
                        "funding_recommendations": funding_advice
                    }
                else:
                    return {"company_info": company_info, "funding_recommendations": "Insufficient company information for funding analysis"}
            else:
                # General analysis
                prompt = f"Analyze this document and provide a comprehensive summary and key insights:\n\n{text[:2000]}..."
                analysis = self.bedrock_service.chat_with_nova_pro(prompt)
                return {"analysis": analysis}
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def process_document(self, file_bytes: bytes, filename: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Process document and extract information with AI analysis"""
        try:
            # Extract text from file
            extracted_text = self.extract_text_from_file(file_bytes, filename)
            
            if not extracted_text.strip():
                raise Exception("No text could be extracted from the document")
            
            # Analyze content with AI
            analysis_result = self.analyze_document_content(extracted_text, analysis_type)
            
            return {
                "filename": filename,
                "file_size": len(file_bytes),
                "extracted_text_preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
                "full_text_length": len(extracted_text),
                "analysis_type": analysis_type,
                "analysis_result": analysis_result,
                "processing_success": True
            }
            
        except Exception as e:
            return {
                "filename": filename,
                "error": str(e),
                "processing_success": False
            }