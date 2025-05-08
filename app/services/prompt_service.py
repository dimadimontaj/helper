from pathlib import Path
from typing import Any, Protocol, Final

from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

from app.schemas.schemas import ChatMessage

TEMPLATE_ROOT: Final[Path] = Path(__file__).parent.with_name("prompts")


class PromptServiceProtocol(Protocol):
    def new_builder(self) -> "ChatPromptBuilder": ...


class PromptService(PromptServiceProtocol):
    _ENV_CACHE: dict[tuple[Path, bool], Environment] = {}

    def __init__(self, base_path: Path | str | None = None, *, auto_reload: bool = False) -> None:
        self.base_path: Path = Path(base_path) if base_path else TEMPLATE_ROOT
        self.auto_reload = auto_reload

        env_key = (self.base_path, self.auto_reload)
        if env_key not in self._ENV_CACHE:
            self._ENV_CACHE[env_key] = Environment(
                loader=FileSystemLoader(self.base_path),
                autoescape=select_autoescape(default=True, disabled_extensions=("txt", "md")),
                trim_blocks=True,
                lstrip_blocks=True,
                cache_size=0 if self.auto_reload else 50,
                enable_async=False,
            )
        self.env: Environment = self._ENV_CACHE[env_key]

    def _get_template(self, relative_path: str) -> Template:
        return self.env.get_template(relative_path)

    def render_template(self, relative_path: str, **context: Any) -> str:
        return self._get_template(relative_path).render(**context)

    def new_builder(self) -> "ChatPromptBuilder":
        return ChatPromptBuilder(self)


class ChatPromptBuilder:
    __slots__ = ("_service", "_messages")

    def __init__(self, service: PromptService) -> None:
        self._service = service
        self._messages: list[ChatMessage] = []

    def _add(self, role: str, *, content: str | None, path: str | None, **ctx: Any) -> "ChatPromptBuilder":
        if content is not None:
            self._messages.append({"role": role, "content": content})
        if path is not None:
            rendered = self._service.render_template(path, **ctx)
            self._messages.append({"role": role, "content": rendered})
        return self

    def add_system(self, *, content: str | None = None, path: str | None = None, **ctx: Any) -> "ChatPromptBuilder":
        return self._add("system", content=content, path=path, **ctx)

    def add_user(self, *, content: str | None = None, path: str | None = None, **ctx: Any) -> "ChatPromptBuilder":
        return self._add("user", content=content, path=path, **ctx)

    def add_assistant(
        self,
        *,
        content: str | None = None,
        path: str | None = None,
        **ctx: Any,
    ) -> "ChatPromptBuilder":
        return self._add("assistant", content=content, path=path, **ctx)

    def build(self) -> list[ChatMessage, ...]:
        return list(self._messages)
