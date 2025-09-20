"""
MyFundFinder AI Terminal - All-in-One Interface
Interactive chat, company extraction testing, and document processing
"""

import os
import sys
from pathlib import Path

# Add the app directory to the path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from dotenv import load_dotenv
load_dotenv()

def interactive_chat():
    """Start interactive chat with Nova Pro"""
    try:
        from bedrock_service import BedrockService
        
        service = BedrockService()
        print("\n🤖 MyFundFinder AI Chat Terminal")
        print("=" * 50)
        print("✅ Connected to Nova Pro!")
        print("💬 Start chatting! (Type 'quit' to exit)")
        print("🎯 Try asking about: company analysis, funding advice, business questions")
        print("-" * 50)
        
        while True:
            # Get user input
            user_input = input("\n🧑 You: ").strip()
            
            # Exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'back']:
                print("\n👋 Returning to main menu...")
                break
            
            if not user_input:
                continue
                
            # Show AI is thinking
            print("\n🤖 AI: (thinking...)", end="", flush=True)
            
            # Get AI response
            try:
                response = service.chat_with_nova_pro(user_input)
                print(f"\r🤖 AI: {response}")
            except Exception as e:
                print(f"\r🤖 AI: Sorry, I encountered an error: {e}")
                
    except Exception as e:
        print(f"❌ Error starting chat: {e}")
        print("💡 Make sure your AWS credentials are set correctly!")

def test_company_extraction():
    """Test company info extraction with sample data"""
    try:
        from bedrock_service import BedrockService
        
        service = BedrockService()
        
        print("\n🧪 Testing Company Info Extraction")
        print("=" * 50)
        
        # Sample company texts to test
        test_companies = [
            "GreenTech Solutions is a startup based in San Francisco with 8 employees. We develop solar panel optimization software for residential homes and need $500k in Series A funding.",
            
            "MedDevice Corp is a medium-sized medical device manufacturer in Boston. We have 150 employees and specialize in cardiac monitoring equipment. Looking for expansion funding.",
            
            "AgriBot Inc is a small agricultural technology company in Iowa with 25 employees. We create autonomous farming robots and need funding for R&D and market expansion."
        ]
        
        for i, company_text in enumerate(test_companies, 1):
            print(f"\n📄 Test Company #{i}:")
            print(f"Input: {company_text}")
            print("\n🤖 Extracted Info:")
            
            try:
                result = service.extract_company_info_from_text(company_text)
                for key, value in result.items():
                    print(f"  • {key}: {value}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
                
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"❌ Error in company extraction test: {e}")

def process_uploaded_document():
    """Handle document upload and processing"""
    try:
        from document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        print("\n📄 MyFundFinder Document Processor")
        print("=" * 50)
        print("📁 Supported formats: PDF, DOCX, TXT, Images (PNG, JPG, etc.)")
        print("💡 Upload business documents, company profiles, funding applications, etc.")
        print("💭 Type 'back' to return to main menu")
        print("-" * 50)
        
        while True:
            # Get file path from user
            file_path = input("\n📂 Enter the full path to your document (or 'back' to return): ").strip()
            
            if file_path.lower() in ['quit', 'exit', 'back']:
                print("👋 Returning to main menu...")
                break
            
            # Remove quotes if user copied path with quotes
            file_path = file_path.strip('"').strip("'")
            
            # Check if file exists
            if not os.path.exists(file_path):
                print("❌ File not found. Please check the path and try again.")
                continue
            
            # Get filename and check extension
            filename = os.path.basename(file_path)
            allowed_extensions = ('.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')
            
            if not filename.lower().endswith(allowed_extensions):
                print(f"❌ Unsupported file type. Please use: {', '.join(allowed_extensions)}")
                continue
            
            print(f"\n🔄 Processing {filename}...")
            
            try:
                # Read file
                with open(file_path, 'rb') as file:
                    file_bytes = file.read()
                
                # Ask for analysis type
                print("\nChoose analysis type:")
                print("1. General analysis")
                print("2. Company info extraction")
                print("3. Funding recommendations")
                
                analysis_choice = input("Enter choice (1-3): ").strip()
                analysis_types = {"1": "general", "2": "company_info", "3": "funding"}
                analysis_type = analysis_types.get(analysis_choice, "general")
                
                # Process document
                result = processor.process_document(file_bytes, filename, analysis_type)
                
                if result['processing_success']:
                    print("✅ Document processed successfully!")
                    
                    # Show extracted text preview
                    print("\n📄 EXTRACTED TEXT PREVIEW:")
                    print("-" * 30)
                    preview_text = result['extracted_text_preview']
                    print(preview_text)
                    
                    # Show analysis results
                    analysis_result = result['analysis_result']
                    if analysis_type == "company_info" and isinstance(analysis_result, dict):
                        print(f"\n📊 COMPANY INFORMATION:")
                        print("-" * 30)
                        for key, value in analysis_result.items():
                            if value and key != 'error':
                                print(f"• {key.replace('_', ' ').title()}: {value}")
                    
                    elif analysis_type == "funding" and isinstance(analysis_result, dict):
                        if analysis_result.get('company_info'):
                            print(f"\n📊 COMPANY INFORMATION:")
                            print("-" * 30)
                            for key, value in analysis_result['company_info'].items():
                                if value and key != 'error':
                                    print(f"• {key.replace('_', ' ').title()}: {value}")
                        
                        if analysis_result.get('funding_recommendations'):
                            print(f"\n💰 FUNDING RECOMMENDATIONS:")
                            print("-" * 30)
                            print(analysis_result['funding_recommendations'])
                    
                    else:
                        print(f"\n🔍 ANALYSIS RESULTS:")
                        print("-" * 30)
                        if isinstance(analysis_result, dict) and 'analysis' in analysis_result:
                            print(analysis_result['analysis'])
                        else:
                            print(analysis_result)
                    
                    # Show document stats
                    print(f"\n📈 DOCUMENT STATS:")
                    print(f"• File size: {result['file_size']:,} bytes")
                    print(f"• Full text length: {result['full_text_length']:,} characters")
                    print(f"• Analysis type: {result['analysis_type']}")
                    
                else:
                    print(f"❌ Processing failed: {result['error']}")
                    
            except Exception as e:
                print(f"❌ Error processing file: {e}")
            
            print("\n" + "=" * 70)
            
    except Exception as e:
        print(f"❌ Error initializing document processor: {e}")

