import os
import jwt
import time
import requests
from typing import Any, Dict, Optional

from routines.read_file import read_json, read_yaml


class YandexGPTConfigManager:
    available_models: list[str] = [
        'yandexgpt',
        'yandexgpt-lite',
        'summarization'
    ]

    def __init__(
            self,
            model_type: str = 'yandexgpt',
            iam_token: Optional[str] = None,
            catalog_id: Optional[str] = None,
            config_path: Optional[str] = None,
            key_file_path: Optional[str] = None
    ) -> None:
        self.model_type: str = model_type
        self.iam_token: Optional[str] = iam_token
        self.catalog_id: Optional[str] = catalog_id
        self._initialize_params(config_path, key_file_path)
        self._check_params()

    def _initialize_params(
            self,
            config_path: Optional[str],
            key_file_path: Optional[str]
    ) -> None:
        if self.iam_token and self.catalog_id:
            # if both IAM token and catalog id are already set, do nothing
            return
        elif config_path and key_file_path:
            # trying to initialize from config path and key file path
            self._initialize_from_files(config_path, key_file_path)
        else:
            # trying to initialize from environment variables
            self._initialize_from_env_vars()

    def _initialize_from_files(
            self,
            config_path: str,
            key_file_path: str
    ) -> None:
        # getting config and key
        config: Dict[str, Any] = read_yaml(config_path)
        key: Dict[str, Any] = read_json(key_file_path)
        # setting catalog id and IAM token
        self._set_catalog_id_from_config(config)
        self._set_iam_token_from_key_and_config(key, config)

    def _set_catalog_id_from_config(
            self,
            config: Dict[str, Any]
    ) -> None:
        self.catalog_id = config['CatalogID']

    def _set_iam_token_from_key_and_config(
            self,
            key: Dict[str, Any],
            config: Dict[str, Any]
    ) -> None:
        # generating JWT token
        jwt_token: str = self._generate_jwt_token(
            service_account_id=config['ServiceAccountID'],
            private_key=key['private_key'],
            key_id=config['ServiceAccountKeyID'],
            url=config.get('IAMURL', 'https://iam.api.cloud.yandex.net/iam/v1/tokens')
        )
        # swapping JWT token to IAM
        self.iam_token = self._swap_jwt_to_iam(
            jwt_token=jwt_token,
            url=config.get('IAMURL', 'https://iam.api.cloud.yandex.net/iam/v1/tokens')
        )

    @staticmethod
    def _generate_jwt_token(
            service_account_id: str,
            private_key: str,
            key_id: str,
            url: str = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    ) -> str:
        # generating JWT token
        now: int = int(time.time())
        payload: Dict[str, Any] = {
            'aud': url,
            'iss': service_account_id,
            'iat': now,
            'exp': now + 360
        }
        encoded_token: str = jwt.encode(
            payload,
            private_key,
            algorithm='PS256',
            headers={'kid': key_id}
        )
        return encoded_token

    @staticmethod
    def _swap_jwt_to_iam(
            jwt_token: str,
            url: str = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    ) -> str:
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        data: Dict[str, str] = {"jwt": jwt_token}
        # swapping JWT token to IAM
        response: requests.Response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            # if succeeded to get IAM token
            return response.json()['iamToken']
        else:
            # if failed to get IAM token
            raise Exception(
                f"Failed to get IAM token. Status code: {response.status_code}\n{response.text}"
            )

    def _initialize_from_env_vars(self) -> None:
        # trying to initialize from environment variables
        self._set_iam_from_env()
        self._set_model_type_from_env()
        self._set_catalog_id_from_env()
        if not self.iam_token:
            # if IAM token is not set, trying to initialize from config and private key
            self._set_iam_from_env_config_and_private_key()

    def _set_iam_from_env(self) -> None:
        self.iam_token = os.getenv('IAM_TOKEN', self.iam_token)

    def _set_model_type_from_env(self) -> None:
        self.model_type = os.getenv('MODEL_TYPE', self.model_type)

    def _set_catalog_id_from_env(self) -> None:
        self.catalog_id = os.getenv('CATALOG_ID', self.catalog_id)

    def _set_iam_from_env_config_and_private_key(self) -> None:
        # getting environment variables
        service_account_id: Optional[str] = os.getenv('SERVICE_ACCOUNT_ID')
        service_account_key_id: Optional[str] = os.getenv('SERVICE_ACCOUNT_KEY_ID')
        catalog_id: Optional[str] = os.getenv('CATALOG_ID')
        private_key: Optional[str] = os.getenv('PRIVATE_KEY')
        iam_url: str = os.getenv('IAM_URL', 'https://iam.api.cloud.yandex.net/iam/v1/tokens')
        # checking environment variables
        if not all([service_account_id, service_account_key_id, private_key, catalog_id]):
            raise ValueError("One or more environment variables for IAM token generation are missing.")
        # generating JWT token
        jwt_token: str = self._generate_jwt_token(
            service_account_id=service_account_id,
            private_key=private_key,
            key_id=service_account_key_id,
            url=iam_url
        )
        # swapping JWT token to IAM
        self.iam_token = self._swap_jwt_to_iam(jwt_token, iam_url)

    def _check_params(self) -> None:
        if not self.iam_token:
            raise ValueError("IAM token is not set")
        if not self.catalog_id:
            raise ValueError("Catalog ID is not set")
        if self.model_type not in self.available_models:
            raise ValueError(f"Model type must be one of {self.available_models}")
