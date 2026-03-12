"""Provider registry: register providers, get by id, list all with availability."""

from typing import Optional

from tdsm.providers.base import BaseProvider


class ProviderRegistry:
    """Holds all known providers. Used by session creation and /providers command."""

    def __init__(self) -> None:
        self._providers: dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider) -> None:
        """Register a provider by its id."""
        self._providers[provider.id] = provider

    def get(self, provider_id: str) -> Optional[BaseProvider]:
        """Return the provider with this id, or None."""
        return self._providers.get(provider_id)

    def list_all(self) -> list[tuple[BaseProvider, bool]]:
        """Return list of (provider, is_available) for all registered providers."""
        return [(p, p.is_available()) for p in self._providers.values()]

    def list_ids(self) -> list[str]:
        """Return list of registered provider ids."""
        return list(self._providers.keys())
