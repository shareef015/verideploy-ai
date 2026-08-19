from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid5

from verideploy.knowledge.schemas import KnowledgeManifest, KnowledgeRetentionPolicy
from verideploy.rag.retrieval.corpus import RetrievalChunkInput, RetrievalDocumentInput

_CHUNK_NAMESPACE = UUID("9d47a333-79c5-43ba-a8e3-65ca3bcf02c6")


@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_id: UUID
    document_id: UUID
    ordinal: int
    content: str
    content_sha256: str


class EngineeringKnowledgeCorpus:
    """Load a validated, file-backed engineering corpus without network access."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.manifest = KnowledgeManifest.model_validate_json((self.root / "manifest.json").read_text(encoding="utf-8"))
        self.retention = KnowledgeRetentionPolicy.model_validate_json((self.root / "retention-policy.json").read_text(encoding="utf-8"))

    def document_path(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        if self.root not in candidate.parents:
            raise ValueError("knowledge document path escapes corpus root")
        return candidate

    def read_document(self, relative_path: str) -> str:
        return self.document_path(relative_path).read_text(encoding="utf-8")

    @staticmethod
    def sha256(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def chunks(self, *, document_id: UUID, content: str, max_chars: int = 1800) -> list[KnowledgeChunk]:
        if max_chars < 256:
            raise ValueError("max_chars must be at least 256")
        paragraphs = [part.strip() for part in content.split("\n\n") if part.strip()]
        grouped: list[str] = []
        current = ""
        for paragraph in paragraphs:
            candidate = paragraph if not current else f"{current}\n\n{paragraph}"
            if current and len(candidate) > max_chars:
                grouped.append(current)
                current = paragraph
            else:
                current = candidate
        if current:
            grouped.append(current)
        chunks: list[KnowledgeChunk] = []
        for ordinal, text in enumerate(grouped):
            content_hash = self.sha256(text)
            chunk_id = uuid5(_CHUNK_NAMESPACE, f"{document_id}:{ordinal}:{content_hash}")
            chunks.append(KnowledgeChunk(chunk_id, document_id, ordinal, text, content_hash))
        return chunks

    def retrieval_inputs(self) -> list[tuple[RetrievalDocumentInput, list[RetrievalChunkInput]]]:
        output: list[tuple[RetrievalDocumentInput, list[RetrievalChunkInput]]] = []
        for item in self.manifest.documents:
            content = self.read_document(item.path)
            document = RetrievalDocumentInput(
                document_id=item.document_id,
                tenant_id=self.manifest.tenant_id,
                source_key=item.provenance_uri,
                title=item.title,
                service=item.service,
                environment=item.environment,
                document_kind=item.retrieval_kind,
            )
            chunks = [
                RetrievalChunkInput(
                    chunk_id=chunk.chunk_id,
                    tenant_id=self.manifest.tenant_id,
                    document_id=item.document_id,
                    ordinal=chunk.ordinal,
                    content=chunk.content,
                )
                for chunk in self.chunks(document_id=item.document_id, content=content)
            ]
            output.append((document, chunks))
        return output

    def manifest_digest(self) -> str:
        canonical = json.dumps(self.manifest.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
