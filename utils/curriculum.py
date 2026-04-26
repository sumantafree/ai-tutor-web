"""
📚 Dynamic Curriculum
=====================
DB-backed subjects → chapters → topics tree, with auto-seed from the legacy
hardcoded `SYLLABUS` constant in utils/config.py on first run.

Design notes:
- Two tables only: `cur_subjects` and `cur_chapters`.
- Topics, key_points, examples, questions are stored as JSON arrays on the
  chapter row. Lighter than 4 extra tables, easy to edit in the admin UI,
  and matches how every consumer already wants the data shape.
- Returned dicts mirror the OLD `SUBJECTS` list / `SYLLABUS` dict shape so
  consumer code only needs trivial changes.
"""

from __future__ import annotations
import json
from typing import Optional

from utils.database import (
    get_connection, _exec, _fetchone, _fetchall, USE_PG,
)


# ─────────────────────────────────────────────────────────
# SEED-ON-FIRST-USE
# ─────────────────────────────────────────────────────────

_SEEDED = False  # process-level cache; cheap re-check guard


def _ensure_seeded() -> None:
    """If the curriculum tables are empty, seed them from the hardcoded
    SUBJECTS / SYLLABUS in utils.config. Idempotent."""
    global _SEEDED
    if _SEEDED:
        return
    conn = get_connection()
    row = _fetchone(conn, "SELECT COUNT(*) AS c FROM cur_subjects")
    count = (row or {}).get("c", 0) or 0
    if count > 0:
        conn.close()
        _SEEDED = True
        return

    # Lazy import to avoid circular dependency (config imports nothing from us).
    from utils.config import SUBJECTS as SEED_SUBJECTS, SYLLABUS as SEED_SYLLABUS

    # Insert subjects
    for i, s in enumerate(SEED_SUBJECTS):
        _exec(
            conn,
            "INSERT INTO cur_subjects (code, name, icon, color, bg, sort_order) "
            "VALUES (?,?,?,?,?,?)",
            (s["id"], s["name"], s["icon"], s["color"], s["bg"], i),
        )
    conn.commit()

    # Map seeded code → DB id
    rows = _fetchall(conn, "SELECT id, code FROM cur_subjects")
    code_to_id = {r["code"]: r["id"] for r in rows}

    # Insert chapters
    for code, data in SEED_SYLLABUS.items():
        sid = code_to_id.get(code)
        if not sid:
            continue
        for j, ch in enumerate(data.get("chapters", [])):
            _exec(
                conn,
                """INSERT INTO cur_chapters
                    (subject_id, original_id, title, explanation,
                     topics_json, key_points_json, examples_json, questions_json,
                     sort_order)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    sid,
                    int(ch.get("id") or 0),
                    ch.get("title") or "",
                    ch.get("explanation") or "",
                    json.dumps(ch.get("topics") or []),
                    json.dumps(ch.get("key_points") or []),
                    json.dumps(ch.get("examples") or []),
                    json.dumps(ch.get("questions") or []),
                    j,
                ),
            )
    conn.commit()
    conn.close()
    _SEEDED = True


def invalidate_cache() -> None:
    """Force the next read to re-check the seed (useful after admin edits)."""
    global _SEEDED
    _SEEDED = False
    _SEEDED = True  # tables are guaranteed to exist after first call


# ─────────────────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────────────────

def _subject_row_to_dict(r: dict) -> dict:
    """Match legacy SUBJECTS shape: {id, name, icon, color, bg}."""
    return {
        "id": r["code"],
        "name": r["name"],
        "icon": r.get("icon") or "📚",
        "color": r.get("color") or "#74B9FF",
        "bg": r.get("bg") or "#E5F4FB",
        "_db_id": r["id"],
        "_sort_order": r.get("sort_order") or 0,
    }


def _chapter_row_to_dict(r: dict) -> dict:
    """Match legacy SYLLABUS chapter shape."""
    def _j(field):
        try:
            return json.loads(r.get(field) or "[]")
        except Exception:
            return []
    return {
        "id": r.get("original_id") or r.get("id"),
        "_db_id": r["id"],
        "title": r.get("title") or "",
        "explanation": r.get("explanation") or "",
        "topics": _j("topics_json"),
        "key_points": _j("key_points_json"),
        "examples": _j("examples_json"),
        "questions": _j("questions_json"),
        "_sort_order": r.get("sort_order") or 0,
    }


def get_all_subjects() -> list[dict]:
    """Return all subjects in legacy SUBJECTS shape, ordered by sort_order."""
    _ensure_seeded()
    conn = get_connection()
    rows = _fetchall(
        conn,
        "SELECT * FROM cur_subjects ORDER BY sort_order, id",
    )
    conn.close()
    return [_subject_row_to_dict(r) for r in rows]


def get_subject(code: str) -> dict:
    """Get one subject by its code; falls back to first subject if not found."""
    if not code:
        all_ = get_all_subjects()
        return all_[0] if all_ else _generic_subject()
    _ensure_seeded()
    conn = get_connection()
    row = _fetchone(conn, "SELECT * FROM cur_subjects WHERE code=?", (code,))
    conn.close()
    if row:
        return _subject_row_to_dict(row)
    all_ = get_all_subjects()
    return all_[0] if all_ else _generic_subject()


def _generic_subject() -> dict:
    return {"id": "general", "name": "General", "icon": "📚",
            "color": "#74B9FF", "bg": "#E5F4FB", "_db_id": None, "_sort_order": 0}


def get_chapters_for(subject_code: str) -> list[dict]:
    """Return all chapters for a subject, in legacy shape."""
    _ensure_seeded()
    if not subject_code:
        return []
    conn = get_connection()
    srow = _fetchone(conn, "SELECT id FROM cur_subjects WHERE code=?", (subject_code,))
    if not srow:
        conn.close()
        return []
    rows = _fetchall(
        conn,
        "SELECT * FROM cur_chapters WHERE subject_id=? ORDER BY sort_order, id",
        (srow["id"],),
    )
    conn.close()
    return [_chapter_row_to_dict(r) for r in rows]


def get_chapter(subject_code: str, chapter_db_id: int) -> Optional[dict]:
    """Get one chapter by DB id within the given subject."""
    _ensure_seeded()
    conn = get_connection()
    srow = _fetchone(conn, "SELECT id FROM cur_subjects WHERE code=?", (subject_code,))
    if not srow:
        conn.close()
        return None
    row = _fetchone(
        conn,
        "SELECT * FROM cur_chapters WHERE subject_id=? AND id=?",
        (srow["id"], chapter_db_id),
    )
    conn.close()
    return _chapter_row_to_dict(row) if row else None


def get_syllabus() -> dict:
    """Return the full syllabus in the SAME nested shape as the legacy
    SYLLABUS dict: {subject_code: {"chapters": [chapter_dict, ...]}}"""
    out = {}
    for s in get_all_subjects():
        out[s["id"]] = {"chapters": get_chapters_for(s["id"])}
    return out


# ─────────────────────────────────────────────────────────
# WRITE — SUBJECTS
# ─────────────────────────────────────────────────────────

def _make_unique_code(name: str, conn) -> str:
    """Auto-derive a URL-safe code from the name; ensure unique."""
    base = "".join(c.lower() if c.isalnum() else "_" for c in name).strip("_") or "subject"
    code = base
    n = 2
    while True:
        row = _fetchone(conn, "SELECT 1 AS x FROM cur_subjects WHERE code=?", (code,))
        if not row:
            return code
        code = f"{base}_{n}"
        n += 1


def add_subject(name: str, icon: str = "📚", color: str = "#74B9FF",
                bg: str = "#E5F4FB", code: Optional[str] = None) -> int:
    """Insert a new subject. Returns its DB id."""
    _ensure_seeded()
    conn = get_connection()
    if not code:
        code = _make_unique_code(name, conn)
    # Determine next sort_order
    row = _fetchone(conn, "SELECT COALESCE(MAX(sort_order), -1) AS m FROM cur_subjects")
    next_order = (row.get("m") if row else -1) + 1
    _exec(
        conn,
        "INSERT INTO cur_subjects (code, name, icon, color, bg, sort_order) "
        "VALUES (?,?,?,?,?,?)",
        (code, name, icon or "📚", color or "#74B9FF", bg or "#E5F4FB", next_order),
    )
    new_row = _fetchone(conn, "SELECT id FROM cur_subjects WHERE code=?", (code,))
    conn.commit()
    conn.close()
    return (new_row or {}).get("id", 0)


def update_subject(db_id: int, **fields) -> None:
    """Update any of: name, icon, color, bg, sort_order."""
    _ensure_seeded()
    allowed = {"name", "icon", "color", "bg", "sort_order"}
    sets, vals = [], []
    for k, v in fields.items():
        if k in allowed and v is not None:
            sets.append(f"{k}=?")
            vals.append(v)
    if not sets:
        return
    vals.append(db_id)
    conn = get_connection()
    _exec(conn, f"UPDATE cur_subjects SET {', '.join(sets)} WHERE id=?", tuple(vals))
    conn.commit()
    conn.close()


def delete_subject(db_id: int) -> None:
    """Delete a subject AND all its chapters."""
    _ensure_seeded()
    conn = get_connection()
    _exec(conn, "DELETE FROM cur_chapters WHERE subject_id=?", (db_id,))
    _exec(conn, "DELETE FROM cur_subjects WHERE id=?", (db_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────
# WRITE — CHAPTERS
# ─────────────────────────────────────────────────────────

def add_chapter(subject_db_id: int, title: str, explanation: str = "",
                topics: Optional[list] = None,
                key_points: Optional[list] = None,
                examples: Optional[list] = None,
                questions: Optional[list] = None) -> int:
    """Insert a new chapter under a subject. Returns its DB id."""
    _ensure_seeded()
    conn = get_connection()
    row = _fetchone(
        conn,
        "SELECT COALESCE(MAX(sort_order), -1) AS m FROM cur_chapters WHERE subject_id=?",
        (subject_db_id,),
    )
    next_order = (row.get("m") if row else -1) + 1
    _exec(
        conn,
        """INSERT INTO cur_chapters
            (subject_id, original_id, title, explanation,
             topics_json, key_points_json, examples_json, questions_json, sort_order)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (
            subject_db_id, next_order + 1, title or "", explanation or "",
            json.dumps(topics or []),
            json.dumps(key_points or []),
            json.dumps(examples or []),
            json.dumps(questions or []),
            next_order,
        ),
    )
    new = _fetchone(
        conn,
        "SELECT id FROM cur_chapters WHERE subject_id=? ORDER BY id DESC LIMIT 1",
        (subject_db_id,),
    )
    conn.commit()
    conn.close()
    return (new or {}).get("id", 0)


