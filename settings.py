# settings.py

FILE_UPLOAD_MAX_MEMORY_SIZE = None  # Default is 2621440 (i.e. 2.5 MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = None  # Default is 2621440 (i.e. 2.5 MB)
FILE_UPLOAD_HANDLERS = [
    "Django.core.files.uploadhandler.TemporaryFileUploadHandler",
    # ... other handlers
]

