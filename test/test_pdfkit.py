"""
Test file to verify pdfkit PDF generation works.
"""
import os
import pdfkit

def test_pdfkit():
    """Test if pdfkit is working properly."""
    print("Testing pdfkit...")
    try:
        # Create a simple HTML file
        html_content = """
        <html>
            <body>
                <h1>PDFKit Test</h1>
                <p>This is a test document.</p>
            </body>
        </html>
        """
        
        # Write HTML to a file
        with open("test_pdfkit.html", "w") as f:
            f.write(html_content)
        
        # Generate PDF
        pdfkit.from_file("test_pdfkit.html", "test_pdfkit.pdf")
        
        # Check if the PDF was created
        if os.path.exists("test_pdfkit.pdf"):
            print("✅ pdfkit is working correctly!")
            print(f"PDF saved to {os.path.abspath('test_pdfkit.pdf')}")
        else:
            print("❌ pdfkit failed to create the PDF.")
    except Exception as e:
        print(f"❌ pdfkit error: {e}")
    finally:
        # Clean up
        if os.path.exists("test_pdfkit.html"):
            os.remove("test_pdfkit.html")

def test_pdfkit_with_path(wkhtmltopdf_path):
    """Test if pdfkit is working with a specific wkhtmltopdf path."""
    print(f"\nTesting pdfkit with custom path: {wkhtmltopdf_path}")
    try:
        # Create a simple HTML file
        html_content = """
        <html>
            <body>
                <h1>PDFKit Custom Path Test</h1>
                <p>This is a test document.</p>
            </body>
        </html>
        """
        
        # Write HTML to a file
        with open("test_pdfkit_path.html", "w") as f:
            f.write(html_content)
        
        # Configure pdfkit with the custom path
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        
        # Generate PDF
        pdfkit.from_file("test_pdfkit_path.html", "test_pdfkit_path.pdf", configuration=config)
        
        # Check if the PDF was created
        if os.path.exists("test_pdfkit_path.pdf"):
            print("✅ pdfkit with custom path is working correctly!")
            print(f"PDF saved to {os.path.abspath('test_pdfkit_path.pdf')}")
        else:
            print("❌ pdfkit with custom path failed to create the PDF.")
    except Exception as e:
        print(f"❌ pdfkit with custom path error: {e}")
    finally:
        # Clean up
        if os.path.exists("test_pdfkit_path.html"):
            os.remove("test_pdfkit_path.html")

if __name__ == "__main__":
    # Test pdfkit
    test_pdfkit()
    
    # If pdfkit failed, ask for a custom path
    if not os.path.exists("test_pdfkit.pdf"):
        print("\nLet's try with a custom path to wkhtmltopdf.")
        print("Common paths:")
        print("Windows: C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        print("macOS: /usr/local/bin/wkhtmltopdf")
        print("Linux: /usr/bin/wkhtmltopdf")
        
        custom_path = input("\nEnter the path to wkhtmltopdf on your system (or press Enter to skip): ") 