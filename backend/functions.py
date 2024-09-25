import os
import base64
import tempfile
import re
import requests
from flask import Blueprint, request, jsonify
# from routes.auth import token_required , subscription_required
# from routes.ipqs_util import check_url_reputation, analyze_file_url, get_file_hash
# from routes.vt_util import scan_url, get_scan_results, format_scan_results, scan_file, determine_safety
from pii_util import analyze_pii, anonymize_text

# from PIL import Image
# import pytesseract
# import fitz  # PyMuPDF for PDF handling
# import cv2
import io
from functools import wraps
# from models import User
import time
import mimetypes
from io import BytesIO
from tempfile import NamedTemporaryFile

function_routes = Blueprint('functions', __name__)

IPQS_API_KEY = 'w0REndl0EIym4aly4naTP21ATEq1p335'
VT_API_KEY = '4e342ae597b2aedd2f9882b959cd3e749497f6bd6621d2c0b2a18e51f426797c'
HIBP_API_KEY = '2442b3cf4bb84e6a99934d6d93d89742'



# Configure Tesseract executable path
# pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'


# def extract_text_from_image(image_path):
#     image = Image.open(image_path)
#     text = pytesseract.image_to_string(image)
#     return text.strip()

# def extract_text_from_pdf(pdf_path):
#     text = ""
#     pdf_document = fitz.open(pdf_path)
#     for page_num in range(len(pdf_document)):
#         page = pdf_document.load_page(page_num)
#         extracted_text = page.get_text()
#         if extracted_text:
#             text += extracted_text + "\n"
#     pdf_document.close()
#     return text.strip()

# def convert_pdf_to_images(pdf_path):
#     pdf_document = fitz.open(pdf_path)
#     image_paths = []
#     for page_num in range(len(pdf_document)):
#         page = pdf_document.load_page(page_num)
#         image_list = page.get_images(full=True)
#         for img_index, img in enumerate(image_list):
#             xref = img[0]
#             base_image = pdf_document.extract_image(xref)
#             image_bytes = base_image["image"]
#             image = Image.open(io.BytesIO(image_bytes))
#             image_frames = tempfile.mkdtemp()
#             image_path = os.path.join(image_frames, f'page_{page_num + 1}img{img_index + 1}.png')
#             image.save(image_path, "PNG")
#             image_paths.append(image_path)
#     pdf_document.close()
#     return image_paths

# def extract_text_from_pdf_images(pdf_path):
#     image_paths = convert_pdf_to_images(pdf_path)
#     text = ""
#     for image_path in image_paths:
#         text += extract_text_from_image(image_path) + "\n"
#     return text.strip()

# def extract_text_from_video(video_path):
#     src_vid = cv2.VideoCapture(video_path)
#     index = 0
#     text = ""
#     while src_vid.isOpened():
#         ret, frame = src_vid.read()
#         if not ret:
#             break
#         if index % 100 == 0:
#             frame_path = tempfile.mktemp(suffix='.png')
#             cv2.imwrite(frame_path, frame)
#             text += extract_text_from_image(frame_path) + "\n"
#         index += 1
#     src_vid.release()
#     return text.strip()

# def is_image(file_path):
#     try:
#         Image.open(file_path)
#         return True
#     except IOError:
#         return False

# def process_file(file_path):
#     if is_image(file_path):
#         text = extract_text_from_image(file_path)
#     elif file_path.lower().endswith('.pdf'):
#         text = extract_text_from_pdf(file_path)
#         if not text:
#             text = extract_text_from_pdf_images(file_path)
#     elif file_path.lower().endswith('.mp4') or file_path.lower().endswith('.avi'):
#         text = extract_text_from_video(file_path)
#     else:
#         raise ValueError("Unsupported file format.")
    
#     return text



# def download_base64_images(image_data, output_dir):
#     os.makedirs(output_dir, exist_ok=True)
    
#     try:
#         encoded_data = image_data.split(',')[1]
#         decoded_data = base64.b64decode(encoded_data)
#         extension = image_data.split(';')[0].split('/')[-1]
#         filename = os.path.join(output_dir, f'uploaded_image.{extension}')
#         with open(filename, 'wb') as file:
#             file.write(decoded_data)
        
#         # Extract text from the downloaded image
#         extracted_text = process_file(filename)
        
#         # Analyze PII in the extracted text
#         pii_results = analyze_pii(extracted_text)
        
#         # Prepare PII detection results
#         detected_entities = [
#             {
#                 'entity': result.entity_type,
#                 'start': result.start,
#                 'end': result.end,
#                 'score': result.score
#             } for result in pii_results
#         ]


#         '''checking the email breachout from the upoaded files'''
#          # Extract emails from the detected entities
#         email_entities = [entity for entity in detected_entities if entity['entity'] == "EMAIL_ADDRESS"]
#         emails = [extracted_text[email_entity['start']:email_entity['end']] for email_entity in email_entities]


