from typing import List, Union, Dict, Any

import aiohttp

from yandex_gpt.yandex_gpt_config_manager import YandexGPTConfigManager


class YandexGPT:
    def __init__(
            self,
            config_manager: Union[YandexGPTConfigManager, Dict[str, Any]],
    ) -> None:
        self.config_manager = config_manager

    async def send_completion_request(
            self,
            messages: List[Dict[str, Any]],
            temperature: float = 0.6,
            max_tokens: int = 1000,
            stream: bool = False,
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    ) -> Dict[str, Any]:
        # checking config manager
        if not all([
            getattr(self.config_manager, 'model_type', None),
            getattr(self.config_manager, 'iam_token', None),
            getattr(self.config_manager, 'catalog_id', None)
        ]):
            raise ValueError("Model type, IAM token, and catalog ID must be set in config manager to send a "
                             "completion request.")

        # making request
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config_manager.iam_token}",
            "x-folder-id": self.config_manager.catalog_id
        }
        data: Dict[str, Any] = {
            "modelUri": f"gpt://"
                        f"{self.config_manager.catalog_id}"
                        f"/{self.config_manager.model_type}"
                        f"/latest",
            "completionOptions": {
                "stream": stream,
                "temperature": temperature,
                "maxTokens": max_tokens
            },
            "messages": messages
        }

        # sending request
        async with aiohttp.ClientSession() as session:
            async with session.post(completion_url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response_text = await response.text()
                    raise Exception(
                        f"Failed to send completion request. "
                        f"Status code: {response.status}"
                        f"\n{response_text}"
                    )
