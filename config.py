from __future__ import annotations

from pathlib import Path
from typing import Tuple


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = (PROJECT_ROOT / "data").resolve()
UPLOADS_DIR = (DATA_DIR / "uploads").resolve()
ARTIFACTS_DIR = (DATA_DIR / "artifacts").resolve()
EXAMPLES_DIR = (PROJECT_ROOT / "examples").resolve()

ALLOWED_FILE_ROOTS: Tuple[Path, ...] = (UPLOADS_DIR, EXAMPLES_DIR)
SUPPORTED_UPLOAD_EXTENSIONS = frozenset(
    {".csv", ".docx", ".md", ".pdf", ".txt", ".xlsx"}
)

MAX_WORKFLOW_STEPS = 20
MAX_UPLOAD_FILES = 10
MAX_SINGLE_FILE_BYTES = 20 * 1024 * 1024
MAX_TOTAL_FILE_BYTES = 50 * 1024 * 1024
MAX_TABLE_ROWS = 100_000

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 120
DEFAULT_RETRIEVAL_TOP_K = 5
