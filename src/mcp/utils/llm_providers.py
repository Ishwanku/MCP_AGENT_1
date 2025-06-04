"""
LLM provider implementations for different model backends.

This module provides implementations for different LLM providers:
- Ollama
- HuggingFace
- vLLM
- OpenAI (for reference)
"""

import json
from typing import Any, Dict, List, Optional, Union
import httpx
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from vllm import LLM, SamplingParams
from ..core.config import settings

class BaseLLMProvider:
    """Base class for LLM providers."""
    
    def __init__(self):
        """Initialize the provider with configuration."""
        self.config = settings.llm
        self.timeout = self.config.TIMEOUT

    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate text using the LLM."""
        raise NotImplementedError

    async def get_embeddings(self, text: Union[str, List[str]]) -> List[List[float]]:
        """Get embeddings for the given text."""
        raise NotImplementedError

class OllamaProvider(BaseLLMProvider):
    """Provider for Ollama models."""

    def __init__(self):
        """Initialize the Ollama provider."""
        super().__init__()
        self.client = httpx.AsyncClient(
            base_url=self.config.LLM_BASE_URL,
            timeout=self.timeout
        )

    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate text using Ollama."""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.post(
            "/api/generate",
            json={
                "model": self.config.LLM_MODEL,
                "messages": messages,
                "temperature": temperature or self.config.TEMPERATURE,
                "max_tokens": max_tokens or self.config.MAX_TOKENS,
                "top_p": self.config.TOP_P,
                "top_k": self.config.TOP_K,
                "repeat_penalty": self.config.REPETITION_PENALTY,
                "stop": self.config.STOP_SEQUENCES,
                "stream": False,
            },
        )
        response.raise_for_status()
        result = response.json()

        return {
            "content": result["response"],
            "function_call": None,  # Ollama doesn't support function calling yet
        }

    async def get_embeddings(self, text: Union[str, List[str]]) -> List[List[float]]:
        """Get embeddings using Ollama."""
        if isinstance(text, str):
            text = [text]

        embeddings = []
        for t in text:
            response = await self.client.post(
                "/api/embeddings",
                json={
                    "model": self.config.EMBEDDING_MODEL,
                    "prompt": t,
                },
            )
            response.raise_for_status()
            result = response.json()
            embeddings.append(result["embedding"])
        return embeddings

class HuggingFaceProvider(BaseLLMProvider):
    """Provider for HuggingFace models."""

    def __init__(self):
        """Initialize the HuggingFace provider."""
        super().__init__()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.LLM_MODEL,
            cache_dir=self.config.CACHE_DIR
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.LLM_MODEL,
            cache_dir=self.config.CACHE_DIR,
            device_map="auto"
        )
        self.embedding_model = pipeline(
            "feature-extraction",
            model=self.config.EMBEDDING_MODEL,
            device_map="auto"
        )

    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate text using HuggingFace model."""
        full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
        inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens or self.config.MAX_TOKENS,
            temperature=temperature or self.config.TEMPERATURE,
            top_p=self.config.TOP_P,
            top_k=self.config.TOP_K,
            repetition_penalty=self.config.REPETITION_PENALTY,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {
            "content": response[len(full_prompt):],
            "function_call": None,
        }

    async def get_embeddings(self, text: Union[str, List[str]]) -> List[List[float]]:
        """Get embeddings using HuggingFace model."""
        if isinstance(text, str):
            text = [text]

        embeddings = self.embedding_model(
            text,
            batch_size=self.config.BATCH_SIZE,
            truncation=True,
            max_length=512
        )
        return [emb[0].mean(dim=0).tolist() for emb in embeddings]

class VLLMProvider(BaseLLMProvider):
    """Provider for vLLM models."""

    def __init__(self):
        """Initialize the vLLM provider."""
        super().__init__()
        self.model = LLM(
            model=self.config.LLM_MODEL,
            trust_remote_code=True,
            tensor_parallel_size=torch.cuda.device_count() if torch.cuda.is_available() else 1
        )
        self.tokenizer = self.model.get_tokenizer()

    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate text using vLLM."""
        full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
        
        sampling_params = SamplingParams(
            temperature=temperature or self.config.TEMPERATURE,
            max_tokens=max_tokens or self.config.MAX_TOKENS,
            top_p=self.config.TOP_P,
            top_k=self.config.TOP_K,
            repetition_penalty=self.config.REPETITION_PENALTY,
            stop=self.config.STOP_SEQUENCES
        )

        outputs = self.model.generate(
            [full_prompt],
            sampling_params
        )

        return {
            "content": outputs[0].outputs[0].text,
            "function_call": None,
        }

    async def get_embeddings(self, text: Union[str, List[str]]) -> List[List[float]]:
        """Get embeddings using vLLM model."""
        if isinstance(text, str):
            text = [text]

        embeddings = []
        for t in text:
            inputs = self.tokenizer(
                t,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            with torch.no_grad():
                outputs = self.model.model(**inputs)
                embeddings.append(outputs.last_hidden_state.mean(dim=1).squeeze().tolist())
        return embeddings

def get_provider() -> BaseLLMProvider:
    """Get the appropriate LLM provider based on configuration."""
    provider_map = {
        "ollama": OllamaProvider,
        "huggingface": HuggingFaceProvider,
        "vllm": VLLMProvider,
    }
    
    provider_class = provider_map.get(settings.llm.LLM_TYPE)
    if not provider_class:
        raise ValueError(f"Unsupported LLM type: {settings.llm.LLM_TYPE}")
    
    return provider_class() 