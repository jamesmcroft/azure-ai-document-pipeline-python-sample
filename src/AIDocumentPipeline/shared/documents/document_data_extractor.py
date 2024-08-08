from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from pdf2image import convert_from_bytes
import base64
from openai import AzureOpenAI
import json


class DocumentDataExtractorOptions:
    def __init__(self, system_prompt: str, extraction_prompt: str, endpoint: str, deployment_name: str, max_tokens: int = 4096, temperature: float = 0.1, top_p: float = 0.1):
        self.system_prompt = system_prompt
        self.extraction_prompt = extraction_prompt
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p


class DocumentDataExtractor:
    def __init__(self, credential: DefaultAzureCredential):
        self.credential = credential

    def from_bytes(self, document_bytes: bytes, options: DocumentDataExtractorOptions) -> dict:
        client = self.__get_openai_client__(options)

        image_uris = self.__get_document_image_uris__(document_bytes)

        user_content = []
        user_content.append({
            "type": "text",
            "text": options.extraction_prompt
        })

        for image_uri in image_uris:
            user_content.append({
                "type": "image_uri",
                "image_url": {
                    "url": image_uri
                }
            })

        response = client.chat.completions.create(
            model=options.deployment_name,
            messages=[
                {
                    "role": "system",
                    "content": options.system_prompt
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            max_tokens=options.max_tokens,
            temperature=options.temperature,
            top_p=options.top_p
        )

        response_content = response.choices[0].message.content
        return json.loads(response_content)

    def __get_openai_client__(self, options: DocumentDataExtractorOptions) -> AzureOpenAI:
        token_provider = get_bearer_token_provider(
            self.credential, "https://cognitiveservices.azure.com/.default")

        client = AzureOpenAI(
            api_version="2024-05-01-preview",
            azure_endpoint=options.endpoint,
            azure_ad_token_provider=token_provider)

        return client

    def __get_document_image_uris__(self, document_bytes: bytes) -> list:
        pages = convert_from_bytes(document_bytes)

        image_uris = []
        for page in pages:
            base64_data = base64.b64encode(page.tobytes()).decode('utf-8')
            image_uris.append(f"data:image/jpeg;base64,{base64_data}")

        return image_uris
