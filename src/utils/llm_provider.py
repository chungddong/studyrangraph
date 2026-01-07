"""LLM Provider 선택 유틸리티"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()  # .env 파일 로드

# 어떤 LLM 제공자를 사용할지 설정
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "claude").strip().lower()
if LLM_PROVIDER not in ("claude", "gemini"):
    raise ValueError("LLM_PROVIDER must be either 'claude' or 'gemini'")

# 모델 이름 설정
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# LLM 설정
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))


def get_llm(temperature: float | None = None):
    """
    환경 변수에 따라 적절한 LLM을 반환

    .env 파일 설정:
    LLM_PROVIDER=claude  # 또는 gemini
    ANTHROPIC_API_KEY=your-key-here  # Claude 사용 시
    GOOGLE_API_KEY=your-key-here     # Gemini 사용 시
    CLAUDE_MODEL=claude-3-5-sonnet-20241022
    GEMINI_MODEL=gemini-1.5-pro
    TEMPERATURE=0.0
    """
    temp = temperature if temperature is not None else TEMPERATURE

    if LLM_PROVIDER == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY가 설정되지 않았습니다. "
                ".env 파일에서 ANTHROPIC_API_KEY를 설정해주세요."
            )

        return ChatAnthropic(
            model=CLAUDE_MODEL,
            temperature=temp,
            anthropic_api_key=api_key
        )

    elif LLM_PROVIDER == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY가 설정되지 않았습니다. "
                ".env 파일에서 GOOGLE_API_KEY를 설정해주세요."
            )

        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            temperature=temp,
            google_api_key=api_key
        )


# 사용 예시
if __name__ == "__main__":
    # 테스트
    try:
        llm = get_llm()
        print(f"[OK] LLM 초기화 성공: {llm.__class__.__name__}")
        print(f"[OK] Provider: {LLM_PROVIDER}")
        print(f"[OK] Model: {CLAUDE_MODEL if LLM_PROVIDER == 'claude' else GEMINI_MODEL}")

        # 간단한 테스트
        response = llm.invoke("Hello! Just say 'Hi' back.")
        print(f"[OK] LLM 응답: {response.content}")

    except ValueError as e:
        print(f"[ERROR] 에러: {e}")
    except Exception as e:
        print(f"[ERROR] 예상치 못한 에러: {e}")