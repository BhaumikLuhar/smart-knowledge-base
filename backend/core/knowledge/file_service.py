from pathlib import Path
from uuid import uuid4
import re

from fastapi import HTTPException, UploadFile

from core.config import settings
from core.knowledge.loaders.factory import LOADER_REGISTRY


class FileService:
    """
    Handles validation and storage
    of uploaded files.
    """

    @staticmethod
    def sanitize_filename(filename: str)->str:
        """
        Convert unsafe filenames into safe ones.

        Example:
        My HR Policy (Final).pdf
        ->
        My_HR_Policy_Final.pdf
        """

        filename=filename.strip().replace(" ","_")

        filename=re.sub(r"[^a-zA-Z0-9._-]","",filename)

        return filename
    

    @staticmethod
    async def validate_extension(uploaded_file: UploadFile)->str:
        """
        Ensure a loader exists
        for this extension.
        """

        extension=Path(uploaded_file.filename).suffix.lower()

        if extension not in LOADER_REGISTRY:
            supported = ", ".join(
                LOADER_REGISTRY.keys()
            )
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported file type "
                    f"'{extension}'. "
                    f"Supported: {supported}"
                )
            )

        return extension
    

    @staticmethod
    async def validate_file_size(upload_file: UploadFile):
        """
        Validate uploaded file size.
        """

        max_size_bytes=settings.MAX_FILE_SIZE_MB * 1024 * 1024

        contents= await upload_file.read()

        file_size=len(contents)

        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"File exceeds "
                    f"{settings.MAX_FILE_SIZE_MB}MB limit"
                )
            )

        await upload_file.seek(0)


    @staticmethod
    async def save_file(upload_file: UploadFile, department_name: str)->str:
        """
        Save file to disk.

        Returns:
            relative file path
        """

        await FileService.validate_extension(upload_file)

        await FileService.validate_file_size(upload_file)

        safe_name=FileService.sanitize_filename(upload_file.filename)

        filename=f"{uuid4()}_{safe_name}"

        department_dir=Path(settings.UPLOAD_DIR) / department_name

        department_dir.mkdir(parents=True, exist_ok=True)

        file_path=department_dir / filename

        contents= await upload_file.read()

        with open(file_path,"wb")as file:
            file.write(contents)

        await upload_file.seek(0)

        return str(file_path.resolve())