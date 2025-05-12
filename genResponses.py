import argparse
from pathlib import Path
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def read_markdown_file(input_file: str) -> str:
    """Read content from the markdown file."""
    with open(input_file, 'r', encoding='utf-8') as f:
        return f.read()

def generate_response(content: str, query: str, api_key: str) -> str:
    """Generate response for the query using the content context."""
    prompt = f"""
You are an AI assistant helping users understand credit report information. Use the following credit report content to answer the user's question.

Content:
{content}

User Question:
{query}

Please provide a clear and concise answer based only on the information available in the credit report content. If the information is not available in the content, please state that clearly.
"""

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use your specific model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes credit reports and provides accurate information based on the given content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1024
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating response: {e}")
        return None

def save_response(query: str, response: str, output_file: str):
    """Save the query and response to a text file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Question:\n{query}\n\nAnswer:\n{response}")

def main():
    parser = argparse.ArgumentParser(description='Generate responses for credit report queries using GPT-4o-mini')
    parser.add_argument('input_file', help='Path to the input markdown file')
    parser.add_argument('query', help='User query about the credit report')
    parser.add_argument('--output', help='Output text file path (default: response.txt)')
    
    args = parser.parse_args()
    
    # Set default output path if not provided
    if args.output is None:
        args.output = 'response.txt'
    
    # Read markdown content
    content = read_markdown_file(args.input_file)
    print(f"Successfully read content from: {args.input_file}")
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")
    
    # Generate response
    print("Generating response...")
    response = generate_response(content, args.query, api_key)
    
    if response:
        # Save response
        save_response(args.query, response, args.output)
        print(f"\nResponse saved to: {args.output}")
        
        # Also print the response to console
        print("\nQuery:", args.query)
        print("\nResponse:", response)
    else:
        print("Failed to generate response")

if __name__ == "__main__":
    main()

"""Based on the data provided, calculate the total combined outstanding balance from all contract types (instalment and non-instalment), including both active and guaranteed contracts. How many of these contracts show any overdue amount?"""