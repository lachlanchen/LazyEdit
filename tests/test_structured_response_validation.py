import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from lazyedit.openai_request_json import OpenAIRequestJSONBase


SCHEMA = {
    "type": "object",
    "properties": {"items": {"type": "array", "items": {"type": "string"}}},
    "required": ["items"],
    "additionalProperties": False,
}
GOOD = {"items": ["Shibuya"]}


def requester(tmp_path, replies):
    client = OpenAIRequestJSONBase.__new__(OpenAIRequestJSONBase)
    client.api_provider, client.model = "deepseek", "test"
    client.cache_dir, client.use_cache, client.max_retries = str(tmp_path), True, 2
    client.activate_openai_fallback = Mock(return_value=False)
    client.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
        create=Mock(side_effect=[SimpleNamespace(choices=[SimpleNamespace(
            message=SimpleNamespace(content=json.dumps(reply), refusal=None)
        )]) for reply in replies])
    )))
    return client


@pytest.mark.parametrize("bad", [SCHEMA, {"items": "not an array"}, {"items": [1]}])
def test_schema_echo_or_wrong_type_is_retried_before_caching(tmp_path, bad):
    client = requester(tmp_path, [bad, GOOD])
    assert client.send_request_with_json_schema("translate", SCHEMA) == GOOD
    assert client.client.chat.completions.create.call_count == 2
    assert json.loads(next(tmp_path.glob("*.json")).read_text())["response"] == GOOD


def test_invalid_cache_is_replaced_and_valid_cache_reused(tmp_path):
    client = requester(tmp_path, [GOOD])
    filename = client.build_cache_filename("translate", SCHEMA, "You are an AI.", "response")
    client.save_to_cache("translate", SCHEMA, filename)
    assert client.send_request_with_json_schema("translate", SCHEMA) == GOOD
    assert client.send_request_with_json_schema("translate", SCHEMA) == GOOD
    assert client.client.chat.completions.create.call_count == 1


def test_invalid_responses_stop_at_retry_bound_without_cache(tmp_path):
    client = requester(tmp_path, [SCHEMA, SCHEMA])
    with pytest.raises(Exception, match="Maximum retries"):
        client.send_request_with_json_schema("translate", SCHEMA)
    assert client.client.chat.completions.create.call_count == 2
    assert not list(tmp_path.glob("*.json"))
