"""Read-only tools over the entire hash-checked snapshot, never over answer files."""

from typing import Literal
from urllib.parse import unquote, urlsplit

from langchain_core.tools import BaseTool, StructuredTool

from benchmark.dataset import Artifact, SnapshotStore

TOOL_VERSION = "snapshot-tools-v1"
PAGE_SIZE = 12_000
SEARCH_LIMIT = 5
SNIPPET_SIZE = 500
GitHubResource = Literal["repository", "latest_release", "issues", "file"]


class SnapshotTools:
    def __init__(self, store: SnapshotStore) -> None:
        self.store = store
        self.artifacts = {artifact.id: artifact for artifact in store.manifest.artifacts}

    def _source(self, artifact: Artifact) -> dict:
        return {
            "artifact_id": artifact.id,
            "url": artifact.url,
            "captured_at": artifact.captured_at.isoformat(),
            "synthetic": self.store.manifest.synthetic,
        }

    def _read(self, artifacts: list[Artifact], offset: int) -> dict:
        if offset < 0:
            raise ValueError("offset must be non-negative")
        if not artifacts:
            return {"status": "not_found", "results": [], "message": "Not in this snapshot"}
        results = []
        for artifact in artifacts:
            content = self.store.contents[artifact.id]
            if offset > len(content):
                raise ValueError("offset exceeds document length")
            end = min(offset + PAGE_SIZE, len(content))
            results.append(
                self._source(artifact)
                | {
                    "content": content[offset:end],
                    "offset": offset,
                    "next_offset": end if end < len(content) else None,
                    "total_characters": len(content),
                }
            )
        return {"status": "ok", "results": results}

    def web_search(self, query: str) -> dict:
        """Discover snapshot URLs. Results are short snippets, not complete evidence.

        Use repository names or English technical terms, then read the matching sources.
        """
        if not query.strip():
            raise ValueError("query must not be empty")
        hits = self.store.search(query)
        results = []
        for artifact_id, content in list(hits.items())[:SEARCH_LIMIT]:
            positions = [content.casefold().find(word) for word in query.casefold().split()]
            first = min((position for position in positions if position >= 0), default=0)
            start = max(0, first - 100)
            artifact = self.artifacts[artifact_id]
            results.append(
                self._source(artifact)
                | {
                    "title": urlsplit(artifact.url).path,
                    "snippet": content[start : start + SNIPPET_SIZE],
                }
            )
        return {"status": "ok" if results else "not_found", "results": results}

    def fetch_page(self, url: str, offset: int = 0) -> dict:
        """Read an exact snapshot URL, 12000 characters at a time.

        Follow next_offset until null when more of the source is needed. No network fallback.
        """
        return self._read(
            [artifact for artifact in self.artifacts.values() if artifact.url == url], offset
        )

    def github_read(
        self,
        repository: str,
        resource: GitHubResource = "repository",
        path: str | None = None,
        offset: int = 0,
    ) -> dict:
        """Read captured GitHub resources for an owner/repository.

        resource: repository (metadata), latest_release, issues (captured query only), or file.
        For file, provide a repository-relative path such as README.md. Reads use the captured
        revision, not live GitHub. Results contain the exact query URL and pagination offsets.
        """
        parts = repository.split("/")
        if len(parts) != 2 or not all(parts):
            raise ValueError("repository must be owner/name")
        if resource not in ("repository", "latest_release", "issues", "file"):
            raise ValueError("unsupported GitHub resource")
        if resource == "file" and (not path or path.startswith("/") or ".." in path.split("/")):
            raise ValueError("file requires a repository-relative path")
        matches = []
        for artifact in self.artifacts.values():
            url = urlsplit(artifact.url)
            segments = unquote(url.path).strip("/").split("/")
            if url.hostname == "api.github.com" and len(segments) >= 3:
                if segments[0] != "repos" or "/".join(segments[1:3]).casefold() != (
                    repository.casefold()
                ):
                    continue
                suffix = "/".join(segments[3:])
                expected = {
                    "repository": "",
                    "latest_release": "releases/latest",
                    "issues": "issues",
                }.get(resource)
                if expected is not None and suffix == expected:
                    matches.append(artifact)
            elif url.hostname == "raw.githubusercontent.com" and len(segments) >= 4:
                if (
                    resource == "file"
                    and "/".join(segments[:2]).casefold() == repository.casefold()
                    and "/".join(segments[3:]) == path
                ):
                    matches.append(artifact)
        return self._read(matches, offset)

    def bindable_tools(self, allowed: list[str]) -> list[BaseTool]:
        available = {
            name: StructuredTool.from_function(getattr(self, name), name=name)
            for name in ("web_search", "fetch_page", "github_read")
        }
        if len(set(allowed)) != len(allowed) or not set(allowed) <= available.keys():
            raise ValueError("allowed_tools contains duplicate or unsupported tool names")
        return [available[name] for name in allowed]
