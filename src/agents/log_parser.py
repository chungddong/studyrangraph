"""Log Parser Agent - PM2 로그 파싱 및 구조화"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import TypedDict


class LogEntry(TypedDict):
    """파싱된 로그 엔트리 구조"""
    timestamp: str
    level: str
    message: str
    raw: str
    line_number: int


class LogStatistics(TypedDict):
    """로그 통계 정보"""
    total_lines: int
    error_count: int
    warn_count: int
    info_count: int
    debug_count: int
    time_range: dict[str, str | None]
    error_patterns: dict[str, int]


class LogParserAgent:
    """PM2 로그 파서 에이전트

    로그 포맷: [Timestamp] [Level] Message
    예시: [2026-01-05 03:14:55] INFO Server is running on port 3333
    """

    # PM2 로그 포맷 정규식
    LOG_PATTERN = re.compile(
        r'^\[(?P<timestamp>[\d\-\s:]+)\]\s+'
        r'(?P<level>INFO|ERROR|WARN|DEBUG)\s+'
        r'(?P<message>.+)$'
    )

    def __init__(self):
        self.logs: list[LogEntry] = []
        self.statistics: LogStatistics | None = None

    def parse_file(self, file_path: str | Path) -> list[LogEntry]:
        """로그 파일을 읽어서 파싱

        Args:
            file_path: 로그 파일 경로

        Returns:
            파싱된 로그 엔트리 리스트
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"로그 파일을 찾을 수 없습니다: {file_path}")

        self.logs = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                log_entry = self._parse_line(line, line_num)
                if log_entry:
                    self.logs.append(log_entry)

        # 통계 생성
        self.statistics = self._generate_statistics()

        return self.logs

    def _parse_line(self, line: str, line_number: int) -> LogEntry | None:
        """단일 로그 라인 파싱

        Args:
            line: 로그 라인
            line_number: 라인 번호

        Returns:
            파싱된 로그 엔트리 또는 None
        """
        match = self.LOG_PATTERN.match(line)

        if match:
            return LogEntry(
                timestamp=match.group('timestamp').strip(),
                level=match.group('level').strip(),
                message=match.group('message').strip(),
                raw=line,
                line_number=line_number
            )

        # 파싱 실패한 경우 (멀티라인 로그 등)
        return None

    def _generate_statistics(self) -> LogStatistics:
        """로그 통계 정보 생성

        Returns:
            로그 통계 정보
        """
        error_count = 0
        warn_count = 0
        info_count = 0
        debug_count = 0
        error_patterns: dict[str, int] = {}

        first_timestamp = None
        last_timestamp = None

        for log in self.logs:
            level = log['level']

            if level == 'ERROR':
                error_count += 1
                # 에러 패턴 추출
                message = log['message']
                # 주요 에러 키워드 추출
                if 'Database' in message or 'database' in message:
                    error_patterns['Database Error'] = error_patterns.get('Database Error', 0) + 1
                elif 'connect' in message.lower() or 'connection' in message.lower():
                    error_patterns['Connection Error'] = error_patterns.get('Connection Error', 0) + 1
                elif '500' in message:
                    error_patterns['HTTP 500'] = error_patterns.get('HTTP 500', 0) + 1
                elif '401' in message:
                    error_patterns['HTTP 401 Unauthorized'] = error_patterns.get('HTTP 401 Unauthorized', 0) + 1
                elif '403' in message:
                    error_patterns['HTTP 403 Forbidden'] = error_patterns.get('HTTP 403 Forbidden', 0) + 1
                elif '400' in message:
                    error_patterns['HTTP 400 Bad Request'] = error_patterns.get('HTTP 400 Bad Request', 0) + 1
                else:
                    error_patterns['Other Error'] = error_patterns.get('Other Error', 0) + 1

            elif level == 'WARN':
                warn_count += 1
            elif level == 'INFO':
                info_count += 1
            elif level == 'DEBUG':
                debug_count += 1

            # 타임스탬프 범위 계산
            if first_timestamp is None:
                first_timestamp = log['timestamp']
            last_timestamp = log['timestamp']

        return LogStatistics(
            total_lines=len(self.logs),
            error_count=error_count,
            warn_count=warn_count,
            info_count=info_count,
            debug_count=debug_count,
            time_range={
                'start': first_timestamp,
                'end': last_timestamp
            },
            error_patterns=error_patterns
        )

    def get_logs_by_level(self, level: str) -> list[LogEntry]:
        """특정 레벨의 로그만 필터링

        Args:
            level: 로그 레벨 (INFO, ERROR, WARN, DEBUG)

        Returns:
            필터링된 로그 리스트
        """
        return [log for log in self.logs if log['level'] == level.upper()]

    def get_error_logs(self) -> list[LogEntry]:
        """에러 로그만 반환"""
        return self.get_logs_by_level('ERROR')

    def get_logs_with_keyword(self, keyword: str, case_sensitive: bool = False) -> list[LogEntry]:
        """특정 키워드를 포함한 로그 필터링

        Args:
            keyword: 검색 키워드
            case_sensitive: 대소문자 구분 여부

        Returns:
            필터링된 로그 리스트
        """
        if case_sensitive:
            return [log for log in self.logs if keyword in log['message']]
        else:
            keyword_lower = keyword.lower()
            return [log for log in self.logs if keyword_lower in log['message'].lower()]

    def get_statistics(self) -> LogStatistics | None:
        """통계 정보 반환"""
        return self.statistics

    def format_for_llm(self) -> str:
        """LLM에 전달할 수 있는 형태로 포맷팅

        Returns:
            포맷팅된 로그 문자열
        """
        if not self.logs:
            return "로그 데이터가 없습니다."

        output = []

        # 통계 정보
        if self.statistics:
            stats = self.statistics
            output.append("=== 로그 통계 정보 ===")
            output.append(f"총 로그 라인 수: {stats['total_lines']}")
            output.append(f"ERROR: {stats['error_count']}, WARN: {stats['warn_count']}, INFO: {stats['info_count']}, DEBUG: {stats['debug_count']}")
            output.append(f"시간 범위: {stats['time_range']['start']} ~ {stats['time_range']['end']}")

            if stats['error_patterns']:
                output.append("\n에러 패턴 분석:")
                for pattern, count in sorted(stats['error_patterns'].items(), key=lambda x: x[1], reverse=True):
                    output.append(f"  - {pattern}: {count}건")

            output.append("\n")

        # 전체 로그 (라인 번호 포함)
        output.append("=== 전체 로그 ===")
        for log in self.logs:
            output.append(f"[Line {log['line_number']:3d}] {log['raw']}")

        return "\n".join(output)


