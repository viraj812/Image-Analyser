"""
This is the main python file that achieves the core functionalities which are Image Analysis, Text Extraction, Visual Element Segmentation.
"""

import boto3
from botocore.config import Config
from image_analysis import ImageAnalysis, analyze_image, isolate_features, extract_text, createHTML


my_config = Config(
    region_name = 'ap-south-1',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    },  
)

# instantiating api client AWS Rekognition client
rekognition_client = boto3.client(
    "rekognition", 
    config=my_config, 
    aws_access_key_id="AKIA3FLD44ZFDXCJNCIB", 
    aws_secret_access_key="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"
)

def analyse_image(IMG):
    # creating analyzer object of the ImageAnalysis Class
    analyzer = ImageAnalysis.from_file(
        IMG, rekognition_client
    )

    # analyze labels identified in the image.
    box_sets, labels = analyze_image(analyzer)

    # isolates image elements into seperate images
    feauture_count = isolate_features(analyzer.image["Bytes"], box_sets)

    analyzer = ImageAnalysis.from_file(
        "analyzed_image.jpg", rekognition_client
    )

    # outputs final image as final_analyzed_image.jpg
    text_content = extract_text(analyzer)

    # creates a basic html structure with identified labels, extracted text content, isolated visual elements 
    createHTML(labels, text_content, feauture_count)
