from typing import List, Union, Dict, Any
import requests

from yandex_gpt.yandex_gpt_config_manager import YandexGPTConfigManager


class YandexGPT:
    def __init__(
            self,
            config_manager: Union[YandexGPTConfigManager, Dict[str, Any]],
    ) -> None:
        self.config_manager = config_manager

    def send_completion_request(
            self,
            messages: List[Dict[str, Any]],
            temperature: float = 0.6,
            max_tokens: int = 1000,
            stream: bool = False,
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    ) -> Dict[str, Any]:
        # ensuring required fields are not None or empty
        if not all([
            getattr(self.config_manager, 'model_type', None),
            getattr(self.config_manager, 'iam_token', None),
            getattr(self.config_manager, 'catalog_id', None)
        ]):
            raise ValueError("Model type, IAM token, and catalog ID must be set to send a completion request.")

        # preparing headers and data for the request
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config_manager.iam_token}",
            "x-folder-id": self.config_manager.catalog_id
        }
        data: Dict[str, Any] = {
            "modelUri": f"gpt:"
                        f"//{self.config_manager.catalog_id}"
                        f"/{self.config_manager.model_type}"
                        f"/latest",
            "completionOptions": {
                "stream": stream,
                "temperature": temperature,
                "maxTokens": max_tokens
            },
            "messages": messages
        }

        # sending the completion request
        response = requests.post(completion_url, headers=headers, json=data)

        # checking and returning the response
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to send completion request. Status code: {response.status_code}\n{response.text}")
