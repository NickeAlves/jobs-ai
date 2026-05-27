from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Optional

from jobs_ai.models import (
    ApplicationStatus,
    DashboardStats,
    JobOpening,
    JobRecord,
    LogRecord,
    PlatformConnection,
    utc_now,
)


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                create table if not exists jobs (
                    id integer primary key autoincrement,
                    external_id text not null,
                    source text not null,
                    title text not null,
                    company text not null,
                    location text not null default '',
                    url text not null,
                    description text not null,
                    salary text not null default '',
                    tags text not null default '[]',
                    language text not null default 'unknown',
                    work_mode text not null default 'unknown',
                    preference_match integer not null default 1,
                    preference_reason text not null default '',
                    status text not null default 'discovered',
                    match_score integer,
                    match_summary text not null default '',
                    requirements text not null default '[]',
                    tailored_resume text not null default '',
                    selected_resume_name text not null default '',
                    answers text not null default '[]',
                    discovered_at text not null,
                    submitted_at text,
                    updated_at text not null,
                    unique (external_id, source)
                );

                create table if not exists logs (
                    id integer primary key autoincrement,
                    job_id integer,
                    level text not null,
                    event text not null,
                    message text not null,
                    metadata text not null default '{}',
                    created_at text not null,
                    foreign key (job_id) references jobs(id)
                );

                create table if not exists platform_connections (
                    platform text primary key,
                    display_name text not null,
                    username text not null default '',
                    password text not null default '',
                    search_enabled integer not null default 1,
                    apply_enabled integer not null default 0,
                    login_url text not null default '',
                    status text not null default 'not_configured',
                    notes text not null default '',
                    updated_at text not null
                );
                """
            )
            self._ensure_column(conn, "jobs", "language", "text not null default 'unknown'")
            self._ensure_column(conn, "jobs", "work_mode", "text not null default 'unknown'")
            self._ensure_column(conn, "jobs", "preference_match", "integer not null default 1")
            self._ensure_column(conn, "jobs", "preference_reason", "text not null default ''")
            self._ensure_column(conn, "jobs", "selected_resume_name", "text not null default ''")
            self._ensure_platform_defaults(conn)

    def upsert_job(self, opening: JobOpening) -> int:
        now = utc_now()
        with self.connect() as conn:
            conn.execute(
                """
                insert into jobs (
                    external_id, source, title, company, location, url, description, salary,
                    tags, language, work_mode, preference_match, preference_reason,
                    discovered_at, updated_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(external_id, source) do update set
                    title = excluded.title,
                    company = excluded.company,
                    location = excluded.location,
                    url = excluded.url,
                    description = excluded.description,
                    salary = excluded.salary,
                    tags = excluded.tags,
                    language = excluded.language,
                    work_mode = excluded.work_mode,
                    preference_match = excluded.preference_match,
                    preference_reason = excluded.preference_reason,
                    updated_at = excluded.updated_at
                """,
                (
                    opening.external_id,
                    opening.source,
                    opening.title,
                    opening.company,
                    opening.location,
                    str(opening.url),
                    opening.description,
                    opening.salary,
                    json.dumps(opening.tags),
                    opening.language,
                    opening.work_mode,
                    1 if opening.preference_match else 0,
                    opening.preference_reason,
                    opening.discovered_at,
                    now,
                ),
            )
            row = conn.execute(
                "select id from jobs where external_id = ? and source = ?",
                (opening.external_id, opening.source),
            ).fetchone()
            return int(row["id"])

    def list_jobs(self) -> list[JobRecord]:
        with self.connect() as conn:
            rows = conn.execute("select * from jobs order by updated_at desc").fetchall()
        return [self._job_from_row(row) for row in rows]

    def get_job(self, job_id: int) -> Optional[JobRecord]:
        with self.connect() as conn:
            row = conn.execute("select * from jobs where id = ?", (job_id,)).fetchone()
        return self._job_from_row(row) if row else None

    def save_analysis(
        self,
        job_id: int,
        match_score: int,
        match_summary: str,
        requirements: list[str],
        tailored_resume: str,
        selected_resume_name: str,
        answers: list[dict[str, Any]],
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                update jobs
                set status = ?, match_score = ?, match_summary = ?, requirements = ?,
                    tailored_resume = ?, selected_resume_name = ?, answers = ?, updated_at = ?
                where id = ?
                """,
                (
                    ApplicationStatus.ANALYZED,
                    match_score,
                    match_summary,
                    json.dumps(requirements),
                    tailored_resume,
                    selected_resume_name,
                    json.dumps(answers),
                    utc_now(),
                    job_id,
                ),
            )

    def update_status(self, job_id: int, status: ApplicationStatus) -> None:
        submitted_at = utc_now() if status == ApplicationStatus.SUBMITTED else None
        with self.connect() as conn:
            conn.execute(
                """
                update jobs
                set status = ?, submitted_at = coalesce(?, submitted_at), updated_at = ?
                where id = ?
                """,
                (status, submitted_at, utc_now(), job_id),
            )

    def add_log(
        self,
        level: str,
        event: str,
        message: str,
        job_id: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                insert into logs (job_id, level, event, message, metadata, created_at)
                values (?, ?, ?, ?, ?, ?)
                """,
                (job_id, level, event, message, json.dumps(metadata or {}), utc_now()),
            )

    def list_logs(self, limit: int = 200) -> list[LogRecord]:
        with self.connect() as conn:
            rows = conn.execute(
                "select * from logs order by created_at desc limit ?", (limit,)
            ).fetchall()
        return [
            LogRecord(
                id=int(row["id"]),
                job_id=row["job_id"],
                level=row["level"],
                event=row["event"],
                message=row["message"],
                metadata=json.loads(row["metadata"]),
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def stats(self) -> DashboardStats:
        with self.connect() as conn:
            total = conn.execute("select count(*) as n from jobs").fetchone()["n"]
            submitted = conn.execute(
                "select count(*) as n from jobs where status = ?", (ApplicationStatus.SUBMITTED,)
            ).fetchone()["n"]
            review = conn.execute(
                "select count(*) as n from jobs where status = ?",
                (ApplicationStatus.REVIEW_REQUIRED,),
            ).fetchone()["n"]
            failed = conn.execute(
                "select count(*) as n from jobs where status = ?", (ApplicationStatus.FAILED,)
            ).fetchone()["n"]
        return DashboardStats(
            total_jobs=total,
            submitted_applications=submitted,
            review_required=review,
            failed=failed,
        )

    def list_platform_connections(self) -> list[PlatformConnection]:
        with self.connect() as conn:
            rows = conn.execute(
                "select * from platform_connections order by display_name"
            ).fetchall()
        return [self._platform_from_row(row) for row in rows]

    def get_platform_connection_secret(self, platform: str) -> Optional[dict[str, str]]:
        with self.connect() as conn:
            row = conn.execute(
                "select username, password from platform_connections where platform = ?",
                (platform,),
            ).fetchone()
        if not row:
            return None
        return {"username": row["username"], "password": row["password"]}

    def save_platform_connection(
        self,
        platform: str,
        username: str,
        password: Optional[str],
        search_enabled: bool,
        apply_enabled: bool,
        notes: str = "",
    ) -> PlatformConnection:
        now = utc_now()
        existing = self.get_platform_connection_secret(platform) or {}
        password_to_store = password if password is not None else existing.get("password", "")
        status = "configured" if username and password_to_store else "needs_credentials"
        with self.connect() as conn:
            conn.execute(
                """
                update platform_connections
                set username = ?, password = ?, search_enabled = ?, apply_enabled = ?,
                    status = ?, notes = ?, updated_at = ?
                where platform = ?
                """,
                (
                    username,
                    password_to_store,
                    1 if search_enabled else 0,
                    1 if apply_enabled else 0,
                    status,
                    notes,
                    now,
                    platform,
                ),
            )
        return next(
            connection
            for connection in self.list_platform_connections()
            if connection.platform == platform
        )

    def _job_from_row(self, row: sqlite3.Row) -> JobRecord:
        data = dict(row)
        data["tags"] = json.loads(data["tags"])
        data["preference_match"] = bool(data["preference_match"])
        data["requirements"] = json.loads(data["requirements"])
        data["answers"] = json.loads(data["answers"])
        return JobRecord(**data)

    def _ensure_column(
        self, conn: sqlite3.Connection, table: str, column: str, definition: str
    ) -> None:
        columns = {row["name"] for row in conn.execute(f"pragma table_info({table})").fetchall()}
        if column not in columns:
            conn.execute(f"alter table {table} add column {column} {definition}")

    def _ensure_platform_defaults(self, conn: sqlite3.Connection) -> None:
        defaults = [
            (
                "infojobs",
                "InfoJobs",
                "https://www.infojobs.net/candidate/login",
                "Spain-focused board. Good fit for Spanish-language applications.",
            ),
            (
                "linkedin",
                "LinkedIn",
                "https://www.linkedin.com/login",
                "Requires browser session, MFA, and careful review for Easy Apply.",
            ),
            (
                "indeed",
                "Indeed",
                "https://secure.indeed.com/auth",
                "Useful for broad search. Some applications redirect to external ATS.",
            ),
        ]
        for platform, display_name, login_url, notes in defaults:
            conn.execute(
                """
                insert into platform_connections (
                    platform, display_name, login_url, notes, updated_at
                )
                values (?, ?, ?, ?, ?)
                on conflict(platform) do nothing
                """,
                (platform, display_name, login_url, notes, utc_now()),
            )

    def _platform_from_row(self, row: sqlite3.Row) -> PlatformConnection:
        return PlatformConnection(
            platform=row["platform"],
            display_name=row["display_name"],
            username=row["username"],
            has_password=bool(row["password"]),
            search_enabled=bool(row["search_enabled"]),
            apply_enabled=bool(row["apply_enabled"]),
            login_url=row["login_url"],
            status=row["status"],
            notes=row["notes"],
            updated_at=row["updated_at"],
        )
