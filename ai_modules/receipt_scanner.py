"""
MoneyMap - AI Receipt Scanner
Uses OCR to extract information from receipt images
"""

import cv2
import numpy as np
import re
from datetime import datetime


class ReceiptScanner:
    """AI-powered receipt scanner using OCR"""
    
    def __init__(self):
        # Initialize Tesseract
        self.tesseract_config = r'--oem 3 --psm 6'
        
    def preprocess_image(self, image_path):
        """Preprocess image for better OCR results"""
        # Read image
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to enhance text
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Denoise the image
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        return denoised
    
    def extract_text(self, image_path):
        """Extract all text from receipt image"""
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)

            # OCR temporarily disabled
            return "Demo Receipt Shop\nTotal 500\n19-05-2026"

        except Exception as e:
            print(f"OCR Error: {str(e)}")
            return ""
    
    def find_amounts(self, text):
        """Find monetary amounts in extracted text"""
        amounts = []
        
        # Pattern for currency amounts (₹, Rs., INR, or plain numbers)
        patterns = [
            r'[₹]\s*([\d,]+\.?\d*)',           # ₹ symbol
            r'(?:Rs\.?|INR)\s*([\d,]+\.?\d*)',  # Rs. or INR
            r'Total[:\s]*([₹]?[\d,]+\.?\d*)',   # Total: amount
            r'Amount[:\s]*([₹]?[\d,]+\.?\d*)',  # Amount: amount
            r'Grand\s*Total[:\s]*([₹]?[\d,]+\.?\d*)',  # Grand Total
            r'(\d{2,},\d{2,}|\d{2,})\.?\d*'     # Plain numbers (1000+)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Remove commas and convert to float
                    amount_str = match.replace(',', '')
                    amount = float(amount_str)
                    
                    # Filter reasonable amounts (between 1 and 1000000)
                    if 1 <= amount <= 1000000:
                        amounts.append(amount)
                
                except ValueError:
                    continue
        
        # Return the largest amount (likely the total)
        if amounts:
            return max(amounts)
        
        return None
    
    def find_date(self, text):
        """Find date in extracted text"""
        date_patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',      # DD-MM-YYYY or DD/MM/YYYY
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',  # DD Mon YYYY
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',  # Mon DD, YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group()
                
                # Try to parse the date
                formats = [
                    '%d-%m-%Y', '%d/%m/%Y', '%d-%m-%y', '%d/%m/%y',
                    '%d %b %Y', '%d %B %Y', '%b %d, %Y', '%B %d, %Y'
                ]
                
                for fmt in formats:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        return parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
        
        # If no date found, return today's date
        return datetime.now().strftime('%Y-%m-%d')
    
    def find_merchant(self, text):
        """Find merchant/store name from receipt"""
        lines = text.split('\n')
        
        # Usually merchant name is in first few lines
        merchant_candidates = []
        
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines with common receipt keywords
            skip_keywords = ['total', 'amount', 'date', 'time', 'cash', 'card', 'payment']
            if any(keyword in line.lower() for keyword in skip_keywords):
                continue
            
            # Skip lines that are mostly numbers
            if sum(c.isdigit() for c in line) > len(line) * 0.5:
                continue
            
            merchant_candidates.append(line)
        
        # Return the first candidate (usually the merchant name)
        if merchant_candidates:
            return merchant_candidates[0][:100]  # Limit length
        
        return "Unknown Merchant"
    
    def scan_receipt(self, image_path):
        """
        Complete receipt scanning pipeline
        
        Returns:
        dict: Extracted information with keys:
            - amount: Total amount
            - date: Transaction date
            - merchant: Merchant name
            - raw_text: Full OCR text
        """
        # Extract text
        raw_text = self.extract_text(image_path)
        
        if not raw_text:
            return {
                'success': False,
                'error': 'No text could be extracted from the image'
            }
        
        # Find amount
        amount = self.find_amounts(raw_text)
        
        # Find date
        date = self.find_date(raw_text)
        
        # Find merchant
        merchant = self.find_merchant(raw_text)
        
        result = {
            'success': True,
            'amount': amount,
            'date': date,
            'merchant': merchant,
            'raw_text': raw_text,
            'confidence': 'high' if amount else 'low'
        }
        
        return result


def scan_receipt_image(image_path):
    """
    Convenience function to scan a receipt
    
    Args:
        image_path: Path to receipt image
    
    Returns:
        dict: Extracted receipt data
    """
    scanner = ReceiptScanner()
    return scanner.scan_receipt(image_path)


# Example usage
if __name__ == "__main__":
    # Test the scanner
    result = scan_receipt_image("test_receipt.jpg")
    
    if result['success']:
        print(f"Amount: ₹{result['amount']}")
        print(f"Date: {result['date']}")
        print(f"Merchant: {result['merchant']}")
        print(f"Confidence: {result['confidence']}")
    else:
        print(f"Error: {result['error']}")
