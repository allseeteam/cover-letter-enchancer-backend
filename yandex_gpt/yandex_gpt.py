from typing import List
import requests
import time
import jwt

from routines.read_file import read_json, read_yaml


class YandexGPT:
    available_models = [
        'yandexgpt',
        'yandexgpt-lite',
        'summarization'
    ]

    def __init__(
            self,
            model_type: str = 'yandexgpt',
            iam_token: str = None,
            catalog_id: str = None,
            yandex_cloud_config_file_path: str = None,
            yandex_gpt_key_file_path: str = None,
            iam_url: str = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    ) -> None:
        # setting config files
        self._yandex_cloud_config_file_path = yandex_cloud_config_file_path
        self._yandex_gpt_key_file_path = yandex_gpt_key_file_path
        self._iam_url = iam_url
        # setting model type
        if model_type not in self.available_models:
            raise ValueError(f"Model type must be one of {self.available_models}")
        else:
            self.model_type = model_type
        # setting IAM token
        if not iam_token:
            self._set_iam_token()
        else:
            self._iam_token = iam_token
        # setting catalog id
        if not catalog_id:
            self._set_catalog_id()
        else:
            self._catalog_id = catalog_id

    def _set_iam_token(self) -> None:
        # reading yaml config
        config = read_yaml(self._yandex_cloud_config_file_path)
        # reading json key
        key = read_json(self._yandex_gpt_key_file_path)
        # generating jwt token
        jwt_token = self._generate_jwt_token(
            service_account_id=config['ServiceAccountID'],
            private_key=key['private_key'],
            key_id=config['ServiceAccountKeyID'],
            url=self._iam_url
        )
        # sending request to get IAM token and setting IAM token
        self._iam_token = self._swap_jwt_to_iam(
            jwt_token=jwt_token,
            url=self._iam_url
        )

    @staticmethod
    def _swap_jwt_to_iam(
            jwt_token: str,
            url: str = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    ) -> str:
        # sending request to get IAM token
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "jwt": jwt_token
        }
        response = requests.post(url, headers=headers, json=data)
        # checking response
        if response.status_code == 200:
            return response.json()['iamToken']
        else:
            raise Exception(
                f"Failed to get IAM token. "
                f"Status code: {response.status_code}"
                f"\n"
                f"{response.text}"
            )

    @staticmethod
    def _generate_jwt_token(
            service_account_id: str,
            private_key: str,
            key_id: str,
            url: str = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    ) -> str:
        # generating jwt token
        now = int(time.time())
        payload = {
            'aud': url,
            'iss': service_account_id,
            'iat': now,
            'exp': now + 360
        }
        encoded_token = jwt.encode(
            payload,
            private_key,
            algorithm='PS256',
            headers={'kid': key_id}
        )
        return encoded_token

    def _set_catalog_id(self) -> None:
        # reading yaml config file
        config = read_yaml(self._yandex_cloud_config_file_path)
        # setting catalog id from config file
        self._catalog_id = config['CatalogID']

    def send_completion_request(
            self,
            messages: List[dict],
            temperature: float = 0.6,
            max_tokens: int = 1000,
            stream: bool = False,
            completion_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    ) -> dict:
        # checking if IAM token and catalog id is set
        if not self._iam_token or not self._catalog_id:
            raise Exception("IAM token and catalog id must be set to send completion requests")
        # sending request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._iam_token}",
            "x-folder-id": self._catalog_id
        }
        data = {
            "modelUri": f"gpt://{self._catalog_id}/{self.model_type}/latest",
            "completionOptions": {
                "stream": stream,
                "temperature": temperature,
                "maxTokens": str(max_tokens)
            },
            "messages": messages
        }
        response = requests.post(completion_url, headers=headers, json=data)
        # checking response
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to send completion request. Status code: {response.status_code}\n{response.text}")
