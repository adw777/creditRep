import os
import json
import requests
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List

class DocumentParsingTool:
    """Tool for extracting and parsing text and images from documents using an API."""

    name: str = "Document Parsing Tool"
    description: str = "Extract text and images from various document formats"
    api_url: str = "https://sweeping-moth-probably.ngrok-free.app/parse_document"
    
    def _validate_input(self, file_path: str) -> Dict:
        """Validate the input document file."""
        result = {
            "valid": False,
            "file_path": "",
            "error": ""
        }
        
        try:
            # Convert to Path object for better path handling
            path = Path(file_path)
            
            # Verify file exists
            if not path.exists():
                result["error"] = f"File not found: {file_path}"
                return result
            
            # Verify it's a supported file type (optional - depends on API capabilities)
            # Common document extensions
            supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.rtf', '.ppt', '.pptx', '.odt']
            if path.suffix.lower() not in supported_extensions:
                result["error"] = f"File type may not be supported: {path.suffix}"
                # Note: We're returning a warning but still setting valid to True
                # as the API might support more formats than we list here
            
            result["file_path"] = str(path.absolute())
            result["valid"] = True
            return result
            
        except Exception as e:
            result["error"] = f"Error validating input: {str(e)}"
            return result
    
    def _extract_from_document(self, file_path: str) -> Dict:
        """Extract content from document using the API."""
        result = {
            "success": False,
            "content": {},
            "output_file": "",
            "error": ""
        }
        
        try:
            # Get file name from path
            file_name = Path(file_path).name
            
            # Prepare the file for upload
            with open(file_path, 'rb') as file:
                files = {
                    'file': (file_name, file, 'application/octet-stream')
                }
                
                # Send POST request
                response = requests.post(self.api_url, files=files)
                response.raise_for_status()  # Raise exception for bad status codes
                
                # Parse JSON response
                content = response.json()
                
                # Generate output filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = Path(file_path).stem
                output_file = f"{base_name}_parsed_{timestamp}.md"
                
                # Save extracted content to markdown file
                self._save_to_markdown(content, output_file)
                
                result["success"] = True
                result["content"] = content
                result["output_file"] = output_file
                return result
                
        except requests.RequestException as e:
            result["error"] = f"Error sending request to document parsing API: {str(e)}"
            return result
        except json.JSONDecodeError as e:
            result["error"] = f"Error parsing API response: {str(e)}"
            return result
        except Exception as e:
            result["error"] = f"Unexpected error during document parsing: {str(e)}"
            return result
    
    def _save_to_markdown(self, content: Dict, output_file: str) -> None:
        """Save the extracted content to a markdown file."""
        try:
            # Create a directory for images if there are any
            img_dir = None
            if "images" in content and content["images"]:
                img_dir = Path(output_file).with_suffix('')
                img_dir = f"{img_dir}_images"
                os.makedirs(img_dir, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as md_file:
                # Add timestamp
                md_file.write(f"# Document Extraction Results\n\n")
                md_file.write(f"_Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n")
                
                # Add text content
                if "text" in content:
                    md_file.write("## Extracted Text\n\n")
                    if isinstance(content["text"], str):
                        md_file.write(content["text"])
                    elif isinstance(content["text"], list):
                        for section in content["text"]:
                            md_file.write(f"{section}\n\n")
                    md_file.write("\n\n---\n\n")
                
                # Add image content
                if "images" in content and content["images"] and img_dir:
                    md_file.write("## Extracted Images\n\n")
                    
                    for i, img_data in enumerate(content["images"]):
                        # Process base64 encoded images
                        if "base64" in img_data and img_data["base64"]:
                            img_binary = base64.b64decode(img_data["base64"])
                            img_format = img_data.get("format", "png")
                            img_path = os.path.join(img_dir, f"image_{i+1}.{img_format}")
                            
                            # Save the image file
                            with open(img_path, 'wb') as img_file:
                                img_file.write(img_binary)
                            
                            # Add relative path to image in markdown
                            relative_path = os.path.relpath(img_path, os.path.dirname(output_file))
                            md_file.write(f"![Image {i+1}]({relative_path})\n\n")
                        
                        # Process URL-based images
                        elif "url" in img_data and img_data["url"]:
                            md_file.write(f"![Image {i+1}]({img_data['url']})\n\n")
                    
                    md_file.write("\n---\n\n")
                
                # Add metadata if available
                if "metadata" in content:
                    md_file.write("## Document Metadata\n\n")
                    md_file.write("```json\n")
                    md_file.write(json.dumps(content["metadata"], indent=2))
                    md_file.write("\n```\n\n")
        
        except Exception as e:
            print(f"Error saving markdown file: {str(e)}")
            raise
    
    def parse_document(self, file_path: str) -> str:
        """Process the input and extract content from the document."""
        # Validate the input file
        input_data = self._validate_input(file_path)
        
        if not input_data["valid"]:
            return f"Error: {input_data['error']}"
        
        # Extract content from the document
        extraction_result = self._extract_from_document(input_data["file_path"])
        
        if not extraction_result["success"]:
            return f"Error: {extraction_result['error']}"
        
        # Return success message
        output = f"Document parsing completed successfully!\n\n"
        output += f"Source: {input_data['file_path']}\n"
        output += f"Results saved to: {extraction_result['output_file']}\n"
        
        if extraction_result.get("error"):
            output += f"\nWarning: {extraction_result['error']}\n"
        
        return output


def main():
    """Main function to run the document parsing tool."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse a document and extract content to markdown')
    parser.add_argument('file_path', help='Path to the document file to be parsed')
    parser.add_argument('--api_url', 
                        default='https://sweeping-moth-probably.ngrok-free.app/parse_document',
                        help='URL of the document parsing API')
    
    args = parser.parse_args()
    
    # Create the document parsing tool
    doc_parser = DocumentParsingTool()
    
    # Override the API URL if provided
    if args.api_url:
        doc_parser.api_url = args.api_url
    
    # Parse the document
    try:
        result = doc_parser.parse_document(args.file_path)
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()