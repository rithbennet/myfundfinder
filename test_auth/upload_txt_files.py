#!/usr/bin/env python3
"""
TXT File Upload Utility for RAG System
Upload and process TXT files through the web interface or directly to the RAG system
"""

import os
import requests
import glob
from pathlib import Path
from dotenv import load_dotenv
from process_txt_files import TXTProcessor

load_dotenv()

class TXTUploader:
    def __init__(self, chatbot_url: str = "http://localhost:9000"):
        self.chatbot_url = chatbot_url
        self.processor = None
        
        # Initialize direct processor if MongoDB is available
        mongo_uri = os.getenv("MONGO_URI")
        if mongo_uri:
            self.processor = TXTProcessor(
                mongo_uri=mongo_uri,
                db_name="dev_trees_hire",
                collection_name="txt_documents_rag"
            )
    
    def upload_via_web(self, file_path: str) -> dict:
        """Upload file through the web interface"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                files = {'file': (os.path.basename(file_path), f, 'text/plain')}
                response = requests.post(f"{self.chatbot_url}/upload", files=files)
                return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def upload_direct(self, file_path: str) -> dict:
        """Upload file directly to RAG system"""
        if not self.processor:
            return {'success': False, 'error': 'Direct upload not available - MongoDB not configured'}
        
        try:
            document_ids = self.processor.process_single_file(file_path)
            return {
                'success': True,
                'message': f"Processed {len(document_ids)} chunks",
                'document_ids': document_ids
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def upload_directory(self, directory_path: str, method: str = "direct") -> dict:
        """Upload all TXT files in a directory"""
        txt_files = glob.glob(os.path.join(directory_path, "*.txt"))
        
        if not txt_files:
            return {'success': False, 'error': 'No TXT files found'}
        
        results = {}
        for file_path in txt_files:
            filename = os.path.basename(file_path)
            print(f"Processing {filename}...")
            
            if method == "web":
                result = self.upload_via_web(file_path)
            else:
                result = self.upload_direct(file_path)
            
            results[filename] = result
            
            if result.get('success'):
                print(f"✅ {filename} uploaded successfully")
            else:
                print(f"❌ {filename} failed: {result.get('error', 'Unknown error')}")
        
        return results
    
    def test_search(self, query: str) -> dict:
        """Test search functionality"""
        try:
            response = requests.post(
                f"{self.chatbot_url}/chat",
                json={'message': query}
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}

def main():
    uploader = TXTUploader()
    
    print("🚀 TXT File Uploader")
    print("=" * 40)
    print("Available methods:")
    print("1. Upload single file via web interface")
    print("2. Upload single file directly to RAG")
    print("3. Upload directory via web interface")
    print("4. Upload directory directly to RAG")
    print("5. Test search")
    print("=" * 40)
    
    while True:
        choice = input("\nEnter choice (1-5) or 'q' to quit: ").strip()
        
        if choice == 'q':
            break
        elif choice == '1':
            file_path = input("Enter file path: ").strip()
            if os.path.exists(file_path):
                result = uploader.upload_via_web(file_path)
                print(f"Result: {result}")
            else:
                print("File not found")
        elif choice == '2':
            file_path = input("Enter file path: ").strip()
            if os.path.exists(file_path):
                result = uploader.upload_direct(file_path)
                print(f"Result: {result}")
            else:
                print("File not found")
        elif choice == '3':
            dir_path = input("Enter directory path: ").strip()
            if os.path.exists(dir_path):
                results = uploader.upload_directory(dir_path, "web")
                print(f"Processed {len(results)} files")
            else:
                print("Directory not found")
        elif choice == '4':
            dir_path = input("Enter directory path: ").strip()
            if os.path.exists(dir_path):
                results = uploader.upload_directory(dir_path, "direct")
                print(f"Processed {len(results)} files")
            else:
                print("Directory not found")
        elif choice == '5':
            query = input("Enter search query: ").strip()
            result = uploader.test_search(query)
            print(f"Search result: {result}")
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
