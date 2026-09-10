"""LLM Provider abstraction and client implementations.

Supports:
1. OllamaProvider (local open-source models via HTTP)
2. CloudOpenAIProvider (OpenAI-compatible endpoints: OpenAI, Gemini, Groq)
3. DeterministicFallbackProvider (rule-based NLP fallback for hermetic offline execution)
"""

from __future__ import annotations

import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any

import httpx

from .prompts import SYSTEM_EXTRACTION_PROMPT, USER_EXTRACTION_TEMPLATE


class LLMProvider(ABC):
    """Abstract interface for LLM extraction providers."""

    name: str

    @abstractmethod
    def generate_json(self, system_prompt: str, user_prompt: str) -> str:
        """Submit prompts to the model and return raw JSON string."""
        pass


class OllamaProvider(LLMProvider):
    """Local LLM provider interfacing with an Ollama daemon."""

    _cached_available: bool | None = None

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.name = "ollama"
        self.base_url = (
            base_url
            or os.environ.get("OLLAMA_BASE_URL")
            or "http://localhost:11434"
        ).rstrip("/")
        self.model = model or os.environ.get("OLLAMA_MODEL") or "llama3.2"
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if local Ollama daemon is reachable (cached)."""
        if OllamaProvider._cached_available is not None:
            return OllamaProvider._cached_available
        try:
            r = httpx.get(f"{self.base_url}/api/tags", timeout=0.15)
            OllamaProvider._cached_available = (r.status_code == 200)
        except Exception:
            OllamaProvider._cached_available = False
        return OllamaProvider._cached_available

    def generate_json(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "format": "json",
            "stream": False,
        }
        response = httpx.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "{}")


class CloudOpenAIProvider(LLMProvider):
    """Cloud provider using the standard OpenAI chat completions format."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.name = "cloud_openai"
        self.api_key = (
            api_key
            or os.environ.get("OPENAI_API_KEY")
            or os.environ.get("LLM_API_KEY")
        )
        self.base_url = (
            base_url
            or os.environ.get("OPENAI_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        self.model = model or os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
        self.timeout = timeout

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate_json(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("API key is not configured for CloudOpenAIProvider")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0,
        }
        response = httpx.post(url, headers=headers, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


class DeterministicFallbackProvider(LLMProvider):
    """Rule-based natural language entity extractor.

    Acts as an offline, zero-dependency fallback ensuring VerifyFlow runs
    reliably without external network connections or GPU servers.
    """

    def __init__(self) -> None:
        self.name = "deterministic_fallback"

    def generate_json(self, system_prompt: str, user_prompt: str) -> str:
        # Isolate message body if present
        msg_match = re.search(r'Message Text:\s*"""([\s\S]*?)"""', user_prompt)
        text = msg_match.group(1) if msg_match else user_prompt
        claims: list[str] = []

        # 1. Vendor name extraction
        vendor_name: str | None = None
        known_candidates = ["Acme Supplies", "Delta Components", "Northstar Office"]
        for cand in known_candidates:
            if re.search(rf"\b{re.escape(cand)}\b", user_prompt, re.IGNORECASE):
                vendor_name = cand
                break
        if not vendor_name:
            if re.search(r"\bacme\b", user_prompt, re.IGNORECASE):
                vendor_name = "Acme Supplies"
            elif re.search(r"\bdelta\b", user_prompt, re.IGNORECASE):
                vendor_name = "Delta Components"
            elif re.search(r"\bnorthstar\b", user_prompt, re.IGNORECASE):
                vendor_name = "Northstar Office"

        # 2. Invoice number (search specifically in message body with word boundary)
        inv_match = re.search(
            r"\b(?:invoice|inv\.?)\s*[:#]?\s*([a-zA-Z0-9_-]{3,15})\b",
            text,
            re.IGNORECASE,
        )
        if not inv_match:
            inv_match = re.search(r"#\s*([0-9]{3,10})\b", text)

        invoice_number: str | None = None
        if inv_match:
            raw_inv = inv_match.group(1).strip()
            # Normalize e.g. "4938" to "INV-4938" if only digits
            invoice_number = f"INV-{raw_inv}" if raw_inv.isdigit() else raw_inv

        # 3. Bank account target
        account: str | None = None
        acc_match = re.search(r"\b(BANK-[A-Z0-9-]+)\b", text)
        if not acc_match:
            acc_match = re.search(
                r"\b(?:account|acct|iban|bank|details|to)\s*[:#]?\s*([A-Z0-9]+-[A-Z0-9-]+|\b[A-Z0-9]{8,20}\b)",
                text,
                re.IGNORECASE,
            )
        if acc_match:
            account = acc_match.group(1).strip()

        # 4. Amount extraction
        amount: float | None = None
        # Candidate numbers with formatting ($125,000, 125000 USD, for 42000, etc.)
        candidates: list[float] = []
        for amt_pat in [
            r"(?:\$|USD|INR|EUR)\s*([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?|[0-9]{3,8}(?:\.[0-9]{1,2})?)",
            r"([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?|[0-9]{3,8}(?:\.[0-9]{1,2})?)\s*(?:USD|INR|EUR|\$)",
            r"\b(?:for|amount|sum|total|transfer|pay)\s*(?:\$|USD|INR|EUR)?\s*([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?|[0-9]{3,8}(?:\.[0-9]{1,2})?)\b",
            r"\b([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?)\b",
        ]:
            for m in re.finditer(amt_pat, text, re.IGNORECASE):
                clean_val = m.group(1).replace(",", "")
                try:
                    candidates.append(float(clean_val))
                except ValueError:
                    pass

        # Filter candidates: exclude invoice numbers or account subparts
        for cand_val in candidates:
            if invoice_number and str(int(cand_val)) in invoice_number:
                continue
            if account and str(int(cand_val)) in account:
                continue
            amount = cand_val
            break

        # 5. Account change intent
        change_pattern = r"(?:new|migrat|updat|differ|replac|chang|no longer active|partner)"
        account_change = bool(re.search(change_pattern, text, re.IGNORECASE))
        if account_change:
            claims.append("Vendor claims banking relationship or account has changed.")

        # 6. Urgency detection
        urgency_pattern = r"(?:urgent|asap|today|immediately|critical|month-end|priority|rush)"
        is_urgent = bool(re.search(urgency_pattern, text, re.IGNORECASE))
        urgency = "urgent" if is_urgent else "normal"
        if is_urgent:
            claims.append("Payment processing requested under immediate time pressure.")

        # 7. Sender email / domain if present in text
        email_match = re.search(r"[\w\.-]+@([\w\.-]+\.[a-zA-Z]{2,})", user_prompt)
        sender_email = email_match.group(0) if email_match else None
        sender_domain = email_match.group(1) if email_match else None

        result_dict = {
            "vendor_name": vendor_name,
            "invoice_number": invoice_number,
            "amount": amount,
            "requested_account": account,
            "sender_email": sender_email,
            "sender_domain": sender_domain,
            "requested_account_change": account_change,
            "urgency": urgency,
            "claims": claims,
            "confidence": 0.95 if (vendor_name and invoice_number) else 0.70,
        }
        return json.dumps(result_dict)


def get_llm_provider(preference: str | None = None) -> LLMProvider:
    """Resolve an LLM provider based on explicit choice or environment availability.

    Order of resolution:
    1. Explicit preference ("ollama", "cloud", "deterministic")
    2. CloudOpenAIProvider (if API key is in environment)
    3. OllamaProvider (if local daemon is running)
    4. DeterministicFallbackProvider (guaranteed offline fallback)
    """
    if preference == "deterministic":
        return DeterministicFallbackProvider()
    if preference == "ollama":
        return OllamaProvider()
    if preference in ("cloud", "openai"):
        return CloudOpenAIProvider()

    # Automatic detection
    cloud = CloudOpenAIProvider()
    if cloud.is_available():
        return cloud

    ollama = OllamaProvider()
    if ollama.is_available():
        return ollama

    return DeterministicFallbackProvider()
