from __future__ import annotations

from voxium.core.interfaces.llm import BaseLLMClient


class LLMRouter:
    """Routes agent names to their designated LLM client."""

    def __init__(
        self,
        default_client: BaseLLMClient,
        routing_map: dict[str, BaseLLMClient] | None = None,
    ) -> None:
        self._default = default_client
        self._map: dict[str, BaseLLMClient] = routing_map or {}

    def get(self, agent_name: str) -> BaseLLMClient:
        """Return the client mapped to agent_name, or the default client."""
        return self._map.get(agent_name, self._default)
