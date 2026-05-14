import base64
import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

load_dotenv()


class FigureCaptioner:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

    def caption_figure(self, image_path: str) -> str:
        image_base64 = self._encode_image(image_path)
        extension = Path(image_path).suffix.lower().strip(".")

        mime_types = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png"}
        mime = mime_types.get(extension, "jpeg")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{mime};base64,{image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "You are analyzing a figure from a scientific paper. Describe what this figure shows in detail: the type of visualization, the data it presents, axes labels if visible, and the main finding it illustrates."
                    }
                ]
            }],
            temperature=0.2
        )
        return response.choices[0].message.content

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        return base64.b64encode(image_bytes).decode("utf-8")
