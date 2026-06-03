from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Sequence, Union

from core.workflow_schema import ExecutionContext


TEXT_EXTENSIONS = frozenset({".txt", ".md"})
DEFERRED_EXTENSIONS = frozenset({".pdf", ".docx"})


class DocumentReadError(ValueError):
    """Raised when a document cannot be read in the current stage."""


def read_document_file(file_path: Union[str, Path]) -> Dict[str, str]:
    path = Path(file_path).resolve()
    if not path.is_file():
        raise DocumentReadError(f"Document file does not exist: {path}")

    extension = path.suffix.lower()
    if extension in DEFERRED_EXTENSIONS:
        raise DocumentReadError(
            f"{extension.upper()} parsing is not supported in the current offline demo. "
            "Full PDF and DOCX parsing will be added in stage 4A."
        )
    if extension not in TEXT_EXTENSIONS:
        raise DocumentReadError(
            f"Unsupported document format: {extension or '<none>'}. "
            "The current offline demo supports TXT and MD files."
        )

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise DocumentReadError(
            f"Document must use UTF-8 encoding in the current offline demo: {path.name}"
        ) from exc
    except OSError as exc:
        raise DocumentReadError(f"Unable to read document: {path.name}") from exc

    if not content.strip():
        raise DocumentReadError(f"Document is empty: {path.name}")
    return {
        "name": path.name,
        "path": str(path),
        "content": content,
    }


def read_documents(file_paths: Sequence[Union[str, Path]]) -> List[Dict[str, str]]:
    if not file_paths:
        raise DocumentReadError("At least one document file is required.")
    return [read_document_file(file_path) for file_path in file_paths]


def read_document(
    inputs: Dict[str, Any],
    params: Dict[str, Any],
    context: ExecutionContext,
) -> Dict[str, Any]:
    files = inputs.get("files")
    if isinstance(files, (str, bytes, Path)) or not isinstance(files, Sequence):
        raise DocumentReadError("read_document requires a list of document files.")
    return {"documents": read_documents(files)}
