"""
Tool: Persist uploaded files securely.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import uuid


class FileUploader:
    def __init__(self, config):
        self.config = config
        Path(self.config.upload_directory).mkdir(parents=True, exist_ok=True)

    def save_upload(self, tmp_path: str) -> str:
        extension = Path(tmp_path).suffix
        dest = Path(self.config.upload_directory) / f"{uuid.uuid4().hex}{extension}"
        shutil.copy2(tmp_path, dest)
        return str(dest)

