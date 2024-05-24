from pprint import pprint
import logging
import io
from botocore.exceptions import ClientError
from PIL import Image, ImageDraw
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class ImageAnalysis:
    """
    Encapsulates an Amazon Rekognition image. This class is a thin wrapper
    around parts of the Boto3 Amazon Rekognition API.
    """

    def __init__(self, image, image_name, rekognition_client):
        """
        Initializes the image object.

        :param image: Data that defines the image, either the image bytes or
                      an Amazon S3 bucket and object key.
        :param image_name: The name of the image.
        :param rekognition_client: A Boto3 Rekognition client.
        """
        self.image = image
        self.image_name = image_name
        self.rekognition_client = rekognition_client


    @classmethod
    def from_file(cls, image_file_name, rekognition_client, image_name=None):
        """
        Creates a RekognitionImage object from a local file.

        :param image_file_name: The file name of the image. The file is opened and its
                                bytes are read.
        :param rekognition_client: A Boto3 Rekognition client.
        :param image_name: The name of the image. If this is not specified, the
                           file name is used as the image name.
        :return: The RekognitionImage object, initialized with image bytes from the
                 file.
        """
        with open(image_file_name, "rb") as img_file:
            image = {"Bytes": img_file.read()}
        name = image_file_name if image_name is None else image_name
        return cls(image, name, rekognition_client)


    def detect_labels(self, max_labels):
        """
        Detects labels in the image. Labels are objects and people.

        :param max_labels: The maximum number of labels to return.
        :return: The list of labels detected in the image.
        """
        try:
            response = self.rekognition_client.detect_labels(
                Image=self.image, MaxLabels=max_labels
            )
            labels = [ImageLabel(label) for label in response["Labels"]]
            logger.info("Found %s labels in %s.", len(labels), self.image_name)
        except ClientError:
            logger.info("Couldn't detect labels in %s.", self.image_name)
            raise
        else:
            return labels

    def detect_text(self):
        """
        Detects text in the image.

        :return The list of text elements found in the image.
        """
        try:
            response = self.rekognition_client.detect_text(Image=self.image)
            texts = [ImageText(text) for text in response["TextDetections"]]
            logger.info("Found %s texts in %s.", len(texts), self.image_name)
        except ClientError:
            logger.exception("Couldn't detect text in %s.", self.image_name)
            raise
        else:
            return texts


    def show_bounding_boxes(image_bytes, box_sets, colors):
        """
        Draws bounding boxes on an image and shows it with the default image viewer.

        :param image_bytes: The image to draw, as bytes.
        :param box_sets: A list of lists of bounding boxes to draw on the image.
        :param colors: A list of colors to use to draw the bounding boxes.
        """
        image = Image.open(io.BytesIO(image_bytes))
        draw = ImageDraw.Draw(image)
        for boxes, color in zip(box_sets, colors):
            for box in boxes:
                left = image.width * box["Left"]
                top = image.height * box["Top"]
                right = (image.width * box["Width"]) + left
                bottom = (image.height * box["Height"]) + top
                draw.rectangle([left, top, right, bottom], outline=color, width=3)
        image.show()



    def show_polygons(image_bytes, polygons, color):
        """
        Draws polygons on an image and shows it with the default image viewer.

        :param image_bytes: The image to draw, as bytes.
        :param polygons: The list of polygons to draw on the image.
        :param color: The color to use to draw the polygons.
        """
        image = Image.open(io.BytesIO(image_bytes))
        draw = ImageDraw.Draw(image)
        for polygon in polygons:
            draw.polygon(
                [
                    (image.width * point["X"], image.height * point["Y"])
                    for point in polygon
                ],
                outline=color,
            )
        image.show()

class ImageLabel:
    """Encapsulates an Amazon Rekognition label."""

    def __init__(self, label, timestamp=None):
        """
        Initializes the label object.

        :param label: Label data, in the format returned by Amazon Rekognition
                      functions.
        :param timestamp: The time when the label was detected, if the label
                          was detected in a video.
        """
        self.name = label.get("Name")
        self.confidence = label.get("Confidence")
        self.instances = label.get("Instances")
        self.parents = label.get("Parents")
        self.timestamp = timestamp

    def to_dict(self):
        """
        Renders some of the label data to a dict.

        :return: A dict that contains the label data.
        """
        rendering = {}
        if self.name is not None:
            rendering["name"] = self.name
        if self.timestamp is not None:
            rendering["timestamp"] = self.timestamp
        return rendering

class ImageText:
    """Encapsulates an Amazon Rekognition text element."""

    def __init__(self, text_data):
        """
        Initializes the text object.

        :param text_data: Text data, in the format returned by Amazon Rekognition
                          functions.
        """
        self.text = text_data.get("DetectedText")
        self.kind = text_data.get("Type")
        self.id = text_data.get("Id")
        self.parent_id = text_data.get("ParentId")
        self.confidence = text_data.get("Confidence")
        self.geometry = text_data.get("Geometry")

    def to_dict(self):
        """
        Renders some of the text data to a dict.

        :return: A dict that contains the text data.
        """
        rendering = {}
        if self.text is not None:
            rendering["text"] = self.text
        if self.kind is not None:
            rendering["kind"] = self.kind
        if self.geometry is not None:
            rendering["polygon"] = self.geometry.get("Polygon")
        return rendering


