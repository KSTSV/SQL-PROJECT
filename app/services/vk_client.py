import requests


class VKClient:
    def __init__(self, token: str, api_version: str = "5.199"):
        if not token:
            raise ValueError("Не указан VK_TOKEN в .env")
        self.token = token
        self.api_version = api_version

    def method(self, method: str, params: dict) -> dict:
        response = requests.get(
            f"https://api.vk.com/method/{method}",
            params={**params, "access_token": self.token, "v": self.api_version},
            timeout=30,
        )
        data = response.json()
        if "error" in data:
            raise RuntimeError(f"VK API error in {method}: {data['error']}")
        return data["response"]

    @staticmethod
    def build_profile_url(vk_id: int, screen_name: str | None = None) -> str:
        if screen_name:
            return f"https://vk.com/{screen_name}"
        if vk_id < 0:
            return f"https://vk.com/club{abs(vk_id)}"
        return f"https://vk.com/id{vk_id}"
