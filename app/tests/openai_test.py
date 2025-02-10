from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LangChain ChatOpenAI 객체 생성
llm = ChatOpenAI(
    temperature=0.1,  # 창의성 (0.0 ~ 2.0)
    model_name="gpt-3.5-turbo",  # 모델명
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    streaming=False  # 스트리밍을 비활성화하여 전체 응답을 한 번에 받음
)

def test_chat():
    # 질의내용
    question = "대한민국의 수도는 어디인가요?"
    print(f"\n[질문]: {question}")

    # 콜백으로 토큰 사용량 추적
    with get_openai_callback() as cb:
        # 질의 실행
        response = llm.invoke(question)
        
        # 답변 출력
        print(f"\n[답변]: {response.content}")
        
        # 토큰 사용량 출력
        print(f"\n[토큰 사용량]")
        print(f"프롬프트 토큰: {cb.prompt_tokens}")
        print(f"응답 토큰: {cb.completion_tokens}")
        print(f"총 토큰: {cb.total_tokens}")
        print(f"총 비용: ${cb.total_cost:.6f}")
        
        # 메타데이터 출력
        print(f"\n[메타데이터]: {response.response_metadata}")

if __name__ == "__main__":
    test_chat()

