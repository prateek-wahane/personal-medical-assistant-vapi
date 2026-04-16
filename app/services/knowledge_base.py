import re
from collections import Counter

from sqlalchemy.orm import Session

from app.models import Report


def _tokens(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-zA-Z0-9_]+", text.lower()) if len(token) > 2]


def search_reports(db: Session, query: str, user_id: str | None = None, limit: int = 5) -> list[dict]:
    query_tokens = Counter(_tokens(query))
    report_query = db.query(Report)
    if user_id:
        report_query = report_query.filter(Report.user_id == user_id)

    reports = report_query.order_by(Report.report_date.desc()).all()

    scored: list[tuple[float, Report]] = []
    for report in reports:
        haystack = f"{report.summary_text} {report.raw_text[:3000]}"
        hay_tokens = Counter(_tokens(haystack))
        score = sum(min(hay_tokens[token], count) for token, count in query_tokens.items())
        if score > 0:
            scored.append((float(score), report))

    scored.sort(key=lambda item: (item[0], item[1].report_date.toordinal()), reverse=True)

    documents = []
    for score, report in scored[:limit]:
        documents.append(
            {
                "content": (
                    f"Report date: {report.report_date.isoformat()}\n"
                    f"Original filename: {report.filename}\n"
                    f"Summary: {report.summary_text}"
                ),
                "similarity": round(min(0.99, 0.5 + score / 10), 2),
                "uuid": report.id,
            }
        )
    return documents
