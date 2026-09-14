"""Stream classified HTML pages from a single open Javadoc archive."""

from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import PurePosixPath
from zipfile import ZipFile

from windchill_api_lookup.models import ApiClass, ApiMethod
from windchill_api_lookup.parser.ptc_javadoc import boolean_values, parse_class_page


@dataclass
class PageResult:
    source_path: str
    status: str
    reason: str = ""
    api_class: ApiClass | None = None
    methods: list[ApiMethod] = field(default_factory=list)
    diagnostics: list[dict] = field(default_factory=list)


@dataclass
class ScanReport:
    html_pages: int = 0
    candidates: int = 0
    parsed_classes: int = 0
    methods: int = 0
    skipped: int = 0
    failed: int = 0
    unknown_class_supported: int = 0
    unknown_class_extendable: int = 0
    unknown_method_supported: int = 0
    skipped_reasons: dict[str, int] = field(default_factory=dict)
    pages: list[dict] = field(default_factory=list)

    def record(self, page: PageResult) -> None:
        self.html_pages += 1
        self.pages.append({
            "source_path": page.source_path, "status": page.status,
            "reason": page.reason, "diagnostics": page.diagnostics,
        })
        if page.status == "skipped":
            self.skipped += 1
            self.skipped_reasons[page.reason] = self.skipped_reasons.get(page.reason, 0) + 1
            return
        self.candidates += 1
        if page.status == "error":
            self.failed += 1
            return
        self.parsed_classes += 1
        self.methods += len(page.methods)
        self.unknown_class_supported += page.api_class.supported is None
        self.unknown_class_extendable += page.api_class.extendable is None
        self.unknown_method_supported += sum(method.supported is None for method in page.methods)

    def summary(self) -> dict:
        return {key: value for key, value in asdict(self).items() if key != "pages"}


def _skip_reason(path: str) -> str | None:
    parts = PurePosixPath(path).parts
    if not parts or parts[0] != "Javadoc":
        return "outside_javadoc_root"
    if "class-use" in parts:
        return "class_use"
    if "doc-files" in parts:
        return "documentation_attachment"
    if "index-files" in parts:
        return "navigation_index"
    if parts[-1] in {"package-summary.html", "package-tree.html", "package-use.html"}:
        return "package_page"
    if len(parts) == 2 and parts[-1] in {
        "index.html", "allclasses-index.html", "allpackages-index.html",
        "overview-summary.html", "overview-tree.html", "deprecated-list.html",
        "constant-values.html", "serialized-form.html", "help-doc.html",
        "index-all.html", "search.html", "allclasses.html", "system-properties.html",
    }:
        return "navigation_page"
    return None


def _metadata_diagnostics(metadata: ApiClass, methods: list[ApiMethod]) -> list[dict]:
    diagnostics = []
    fields = [(metadata.qualified_name, metadata.description, "Supported API"),
              (metadata.qualified_name, metadata.description, "Extendable")]
    fields.extend((method.javadoc_id, method.description, "Supported API") for method in methods)
    for subject, text, label in fields:
        values = boolean_values(text, label)
        if len(values) != 1:
            diagnostics.append({
                "code": "METADATA_CONFLICT" if values else "METADATA_MISSING_OR_INVALID",
                "subject": subject, "field": label,
            })
    return diagnostics


def scan_javadoc(zip_path: str):
    """Every HTML entry gets a result; unknown candidate layouts are errors."""
    with ZipFile(zip_path) as archive:
        entries = [entry for entry in archive.infolist() if entry.filename.endswith(".html") and not entry.is_dir()]
        counts = Counter(entry.filename for entry in entries)
        for entry in entries:
            path = entry.filename
            if counts[path] > 1:
                yield PageResult(path, "error", "duplicate_archive_path")
                continue
            reason = _skip_reason(path)
            if reason:
                yield PageResult(path, "skipped", reason)
                continue
            try:
                # Do not silently replace invalid bytes in indexed source pages.
                html = archive.read(entry).decode("utf-8")
                qualified_name = path[len("Javadoc/"):-5].replace("/", ".")
                metadata, methods = parse_class_page(html, qualified_name, path)
            except (ValueError, OSError, KeyError) as exc:
                yield PageResult(path, "error", str(exc))
                continue
            yield PageResult(path, "parsed", api_class=metadata, methods=methods,
                             diagnostics=_metadata_diagnostics(metadata, methods))