#          # Perform file scanning after saving
#         scan_results = scan_downloaded_file(filename)
        
#         # Check for email breaches if there are any emails detected
#         if emails:
#             breach_results = check_email_breach(emails)
#             email_breach_results = [{'email': email, 'breaches': breach_results[email]} for email in emails]
#         else:
#             email_breach_results = []
        
#         return {
#             'extracted_text': extracted_text,
#             'detected_entities': detected_entities,
#             'email_breach_results': email_breach_results,
#             'scan_file': scan_results,
#             'download from ': 'based64'
#         }
#         # return {'extracted_text': extracted_text, 'detected_entities': detected_entities}
        
#     except IndexError:
#         return {'error': f'Invalid format for image data: {image_data}'}
#     except Exception as e:
#         return {'error': f'Failed to process image data: {str(e)}'}
    


# def download_from_url(url):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Check if request was successful
        
#         # Get file extension from URL or content type
#         content_type = response.headers.get('Content-Type', '')
#         extension = content_type.split('/')[-1] if '/' in content_type else url.split('.')[-1]
#         filename = os.path.join('downloaded_files', f'downloaded_file.{extension}')
        
#         os.makedirs(os.path.dirname(filename), exist_ok=True)
        
#         with open(filename, 'wb') as file:
#             file.write(response.content)
        
#         # Process downloaded file
#         extracted_text = process_file(filename)
        
#         # Analyze PII in the extracted text
#         pii_results = analyze_pii(extracted_text)
        
#         detected_entities = [
#             {
#                 'entity': result.entity_type,
#                 'start': result.start,
#                 'end': result.end,
#                 'score': result.score
#             } for result in pii_results
#         ]
        
#         email_entities = [entity for entity in detected_entities if entity['entity'] == "EMAIL_ADDRESS"]
#         emails = [extracted_text[email_entity['start']:email_entity['end']] for email_entity in email_entities]
        
#         scan_results = scan_downloaded_file(filename)
        
#         if emails:
#             breach_results = check_email_breach(emails)
#             email_breach_results = [{'email': email, 'breaches': breach_results[email]} for email in emails]
#         else:
#             email_breach_results = []
        
#         return {
#             'extracted_text': extracted_text,
#             'detected_entities': detected_entities,
#             'email_breach_results': email_breach_results,
#             'scan_file': scan_results,
#             'download form':'url'
#         }
    
#     except requests.RequestException as e:
#         return {'error': f'Failed to download file from URL: {str(e)}'}
#     except Exception as e:
#         return {'error': f'Failed to process downloaded file: {str(e)}'}
    

# def download_from_url(url):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Check if request was successful
        
#         # Get file extension from URL or content type
#         content_type = response.headers.get('Content-Type', '')
#         extension = content_type.split('/')[-1] if '/' in content_type else url.split('.')[-1]
#         filename = os.path.join('downloaded_files', f'downloaded_file.{extension}')
        
#         os.makedirs(os.path.dirname(filename), exist_ok=True)
        
#         with open(filename, 'wb') as file:
#             file.write(response.content)
        
#         # Process downloaded file
#         extracted_text = process_file(filename)
        
#         # Analyze PII in the extracted text
#         pii_results = analyze_pii(extracted_text)
        
#         detected_entities = [
#             {
#                 'entity': result.entity_type,
#                 'start': result.start,
#                 'end': result.end,
#                 'score': result.score
#             } for result in pii_results
#         ]
        
#         email_entities = [entity for entity in detected_entities if entity['entity'] == "EMAIL_ADDRESS"]
#         emails = [extracted_text[email_entity['start']:email_entity['end']] for email_entity in email_entities]
        
#         scan_results = scan_downloaded_file(filename)
        
#         if emails:
#             breach_results = check_email_breach(emails)
#             email_breach_results = [{'email': email, 'breaches': breach_results[email]} for email in emails]
#         else:
#             email_breach_results = []
        
#         return {
#             'extracted_text': extracted_text,
#             'detected_entities': detected_entities,
#             'email_breach_results': email_breach_results,
#             'scan_file': scan_results
#         }
    
#     except requests.RequestException as e:
#         return {'error': f'Failed to download file from URL: {str(e)}'}
#     except Exception as e:
#         return {'error': f'Failed to process downloaded file: {str(e)}'}


# def download_from_url(url):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Check if request was successful
#         # Use in-memory BytesIO object
#         file_content = BytesIO(response.content)
        
#         # Temporarily save the file and use its path
#         with NamedTemporaryFile(delete=False) as temp_file:
#             temp_file.write(file_content.getvalue())  # Write the in-memory content to the temp file
#             temp_file_path = temp_file.name  # Get the temporary file path
        
