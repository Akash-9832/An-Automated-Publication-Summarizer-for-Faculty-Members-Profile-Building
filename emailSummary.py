import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication # For attaching PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from dotenv import load_dotenv
import os

load_dotenv()

def create_pdf_from_string(text_content, filename="email_content.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    textobject = c.beginText()
    textobject.setTextOrigin(50, 750) # Set starting position (x, y)

    # Split the long string into lines that fit the page width
    # This is a basic line-wrapping; for complex text, consider ReportLab's flowables
    max_width = 500 # Approximate width for default font
    words = text_content.split(' ')
    line = []
    for word in words:
        if c.stringWidth(' '.join(line + [word]), "Times New Roman", 14) < max_width:
            line.append(word)
        else:
            textobject.textLine(' '.join(line))
            line = [word]
    if line: # Add any remaining words
        textobject.textLine(' '.join(line))

    c.drawText(textobject)
    c.save()
    return filename

def send_email_with_pdf(sender_email, sender_password, receiver_email, subject, message_body, pdf_filepath):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Attach the main message body as plain text
    msg.attach(MIMEText(message_body, 'plain'))

    # Attach the PDF file
    try:
        with open(pdf_filepath, 'rb') as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_filepath))
            msg.attach(attach)
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_filepath}")
        return

    try:
        # Connect to the SMTP server (for Gmail, use smtp.gmail.com)
        # Use 465 for SSL (recommended) or 587 for TLS
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            # Login to your email account
            smtp.login(sender_email, sender_password)
            # Send the email
            smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def user_config(SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL, EMAIL_SUBJECT, EMAIL_BODY_TEXT, LONG_STRING):
    pdf_filename = "Scholarly_Summary.pdf"
    generated_pdf_path = create_pdf_from_string(LONG_STRING, pdf_filename)
    if generated_pdf_path:
        send_email_with_pdf(SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL, EMAIL_SUBJECT, EMAIL_BODY_TEXT, generated_pdf_path)
        # Clean up the generated PDF file after sending
        try:
            os.remove(generated_pdf_path)
            print(f"Removed temporary PDF file: {generated_pdf_path}")
        except OSError as e:
            print(f"Error removing file {generated_pdf_path}: {e}")

if __name__ == "__main__":
    SENDER_EMAIL = "akash24400221003@tecb.edu.in"  # Your Gmail address
    SENDER_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # Your generated App Password
    RECEIVER_EMAIL = "akashmodak266@gmail.com" # The recipient's email address
    EMAIL_SUBJECT = "Your Publication Summary from Scholarly"
    EMAIL_BODY_TEXT = "Please find the detailed information about CVD research in the attached PDF document."
    LONG_STRING = """Diagnosing cardiovascular disease (CVD) is a crucial issue in healthcare and research on machine learning. Machine-learning techniques can predict risk at an early stage of CVD based on the features of regular lifestyles and results of a few medical tests. The Framingham Heart Study dataset has 15.2% of patients with CVD, which increases the likelihood of classifying CVD patients as healthy. We create approximately equal instances of each class by over-sampling."""
    user_config(SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL, EMAIL_SUBJECT, EMAIL_BODY_TEXT, LONG_STRING)


