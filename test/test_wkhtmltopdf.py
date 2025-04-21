"""
Test file to verify the wkhtmltopdf path configuration works.
"""
import os
import pdfkit

# Use the specific path from resume_export.py
WKHTMLTOPDF_PATH = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"

def test_wkhtmltopdf_with_path():
    """Test if wkhtmltopdf at the specific path works."""
    print(f"Testing wkhtmltopdf with path: {WKHTMLTOPDF_PATH}")
    
    # Check if the executable exists
    if not os.path.exists(WKHTMLTOPDF_PATH):
        print(f"❌ Error: The executable does not exist at the specified path: {WKHTMLTOPDF_PATH}")
        return False
    
    try:
        # Create a simple HTML file
        html_content = """
        <html>
            <body>
                <h1>wkhtmltopdf Test</h1>
                <p>This is a test document to verify if the path is correctly configured.</p>
            </body>
        </html>
        """
        
        # Write HTML to a file
        with open("test_wkhtmltopdf.html", "w") as f:
            f.write(html_content)
        
        # Configure pdfkit with the specific path
        config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
        
        # Generate PDF
        pdfkit.from_file("test_wkhtmltopdf.html", "test_wkhtmltopdf.pdf", configuration=config)
        
        # Check if the PDF was created
        if os.path.exists("test_wkhtmltopdf.pdf"):
            print("✅ Success! PDF generation with wkhtmltopdf works correctly.")
            print(f"PDF saved to {os.path.abspath('test_wkhtmltopdf.pdf')}")
            return True
        else:
            print("❌ Error: PDF file was not created.")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists("test_wkhtmltopdf.html"):
            os.remove("test_wkhtmltopdf.html")

if __name__ == "__main__":
    success = test_wkhtmltopdf_with_path()
    if success:
        print("\nYour configuration is correct. PDF generation should work in the app.")
    else:
        print("\nThere seems to be an issue with the wkhtmltopdf configuration.")
        print("Make sure:")
        print("1. The path is correct (check for typos)")
        print("2. The executable is actually located at that path")
        print("3. The executable has the necessary permissions") 