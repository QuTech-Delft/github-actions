import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import requests


@dataclass
class AuthInfo:
    host: str
    access_token: str
    member_id: int


@dataclass
class IdentityProviderCredentials:
    username: str
    password: str


class QI2API:
    def __init__(self, host: str):
        self.host = host

    def fetch_team_member_id(self, access_token: str) -> int:
        members_url = f"{self.host}/members"
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(members_url, headers=headers)
        response.raise_for_status()
        members_pages = cast(dict[str, Any], response.json())
        members = members_pages["items"]

        if len(members) == 1:
            member_id = members[0]["id"]
            return cast(int, member_id)

        raise ValueError("Authentication associated with more than one team member")


class IdentityProvider:
    """Class for interfacing with the IdentityProvider."""

    def __init__(
        self,
        well_known_endpoint: str,
        client_id: str,
        credentials: IdentityProviderCredentials,
        audience: str,
    ):
        self.well_known_endpoint = well_known_endpoint
        self._credentials = credentials
        self.client_id = client_id
        self._audience = audience
        self._token_endpoint = self._get_endpoints()
        self._headers = {"Content-Type": "application/x-www-form-urlencoded"}

    def _get_endpoints(self) -> str:
        response = requests.get(self.well_known_endpoint)
        response.raise_for_status()
        config = response.json()
        return str(config["token_endpoint"])

    def get_access_info(self) -> dict[str, Any]:
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "username": self._credentials.username,
            "password": self._credentials.password,
            "scope": "api-access openid profile email offline_access",
            "audience": self._audience,
        }
        response = requests.post(self._token_endpoint, headers=self._headers, data=data)
        response.raise_for_status()
        _token_info = cast(dict[str, Any], response.json())
        _token_info["generated_at"] = time.time()
        return _token_info


class ConfigurationFile:
    def __init__(self, identity_provider: IdentityProvider, qi2api: QI2API):
        self._identity_provider = identity_provider
        self._api = qi2api
        self._config_file = Path.joinpath(Path.home(), ".quantuminspire", "config.json")
        self._file_encoding = "utf-8"
        self._tokens_keys = [
            "access_token",
            "expires_in",
            "refresh_token",
            "refresh_expires_in",
            "generated_at",
        ]

    def update_file(self) -> None:
        assert self._api.host
        _token_info = self._identity_provider.get_access_info()
        _team_member_id = self._api.fetch_team_member_id(_token_info["access_token"])
        _config = json.dumps(
            {
                "auths": {
                    self._api.host: {
                        "tokens": {
                            key: _token_info.get(key, None) for key in self._tokens_keys
                        },
                        "team_member_id": _team_member_id,
                        "client_id": self._identity_provider.client_id,
                        "code_challenge_method": "S256",
                        "code_verifyer_length": 64,
                        "well_known_endpoint": self._identity_provider.well_known_endpoint,
                    }
                },
                "default_host": self._api.host,
            },
            indent=2,
        )
        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        self._config_file.open("w", encoding=self._file_encoding).write(_config)


_identity_provider = IdentityProvider(
    f"{os.getenv('IDP_URL')}/.well-known/openid-configuration",
    os.getenv("IDP_CLIENT_ID", ""),
    IdentityProviderCredentials(
        os.getenv("E2E_USERNAME", ""), os.getenv("E2E_PASSWORD", "")
    ),
    os.getenv("API_AUDIENCE", ""),
)
_api = QI2API(os.getenv("DEFAULT_HOST", ""))


def get_auth_info() -> AuthInfo:
    _token_info = _identity_provider.get_access_info()
    _access_token = _token_info["access_token"]
    return AuthInfo(
        host=_api.host,
        access_token=_access_token,
        member_id=_api.fetch_team_member_id(_access_token),
    )


def create_config_file() -> None:
    _config_file = ConfigurationFile(identity_provider=_identity_provider, qi2api=_api)
    _config_file.update_file()


if __name__ == "__main__":
    print(get_auth_info())