#         # Scan the temporary file using its path
#         scan_results = scan_download_url(temp_file_path)
        
#         return {
#             'scan_file': scan_results,
#             'download from': 'url'
#         }
    
#     except requests.RequestException as e:
#         return {'error': f'Failed to download file from URL: {str(e)}'}
#     except Exception as e:
#         return {'error': f'Failed to process downloaded file: {str(e)}'}
#     finally:
#         # Clean up the temporary file if it exists
#         if 'temp_file_path' in locals():
#             try:
#                 os.remove(temp_file_path)
#             except Exception as e:
#                 print(f"Failed to delete temporary file: {str(e)}")


# def analyze_file_(url):
        
    # uploaded_file = url
    # if uploaded_file.filename == '':
    #     return 'No selected file', 400

    # file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
    # uploaded_file.save(file_path)

    # # Optionally, use the file hash for malware analysis
    # file_hash = get_file_hash(file_path)
    
    # # Example: Sending the file hash to IPQS for malware analysis
    # result = analyze_file_url(file_hash)  

    # return jsonify(result)

# def analyze_file(url,IPQS_API_KEY):
    

    # if not url:
    #     return 'No URL provided', 400

    # # Send the file URL to IPQS for malware analysis
    # result = analyze_file_url(url,IPQS_API_KEY)

    # return jsonify(result)

    # if not url:
    #     return {'error': 'No URL provided'}, 400

    # # If it's a URL, send the file URL to IPQS for malware analysis
    # if url.startswith('http://') or url.startswith('https://'):
    #     result = analyze_file_url(url, IPQS_API_KEY)
    # else:
    #     return {'error': 'Invalid URL provided'}, 400

    # return result
# def scan_downloaded_file(file_path):
#     file_id = scan_file(file_path)
#     if file_id:
#         scan_results = get_scan_results(file_id)
#         if scan_results:
#             formatted_results = format_scan_results(scan_results)
#             return {'scan_results': formatted_results}
#         else:
#             return {'error': 'Failed to retrieve scan results'}
#     else:
#         return {'error': 'File scan failed'}
    

# def scan_download_url(file_path):
#     '''url file scan for simple results'''
#     file_id = scan_file(file_path)
#     if file_id:
#         scan_results = get_scan_results(file_id)
#         if scan_results:
#             simple_results = determine_safety(scan_results)
#             return {'scan_results': simple_results}
#         else:
#             return {'error':'Failed to retrieve scan results'}
#     else:
#         return {'error':'File scan failed'}

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None




def check_email_breach(emails):
    breaches = {}
    
    for email in emails:
        if is_valid_email(email):
            url = f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}'
            headers = {
                'hibp-api-key': HIBP_API_KEY,
                'User-Agent': 'FlaskApp',
                'Content-Type': 'application/json'
            }
            try:
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    breach_list = response.json()
                    detailed_breaches = []
                    
                    for breach in breach_list:
                        breach_name = breach.get('Name', 'N/A')
                        breach_details_url = f"https://haveibeenpwned.com/api/v3/breach/{breach_name}"
                        breach_details_response = requests.get(breach_details_url, headers=headers)
                        
                        if breach_details_response.status_code == 200:
                            breach_details = breach_details_response.json()
                            detailed_breach_info = {
                                'Name': breach.get('Name', 'N/A'),
                                'Title': breach_details.get('Title', 'N/A'),
                                'Description': breach_details.get('Description', 'N/A'),
                                'BreachDate': breach_details.get('BreachDate', 'N/A'),
                                'DataClasses': breach_details.get('DataClasses', []),
                                'AddedDate': breach_details.get('AddedDate', 'N/A'),
                                'ModifiedDate': breach_details.get('ModifiedDate', 'N/A'),
                                'PwnCount': breach_details.get('PwnCount', 0),
                                'IsVerified': breach_details.get('IsVerified', False),
                                'IsFabricated': breach_details.get('IsFabricated', False),
                                'IsSensitive': breach_details.get('IsSensitive', False),
                                'IsSpamList': breach_details.get('IsSpamList', False)
                            }
                            detailed_breaches.append(detailed_breach_info)
                        else:
                            detailed_breaches.append({
                                'Name': breach.get('Name', 'N/A'),
                                'Title': 'N/A',
                                'Error': 'Failed to fetch detailed information'
                            })
                    
                    breaches[email] = detailed_breaches
                
                elif response.status_code == 404:
                    breaches[email] = [{'message': 'Email not found in any breaches'}]
                
                elif response.status_code == 401:
                    breaches[email] = [{'error': 'Unauthorized. Check your API key.'}]
                
                elif response.status_code == 403:
                    breaches[email] = [{'error': 'Forbidden. You are not allowed to access this resource.'}]
                
                elif response.status_code == 429:
                    breaches[email] = [{'error': 'Too many requests. You are being rate limited.'}]
                    time.sleep(5)
                    # Recursively call the function with the same email to retry
                    retry_result = check_email_breach([email])
                    breaches.update(retry_result)
                else:
                    breaches[email] = [{'error': f'Unexpected error: {response.status_code}'}]
            
            except requests.exceptions.RequestException as e:
                breaches[email] = [{'error': f'Request error: {str(e)}'}]
            
        else:
            breaches[email] = [{'error': 'Invalid email format'}]
    
    return breaches