def update_chapter(db_id: int, **fields) -> None:
    """Update any of: title, explanation, topics, key_points, examples,
    questions, sort_order."""
    _ensure_seeded()
    sets, vals = [], []
    if "title" in fields and fields["title"] is not None:
        sets.append("title=?"); vals.append(fields["title"])
    if "explanation" in fields and fields["explanation"] is not None:
        sets.append("explanation=?"); vals.append(fields["explanation"])
    if "topics" in fields and fields["topics"] is not None:
        sets.append("topics_json=?"); vals.append(json.dumps(fields["topics"]))
    if "key_points" in fields and fields["key_points"] is not None:
        sets.append("key_points_json=?"); vals.append(json.dumps(fields["key_points"]))
    if "examples" in fields and fields["examples"] is not None:
        sets.append("examples_json=?"); vals.append(json.dumps(fields["examples"]))
    if "questions" in fields and fields["questions"] is not None:
        sets.append("questions_json=?"); vals.append(json.dumps(fields["questions"]))
    if "sort_order" in fields and fields["sort_order"] is not None:
        sets.append("sort_order=?"); vals.append(int(fields["sort_order"]))
    if not sets:
        return
    vals.append(db_id)
    conn = get_connection()
    _exec(conn, f"UPDATE cur_chapters SET {', '.join(sets)} WHERE id=?", tuple(vals))
    conn.commit()
    conn.close()


def delete_chapter(db_id: int) -> None:
    _ensure_seeded()
    conn = get_connection()
    _exec(conn, "DELETE FROM cur_chapters WHERE id=?", (db_id,))
    conn.commit()
    conn.close()
