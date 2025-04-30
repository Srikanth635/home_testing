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

# Input directory containing PDFs
input_dir = "resources/set1"
output_dir = "data_resources"

# Ensure the input directory exists
if not os.path.exists(input_dir):
    raise FileNotFoundError(f"Input directory {input_dir} does not exist")

for pdf_file in os.listdir(input_dir):
    if not pdf_file.lower().endswith(".pdf"):
        continue  # Skip non-PDF files

    pdf_path = os.path.join(input_dir, pdf_file)
    pdf_filename = os.path.splitext(pdf_file)[0]  # Get filename without extension (e.g., 'OG')

    # Create output folder named after the PDF file
    output_folder = os.path.join(output_dir, pdf_filename)
    os.makedirs(output_folder, exist_ok=True)

    # Create images subfolder
    image_folder = os.path.join(output_folder, "images")
    os.makedirs(image_folder, exist_ok=True)

    print(f"Processing {pdf_file}...")

    # Convert PDF to markdown and extract images
    try:
        rendered = converter(pdf_path)
        text, middle, images = text_from_rendered(rendered)

        # Save markdown output
        markdown_path = os.path.join(output_folder, f"{pdf_filename}.md")
        with open(markdown_path, 'w') as f:
            f.write(text)
        print(f"Saved markdown: {markdown_path}")

        # Save images to the images subfolder
        for image_name, image_obj in images.items():
            image_path = os.path.join(image_folder, image_name)
            image_obj.save(image_path, format="JPEG")
            print(f"Saved image: {image_path}")

    except Exception as e:
        print(f"Error processing {pdf_file}: {e}")

print("Processing complete.")



# rendered = converter("resources/set1/OG.pdf")
# text, middle, images = text_from_rendered(rendered)
#
# pdf_filename = os.path.splitext(os.path.basename(pdf_file))[0]  # Get 'OG' from 'OG.pdf'
# image_folder = f"{pdf_filename}_images"  # e.g., 'OG_images'
# os.makedirs(image_folder, exist_ok=True)
#
# with open("OG_markdown.md",'w') as f:
#     f.write(text)
#
# # converter = TableConverter(
# #     artifact_dict=create_model_dict(),
# # )
# # rendered = converter("OG.pdf")
# # text, middle, images = text_from_rendered(rendered)
#
# # print(text)
# print(middle)
# print(images)
# print(images.keys())
#
# # from PIL import Image
# #
# # # Your dictionary with PIL.Image.Image objects
# # image_dict = {
# #     '_page_0_Picture_1.jpeg': Image.open('_page_0_Picture_1.jpeg'),  # Example; replace with your actual images
# #     '_page_0_Picture_17.jpeg': Image.open('_page_0_Picture_17.jpeg')
# # }
# #
# # # Iterate through the dictionary and display each image
# # for image_name, image in image_dict.items():
# #     print(f"Displaying: {image_name}")
# #     image.show()