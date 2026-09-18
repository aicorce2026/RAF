from pathlib import Path

from django.core.exceptions import ValidationError


MEBIBYTE = 1024 * 1024
RECEIPT_MAX_SIZE = 5 * MEBIBYTE
BOOK_PDF_MAX_SIZE = 50 * MEBIBYTE


def _validate_upload(upload, *, allowed_signatures, max_size, file_label):
    """Validate an upload without trusting its browser-provided content type."""
    if not upload:
        raise ValidationError(f"ملف {file_label} مطلوب.", code="required")

    try:
        size = upload.size
    except (AttributeError, OSError, ValueError) as exc:
        raise ValidationError(
            f"تعذر قراءة ملف {file_label}.",
            code="unreadable_file",
        ) from exc

    if size == 0:
        raise ValidationError(f"ملف {file_label} فارغ.", code="empty_file")
    if size > max_size:
        limit_mb = max_size // MEBIBYTE
        raise ValidationError(
            f"حجم ملف {file_label} يجب ألا يتجاوز {limit_mb} ميجابايت.",
            code="file_too_large",
        )

    extension = Path(upload.name).suffix.lower()
    expected_signature = allowed_signatures.get(extension)
    if expected_signature is None:
        allowed = "، ".join(sorted(allowed_signatures))
        raise ValidationError(
            f"امتداد ملف {file_label} غير مسموح. الامتدادات المسموحة: {allowed}.",
            code="invalid_extension",
        )

    try:
        file_object = upload.file
        original_position = file_object.tell()
        file_object.seek(0)
        header = file_object.read(
            max(len(signature) for signature in allowed_signatures.values())
        )
        file_object.seek(original_position)
    except (AttributeError, OSError, ValueError) as exc:
        raise ValidationError(
            f"تعذر قراءة محتوى ملف {file_label}.",
            code="unreadable_file",
        ) from exc

    if not header.startswith(expected_signature):
        raise ValidationError(
            f"محتوى ملف {file_label} لا يطابق امتداده.",
            code="invalid_file_content",
        )


def validate_receipt_upload(upload):
    _validate_upload(
        upload,
        allowed_signatures={
            ".pdf": b"%PDF-",
            ".jpg": b"\xff\xd8\xff",
            ".jpeg": b"\xff\xd8\xff",
            ".png": b"\x89PNG\r\n\x1a\n",
        },
        max_size=RECEIPT_MAX_SIZE,
        file_label="الإيصال",
    )


def validate_book_pdf_upload(upload):
    _validate_upload(
        upload,
        allowed_signatures={".pdf": b"%PDF-"},
        max_size=BOOK_PDF_MAX_SIZE,
        file_label="PDF الكتاب",
    )
