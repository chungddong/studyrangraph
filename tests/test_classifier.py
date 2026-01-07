"""Classification Agent 테스트"""

from __future__ import annotations

import sys
from pathlib import Path

# UTF-8 출력 설정
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.classifier import ClassificationAgent
from src.agents.log_parser import LogParserAgent


def test_db_connection_failure():
    """시나리오 1: DB 연결 실패 - infrastructure로 분류되어야 함"""
    print("=== Test 1: DB 연결 실패 분류 ===")

    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다: {test_file}")
        return

    # 로그 파싱
    parser = LogParserAgent()
    parser.parse_file(test_file)
    log_data = parser.format_for_llm()

    # 분류
    classifier = ClassificationAgent()
    result = classifier.classify(log_data)

    print(f"✓ 분류 완료")
    print(f"  카테고리: {result['category']}")
    print(f"  심각도: {result['severity']}")
    print(f"  신뢰도: {result['confidence']}")
    print(f"  이유: {result['reason']}")
    print(f"  주요 지표: {', '.join(result['key_indicators'][:3])}")

    # 검증
    assert result['category'] == 'infrastructure', \
        f"DB 연결 실패는 infrastructure로 분류되어야 합니다 (현재: {result['category']})"
    assert result['severity'] in ['critical', 'high'], \
        f"DB 연결 실패는 critical 또는 high 심각도여야 합니다 (현재: {result['severity']})"

    # 라우팅 확인
    routing = classifier.get_routing_decision(result)
    assert routing == 'infrastructure_analyst', \
        f"infrastructure_analyst로 라우팅되어야 합니다 (현재: {routing})"
    print(f"✓ 라우팅: {routing}")


def test_xss_attack():
    """시나리오 2: XSS 공격 - security로 분류되어야 함"""
    print("\n=== Test 2: XSS 공격 분류 ===")

    test_file = project_root / "datasets/scenario-02-xss-attack/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다: {test_file}")
        return

    # 로그 파싱
    parser = LogParserAgent()
    parser.parse_file(test_file)
    log_data = parser.format_for_llm()

    # 분류
    classifier = ClassificationAgent()
    result = classifier.classify(log_data)

    print(f"✓ 분류 완료")
    print(f"  카테고리: {result['category']}")
    print(f"  심각도: {result['severity']}")
    print(f"  신뢰도: {result['confidence']}")
    print(f"  이유: {result['reason']}")
    print(f"  주요 지표: {', '.join(result['key_indicators'][:3])}")

    # 검증
    assert result['category'] == 'security', \
        f"XSS 공격은 security로 분류되어야 합니다 (현재: {result['category']})"
    assert result['severity'] in ['high', 'critical'], \
        f"XSS 공격은 high 또는 critical 심각도여야 합니다 (현재: {result['severity']})"

    # 라우팅 확인
    routing = classifier.get_routing_decision(result)
    assert routing == 'security_analyst', \
        f"security_analyst로 라우팅되어야 합니다 (현재: {routing})"
    print(f"✓ 라우팅: {routing}")


def test_n_plus_one_query():
    """시나리오 3: N+1 쿼리 - performance로 분류되어야 함"""
    print("\n=== Test 3: N+1 쿼리 분류 ===")

    test_file = project_root / "datasets/scenario-03-n-plus-one-query/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다: {test_file}")
        return

    # 로그 파싱
    parser = LogParserAgent()
    parser.parse_file(test_file)
    log_data = parser.format_for_llm()

    # 분류
    classifier = ClassificationAgent()
    result = classifier.classify(log_data)

    print(f"✓ 분류 완료")
    print(f"  카테고리: {result['category']}")
    print(f"  심각도: {result['severity']}")
    print(f"  신뢰도: {result['confidence']}")
    print(f"  이유: {result['reason']}")
    print(f"  주요 지표: {', '.join(result['key_indicators'][:3])}")

    # 검증
    assert result['category'] == 'performance', \
        f"N+1 쿼리는 performance로 분류되어야 합니다 (현재: {result['category']})"
    assert result['severity'] in ['medium', 'high'], \
        f"N+1 쿼리는 medium 또는 high 심각도여야 합니다 (현재: {result['severity']})"

    # 라우팅 확인
    routing = classifier.get_routing_decision(result)
    assert routing == 'performance_analyst', \
        f"performance_analyst로 라우팅되어야 합니다 (현재: {routing})"
    print(f"✓ 라우팅: {routing}")


def test_classification_result_structure():
    """분류 결과 구조 검증"""
    print("\n=== Test 4: 분류 결과 구조 검증 ===")

    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다")
        return

    parser = LogParserAgent()
    parser.parse_file(test_file)
    log_data = parser.format_for_llm()

    classifier = ClassificationAgent()
    result = classifier.classify(log_data)

    # 필수 필드 존재 확인
    required_fields = ['category', 'confidence', 'reason', 'severity', 'key_indicators']
    for field in required_fields:
        assert field in result, f"필수 필드 누락: {field}"

    # 카테고리 값 검증
    valid_categories = ['infrastructure', 'security', 'performance', 'application', 'user']
    assert result['category'] in valid_categories, \
        f"유효하지 않은 카테고리: {result['category']}"

    # 심각도 값 검증
    valid_severities = ['critical', 'high', 'medium', 'low']
    assert result['severity'] in valid_severities, \
        f"유효하지 않은 심각도: {result['severity']}"

    # 신뢰도 값 검증
    valid_confidences = ['high', 'medium', 'low']
    assert result['confidence'] in valid_confidences, \
        f"유효하지 않은 신뢰도: {result['confidence']}"

    # key_indicators가 리스트인지 확인
    assert isinstance(result['key_indicators'], list), \
        "key_indicators는 리스트여야 합니다"

    print(f"✓ 모든 필드 검증 완료")
    print(f"  필수 필드: {', '.join(required_fields)}")
    print(f"  카테고리: {result['category']} (유효함)")
    print(f"  심각도: {result['severity']} (유효함)")
    print(f"  신뢰도: {result['confidence']} (유효함)")
    print(f"  주요 지표 개수: {len(result['key_indicators'])}개")


if __name__ == "__main__":
    try:
        print("Classification Agent 테스트 시작\n")
        print("⚠️  이 테스트는 LLM API를 호출합니다.")
        print("⚠️  .env 파일에 API 키가 설정되어 있어야 합니다.\n")

        test_classification_result_structure()
        test_db_connection_failure()
        test_xss_attack()
        test_n_plus_one_query()

        print("\n" + "=" * 60)
        print("모든 테스트 통과! ✓")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
    except Exception as e:
        print(f"\n[ERROR] 예상치 못한 에러: {e}")
        import traceback
        traceback.print_exc()
