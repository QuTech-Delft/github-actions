import asyncio
import json
import os
import time
from pathlib import Path
from typing import cast

import requests
from compute_api_client import ApiClient, Configuration, MembersApi


async def _fetch_team_member_id(host: str, access_token: str) -> int:
    config = Configuration(host=host, access_token=access_token)
    async with ApiClient(config) as api_client:
        api_instance = MembersApi(api_client)
        members_page = await api_instance.read_members_members_get()
        members = members_page.items
        if len(members) == 1:
            member_id = members[0].id
            return cast(int, member_id)
        raise ValueError("Too many member IDs found")


def get_team_member_id(host: str, access_token: str) -> int:
    return asyncio.run(_fetch_team_member_id(host, access_token))


def main():
    config_file = Path.joinpath(Path.home(), ".quantuminspire", "config.json")
    well_known_endpoint = f"{os.getenv('IDP_URL')}/.well-known/openid-configuration"
    token_endpoint = requests.get(well_known_endpoint).json()["token_endpoint"]
    client_id = os.getenv("IDP_CLIENT_ID")
    file_encoding = "utf-8"

    payload = {
        "grant_type": "password",
        "client_id": client_id,
        "username": os.getenv("E2E_USERNAME"),
        "password": os.getenv("E2E_PASSWORD"),
        "scope": "api-access openid profile email offline_access",
        "audience": os.getenv("API_AUDIENCE"),
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(token_endpoint, data=payload, headers=headers)
    response.raise_for_status()
    token_info = response.json()

    token_info["generated_at"] = time.time()
    host = os.getenv("DEFAULT_HOST")
    team_member_id = get_team_member_id(
        host=host, access_token=token_info["access_token"]
    )
    config = json.dumps(
        {
            "auths": {
                host: {
                    "tokens": token_info,
                    "team_member_id": team_member_id,
                    "client_id": client_id,
                    "code_challenge_method": "S256",
                    "code_verifyer_length": 64,
                    "well_known_endpoint": well_known_endpoint,
                }
            },
            "default_host": host,
        },
        indent=2,
    )
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.open("w", encoding=file_encoding).write(config)


if __name__ == "__main__":
    main()
