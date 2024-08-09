from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from pdf2image import convert_from_bytes
import base64
from openai import AzureOpenAI
import json
import io


class DocumentDataExtractorOptions:
    """Defines the configuration options for extracting data from a document using Azure OpenAI."""

    def __init__(self, system_prompt: str, extraction_prompt: str, endpoint: str, deployment_name: str, max_tokens: int = 4096, temperature: float = 0.1, top_p: float = 0.1):
        """Initializes a new instance of the DocumentDataExtractorOptions class.

        :param system_prompt: The system prompt to provide context to the model on its function.
        :param extraction_prompt: The prompt to use for extracting data from the document, including the expected output format.
        :param endpoint: The Azure OpenAI endpoint to use for the request.
        :param deployment_name: The name of the model deployment to use for the request.
        :param max_tokens: The maximum number of tokens to generate in the response. Default is 4096.
        :param temperature: The sampling temperature for the model. Default is 0.1.
        :param top_p: The nucleus sampling parameter for the model. Default is 0.1.
        """

        self.system_prompt = system_prompt
        self.extraction_prompt = extraction_prompt
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p


class DocumentDataExtractor:
    """Defines a class for extracting structured data from a document using Azure OpenAI GPT models that support image inputs."""

    def __init__(self, credential: DefaultAzureCredential):
        """Initializes a new instance of the DocumentDataExtractor class.

        :param credential: The Azure credential to use for authenticating with the Azure OpenAI service.
        """

        self.credential = credential

    def from_bytes(self, document_bytes: bytes, options: DocumentDataExtractorOptions) -> dict:
        """Extracts structured data from the specified document bytes by converting the document to images and using an Azure OpenAI model to extract the data.

        :param document_bytes: The byte array content of the document to extract data from.
        :param options: The options for configuring the Azure OpenAI request for extracting data.
        :return: The structured data extracted from the document as a dictionary.
        """

        client = self.__get_openai_client__(options)

        image_uris = self.__get_document_image_uris__(document_bytes)

        user_content = []
        user_content.append({
            "type": "text",
            "text": options.extraction_prompt
        })

        for image_uri in image_uris:
            user_content.append({
                "type": "image_url",
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
        """Converts the specified document bytes to images using the pdf2image library and returns the image URIs.

        To call this method, poppler-utils must be installed on the system.
        """

        pages = convert_from_bytes(document_bytes)

        image_uris = []
        for page in pages:
            byteIO = io.BytesIO()
            page.save(byteIO, format='PNG')
            base64_data = base64.b64encode(byteIO.getvalue()).decode('utf-8')
            image_uris.append(f"data:image/png;base64,{base64_data}")

        return image_uris
