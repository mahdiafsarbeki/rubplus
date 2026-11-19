import httpx
import pytest

from rubplus import RubPlus


@pytest.mark.asyncio
async def test_send_uses_async_transport():
    def handler(request):
        assert request.url.path.endswith("/sendMessage")
        return httpx.Response(200, json={"status": "OK", "data": {"message_id": "m1"}})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    bot = RubPlus("12345678901234567890", client=client)
    result = await bot.send("b012345", "hello")
    assert result["status"] == "OK"
    assert result["data"]["message_id"] == "m1"
    await client.aclose()


@pytest.mark.asyncio
async def test_invalid_api_http_status_returns_error():
    def handler(_request):
        return httpx.Response(503, json={"status": "ERROR"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    bot = RubPlus("12345678901234567890", client=client)
    result = await bot.me()
    assert result["status"] == "ERROR"
    await client.aclose()
