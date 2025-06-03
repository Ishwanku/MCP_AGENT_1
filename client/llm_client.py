import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from openai import AsyncOpenAI
from ollama import AsyncClient as OllamaClient
import aiohttp
import asyncio

load_dotenv()

class LLMClient:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        self.model = os.getenv("LLM_MODEL", "qwen2:7b-instruct")  # Default to tool-call capable model
        self.client = None
        self.initialize_client()

    def initialize_client(self):
        """Initialize the appropriate LLM client based on provider."""
        try:
            if self.provider == "gemini":
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ValueError("GEMINI_API_KEY not set in .env")
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel(self.model)
            elif self.provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                base_url = os.getenv("OPENAI_BASE_URL")  # Support Ollama's OpenAI-compatible endpoint
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not set in .env")
                self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            elif self.provider == "grok":
                api_key = os.getenv("GROK_API_KEY")
                if not api_key:
                    raise ValueError("GROK_API_KEY not set in .env")
                self.client = {"api_key": api_key, "endpoint": "https://api.x.ai/v1"}
            elif self.provider == "ollama":
                host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
                self.client = OllamaClient(host=host)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize {self.provider} client: {str(e)}")

    async def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Handle chat completion with tool calls for any provider."""
        try:
            if self.provider == "gemini":
                return await self._gemini_chat(messages, tools)
            elif self.provider == "openai":
                return await self._openai_chat(messages, tools)
            elif self.provider == "grok":
                return await self._grok_chat(messages, tools)
            elif self.provider == "ollama":
                return await self._ollama_chat(messages, tools)
        except Exception as e:
            return {"error": f"Chat failed: {str(e)}"}

    async def _gemini_chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]]) -> Dict[str, Any]:
        """Handle Gemini chat completion."""
        formatted_tools = [{"function_declarations": tools}] if tools else None
        response = await asyncio.to_thread(
            self.client.generate_content,
            contents=[{"role": m["role"], "parts": [{"text": m["content"]}]} for m in messages],
            tools=formatted_tools
        )
        if response.candidates and response.candidates[0].content.parts:
            if any(part.function_call for part in response.candidates[0].content.parts):
                tool_calls = [
                    {
                        "type": "function",
                        "function": {
                            "name": part.function_call.name,
                            "arguments": dict(part.function_call.args)
                        }
                    }
                    for part in response.candidates[0].content.parts
                    if part.function_call
                ]
                return {"tool_calls": tool_calls}
        return {
            "message": {"content": response.candidates[0].content.parts[0].text if response.candidates[0].content.parts else ""}, 
            "type": "response"
        }

    async def _openai_chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]]) -> Dict[str, Any]:
        """Handle OpenAI chat completion."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None
        )
        if response.choices[0].message.tool_calls:
            return {
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": json.loads(tc.function.arguments)
                        }
                    }
                    for tc in response.choices[0].message.tool_calls
                ]
            }
        return {
            "message": {"content": response.choices[0].message.content or ""}, 
            "type": "response"
        }

    async def _grok_chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]]) -> Dict[str, Any]:
        """Handle Grok chat completion."""
        headers = {
            "Authorization": f"Bearer {self.client['api_key']}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools if tools else None
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.client['endpoint']}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Grok API error: {await response.text()}")
                data = await response.json()
        
        if data.get("choices") and data["choices"][0]["message"].get("tool_calls"):
            return {
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": json.loads(tc["function"]["arguments"])
                        }
                    }
                    for tc in data["choices"][0]["message"]["tool_calls"]
                ]
            }
        return {
            "message": {"content": data["choices"][0]["message"]["content"] or ""}, 
            "type": "response"
        }

    async def _ollama_chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]]) -> Dict[str, Any]:
        """Handle Ollama chat completion."""
        response = await self.client.chat(
            model=self.model,
            messages=messages,
            tools=tools
        )
        if response.get("message", {}).get("tool_calls"):
            return {
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"]
                        }
                    }
                    for tc in response["message"]["tool_calls"]
                ]
            }
        return {"message": response["message"], "type": "response"}