@function_routes.route('/scan', methods=['POST'])
# @token_required
# @subscription_required
# def scan(current_user):
def scan():
    # if 'file' in request.json:
    #     file_data = request.json['file']
    #     print(file_data)
    #     # Check if the file data is a URL or Base64 data
    #     if file_data.startswith('http://') or file_data.startswith('https://'):
    #         response = download_from_url(file_data)
        
    #     else:
    #         output_directory = 'downloaded_images'
    #         response = download_base64_images(file_data, output_directory)
        
    #     if 'error' in response:
    #         return jsonify(response), 400
        
        # return jsonify(response), 200

    # elif 'url' in request.json:
    #     url = request.json['url']
    #     reputation_results = check_url_reputation(url, IPQS_API_KEY)
    #     url_id = scan_url(url)
    #     if url_id:
    #         vt_scan_results = get_scan_results(url_id)
    #         if vt_scan_results:
    #             formatted_vt_results = format_scan_results(vt_scan_results)
    #         else:
    #             return jsonify({'error': 'Failed to retrieve VirusTotal scan results'}), 500
    #     else:
    #         return jsonify({'error': 'URL submission to VirusTotal failed'}), 500

    #     combined_results = {'ipqs': reputation_results, 'virustotal': formatted_vt_results}
    #     return jsonify(combined_results)

    # elif 'url_reputation' in request.json:
    #     url = request.json['url_reputation']
    #     reputation_results = check_url_reputation(url, IPQS_API_KEY)
    #     url_id = scan_url(url)
    #     if url_id:
    #         vt_scan_results = get_scan_results(url_id)
    #         if vt_scan_results:
    #             formatted_vt_results = format_scan_results(vt_scan_results)
    #         else:
    #             return jsonify({'error': 'Failed to retrieve VirusTotal scan results'}), 500
    #     else:
    #         return jsonify({'error': 'URL submission to VirusTotal failed'}), 500

    #     combined_results = {'ipqs': reputation_results, 'virustotal': formatted_vt_results}
    #     return jsonify(combined_results)

    if 'pii_text' in request.json:
        text = request.json['pii_text']
        print(text)
        results = analyze_pii(text)
        detected_entities = [
            {
                'entity': result.entity_type,
                'start': result.start,
                'end': result.end,
                'score': result.score
            } for result in results
        ]
        
        email_entities = [entity for entity in detected_entities if entity['entity'] == "EMAIL_ADDRESS"]
        emails = [text[email_entity['start']:email_entity['end']] for email_entity in email_entities]
        
        if emails:
            breach_results = check_email_breach(emails)
            email_breach_results = [{'email': email, 'breaches': breach_results[email]} for email in emails]
            print(email_breach_results)
        else:
            email_breach_results = []

        return jsonify({'detected_entities': detected_entities, 'email_breach_results': email_breach_results})
    

    # elif 'filename' in request.json:
    #     data = request.json
    #     downloadurl = data.get('downloadurl')
    #     filename = data.get('filename')

    #     if not downloadurl or not filename:
    #         return jsonify({'error': 'File data or filename missing'}), 400

        # try:
            # # Remove base64 metadata if present
            # if downloadurl.startswith("data:image"):
            #     downloadurl = downloadurl.split(",")[1]

            # # Decode base64 file data
            # file_data = base64.b64decode(downloadurl)
            
            # # Save the file temporarily
            # with open(filename, 'wb') as f:
            #     f.write(file_data)

            # # Scan the file using VirusTotal
            # scan_results = scan_downloaded_file(filename)
            # # formatted_results = format_scan_results(scan_results)
            # print(scan_results)
            # # Optionally, delete the file after scanning
            # os.remove(filename)
            # return jsonify({'message': 'File processed successfully', 'scan_results': scan_results})

        # except Exception as e:
        #     return jsonify({'error': str(e)}), 500
    
    # elif 'anonymize_text' in request.json:
    #     text = request.json['anonymize_text']
    #     results = analyze_pii(text)
    #     anonymized_text = anonymize_text(text, results)
    #     return jsonify({'anonymized_text': anonymized_text})
    
    else:
        return jsonify({'error': 'No file, URL, URL reputation, PII text, or anonymize text provided'}), 400