# 사용 예시
if __name__ == "__main__":
    # 테스트
    parser = LogParserAgent()

    # 예시 로그 파일 경로
    test_file = Path("datasets/scenario-01-db-connection-failure/dataset-01.log")

    if test_file.exists():
        print(f"[OK] 로그 파일 파싱 시작: {test_file}")

        # 로그 파싱
        logs = parser.parse_file(test_file)
        print(f"[OK] 총 {len(logs)}개의 로그 파싱 완료")

        # 통계 출력
        stats = parser.get_statistics()
        if stats:
            print(f"\n[통계]")
            print(f"  ERROR: {stats['error_count']}")
            print(f"  WARN: {stats['warn_count']}")
            print(f"  INFO: {stats['info_count']}")
            print(f"  시간 범위: {stats['time_range']['start']} ~ {stats['time_range']['end']}")

            if stats['error_patterns']:
                print(f"\n[에러 패턴]")
                for pattern, count in stats['error_patterns'].items():
                    print(f"  {pattern}: {count}건")

        # 에러 로그만 출력
        error_logs = parser.get_error_logs()
        print(f"\n[에러 로그] {len(error_logs)}건")
        for log in error_logs[:5]:  # 처음 5개만
            print(f"  [Line {log['line_number']}] {log['message'][:80]}...")

        # LLM용 포맷 출력 (일부만)
        print("\n[LLM용 포맷 (처음 20라인)]")
        llm_format = parser.format_for_llm()
        lines = llm_format.split('\n')[:30]
        print('\n'.join(lines))
    else:
        print(f"[ERROR] 테스트 파일을 찾을 수 없습니다: {test_file}")