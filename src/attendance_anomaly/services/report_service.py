"""考勤报告生成服务。

将考勤汇总、异常、绩效结论等结果导出为 JSON、CSV、Markdown、HTML 格式，
便于归档与月度汇报。
"""
from __future__ import annotations

import csv
import html
import io
import json
from typing import Any, Dict, List, Sequence


class ReportService:
    """多格式考勤报告生成器。"""

    def to_json(self, payload: Any) -> str:
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def to_csv(self, rows: Sequence[Dict[str, Any]]) -> str:
        if not rows:
            return ""
        columns = self._collect_columns(rows)
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: self._cell(row.get(k)) for k in columns})
        return buffer.getvalue()

    def to_markdown_table(self, rows: Sequence[Dict[str, Any]]) -> str:
        if not rows:
            return ""
        columns = self._collect_columns(rows)
        header = "| " + " | ".join(columns) + " |"
        separator = "| " + " | ".join("---" for _ in columns) + " |"
        body = [
            "| " + " | ".join(self._cell(r.get(c)) for c in columns) + " |"
            for r in rows
        ]
        return "\n".join([header, separator, *body])

    def to_html_page(self, title: str, sections: List[Dict[str, Any]]) -> str:
        blocks = [f"<h1>{html.escape(title)}</h1>"]
        for section in sections:
            heading = section.get("heading", "")
            rows = section.get("rows", [])
            if heading:
                blocks.append(f"<h2>{html.escape(heading)}</h2>")
            if rows:
                blocks.append(self._html_table(rows))
        return (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>{html.escape(title)}</title></head><body>"
            + "".join(blocks)
            + "</body></html>"
        )

    def _html_table(self, rows: Sequence[Dict[str, Any]]) -> str:
        columns = self._collect_columns(rows)
        head = "".join(f"<th>{html.escape(c)}</th>" for c in columns)
        body = [
            "<tr>" + "".join(f"<td>{html.escape(self._cell(r.get(c)))}</td>" for c in columns) + "</tr>"
            for r in rows
        ]
        return (
            "<table border='1' cellspacing='0' cellpadding='4'>"
            f"<thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"
        )

    @staticmethod
    def _collect_columns(rows: Sequence[Dict[str, Any]]) -> List[str]:
        seen: List[str] = []
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.append(key)
        return seen

    @staticmethod
    def _cell(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)