def create_sample_document():
    """Create a sample business document for testing"""
    sample_content = """
COMPANY PROFILE: TechInnovate Solutions

Company Overview:
TechInnovate Solutions is a dynamic technology startup founded in 2023 and based in Austin, Texas. 
We specialize in developing artificial intelligence-powered software solutions for small and medium enterprises.

Company Details:
- Founded: 2023
- Location: Austin, Texas
- Industry: Technology / Software Development
- Company Size: 12 employees
- Specialty: AI-powered business automation tools

Business Description:
Our mission is to democratize artificial intelligence for smaller businesses. We develop user-friendly 
AI tools that help companies automate routine tasks, analyze customer data, and optimize their operations 
without requiring technical expertise.

Current Products:
1. SmartAnalytics - Customer behavior analysis platform
2. AutoFlow - Business process automation suite
3. ChatBot Pro - Customer service AI assistant

Financial Information:
- Current Revenue: $450,000 annually
- Growth Rate: 180% year-over-year
- Seeking: $2.5 million Series A funding
- Use of Funds: Product development (40%), Marketing (35%), Team expansion (25%)

Funding Requirements:
We are actively seeking Series A funding to accelerate our growth and expand our product offerings. 
The funding will primarily be used for enhancing our AI capabilities, expanding our sales and marketing 
efforts, and growing our engineering team.

Market Analysis:
The global business automation software market is projected to reach $19.6 billion by 2026, growing at 
a CAGR of 12.2%. Our target market includes over 30 million small and medium businesses in North America 
that currently lack access to advanced AI tools.

Competitive Advantages:
1. User-friendly interface requiring no technical expertise
2. Affordable pricing model accessible to SMEs
3. Industry-specific customization capabilities
4. Strong customer support and training programs

Contact Information:
CEO: Sarah Johnson
Email: sarah@techinnovate.com
Phone: (512) 555-0123
Website: www.techinnovate.com
"""
    
    sample_file = "sample_company_profile.txt"
    try:
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        full_path = os.path.abspath(sample_file)
        print(f"✅ Sample document created: {full_path}")
        print(f"💡 You can now test document processing with this file!")
        return full_path
    except Exception as e:
        print(f"❌ Error creating sample document: {e}")
        return None

def show_help():
    """Show help and usage information"""
    print("\n📖 MyFundFinder Terminal Help")
    print("=" * 50)
    print("🎯 This terminal provides comprehensive AI testing for your fund finder:")
    print()
    print("1. 💬 Interactive Chat:")
    print("   • Chat directly with Nova Pro AI")
    print("   • Ask about funding, business analysis, etc.")
    print("   • Perfect for testing conversational AI features")
    print()
    print("2. 🧪 Company Extraction Testing:")
    print("   • Test AI's ability to extract company information")
    print("   • Uses predefined test cases")
    print("   • Validates core fund-matching logic")
    print()
    print("3. 📄 Document Processing:")
    print("   • Upload business documents, PDFs, images")
    print("   • Extract text and analyze with AI")
    print("   • Test document-based fund recommendations")
    print()
    print("4. 📝 Sample Document Creation:")
    print("   • Creates test company profile")
    print("   • Perfect for testing document processing")
    print()
    print("💡 Tips:")
    print("   • Use 'back' or 'quit' to return to main menu")
    print("   • Test different document types and analysis modes")
    print("   • Try various chat prompts to test AI responses")
    print("=" * 50)

def main():
    """Main menu for the combined terminal"""
    print("🚀 MyFundFinder AI Terminal - All-in-One")
    print("=" * 50)
    print("🎯 Interactive Chat • Company Extraction • Document Processing")
    print()
    
    while True:
        print("\nChoose an option:")
        print("1. 💬 Interactive Chat with AI")
        print("2. 🧪 Test Company Info Extraction")
        print("3. 📄 Process Documents")
        print("4. 📝 Create Sample Document")
        print("5. 📖 Help & Usage Guide")
        print("6. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            interactive_chat()
        elif choice == "2":
            test_company_extraction()
        elif choice == "3":
            process_uploaded_document()
        elif choice == "4":
            create_sample_document()
        elif choice == "5":
            show_help()
        elif choice == "6":
            print("\n👋 Thank you for using MyFundFinder AI Terminal!")
            print("🎯 Your fund finder is ready for the hackathon!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main()