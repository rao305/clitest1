"""
CLI Chat Service Adapter
------------------------
Wraps the existing CLI components into a callable service for API usage.

This provides a simple interface:
    response = CLIChatService().process_message(session_id, message)

It manages session history using the existing SessionManager and generates
responses via SmartAIEngine with contextual information.
"""

from __future__ import annotations

import threading
from datetime import datetime
from typing import Any, Dict, Optional

# Reuse existing components powering the CLI
from ..session_manager import SessionManager
from ..smart_ai_engine import SmartAIEngine


class CLIChatService:
    """Adapter to expose CLI chat logic as a simple callable service."""

    _instance_lock: threading.Lock = threading.Lock()
    _instance: Optional["CLIChatService"] = None

    def __new__(cls, *args, **kwargs):
        # Singleton to share session manager state across requests
        if not hasattr(cls, "_instance") or cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):  # avoid re-init in singleton
            return
        self.session_manager = SessionManager()
        self.smart_ai = SmartAIEngine()
        self._initialized = True

    def process_message(self, session_id: Optional[str], message: str) -> Dict[str, Any]:
        """Process a single user message and return structured result.

        Args:
            session_id: Existing session identifier; if None, a new session is created.
            message: The user's message text.

        Returns:
            Dict with keys: session_id, response, response_time_ms, intent (optional),
            entities (optional), metadata (optional)
        """
        if not message or not message.strip():
            raise ValueError("Message must be a non-empty string")

        # Ensure we have a session
        if not session_id:
            session_id = self.session_manager.create_session()

        # Build context from conversation and current query
        conversation_context = self.session_manager.get_conversation_context(session_id)
        query_context = self.session_manager.extract_context_from_query(message)

        full_context: Dict[str, Any] = {
            "conversation_history": conversation_context,
            "query_context": query_context,
        }

        start_time = datetime.now()
        ai_result: Dict[str, Any] = self.smart_ai.generate_intelligent_response(message, full_context)
        end_time = datetime.now()

        response_time_ms = int((end_time - start_time).total_seconds() * 1000)

        # Persist turn in session history
        self.session_manager.update_session(
            session_id=session_id,
            user_input=message,
            bot_response=ai_result.get("response", ""),
            context=query_context,
        )

        result: Dict[str, Any] = {
            "session_id": session_id,
            "response": ai_result.get("response", ""),
            "response_time_ms": response_time_ms,
            "intent": ai_result.get("intent"),
            "entities": ai_result.get("entities", {}),
            "metadata": {
                "method": ai_result.get("method"),
                "source": ai_result.get("source"),
            },
        }
        return result





