from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from pathlib import Path
from typing import Any

from research_mcp.models import (
    ContextBundleResponse,
    ContextBundleSummary,
    DownloadRecord,
    LibraryDetailResponse,
    LibraryItemEntry,
    LibrariesResponse,
    LibraryMutationResponse,
    LibrarySummary,
)
from research_mcp.paths import LIBRARY_DIR
from research_mcp.utils import canonical_doi, normalize_title, now_utc_iso, slugify


class CatalogStore:
    def __init__(self, db_path: Path) -> None:
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS libraries (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    slug TEXT NOT NULL,
                    source_kind TEXT NOT NULL,
                    source_ref TEXT NOT NULL,
                    root_path TEXT NOT NULL,
                    manifest_path TEXT NOT NULL,
                    csv_path TEXT NOT NULL,
                    markdown_path TEXT NOT NULL,
                    bibtex_path TEXT NOT NULL,
                    checklist_csv_path TEXT NOT NULL,
                    checklist_markdown_path TEXT NOT NULL,
                    notes TEXT,
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    archived INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS library_items (
                    id TEXT PRIMARY KEY,
                    library_id TEXT NOT NULL,
                    rank INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    title_alias TEXT,
                    authors_json TEXT NOT NULL DEFAULT '[]',
                    source TEXT NOT NULL,
                    year INTEGER,
                    doi TEXT,
                    landing_url TEXT,
                    pdf_url TEXT,
                    open_access_url TEXT,
                    local_pdf_path TEXT,
                    download_status TEXT,
                    category TEXT,
                    notes TEXT,
                    favorite INTEGER NOT NULL DEFAULT 0,
                    archived INTEGER NOT NULL DEFAULT 0,
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    metadata_path TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS context_bundles (
                    id TEXT PRIMARY KEY,
                    library_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    max_items INTEGER NOT NULL,
                    item_ids_json TEXT NOT NULL,
                    text TEXT NOT NULL,
                    preview TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def upsert_library(
        self,
        *,
        name: str,
        source_kind: str,
        source_ref: str,
        root_path: str,
        manifest_path: str,
        csv_path: str,
        markdown_path: str,
        bibtex_path: str,
        checklist_csv_path: str,
        checklist_markdown_path: str,
        items: list[dict[str, Any]],
        records: list[DownloadRecord],
    ) -> LibrarySummary:
        now = now_utc_iso()
        root = str(Path(root_path).expanduser().resolve())
        library_id = self._existing_library_id_for_root(root) or self._manifest_library_id(Path(manifest_path)) or uuid.uuid4().hex[:12]
        previous_items = self._load_existing_items_map(library_id)
        created_at = self._existing_library_created_at(library_id) or now

        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO libraries(
                    id, name, slug, source_kind, source_ref, root_path, manifest_path, csv_path,
                    markdown_path, bibtex_path, checklist_csv_path, checklist_markdown_path,
                    notes, tags_json, archived, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    slug = excluded.slug,
                    source_kind = excluded.source_kind,
                    source_ref = excluded.source_ref,
                    root_path = excluded.root_path,
                    manifest_path = excluded.manifest_path,
                    csv_path = excluded.csv_path,
                    markdown_path = excluded.markdown_path,
                    bibtex_path = excluded.bibtex_path,
                    checklist_csv_path = excluded.checklist_csv_path,
                    checklist_markdown_path = excluded.checklist_markdown_path,
                    updated_at = excluded.updated_at
                """,
                (
                    library_id,
                    name,
                    slugify(name, max_length=64),
                    source_kind,
                    source_ref,
                    root,
                    manifest_path,
                    csv_path,
                    markdown_path,
                    bibtex_path,
                    checklist_csv_path,
                    checklist_markdown_path,
                    "",
                    "[]",
                    created_at,
                    now,
                ),
            )
            self._conn.execute("DELETE FROM library_items WHERE library_id = ?", (library_id,))
            for item in items:
                previous = previous_items.get(self._item_identity(item))
                item_id = previous["id"] if previous else uuid.uuid4().hex[:16]
                title_alias = previous["title_alias"] if previous else None
                notes = previous["notes"] if previous else None
                favorite = previous["favorite"] if previous else 0
                archived = previous["archived"] if previous else 0
                tags_json = previous["tags_json"] if previous else "[]"
                created_item_at = previous["created_at"] if previous else now
                self._conn.execute(
                    """
                    INSERT INTO library_items(
                        id, library_id, rank, title, title_alias, authors_json, source, year, doi,
                        landing_url, pdf_url, open_access_url, local_pdf_path, download_status,
                        category, notes, favorite, archived, tags_json, metadata_path, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item_id,
                        library_id,
                        item["rank"],
                        item["title"],
                        title_alias,
                        json.dumps(item.get("authors", []), ensure_ascii=False),
                        item.get("source") or "",
                        item.get("year"),
                        canonical_doi(item.get("doi")),
                        item.get("landing_url"),
                        item.get("pdf_url"),
                        item.get("open_access_url"),
                        item.get("local_pdf_path"),
                        item.get("download_status"),
                        item.get("category"),
                        notes,
                        favorite,
                        archived,
                        tags_json,
                        item.get("metadata_path"),
                        created_item_at,
                        now,
                    ),
                )

        self._update_manifest(
            Path(manifest_path),
            {
                "library_id": library_id,
                "name": name,
                "source_kind": source_kind,
                "source_ref": source_ref,
                "root_path": root,
            },
        )
        return self._library_summary(library_id)

    def list_libraries(self, *, include_archived: bool = False) -> LibrariesResponse:
        query = "SELECT * FROM libraries"
        params: tuple[Any, ...] = ()
        if not include_archived:
            query += " WHERE archived = 0"
        query += " ORDER BY updated_at DESC"
        rows = self._conn.execute(query, params).fetchall()
        return LibrariesResponse(
            status="ok",
            generated_at=now_utc_iso(),
            libraries=[self._library_summary_from_row(row) for row in rows],
        )

    def read_library(self, library_id: str, *, include_archived_items: bool = False) -> LibraryDetailResponse:
        row = self._conn.execute("SELECT * FROM libraries WHERE id = ?", (library_id,)).fetchone()
        if not row:
            return LibraryDetailResponse(status="error", generated_at=now_utc_iso(), warnings=[f"Unknown library: {library_id}"])

        query = "SELECT * FROM library_items WHERE library_id = ?"
        params: tuple[Any, ...] = (library_id,)
        if not include_archived_items:
            query += " AND archived = 0"
        query += " ORDER BY rank ASC, title ASC"
        items = [self._item_entry_from_row(item) for item in self._conn.execute(query, params).fetchall()]
        bundles = self.list_context_bundles(library_id=library_id)
        return LibraryDetailResponse(
            status="ok",
            generated_at=now_utc_iso(),
            library=self._library_summary_from_row(row),
            items=items,
            bundles=bundles,
        )

    def rename_library(self, library_id: str, new_name: str) -> LibraryMutationResponse:
        now = now_utc_iso()
        with self._lock, self._conn:
            cursor = self._conn.execute(
                "UPDATE libraries SET name = ?, slug = ?, updated_at = ? WHERE id = ?",
                (new_name, slugify(new_name, max_length=64), now, library_id),
            )
        if cursor.rowcount == 0:
            return LibraryMutationResponse(status="error", generated_at=now, message=f"Unknown library: {library_id}")
        summary = self._library_summary(library_id)
        self._update_manifest(Path(summary.root_path) / "manifest.json", {"name": new_name})
        return LibraryMutationResponse(status="ok", generated_at=now, message="Library renamed.", library=summary)

    def archive_library(self, library_id: str) -> LibraryMutationResponse:
        return self._set_library_archived(library_id, archived=True)

    def restore_library(self, library_id: str) -> LibraryMutationResponse:
        return self._set_library_archived(library_id, archived=False)

    def tag_library(self, library_id: str, tags: list[str]) -> LibraryMutationResponse:
        row = self._conn.execute("SELECT tags_json FROM libraries WHERE id = ?", (library_id,)).fetchone()
        if not row:
            return LibraryMutationResponse(status="error", generated_at=now_utc_iso(), message=f"Unknown library: {library_id}")
        merged = sorted(set(self._decode_json_list(row["tags_json"])) | {tag.strip() for tag in tags if tag.strip()})
        now = now_utc_iso()
        with self._lock, self._conn:
            self._conn.execute(
                "UPDATE libraries SET tags_json = ?, updated_at = ? WHERE id = ?",
                (json.dumps(merged, ensure_ascii=False), now, library_id),
            )
        return LibraryMutationResponse(status="ok", generated_at=now, message="Library tags updated.", library=self._library_summary(library_id))

    def list_library_items(self, library_id: str, *, include_archived: bool = False) -> list[LibraryItemEntry]:
        query = "SELECT * FROM library_items WHERE library_id = ?"
        params: tuple[Any, ...] = (library_id,)
        if not include_archived:
            query += " AND archived = 0"
        query += " ORDER BY rank ASC, title ASC"
        return [self._item_entry_from_row(row) for row in self._conn.execute(query, params).fetchall()]

    def update_library_item(
        self,
        item_id: str,
        *,
        title_alias: str | None = None,
        notes: str | None = None,
        favorite: bool | None = None,
        tags: list[str] | None = None,
    ) -> LibraryMutationResponse:
        row = self._conn.execute("SELECT * FROM library_items WHERE id = ?", (item_id,)).fetchone()
        if not row:
            return LibraryMutationResponse(status="error", generated_at=now_utc_iso(), message=f"Unknown item: {item_id}")
        updated_tags = self._decode_json_list(row["tags_json"])
        if tags is not None:
            updated_tags = sorted(set(tag.strip() for tag in tags if tag.strip()))
        payload = {
            "title_alias": title_alias if title_alias is not None else row["title_alias"],
            "notes": notes if notes is not None else row["notes"],
            "favorite": int(favorite) if favorite is not None else int(row["favorite"]),
            "tags_json": json.dumps(updated_tags, ensure_ascii=False),
            "updated_at": now_utc_iso(),
            "item_id": item_id,
        }
        with self._lock, self._conn:
            self._conn.execute(
                """
                UPDATE library_items
                SET title_alias = :title_alias,
                    notes = :notes,
                    favorite = :favorite,
                    tags_json = :tags_json,
                    updated_at = :updated_at
                WHERE id = :item_id
                """,
                payload,
            )
        return LibraryMutationResponse(
            status="ok",
            generated_at=payload["updated_at"],
            message="Library item updated.",
            item=self._item_entry(item_id),
        )

    def archive_library_item(self, item_id: str) -> LibraryMutationResponse:
        return self._set_item_archived(item_id, archived=True)

    def restore_library_item(self, item_id: str) -> LibraryMutationResponse:
        return self._set_item_archived(item_id, archived=False)

    def list_context_bundles(self, *, library_id: str | None = None) -> list[ContextBundleSummary]:
        query = "SELECT * FROM context_bundles"
        params: tuple[Any, ...] = ()
        if library_id:
            query += " WHERE library_id = ?"
            params = (library_id,)
        query += " ORDER BY updated_at DESC"
        return [self._bundle_summary_from_row(row) for row in self._conn.execute(query, params).fetchall()]

    def generate_context_bundle(
        self,
        library_id: str,
        *,
        name: str | None = None,
        mode: str = "compact",
        max_items: int = 12,
        favorites_only: bool = False,
    ) -> ContextBundleResponse:
        detail = self.read_library(library_id)
        if detail.status != "ok" or not detail.library:
            return ContextBundleResponse(status="error", generated_at=now_utc_iso(), warnings=[f"Unknown library: {library_id}"])
        items = detail.items
        if favorites_only:
            items = [item for item in items if item.favorite]
        items = items[:max_items]
        text = self._build_bundle_text(detail.library, items, max_items=max_items)
        preview = "\n".join(text.splitlines()[:6])
        bundle_id = uuid.uuid4().hex[:12]
        bundle_name = name or f"{detail.library.name} ({mode})"
        now = now_utc_iso()
        bundles_dir = Path(detail.library.root_path) / "bundles"
        bundles_dir.mkdir(parents=True, exist_ok=True)
        bundle_path = bundles_dir / f"{bundle_id}.md"
        bundle_path.write_text(text, encoding="utf-8")
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO context_bundles(id, library_id, name, mode, max_items, item_ids_json, text, preview, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    bundle_id,
                    library_id,
                    bundle_name,
                    mode,
                    max_items,
                    json.dumps([item.id for item in items]),
                    text,
                    preview,
                    now,
                    now,
                ),
            )
        return ContextBundleResponse(
            status="ok",
            generated_at=now,
            bundle=self._bundle_summary(bundle_id),
            text=text,
            item_ids=[item.id for item in items],
        )

    def read_context_bundle(self, bundle_id: str) -> ContextBundleResponse:
        row = self._conn.execute("SELECT * FROM context_bundles WHERE id = ?", (bundle_id,)).fetchone()
        if not row:
            return ContextBundleResponse(status="error", generated_at=now_utc_iso(), warnings=[f"Unknown context bundle: {bundle_id}"])
        return ContextBundleResponse(
            status="ok",
            generated_at=now_utc_iso(),
            bundle=self._bundle_summary_from_row(row),
            text=row["text"],
            item_ids=self._decode_json_list(row["item_ids_json"]),
        )

    def manifest_for_library(self, library_id: str) -> dict[str, Any]:
        row = self._conn.execute("SELECT * FROM libraries WHERE id = ?", (library_id,)).fetchone()
        if not row:
            raise KeyError(library_id)
        summary = self._library_summary_from_row(row)
        return summary.model_dump(mode="json")

    def compact_summary_for_library(self, library_id: str, *, max_items: int = 12) -> str:
        detail = self.read_library(library_id)
        if detail.status != "ok" or not detail.library:
            raise KeyError(library_id)
        return self._build_bundle_text(detail.library, detail.items[:max_items], max_items=max_items)

    def library_items_markdown(self, library_id: str, *, max_items: int = 50) -> str:
        detail = self.read_library(library_id)
        if detail.status != "ok" or not detail.library:
            raise KeyError(library_id)
        lines = [f"# {detail.library.name}", "", "| Rank | Title | Year | Source | DOI |", "| --- | --- | --- | --- | --- |"]
        for item in detail.items[:max_items]:
            lines.append(
                f"| {item.rank} | {item.effective_title} | {item.year or ''} | {item.source} | {item.doi or ''} |"
            )
        return "\n".join(lines)

    def _set_library_archived(self, library_id: str, *, archived: bool) -> LibraryMutationResponse:
        now = now_utc_iso()
        with self._lock, self._conn:
            cursor = self._conn.execute(
                "UPDATE libraries SET archived = ?, updated_at = ? WHERE id = ?",
                (1 if archived else 0, now, library_id),
            )
        if cursor.rowcount == 0:
            return LibraryMutationResponse(status="error", generated_at=now, message=f"Unknown library: {library_id}")
        return LibraryMutationResponse(
            status="ok",
            generated_at=now,
            message="Library archived." if archived else "Library restored.",
            library=self._library_summary(library_id),
        )

    def _set_item_archived(self, item_id: str, *, archived: bool) -> LibraryMutationResponse:
        now = now_utc_iso()
        with self._lock, self._conn:
            cursor = self._conn.execute(
                "UPDATE library_items SET archived = ?, updated_at = ? WHERE id = ?",
                (1 if archived else 0, now, item_id),
            )
        if cursor.rowcount == 0:
            return LibraryMutationResponse(status="error", generated_at=now, message=f"Unknown item: {item_id}")
        return LibraryMutationResponse(
            status="ok",
            generated_at=now,
            message="Library item archived." if archived else "Library item restored.",
            item=self._item_entry(item_id),
        )

    def _existing_library_id_for_root(self, root_path: str) -> str | None:
        row = self._conn.execute("SELECT id FROM libraries WHERE root_path = ?", (root_path,)).fetchone()
        return str(row["id"]) if row else None

    def _manifest_library_id(self, manifest_path: Path) -> str | None:
        if not manifest_path.exists():
            return None
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return None
        catalog = payload.get("catalog") or {}
        library_id = catalog.get("library_id")
        return str(library_id) if library_id else None

    def _existing_library_created_at(self, library_id: str) -> str | None:
        row = self._conn.execute("SELECT created_at FROM libraries WHERE id = ?", (library_id,)).fetchone()
        return str(row["created_at"]) if row else None

    def _load_existing_items_map(self, library_id: str) -> dict[str, sqlite3.Row]:
        rows = self._conn.execute("SELECT * FROM library_items WHERE library_id = ?", (library_id,)).fetchall()
        return {self._row_identity(row): row for row in rows}

    def _row_identity(self, row: sqlite3.Row) -> str:
        doi = canonical_doi(row["doi"])
        if doi:
            return f"doi:{doi}"
        title = normalize_title(row["title"])
        if title:
            return f"title:{title}"
        return f"rank:{row['rank']}"

    def _item_identity(self, item: dict[str, Any]) -> str:
        doi = canonical_doi(item.get("doi"))
        if doi:
            return f"doi:{doi}"
        title = normalize_title(item.get("title"))
        if title:
            return f"title:{title}"
        return f"rank:{item.get('rank')}"

    def _update_manifest(self, manifest_path: Path, patch: dict[str, Any]) -> None:
        payload: dict[str, Any] = {}
        if manifest_path.exists():
            try:
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                payload = {}
        payload["catalog"] = {**(payload.get("catalog") or {}), **patch}
        manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def _library_summary(self, library_id: str) -> LibrarySummary:
        row = self._conn.execute("SELECT * FROM libraries WHERE id = ?", (library_id,)).fetchone()
        if not row:
            raise KeyError(library_id)
        return self._library_summary_from_row(row)

    def _library_summary_from_row(self, row: sqlite3.Row) -> LibrarySummary:
        item_count = self._count_items(row["id"], include_archived=True)
        active_item_count = self._count_items(row["id"], include_archived=False)
        favorite_count = self._count_favorites(row["id"])
        return LibrarySummary(
            id=str(row["id"]),
            name=str(row["name"]),
            slug=str(row["slug"]),
            source_kind=str(row["source_kind"]),
            source_ref=str(row["source_ref"]),
            root_path=str(row["root_path"]),
            archived=bool(row["archived"]),
            tags=self._decode_json_list(row["tags_json"]),
            item_count=item_count,
            active_item_count=active_item_count,
            favorite_count=favorite_count,
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )

    def _count_items(self, library_id: str, *, include_archived: bool) -> int:
        query = "SELECT COUNT(*) AS c FROM library_items WHERE library_id = ?"
        params: tuple[Any, ...] = (library_id,)
        if not include_archived:
            query += " AND archived = 0"
        row = self._conn.execute(query, params).fetchone()
        return int(row["c"]) if row else 0

    def _count_favorites(self, library_id: str) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) AS c FROM library_items WHERE library_id = ? AND favorite = 1 AND archived = 0",
            (library_id,),
        ).fetchone()
        return int(row["c"]) if row else 0

    def _item_entry(self, item_id: str) -> LibraryItemEntry:
        row = self._conn.execute("SELECT * FROM library_items WHERE id = ?", (item_id,)).fetchone()
        if not row:
            raise KeyError(item_id)
        return self._item_entry_from_row(row)

    def _item_entry_from_row(self, row: sqlite3.Row) -> LibraryItemEntry:
        title = str(row["title"])
        title_alias = row["title_alias"]
        return LibraryItemEntry(
            id=str(row["id"]),
            library_id=str(row["library_id"]),
            rank=int(row["rank"]),
            title=title,
            title_alias=str(title_alias) if title_alias else None,
            effective_title=str(title_alias) if title_alias else title,
            authors=self._decode_json_list(row["authors_json"]),
            source=str(row["source"]),
            year=int(row["year"]) if row["year"] is not None else None,
            doi=str(row["doi"]) if row["doi"] else None,
            landing_url=str(row["landing_url"]) if row["landing_url"] else None,
            pdf_url=str(row["pdf_url"]) if row["pdf_url"] else None,
            open_access_url=str(row["open_access_url"]) if row["open_access_url"] else None,
            local_pdf_path=str(row["local_pdf_path"]) if row["local_pdf_path"] else None,
            download_status=str(row["download_status"]) if row["download_status"] else None,
            category=str(row["category"]) if row["category"] else None,
            notes=str(row["notes"]) if row["notes"] else None,
            favorite=bool(row["favorite"]),
            archived=bool(row["archived"]),
            tags=self._decode_json_list(row["tags_json"]),
            metadata_path=str(row["metadata_path"]) if row["metadata_path"] else None,
        )

    def _bundle_summary(self, bundle_id: str) -> ContextBundleSummary:
        row = self._conn.execute("SELECT * FROM context_bundles WHERE id = ?", (bundle_id,)).fetchone()
        if not row:
            raise KeyError(bundle_id)
        return self._bundle_summary_from_row(row)

    def _bundle_summary_from_row(self, row: sqlite3.Row) -> ContextBundleSummary:
        item_ids = self._decode_json_list(row["item_ids_json"])
        return ContextBundleSummary(
            id=str(row["id"]),
            library_id=str(row["library_id"]),
            name=str(row["name"]),
            mode="compact",
            max_items=int(row["max_items"]),
            item_count=len(item_ids),
            preview=str(row["preview"]),
            resource_uri=f"research://bundle/{row['id']}",
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )

    def _build_bundle_text(self, library: LibrarySummary, items: list[LibraryItemEntry], *, max_items: int) -> str:
        lines = [
            f"# Library Context: {library.name}",
            "",
            f"Source kind: {library.source_kind}",
            f"Source ref: {library.source_ref}",
            f"Library id: {library.id}",
            f"Tags: {', '.join(library.tags) if library.tags else 'none'}",
            "",
            f"Top {min(len(items), max_items)} items to use as working context:",
            "",
        ]
        for item in items[:max_items]:
            lines.append(f"- [{item.rank}] {item.effective_title} ({item.year or 'n.d.'}, {item.source})")
            if item.category:
                lines.append(f"  category: {item.category}")
            if item.notes:
                lines.append(f"  notes: {item.notes}")
            if item.doi:
                lines.append(f"  doi: {item.doi}")
            if item.landing_url:
                lines.append(f"  url: {item.landing_url}")
            if item.metadata_path:
                lines.append(f"  metadata_path: {item.metadata_path}")
        lines.extend(
            [
                "",
                "Use this bundle as compressed background context. Ask for specific items or the full library resource if you need more detail.",
            ]
        )
        return "\n".join(lines)

    def _decode_json_list(self, value: str | None) -> list[Any]:
        if not value:
            return []
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []
        return parsed if isinstance(parsed, list) else []
