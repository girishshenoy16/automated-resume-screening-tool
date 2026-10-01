"""
Automated Resume Screening Tool — NLP Text Normalization Engine.

Performs robust text sanitization, removes URLs, emails, and noisy punctuation,
normalizes whitespace, and strictly safeguards programming tokens such as
C++, C#, .NET, Node.js, and CI/CD.
"""

import re

# Mask mappings for protected technical symbols during punctuation stripping
PROTECTED_TOKEN_PATTERNS = [
    (r"(?i)\bc\+\+", "__TOKEN_CPP__"),
    (r"(?i)\bc\#", "__TOKEN_CSHARP__"),
    (r"(?i)(?<!\w)\.net\b", "__TOKEN_DOTNET__"),
    (r"(?i)\bnode\.js\b", "__TOKEN_NODEJS__"),
    (r"(?i)\bci/cd\b", "__TOKEN_CICD__"),
]

UNMASK_MAPPING = {
    "__token_cpp__": "c++",
    "__token_csharp__": "c#",
    "__token_dotnet__": ".net",
    "__token_nodejs__": "node.js",
    "__token_cicd__": "ci/cd",
}

def clean_text(text: str) -> str:
    """
    Sanitize and normalize raw document text into clean, lowercase tokens
    while preserving protected programming symbols.

    Steps:
    1. Strip web URLs and hyperlinked domains.
    2. Strip email addresses.
    3. Apply token masking to protected technical terms (C++, C#, .NET, Node.js, CI/CD).
    4. Convert string to lowercase.
    5. Strip non-alphanumeric punctuation.
    6. Unmask protected tokens to lowercase equivalents.
    7. Compress consecutive whitespace and newlines.

    Args:
        text: Raw document string.

    Returns:
        str: Normalized, token-safe string.
    """
    if not text or not isinstance(text, str):
        return ""

    # Step 1: Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Step 2: Remove email addresses
    text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", " ", text)

    # Step 3: Mask protected tokens before punctuation stripping
    for pattern, mask in PROTECTED_TOKEN_PATTERNS:
        text = re.sub(pattern, mask, text)

    # Step 4: Lowercase
    text = text.lower()

    # Step 5: Strip noisy punctuation (keeping alphanumeric, spaces, and underscores for masks)
    text = re.sub(r"[^\w\s]", " ", text)

    # Step 6: Unmask protected tokens back to normalized form
    for mask, original in UNMASK_MAPPING.items():
        text = text.replace(mask, original)

    # Step 7: Collapse redundant whitespace and trim
    text = re.sub(r"\s+", " ", text).strip()

    return text