def show_bounding_boxes(image_bytes, box_sets, colors):
    """
    Draws bounding boxes on an image and shows it with the default image viewer.

    :param image_bytes: The image to draw, as bytes.
    :param box_sets: A list of lists of bounding boxes to draw on the image.
    :param colors: A list of colors to use to draw the bounding boxes.
    """
    image = Image.open(io.BytesIO(image_bytes))
    draw = ImageDraw.Draw(image)
    for boxes, color in zip(box_sets, colors):
        for box in boxes:
            left = image.width * box["Left"]
            top = image.height * box["Top"]
            right = (image.width * box["Width"]) + left
            bottom = (image.height * box["Height"]) + top
            draw.rectangle([left, top, right, bottom], outline=color, width=3)
    
    image = image.convert('RGB')
    image.save('analyzed_image.jpg')

    return image

def show_polygons(image_bytes, polygons, color):
    """
    Draws polygons on an image and shows it with the default image viewer.

    :param image_bytes: The image to draw, as bytes.
    :param polygons: The list of polygons to draw on the image.
    :param color: The color to use to draw the polygons.
    """
    image = Image.open(io.BytesIO(image_bytes))
    draw = ImageDraw.Draw(image)
    for polygon in polygons:
        draw.polygon(
            [
                (image.width * point["X"], image.height * point["Y"])
                for point in polygon
            ],
            outline=color,
        )
    image.show()
    image = image.convert('RGB')
    image.save('final_analyzed_image.jpg')

    return image

def analyze_image(analyzer):
    """
    Analyze image and highlight the elements and list the analysis labels.
    This function returns a list containing bounding box coordinates and a list containing labels.
    """

    labels = analyzer.detect_labels(100)
    print(f"\nAnalyzed {len(labels)} labels.")
    for label in labels:
        pprint(label.to_dict())
    names = []
    box_sets = []
    colors = ["aqua", "red", "white", "blue", "yellow", "green", "yellow", "lightgreen"]

    for label in labels:
        if label.instances:
            names.append(label.name)
            box_sets.append([inst["BoundingBox"] for inst in label.instances])

    print(f"\n\nShowing bounding boxes for {names}.")
    show_bounding_boxes(
        analyzer.image["Bytes"], box_sets, colors[: len(names)]
    )

    return box_sets, labels

def extract_text(analyzer):
    """
    Extract text content from the given image using Amazon Rekognition. This function will output extracted text content in a txt file named "extracted_text.txt and returns the extracted text content."
    """

    texts = analyzer.detect_text()

    print(f"\nFound {len(texts)} text instances. Here are the texts:")

    text_content = []

    with open("extracted_text.txt", "w+", encoding='utf-8') as f:
        for text in texts:
            content = text.to_dict()['text']
            text_content.append(content)
            pprint(content)
            content += "\n"
            f.write(content)

    show_polygons(
        analyzer.image["Bytes"], [text.geometry["Polygon"] for text in texts], "aqua"
    )

    return text_content

def isolate_features(image_bytes, box_sets):
    """
    Isolate the analyzed elements and save the isolated elements or image named like element0.jpg, element1.jpg, element2.jpg, ... 
    """

    image = Image.open(io.BytesIO(image_bytes))
    im = []
    modified_box_set = []

    for box in box_sets:
        if box not in modified_box_set:
            modified_box_set.append(box)
    
    for boxes in modified_box_set:
        for box in boxes:
            left = image.width * box["Left"]
            top = image.height * box["Top"]
            right = (image.width * box["Width"]) + left
            bottom = (image.height * box["Height"]) + top
            im.append(image.crop((left, top, right, bottom)))
    count = 0
    for i in im:
        i = i.convert('RGB')
        i.save(f'element{count}.jpg')
        count += 1
        i.show()
    
    return count

def createHTML(labels, text_content, count):
    """
    creates a basic html structure with labels, text data and isolated images and outputs a file "index.html".
    """

    html_template = """<html>
    <head></head>
    <body>
    </body>
    </html>
    """

    soup = BeautifulSoup(html_template, 'html.parser')

    text_label = soup.new_tag("h3")
    text_label.string = "Analyzed following labels from the image: "
    soup.body.append(text_label)

    for label in labels:
        tag = soup.new_tag("p")
        tag.string = label.to_dict()['name']
        soup.body.append(tag)

    text_label = soup.new_tag("h3")
    text_label.string = "Text Content Extracted from the image: "
    soup.body.append(text_label)

    for text in text_content:
        tag = soup.new_tag("p")
        tag.string = text
        soup.body.append(tag)

    for i in range(count):
        img_tag = soup.new_tag("img")
        img_tag['src'] = f'./element{i}.jpg'
        soup.body.append(img_tag)

    html_content = soup.contents
    
    with open('index.html', 'w') as html_file:
        for item in html_content:
            html_file.write(str(item))

    return html_content

# createHTML()