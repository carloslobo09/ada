from pathlib import Path


class FilesystemStorage:
    """Persiste archivos subidos en disco bajo un directorio base configurable."""

    def __init__(self, base_dir: Path) -> None:
        self._base = base_dir
        self._base.mkdir(parents=True, exist_ok=True)

    def save(self, file_id: str, filename: str, content: bytes) -> Path:
        extension = Path(filename).suffix.lower()
        target = self._base / f"{file_id}{extension}"
        target.write_bytes(content)
        return target
