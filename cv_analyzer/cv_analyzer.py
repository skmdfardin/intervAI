import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import logging
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate

# Configure logging
logging.basicConfig(
    filename='cv_analysis.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extract_text_from_pdf(pdf_path):
    logging.info(f"Starting text extraction from: {pdf_path}")
    
    # Try normal PDF text extraction first
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            text += page_text
            logging.info(f"Extracted text from page {page_num + 1} using PyPDF2")
    
    # If extracted text is too short or empty, use OCR
    if len(text.strip()) < 100:
        logging.info("Insufficient text extracted, switching to OCR")
        text = ''
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        for i, image in enumerate(images):
            # Perform OCR on each image
            page_text = pytesseract.image_to_string(image)
            text += page_text
            logging.info(f"Extracted text from page {i + 1} using OCR")
    
    logging.info("Text extraction completed")
    return text

def analyze_cv(job_description, cv_text):
    logging.info("Starting CV analysis")
    
    # First get candidate details
    candidate_details = extract_candidate_details(cv_text)
    
    # Then do the regular analysis
    llm = Ollama(model="llama3.2", temperature=0.7)
    template = """
    You are a professional Technical HR analyst. Analyze the following CV against the job description and provide a score out of 10.
    Also provide a brief explanation for the score.
    
    Job Description:
    {job_description}
    
    CV Content:
    {cv_text}
    
    Please provide your analysis in the following format:
    Score: [number]/10
    Explanation: [your detailed explanation]
    """
    
    prompt = PromptTemplate(
        input_variables=["job_description", "cv_text"],
        template=template,
    )
    
    final_prompt = prompt.format(job_description=job_description, cv_text=cv_text)
    logging.info("Sending request to Ollama")
    response = llm(final_prompt)
    
    # Combine the results
    full_response = f"{candidate_details}\n\n{response}"
    logging.info("Analysis completed with candidate details")
    return full_response

def extract_candidate_details(cv_text):
    logging.info("Extracting candidate details")
    llm = Ollama(model="llama3.2", temperature=0.1)
    template = """
    Extract the following information from the CV text. If any field is not found, return "Not found".
    Return the response in exactly this format:
    Name: [full name]
    Email: [email address]
    Phone: [phone number]
    Location: [city/country]

    CV Content:
    {cv_text}
    """
    
    prompt = PromptTemplate(
        input_variables=["cv_text"],
        template=template,
    )
    
    final_prompt = prompt.format(cv_text=cv_text)
    response = llm(final_prompt)
    logging.info("Extracted candidate details")
    return response

def main():
    logging.info("Starting CV Analysis Program")
    print("CV Analysis Program")
    print("-----------------")
    
    print("\nPlease enter the job description:")
    job_description = input()
    logging.info("Job description received")
    
    print("\nPlease enter the path to the CV (PDF file):")
    pdf_path = input()
    
    try:
        cv_text = extract_text_from_pdf(pdf_path)
        
        print("\nAnalyzing CV...")
        result = analyze_cv(job_description, cv_text)
        
        print("\nAnalysis Result:")
        print(result)
        logging.info("Analysis completed successfully")
        
    except FileNotFoundError:
        logging.error(f"PDF file not found: {pdf_path}")
        print("Error: PDF file not found!")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

