from marker.converters.pdf import PdfConverter
from marker.converters.table import TableConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.config.parser import ConfigParser
# filepath = "../"
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(),override=True)
import os
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

config = {
    "output_format": "markdown", # markdown|json|html
    "use_llm": False,
    "gemini_api_key":GEMINI_API_KEY,
}
config_parser = ConfigParser(config)

converter = PdfConverter(
    config=config_parser.generate_config_dict(),
    artifact_dict=create_model_dict(),
    processor_list=config_parser.get_processors(),
    renderer=config_parser.get_renderer(),
    llm_service=config_parser.get_llm_service()
)
rendered = converter("OG.pdf")
text, middle, images = text_from_rendered(rendered)

with open("OG_markdown.md",'w') as f:
    f.write(text)

# converter = TableConverter(
#     artifact_dict=create_model_dict(),
# )
# rendered = converter("OG.pdf")
# text, middle, images = text_from_rendered(rendered)

# print(text)
print(middle)
print(images)
print(images.keys())

# from PIL import Image
#
# # Your dictionary with PIL.Image.Image objects
# image_dict = {
#     '_page_0_Picture_1.jpeg': Image.open('_page_0_Picture_1.jpeg'),  # Example; replace with your actual images
#     '_page_0_Picture_17.jpeg': Image.open('_page_0_Picture_17.jpeg')
# }
#
# # Iterate through the dictionary and display each image
# for image_name, image in image_dict.items():
#     print(f"Displaying: {image_name}")
#     image.show()