import logging
import zipfile
import io
import json
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult

# Initialize the logger
logging.basicConfig(level=logging.INFO)

def clean_json(content: json) -> json:

    keys_to_remove = ['Bounds', 'Font', "HasClip", "Lang", "ObjectID", "attributes", "Path", "TextSize"]
    for element in content['elements']:
        for key in keys_to_remove:
            if key in element:
                del element[key]

    indices_to_remove = []
    for i, element in enumerate(content['elements']):
        if 'Text' not in element:
            indices_to_remove.append(i)
            continue
        if element.get('Text') == "\u2022 ":
            indices_to_remove.append(i)
            
    for index in reversed(indices_to_remove):
        del content['elements'][index]

    # print(json.dumps(parsed, indent=4))
    return content

def extract_text_from_pdf(path: str, credentials: ServicePrincipalCredentials):
    file = open(path, 'rb')
    input_stream = file.read()
    file.close()
    # Creates a PDF Services instance
    pdf_services = PDFServices(credentials=credentials)

    # Creates an asset(s) from source file(s) and upload
    input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)

    # Create parameters for the job
    extract_pdf_params = ExtractPDFParams(
        elements_to_extract=[ExtractElementType.TEXT],
    )

    # Creates a new job instance
    extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)

    # Submit the job and gets the job result
    location = pdf_services.submit(extract_pdf_job)
    pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)

    # Get content from the resulting asset(s)
    result_asset: CloudAsset = pdf_services_response.get_result().get_resource()
    stream_asset: StreamAsset = pdf_services.get_content(result_asset)

    # Assuming stream_asset.get_input_stream() returns a file-like object
    input_stream = stream_asset.get_input_stream()

    # Create a BytesIO object from the input stream
    bytes_io = io.BytesIO(input_stream)

    # Open the zip file
    with zipfile.ZipFile(bytes_io, 'r') as zip_ref:
        # List all files in the zip archive
        with zip_ref.open('structuredData.json') as f:
            content = f.read()
            parsed = json.loads(content.decode('utf-8'))
            return(clean_json(parsed))  # Assuming the file is text; decode accordingly