import json
import os
from typing import List, Dict
from llama_index.core import Document, SimpleDirectoryReader
from llama_index.readers.file.flat.base import BaseReader

class CustomJsonLoader(BaseReader):
    def __init__(self, input_dir:str):
        self.input_dir = input_dir

    def _extract_data_and_metadata(self, json_obj:dict, path: str = "", metadata={}) -> List[Dict[str, any]]:
        """Recursively extract text from JSON, including the path to the data, keeping metadata"""
        data = []

        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                new_path = f"{path}/{key}"
                new_metadata = metadata.copy()
                new_metadata["path"]=new_path
                data.extend(self._extract_data_and_metadata(value, new_path, new_metadata))
        elif isinstance(json_obj, list):
            for idx, item in enumerate(json_obj):
                new_path = f"{path}/{idx}"
                new_metadata = metadata.copy()
                new_metadata["path"]=new_path
                data.extend(self._extract_data_and_metadata(item, new_path, new_metadata))
        elif isinstance(json_obj, str):
            metadata_copy = metadata.copy()
            metadata_copy["value"]=json_obj
            data.append({"text":f"{path}: {json_obj}", "metadata":metadata_copy})

        return data

    def load_data(self) -> List[Document]:
        docs = []
        for filename in os.listdir(self.input_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.input_dir, filename)
                with open(filepath, 'r') as f:
                  try:
                    json_data = json.load(f)
                    data = self._extract_data_and_metadata(json_data)
                    for d in data:
                        d["metadata"]["file_name"] = filename
                        doc = Document(text=d["text"], metadata=d["metadata"])
                        docs.append(doc)
                  except json.JSONDecodeError:
                        print(f"Error parsing JSON file: {filename}")
        return docs

if __name__ == "__main__":

    path = os.path.join(os.curdir,"../resources")

    cjl = CustomJsonLoader(path)
    docs = cjl.load_data()
    for doc in docs:
        print(doc.text)

    ad = {
        "action" : "Cutting",
        "template" : "this is template action designator",
        "parameters" : {
            "object" : {
                "name" : "apple",
                "color" : "red",
                "size" : "small",
                "shape" : "round"
            },
            "tool": {
                "name": "knife",
                "color": "black",
                "size": "big",
                "shape": "plane"
            }
        }
    }