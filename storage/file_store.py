from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Sequence, Union
from uuid import UUID, uuid4

from config import (
    ALLOWED_FILE_ROOTS,
    ARTIFACTS_DIR,
    MAX_SINGLE_FILE_BYTES,
    SUPPORTED_UPLOAD_EXTENSIONS,
    UPLOADS_DIR,
)


class FileStoreError(ValueError):
    """Raised when a local file cannot be stored safely."""


class FileStore:
    def __init__(
        self,
        *,
        uploads_dir: Union[str, Path] = UPLOADS_DIR,
        artifacts_dir: Union[str, Path] = ARTIFACTS_DIR,
        allowed_source_roots: Sequence[Path] = ALLOWED_FILE_ROOTS,
    ) -> None:
        self.uploads_dir = Path(uploads_dir).resolve()
        self.artifacts_dir = Path(artifacts_dir).resolve()
        self.allowed_source_roots = tuple(
            Path(root).resolve() for root in allowed_source_roots
        )
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(
        self,
        *,
        original_filename: str,
        content: bytes,
        file_id: Optional[UUID] = None,
    ) -> Path:
        if not isinstance(content, bytes):
            raise FileStoreError("Uploaded file content must be bytes.")
        if len(content) > MAX_SINGLE_FILE_BYTES:
            raise FileStoreError(
                f"Uploaded file exceeds the {MAX_SINGLE_FILE_BYTES} byte limit."
            )
        extension = _validated_extension(original_filename)
        destination = (self.uploads_dir / f"{file_id or uuid4()}{extension}").resolve()
        _require_within_root(destination, self.uploads_dir)
        try:
            destination.write_bytes(content)
        except OSError as exc:
            raise FileStoreError("Unable to save uploaded file.") from exc
        return destination

    def copy_allowed_upload(
        self,
        source_path: Union[str, Path],
        *,
        file_id: Optional[UUID] = None,
    ) -> Path:
        source = Path(source_path).resolve()
        _require_within_any_root(source, self.allowed_source_roots)
        if not source.is_file():
            raise FileStoreError(f"Source file does not exist: {source}")
        try:
            content = source.read_bytes()
        except OSError as exc:
            raise FileStoreError(f"Unable to read source file: {source.name}") from exc
        return self.save_upload(
            original_filename=source.name,
            content=content,
            file_id=file_id,
        )

    def resolve_upload(self, stored_path: Union[str, Path]) -> Path:
        resolved_path = Path(stored_path).resolve()
        _require_within_root(resolved_path, self.uploads_dir)
        if not resolved_path.is_file():
            raise FileStoreError(f"Uploaded file does not exist: {resolved_path}")
        return resolved_path

    def save_artifact(
        self,
        *,
        original_filename: str,
        content: bytes,
        file_id: Optional[UUID] = None,
    ) -> Path:
        if not isinstance(content, bytes):
            raise FileStoreError("Artifact content must be bytes.")
        extension = Path(original_filename).suffix.lower()
        destination = (self.artifacts_dir / f"{file_id or uuid4()}{extension}").resolve()
        _require_within_root(destination, self.artifacts_dir)
        try:
            destination.write_bytes(content)
        except OSError as exc:
            raise FileStoreError("Unable to save artifact.") from exc
        return destination


def _validated_extension(original_filename: str) -> str:
    extension = Path(original_filename).suffix.lower()
    if extension not in SUPPORTED_UPLOAD_EXTENSIONS:
        raise FileStoreError(
            f"Unsupported uploaded file format: {extension or '<none>'}"
        )
    return extension


def _require_within_any_root(path: Path, roots: Iterable[Path]) -> None:
    for root in roots:
        try:
            path.relative_to(root.resolve())
            return
        except ValueError:
            continue
    raise FileStoreError(f"File path is outside allowed roots: {path}")


def _require_within_root(path: Path, root: Path) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise FileStoreError(f"File path is outside allowed root: {path}") from exc
