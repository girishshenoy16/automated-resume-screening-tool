"""
Automated unit tests for text cleaning, normalization, and token protection (TASK-18).
Validates URL/email stripping, whitespace collapse, and protected programming symbols (C++, C#, .NET, Node.js, CI/CD).
"""

import pytest
from src.cleaner import clean_text

def test_url_stripping():
    """Verify that HTTP, HTTPS, and WWW URLs are stripped from text."""
    raw = "Profile: https://github.com/alexmorgan-dev and http://alex.io or www.linkedin.com/in/alex"
    cleaned = clean_text(raw)
    assert "https" not in cleaned
    assert "github.com" not in cleaned
    assert "http" not in cleaned
    assert "linkedin.com" not in cleaned
    assert "profile" in cleaned

def test_email_stripping():
    """Verify email addresses are removed cleanly."""
    raw = "Contact: alex.morgan@example.com or lead_dev+tag@sub.domain.co.uk for inquiries."
    cleaned = clean_text(raw)
    assert "alex.morgan" not in cleaned
    assert "@" not in cleaned
    assert "example.com" not in cleaned
    assert "contact" in cleaned
    assert "inquiries" in cleaned

def test_whitespace_normalization():
    """Verify tabs, newlines, and multiple spaces collapse to single spaces."""
    raw = "  Python   \t\t\n\n  developer \r\n   with   Docker   "
    cleaned = clean_text(raw)
    assert cleaned == "python developer with docker"

def test_protected_tokens_c_plus_plus():
    """Verify C++ survives punctuation stripping and is preserved as 'c++'."""
    raw = "Experienced C++ engineer developing low-latency trading algorithms."
    cleaned = clean_text(raw)
    tokens = cleaned.split()
    assert "c++" in tokens
    assert "c" not in tokens or "c++" in cleaned

def test_protected_tokens_c_sharp():
    """Verify C# survives punctuation stripping and is preserved as 'c#'."""
    raw = "Backend services built with C# and .NET Core."
    cleaned = clean_text(raw)
    assert "c#" in cleaned.split()
    assert ".net" in cleaned.split()

def test_protected_tokens_dotnet():
    """Verify .NET survives punctuation stripping and preserves leading dot."""
    raw = "Architected .NET microservices and ASP.NET backends."
    cleaned = clean_text(raw)
    assert ".net" in cleaned.split()

def test_protected_tokens_nodejs():
    """Verify Node.js is preserved as 'node.js'."""
    raw = "Full-stack engineer using Node.js, React, and PostgreSQL."
    cleaned = clean_text(raw)
    assert "node.js" in cleaned.split()

def test_protected_tokens_cicd():
    """Verify CI/CD is preserved as 'ci/cd'."""
    raw = "Implemented automated CI/CD deployment pipelines."
    cleaned = clean_text(raw)
    assert "ci/cd" in cleaned.split()

def test_mixed_protected_tokens_in_single_document():
    """Verify that multiple protected programming symbols in one paragraph all survive intact."""
    raw = "Skills include C++, C#, .NET 8, Node.js runtime, and automated CI/CD with Git."
    cleaned = clean_text(raw)
    tokens = cleaned.split()
    assert "c++" in tokens
    assert "c#" in tokens
    assert ".net" in tokens
    assert "node.js" in tokens
    assert "ci/cd" in tokens
    assert "git" in tokens

def test_punctuation_stripping():
    """Verify noisy punctuation (brackets, quotes, exclamation marks) is stripped."""
    raw = "FastAPI! [Docker] {Kubernetes} (Pandas) / SQL:; \"PostgreSQL\"?"
    cleaned = clean_text(raw)
    assert "!" not in cleaned
    assert "[" not in cleaned
    assert "{" not in cleaned
    assert "\"" not in cleaned
    assert "?" not in cleaned
    for expected in ["fastapi", "docker", "kubernetes", "pandas", "sql", "postgresql"]:
        assert expected in cleaned

def test_cleaner_edge_cases():
    """Verify robustness on empty, None, whitespace, numeric, and Unicode inputs."""
    assert clean_text("") == ""
    assert clean_text(None) == ""
    assert clean_text("   \n\t   ") == ""
    assert clean_text("123 456 789") == "123 456 789"
    assert clean_text("Python 🚀 Developer 🔥") == "python developer"
