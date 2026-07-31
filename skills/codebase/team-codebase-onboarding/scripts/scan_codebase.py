#!/usr/bin/env python3
"""Read-only codebase scanner for team-codebase-onboarding.

The scanner intentionally stays conservative. It builds a machine-readable
index and candidates from repository evidence, but it does not claim that a
candidate is a confirmed feature or API.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


VERSION = "1.0"

DEFAULT_EXCLUDE_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "target",
    ".next",
    ".nuxt",
    "coverage",
    "out",
    "bin",
    "obj",
    "Pods",
    "DerivedData",
    "__pycache__",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
}

BINARY_EXTENSIONS = {
    ".o",
    ".a",
    ".so",
    ".dylib",
    ".dll",
    ".exe",
    ".class",
    ".jar",
    ".war",
    ".ear",
    ".pyc",
    ".pyo",
    ".gcda",
    ".gcno",
    ".profraw",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".bz2",
    ".xz",
    ".7z",
}

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".kts",
    ".swift",
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hpp",
    ".hh",
    ".cs",
    ".rb",
    ".php",
    ".ex",
    ".exs",
    ".scala",
    ".sh",
    ".sql",
}

LANG_BY_EXT = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".swift": "Swift",
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".cxx": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C/C++ Header",
    ".hh": "C/C++ Header",
    ".cs": "C#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".scala": "Scala",
    ".sh": "Shell",
    ".sql": "SQL",
}

MANIFEST_LANGUAGE_HINTS = {
    "package.json": "JavaScript/TypeScript",
    "pyproject.toml": "Python",
    "requirements.txt": "Python",
    "poetry.lock": "Python",
    "Pipfile": "Python",
    "go.mod": "Go",
    "Cargo.toml": "Rust",
    "pom.xml": "Java",
    "build.gradle": "Java/Kotlin",
    "build.gradle.kts": "Java/Kotlin",
    "Gemfile": "Ruby",
    "composer.json": "PHP",
    "mix.exs": "Elixir",
}

THIRD_PARTY_KEYWORDS = {
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mariadb": "MariaDB",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "kafka": "Kafka",
    "rabbitmq": "RabbitMQ",
    "sqs": "AWS SQS",
    "sns": "AWS SNS",
    "s3": "AWS S3",
    "gcs": "Google Cloud Storage",
    "azure": "Azure",
    "smtp": "SMTP",
    "sendgrid": "SendGrid",
    "stripe": "Stripe",
    "auth0": "Auth0",
    "oauth": "OAuth",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "jaeger": "Jaeger",
    "opentelemetry": "OpenTelemetry",
    "elasticsearch": "Elasticsearch",
}

ENV_PATTERNS = [
    re.compile(r"\bprocess\.env\.([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"\bos\.environ(?:\.get)?\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
    re.compile(r"\bgetenv\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
    re.compile(r"\bstd::getenv\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
    re.compile(r"\bSystem\.getenv\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
]

ROUTE_PATTERNS = [
    re.compile(r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(/[^\s\"'`]+)", re.I),
    re.compile(r"@\w*Mapping\(\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"\brouter\.(get|post|put|patch|delete|use)\(\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"\bapp\.(get|post|put|patch|delete|use)\(\s*['\"]([^'\"]+)['\"]"),
]

TODO_PATTERN = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b[:\-\s]*(.*)", re.I)

INTENT_TOKENS = {
    "prd",
    "trd",
    "spec",
    "design",
    "architecture",
    "roadmap",
    "rfc",
    "adr",
    "requirements",
    "requirement",
    "product",
    "proposal",
}

TEST_TOKENS = {
    "test",
    "tests",
    "spec",
    "__tests__",
    "fixture",
    "fixtures",
    "mock",
    "mocks",
    "fake",
    "fakes",
}

SECURITY_TOKENS = {
    "security",
    "codeql",
    "dependabot",
    "semgrep",
    "snyk",
    "bandit",
    "trivy",
    "grype",
    "osv",
    "sbom",
    "audit",
}

PERFORMANCE_TOKENS = {
    "benchmark",
    "bench",
    "perf",
    "performance",
    "loadtest",
    "load-test",
    "stress",
    "profiling",
    "profile",
    "jmeter",
    "gatling",
    "locust",
    "k6",
}

DOC_EXTENSIONS = {".md", ".mdx", ".txt", ".rst", ".adoc"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only scanner that emits a codebase onboarding JSON summary."
    )
    parser.add_argument("repo_path", help="Repository path to scan")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional glob pattern to exclude. Can be passed multiple times.",
    )
    parser.add_argument(
        "--output",
        help="Optional JSON output path. Without this flag the JSON is printed to stdout.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=200000,
        help="Stop scanning after this many included files. Default: 200000.",
    )
    parser.add_argument(
        "--max-content-bytes",
        type=int,
        default=2_000_000,
        help="Maximum file size to read for lightweight text extraction. Default: 2000000.",
    )
    parser.add_argument(
        "--important-limit",
        type=int,
        default=2000,
        help="Maximum important files retained in JSON. Default: 2000.",
    )
    parser.add_argument(
        "--marker-limit",
        type=int,
        default=500,
        help="Maximum TODO/FIXME/HACK markers retained in JSON. Default: 500.",
    )
    parser.add_argument(
        "--git-log-limit",
        type=int,
        default=20,
        help="Maximum recent commits retained when .git is available. Default: 20.",
    )
    parser.add_argument(
        "--git-churn-days",
        type=int,
        default=90,
        help="Lookback window in days for high-churn files. Default: 90.",
    )
    parser.add_argument(
        "--git-churn-limit",
        type=int,
        default=50,
        help="Maximum high-churn files retained when .git is available. Default: 50.",
    )
    parser.add_argument(
        "--skip-git",
        action="store_true",
        help="Skip git history signals even when .git is available.",
    )
    return parser.parse_args()


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def matches_any(path: str, name: str, patterns: list[str]) -> bool:
    candidates = {path, name, f"{path}/" if not path.endswith("/") else path}
    return any(
        fnmatch.fnmatch(candidate, pattern)
        for pattern in patterns
        for candidate in candidates
    )


def is_text_candidate(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return False
    return True


def read_text(path: Path, max_bytes: int) -> str:
    try:
        if path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def text_line_count(text: str) -> int:
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def split_path_tokens(path: str) -> set[str]:
    return {token for token in re.split(r"[/_.\-\s]+", path.lower()) if token}


def classify_area(path: str) -> str:
    tokens = split_path_tokens(path)
    lower = path.lower()
    suffix = Path(path).suffix.lower()
    if generated_candidate(path):
        return "generated"
    if (
        suffix in DOC_EXTENSIONS
        or "docs" in tokens
        or lower.startswith("doc/")
        or lower.startswith("docs/")
        or lower.startswith("references/")
    ):
        return "docs"
    test_tokens = TEST_TOKENS - {"spec"}
    if (
        tokens & test_tokens
        or lower.startswith("test/")
        or lower.startswith("tests/")
        or Path(path).name.lower().endswith((".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", ".test.js", ".spec.js"))
    ):
        return "test"
    return "source"


def add_unique(bucket: list[dict[str, Any]], seen: set[str], item: dict[str, Any]) -> None:
    key = f"{item.get('path')}::{item.get('symbol', '')}::{item.get('role', '')}"
    if key in seen:
        return
    seen.add(key)
    bucket.append(item)


def role_item(path: str, role: str, evidence: str, confidence: str = "medium", **extra: Any) -> dict[str, Any]:
    item: dict[str, Any] = {
        "path": path,
        "role": role,
        "evidence": evidence,
        "confidence": confidence,
    }
    item.update({k: v for k, v in extra.items() if v not in (None, "", [])})
    return item


def extract_todo_markers(text: str, path: str, limit: int) -> list[dict[str, Any]]:
    markers: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = TODO_PATTERN.search(line)
        if not match:
            continue
        markers.append(
            {
                "path": path,
                "line": line_number,
                "marker": match.group(1).upper(),
                "text": line.strip()[:220],
                "area": classify_area(path),
                "confidence": "medium",
            }
        )
        if len(markers) >= limit:
            break
    return markers


def suffix_is_text_doc(name_lower: str) -> bool:
    return name_lower.endswith(
        (
            ".md",
            ".mdx",
            ".txt",
            ".rst",
            ".adoc",
            ".yaml",
            ".yml",
            ".json",
            ".toml",
        )
    )


def is_intent_document(path: str, filename: str) -> bool:
    lower = path.lower()
    name_lower = filename.lower()
    stem_tokens = split_path_tokens(Path(filename).stem)
    path_tokens = split_path_tokens(path)
    if name_lower.startswith("readme"):
        return True
    if lower.startswith("docs/") or lower.startswith("doc/"):
        return True
    if stem_tokens & INTENT_TOKENS:
        return True
    if any(token in path_tokens for token in ["adr", "adrs", "rfc", "rfcs", "roadmap"]):
        return True
    if "team-spec" in path_tokens and any(token in path_tokens for token in ["prd", "refine", "reviews", "context", "decision", "decisions", "alignment", "brief"]):
        return True
    return False


def run_git(root: Path, args: list[str], timeout: int = 5) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if completed.returncode != 0:
        return []
    return completed.stdout.splitlines()


def collect_git_recent_commits(root: Path, limit: int) -> list[dict[str, str]]:
    lines = run_git(
        root,
        [
            "log",
            f"--max-count={limit}",
            "--date=short",
            "--pretty=format:%h%x09%ad%x09%s",
        ],
    )
    commits: list[dict[str, str]] = []
    for line in lines:
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        commits.append({"hash": parts[0], "date": parts[1], "subject": parts[2]})
    return commits


def collect_git_churn(root: Path, days: int, limit: int) -> list[dict[str, Any]]:
    lines = run_git(
        root,
        [
            "log",
            f"--since={days} days ago",
            "--name-only",
            "--pretty=format:",
        ],
        timeout=10,
    )
    counts: Counter[str] = Counter(line.strip() for line in lines if line.strip())
    return [
        {
            "path": path,
            "change_mentions": count,
            "window_days": days,
            "confidence": "medium",
        }
        for path, count in counts.most_common(limit)
    ]


def classify_path(path: str, filename: str) -> list[tuple[str, str, str]]:
    lower = path.lower()
    name_lower = filename.lower()
    path_parts = set(re.split(r"[/_.-]+", lower))
    is_doc_file = Path(filename).suffix.lower() in DOC_EXTENSIONS
    roles: list[tuple[str, str, str]] = []

    if name_lower.startswith("readme"):
        roles.append(("important_files", "readme", "README-like file"))
    if suffix_is_text_doc(name_lower) and is_intent_document(path, filename):
        roles.append(("declared_intent_sources", "declared-intent-source", "intent/design documentation naming convention"))
    if name_lower in MANIFEST_LANGUAGE_HINTS or name_lower.endswith(".csproj"):
        roles.append(("important_files", "dependency-manifest", "dependency or package manifest"))
    if name_lower in {"makefile", "justfile"} or name_lower.startswith("taskfile") or name_lower in {"turbo.json", "nx.json"}:
        roles.append(("build_scripts", "build-script", "build or task file"))
    if name_lower.startswith("dockerfile") or "docker-compose" in name_lower or name_lower == "compose.yaml":
        roles.append(("docker_files", "container-config", "container or compose file"))
    if path.startswith(".github/workflows/") or name_lower in {".gitlab-ci.yml", "jenkinsfile", "azure-pipelines.yml", ".travis.yml", "circle.yml", "appveyor.yml", "bitbucket-pipelines.yml"}:
        roles.append(("ci_files", "ci-config", "CI/CD configuration"))
    if name_lower.startswith(".env") or name_lower.endswith(".env") or ".env." in name_lower:
        roles.append(("env_files", "env-file", "environment variable file or template"))
    if "/config/" in lower or name_lower.startswith("application") or name_lower.startswith("settings."):
        roles.append(("config_files", "config-file", "configuration file"))
    if (
        name_lower in {"procfile", "chart.yaml", "kustomization.yaml", "kustomization.yml", "serverless.yml", "serverless.yaml", "fly.toml", "render.yaml"}
        or any(token in path_parts for token in ["k8s", "kubernetes", "helm", "terraform", "pulumi", "serverless"])
    ):
        roles.append(("orchestration_files", "orchestration-or-deploy-config", "deployment/orchestration naming convention"))
    test_path_tokens = TEST_TOKENS - {"spec"}
    if (
        path_parts & test_path_tokens
        or name_lower in {"pytest.ini", "tox.ini", "phpunit.xml", "jest.config.js", "jest.config.ts", "vitest.config.js", "vitest.config.ts", "conftest.py"}
        or name_lower.endswith((".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", ".test.js", ".spec.js"))
    ):
        roles.append(("test_files", "test-or-fixture-candidate", "test/fixture/mock naming convention"))
    if (
        name_lower in {".editorconfig", ".pre-commit-config.yaml", ".pre-commit-config.yml", "mypy.ini", "pyrightconfig.json", "ruff.toml", ".ruff.toml", "tsconfig.json", "eslint.config.js", "eslint.config.mjs", "prettier.config.js", "prettier.config.cjs"}
        or name_lower.startswith((".eslintrc", ".prettierrc"))
        or any(token in path_parts for token in ["lint", "formatter", "format", "typecheck", "checkstyle", "spotbugs", "ktlint", "detekt", "golangci"])
    ):
        roles.append(("lint_and_quality_files", "lint-quality-config", "lint/format/typecheck naming convention"))
    if name_lower == "security.md" or path_parts & SECURITY_TOKENS:
        roles.append(("security_configs", "security-config-candidate", "security/audit naming convention"))
    if path_parts & PERFORMANCE_TOKENS or name_lower in {"locustfile.py", "k6.js"}:
        roles.append(("performance_markers", "performance-marker-candidate", "benchmark/performance naming convention"))
    if not is_doc_file and any(part in lower for part in ["/migrations/", "/migration/", "/prisma/", "/models/", "/schema"]):
        roles.append(("data_models", "data-model-source", "data model or schema path"))
    if any(token in name_lower for token in ["openapi", "swagger"]) or lower.endswith(".proto") or lower.endswith(".graphql") or "/proto/" in lower:
        roles.append(("public_apis", "api-contract", "API or protocol contract"))
    if not is_doc_file and ("routes" in path_parts or "router" in path_parts or name_lower in {"routes.py", "router.py", "routes.ts", "router.ts"}):
        roles.append(("routes", "route-candidate", "route/router path candidate"))
    if not is_doc_file and ("controller" in path_parts or "controllers" in path_parts or "handler" in path_parts or "handlers" in path_parts):
        roles.append(("controllers", "controller-candidate", "controller/handler path candidate"))
    if not is_doc_file and any(token in path_parts for token in ["endpoint", "interface", "sctpserver"]):
        roles.append(("public_apis", "protocol-interface-candidate", "protocol endpoint/interface naming convention"))
    if not is_doc_file and "service" in lower:
        roles.append(("services", "service-candidate", "service path candidate"))
    if not is_doc_file and any(token in lower for token in ["repository", "/repo/", "/dao/", "query"]):
        roles.append(("data_access_layers", "data-access-candidate", "data access path candidate"))
    if not is_doc_file and is_entrypoint_name(name_lower, lower):
        roles.append(("entry_points", "entrypoint-candidate", "entrypoint naming convention"))
    return roles


def is_entrypoint_name(name_lower: str, lower_path: str) -> bool:
    if name_lower in {
        "main.py",
        "main.go",
        "main.rs",
        "main.c",
        "main.cc",
        "main.cpp",
        "app.py",
        "server.py",
        "server.js",
        "server.ts",
        "index.js",
        "index.ts",
        "bootstrap.py",
    }:
        return True
    if "/cmd/" in lower_path and name_lower == "main.go":
        return True
    if name_lower.endswith("main.cc") or name_lower.endswith("main.cpp"):
        return True
    return False


def generated_candidate(path: str) -> bool:
    lower = path.lower()
    name = Path(path).name
    if any(token in lower for token in ["generated", "autogen", "/gen/", "/gensrc/", "/asnlab/"]):
        return True
    if name.startswith("AL_") and Path(name).suffix.lower() in {".c", ".h", ".cc", ".cpp"}:
        return True
    if name.endswith("_AllSrc.cc") or name.endswith("_AllSrc.cpp"):
        return True
    return False


def generated_group(path: str) -> str:
    parts = path.split("/")
    if len(parts) >= 3 and parts[0] == "cp" and parts[1] == "asnlab":
        return "/".join(parts[:3])
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return parts[0] if parts else path


def infer_module_role(path: str) -> tuple[str, str, str]:
    lower = path.lower()
    role = "module-or-directory"
    confidence = "low"
    evidence = "directory path"

    explicit_roles = {
        "cp": ("control-plane-root", "high", "top-level cp directory"),
        "up": ("user-plane-root", "high", "top-level up directory"),
        "cp/asnlab": ("protocol-model-generated-code", "high", "asnlab generated protocol directory"),
        "cp/cpcellapp": ("cell-control-application", "high", "cpcellapp directory name"),
        "cp/cpgnbapp": ("gnb-control-application", "high", "cpgnbapp directory name"),
        "cp/bh_interface": ("cp-up-backhaul-interface", "high", "bh_interface directory name"),
        "cp/nsa_interface": ("nsa-x2-interface", "medium", "nsa_interface directory name"),
        "cp/emulators": ("emulator-support", "medium", "emulators directory name"),
        "up/l2appbh": ("user-plane-backhaul-application", "high", "l2appbh directory name"),
        "up/l2bh_interface": ("l2-pdcp-backhaul-interface", "high", "l2bh_interface directory name"),
        "up/libfdt": ("fast-data-transport-library", "medium", "libfdt directory name"),
        "up/ofp": ("packet-fragment-support", "medium", "ofp directory name"),
        "up/pdcp": ("pdcp-protocol-layer", "high", "pdcp directory name"),
        "up/pdcp_ci": ("pdcp-cipher-integrity", "high", "pdcp_ci directory name"),
        "up/pdcp_common": ("pdcp-common-types", "high", "pdcp_common directory name"),
        "up/pdcp_fp": ("pdcp-fast-path", "high", "pdcp_fp directory name"),
        "up/pdcp_fp_debug": ("pdcp-fast-path-debug", "medium", "pdcp_fp_debug directory name"),
        "up/pdcp_oam": ("pdcp-oam-pm", "high", "pdcp_oam directory name"),
        "up/pdcptest": ("pdcp-tests", "high", "pdcptest directory name"),
    }
    if path in explicit_roles:
        return explicit_roles[path]
    if "/ut_" in f"/{lower}" or lower.startswith("cp/ut_"):
        return ("unit-test-suite", "high", "ut_* directory name")
    return role, confidence, evidence


def extract_env_vars(text: str) -> set[str]:
    found: set[str] = set()
    for pattern in ENV_PATTERNS:
        found.update(match.group(1) for match in pattern.finditer(text))
    return found


def extract_env_file_vars(text: str) -> set[str]:
    found: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
            found.add(key)
    return found


def extract_config_keys(text: str, suffix: str) -> set[str]:
    if suffix not in {".yml", ".yaml", ".properties", ".toml", ".ini", ".cfg", ".conf", ".json"}:
        return set()
    found: set[str] = set()
    for line in text.splitlines()[:5000]:
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "//")):
            continue
        match = re.match(r"^['\"]?([A-Za-z0-9_.-]{2,})['\"]?\s*[:=]", stripped)
        if match:
            found.add(match.group(1))
    return found


def extract_routes(text: str) -> list[dict[str, str]]:
    routes: list[dict[str, str]] = []
    for pattern in ROUTE_PATTERNS:
        for match in pattern.finditer(text):
            groups = match.groups()
            if len(groups) == 2:
                method, route = groups
            else:
                method, route = "UNKNOWN", groups[0]
            routes.append({"method": method.upper(), "path": route})
    return routes[:50]


def detect_project_type(summary: dict[str, Any], file_paths: list[str]) -> dict[str, Any]:
    evidence: list[str] = []
    value = "unspecified"
    confidence = "low"
    lower_paths = [path.lower() for path in file_paths]

    has_cp = any(path.startswith("cp/") for path in lower_paths)
    has_up = any(path.startswith("up/") for path in lower_paths)
    has_asnlab = any(path.startswith("cp/asnlab/") for path in lower_paths)
    has_pdcp = any("/pdcp" in path or path.startswith("up/pdcp") for path in lower_paths)
    protocol_prefixes = ("al_e1_", "al_f1_", "al_ng_", "al_x2_", "al_xn_", "al_rrc_", "al_nrrrc_")
    protocol_evidence = [
        path for path in file_paths
        if Path(path).name.lower().startswith(protocol_prefixes)
    ][:12]
    if has_cp and has_up and (has_asnlab or has_pdcp):
        evidence.extend([path for path in file_paths if path in {"cp/asnlab/.ubuild.built"}])
        evidence.extend(protocol_evidence)
        evidence.extend(
            path for path in file_paths
            if path in {
                "up/pdcp_fp/src/pdcpMainProcess.cc",
                "up/pdcp/export/PdcpDrbFlow.h",
                "cp/cpcellapp/src/CpCellAppProcess.cc",
                "cp/cpgnbapp/src/CpGnbAppControl.cc",
            }
        )
        return {
            "value": "telecom-cp-up-c-cpp-system",
            "confidence": "high",
            "evidence": evidence[:20],
        }

    package_count = sum(1 for path in lower_paths if path.endswith("package.json"))
    has_workspace = any(
        path.endswith(("pnpm-workspace.yaml", "turbo.json", "nx.json", "lerna.json"))
        for path in lower_paths
    )
    if has_workspace or package_count > 1:
        return {
            "value": "monorepo",
            "confidence": "medium",
            "evidence": [path for path in file_paths if Path(path).name in {"pnpm-workspace.yaml", "turbo.json", "nx.json", "lerna.json", "package.json"}][:10],
        }

    if summary["routes"] or summary["controllers"] or any("openapi" in path or "swagger" in path for path in lower_paths):
        value = "service"
        confidence = "medium"
        evidence.extend([item["path"] for item in summary["routes"][:5]])
        evidence.extend([item["path"] for item in summary["controllers"][:5]])

    if any(path.endswith(("index.html", "vite.config.ts", "vite.config.js", "next.config.js", "next.config.ts")) for path in lower_paths):
        value = "web"
        confidence = "medium"
        evidence.extend(path for path in file_paths if Path(path).name in {"index.html", "vite.config.ts", "vite.config.js", "next.config.js", "next.config.ts"})

    if any(path.endswith(("setup.py", "pyproject.toml", "Cargo.toml", "go.mod")) for path in file_paths) and value == "unspecified":
        value = "library-or-cli"
        confidence = "low"
        evidence.extend(path for path in file_paths if Path(path).name in {"setup.py", "pyproject.toml", "Cargo.toml", "go.mod"})

    if len(summary["detected_languages"]) >= 3 and value == "unspecified":
        value = "mixed"
        confidence = "low"
        evidence.extend(summary["detected_languages"][:5])

    return {"value": value, "confidence": confidence, "evidence": evidence[:20]}


def scan_repo(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_path).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository path is not a directory: {root}")

    exclude_patterns = list(args.exclude)
    counts: Counter[str] = Counter()
    extension_counts: Counter[str] = Counter()
    language_counts: Counter[str] = Counter()
    category_seen: defaultdict[str, set[str]] = defaultdict(set)
    file_paths: list[str] = []
    excluded: list[dict[str, str]] = []
    generated_candidates: list[dict[str, Any]] = []
    generated_group_counts: Counter[str] = Counter()
    artifact_files: list[dict[str, Any]] = []
    important_files: list[dict[str, Any]] = []
    todo_markers: list[dict[str, Any]] = []
    largest_text_files: list[dict[str, Any]] = []
    third_party_hits: dict[str, set[str]] = defaultdict(set)
    env_vars: dict[str, set[str]] = defaultdict(set)
    config_keys: dict[str, set[str]] = defaultdict(set)
    source_lines_by_language: Counter[str] = Counter()

    summary: dict[str, Any] = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scanner": {"name": "team-codebase-onboarding scan_codebase.py", "version": VERSION},
        "repo_path": str(root),
        "initial_assumptions": {
            "project_languages": "unspecified",
            "project_type": "unspecified",
            "repo_size": "unspecified",
        },
        "detected_languages": [],
        "detected_project_type": {"value": "unspecified", "confidence": "low", "evidence": []},
        "declared_intent_sources": [],
        "intent_reality_gaps": [],
        "repo_size": {"files": 0, "directories": 0, "source_files": 0, "is_large_repo": False},
        "code_metrics": {
            "total_text_lines": 0,
            "source_lines_by_language": {},
            "largest_text_files": [],
        },
        "top_level_directories": [],
        "extension_counts": {},
        "entry_points": [],
        "routes": [],
        "controllers": [],
        "services": [],
        "data_access_layers": [],
        "config_files": [],
        "env_files": [],
        "build_scripts": [],
        "ci_files": [],
        "docker_files": [],
        "orchestration_files": [],
        "test_files": [],
        "lint_and_quality_files": [],
        "security_configs": [],
        "performance_markers": [],
        "modules": [],
        "public_apis": [],
        "data_models": [],
        "db_schema_sources": [],
        "config_keys": [],
        "environment_variables": [],
        "third_party_services": [],
        "important_files": [],
        "todo_markers": [],
        "git_recent_commits": [],
        "high_churn_files": [],
        "generated_code_candidates": [],
        "generated_code_groups": [],
        "artifact_files": [],
        "created_files": [],
        "updated_files": [],
        "excluded_paths": [],
        "unknowns": [],
        "verification_checklist": [],
        "human_review_next_steps": [],
    }

    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        current_rel = "" if current_path == root else relpath(current_path, root)
        counts["directories"] += 1

        kept_dirs = []
        for dirname in dirnames:
            dir_rel = f"{current_rel}/{dirname}" if current_rel else dirname
            if dirname in DEFAULT_EXCLUDE_NAMES or matches_any(dir_rel, dirname, exclude_patterns):
                if len(excluded) < 500:
                    excluded.append({"path": dir_rel, "reason": "default/user exclude directory"})
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs

        for filename in filenames:
            path = current_path / filename
            rel = relpath(path, root)
            if matches_any(rel, filename, exclude_patterns):
                if len(excluded) < 500:
                    excluded.append({"path": rel, "reason": "user exclude pattern"})
                continue

            if counts["files"] >= args.max_files:
                summary["unknowns"].append(
                    {
                        "item": "file-scan-limit",
                        "reason": f"Stopped after {args.max_files} included files.",
                    }
                )
                break

            counts["files"] += 1
            file_paths.append(rel)
            suffix = path.suffix.lower()
            extension_counts[suffix or "<none>"] += 1
            if suffix in SOURCE_EXTENSIONS:
                counts["source_files"] += 1
                if suffix in LANG_BY_EXT:
                    language_counts[LANG_BY_EXT[suffix]] += 1
            if filename in MANIFEST_LANGUAGE_HINTS:
                language_counts[MANIFEST_LANGUAGE_HINTS[filename]] += 3

            if suffix in BINARY_EXTENSIONS:
                if len(artifact_files) < args.important_limit:
                    artifact_files.append(
                        role_item(rel, "binary-or-build-artifact", "binary/archive extension", "medium")
                    )
                continue

            if generated_candidate(rel):
                generated_group_counts[generated_group(rel)] += 1
                generated_candidates.append(
                    role_item(rel, "generated-code-candidate", "path/name suggests generated code", "medium")
                )

            for bucket, role, evidence in classify_path(rel, filename):
                item = role_item(rel, role, evidence, "medium")
                if bucket == "important_files":
                    add_unique(important_files, category_seen[bucket], item)
                else:
                    add_unique(summary[bucket], category_seen[bucket], item)
                    add_unique(important_files, category_seen["important_files"], item)

            if suffix in {".sql"} or "/migrations/" in rel.lower() or "/migration/" in rel.lower() or filename.lower() == "schema.sql":
                add_unique(
                    summary["db_schema_sources"],
                    category_seen["db_schema_sources"],
                    role_item(rel, "db-schema-source", "schema or migration path", "medium"),
                )

            if not is_text_candidate(path):
                continue
            try:
                size_bytes = path.stat().st_size
            except OSError:
                size_bytes = 0
            if size_bytes:
                largest_text_files.append(
                    {
                        "path": rel,
                        "size_bytes": size_bytes,
                        "area": classify_area(rel),
                        "confidence": "medium",
                    }
                )
            text = read_text(path, args.max_content_bytes)
            if not text:
                continue
            line_count = text_line_count(text)
            counts["text_lines"] += line_count
            if suffix in SOURCE_EXTENSIONS and suffix in LANG_BY_EXT:
                source_lines_by_language[LANG_BY_EXT[suffix]] += line_count

            if rel.lower().endswith((".env", ".env.example")) or Path(rel).name.startswith(".env"):
                for key in extract_env_file_vars(text):
                    env_vars[key].add(rel)
            for key in extract_env_vars(text):
                env_vars[key].add(rel)
            for key in extract_config_keys(text, suffix):
                config_keys[key].add(rel)

            for route in extract_routes(text):
                add_unique(
                    summary["routes"],
                    category_seen["routes"],
                    role_item(rel, "route-candidate", "route-like syntax", "low", symbol=f"{route['method']} {route['path']}"),
                )

            if len(todo_markers) < args.marker_limit:
                remaining = args.marker_limit - len(todo_markers)
                todo_markers.extend(extract_todo_markers(text, rel, remaining))

            lower_text = text.lower()
            for keyword, service in THIRD_PARTY_KEYWORDS.items():
                if keyword in lower_text:
                    third_party_hits[service].add(rel)

    top_level_dirs = []
    try:
        for child in sorted(root.iterdir()):
            if child.is_dir() and child.name not in DEFAULT_EXCLUDE_NAMES:
                top_level_dirs.append(child.name)
    except OSError:
        pass

    modules = []
    for dirname in top_level_dirs:
        role, confidence, evidence = infer_module_role(dirname)
        modules.append(
            {
                "name": dirname,
                "path": dirname,
                "role": role,
                "evidence": evidence,
                "confidence": confidence,
            }
        )
        parent = root / dirname
        try:
            for child in sorted(parent.iterdir()):
                if not child.is_dir() or child.name in DEFAULT_EXCLUDE_NAMES:
                    continue
                module_path = f"{dirname}/{child.name}"
                role, confidence, evidence = infer_module_role(module_path)
                modules.append(
                    {
                        "name": child.name,
                        "path": module_path,
                        "role": role,
                        "evidence": evidence,
                        "confidence": confidence,
                    }
                )
        except OSError:
            pass

    env_items = [
        {"name": key, "sources": sorted(paths)[:20], "confidence": "medium"}
        for key, paths in sorted(env_vars.items())
    ]
    config_items = [
        {"key": key, "sources": sorted(paths)[:20], "confidence": "low"}
        for key, paths in sorted(config_keys.items())
    ]
    third_party_items = [
        {"service": service, "sources": sorted(paths)[:20], "confidence": "low"}
        for service, paths in sorted(third_party_hits.items())
    ]

    summary["top_level_directories"] = top_level_dirs
    summary["repo_size"] = {
        "files": counts["files"],
        "directories": counts["directories"],
        "source_files": counts["source_files"],
        "is_large_repo": counts["source_files"] > 1000 or counts["files"] > 5000,
    }
    summary["code_metrics"] = {
        "total_text_lines": counts["text_lines"],
        "source_lines_by_language": dict(source_lines_by_language.most_common()),
        "largest_text_files": sorted(
            largest_text_files,
            key=lambda item: item.get("size_bytes", 0),
            reverse=True,
        )[:25],
    }
    summary["extension_counts"] = dict(extension_counts.most_common(100))
    summary["detected_languages"] = [
        {"language": language, "score": score}
        for language, score in language_counts.most_common()
    ]
    summary["modules"] = modules
    summary["important_files"] = important_files[: args.important_limit]
    summary["generated_code_candidates"] = generated_candidates[: args.important_limit]
    summary["generated_code_groups"] = [
        {
            "path": path,
            "file_count": count,
            "role": "generated-code-group",
            "evidence": "grouped generated-code candidates by directory",
            "confidence": "medium",
        }
        for path, count in generated_group_counts.most_common()
    ]
    summary["artifact_files"] = artifact_files
    summary["environment_variables"] = env_items
    summary["config_keys"] = config_items
    summary["third_party_services"] = third_party_items
    summary["todo_markers"] = todo_markers
    if not args.skip_git:
        if (root / ".git").exists():
            summary["git_recent_commits"] = collect_git_recent_commits(root, args.git_log_limit)
            summary["high_churn_files"] = collect_git_churn(root, args.git_churn_days, args.git_churn_limit)
            if not summary["git_recent_commits"] and not summary["high_churn_files"]:
                summary["unknowns"].append(
                    {
                        "item": "git-history-signals",
                        "reason": "Git metadata exists but recent commits/churn could not be read.",
                    }
                )
        else:
            summary["unknowns"].append(
                {
                    "item": "git-history-signals",
                    "reason": "No .git directory detected; recent commits and churn were not collected.",
                }
            )
    summary["excluded_paths"] = excluded
    summary["detected_project_type"] = detect_project_type(summary, file_paths)
    summary["unknowns"].extend(
        [
            {
                "item": "confirmed-project-type",
                "reason": "Requires human review of evidence and docs before treating detected type as authoritative.",
            },
            {
                "item": "complete-feature-inventory",
                "reason": "Scanner only produces candidates; feature confirmation requires code reading.",
            },
        ]
    )
    summary["verification_checklist"] = [
        "Repository recursively scanned with configured excludes.",
        "Important files and candidate structures classified.",
        "Generated-code and excluded-path candidates recorded.",
        "Declared-intent, test, quality, security, performance, TODO, and git history signals collected when available.",
        "JSON emitted successfully.",
    ]
    summary["human_review_next_steps"] = [
        "Review README, manifests, build files, CI files, and Docker/config evidence.",
        "Compare declared intent from docs/README against source-code reality before writing conclusions.",
        "Confirm detected project type and language list.",
        "Review TODO/FIXME/HACK, recent commits, and high-churn files as risk signals rather than automatic defects.",
        "Promote high-confidence candidates into formal documentation only after reading source evidence.",
    ]

    return summary


def main() -> int:
    args = parse_args()
    summary = scan_repo(args)
    data = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=False)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(data + "\n", encoding="utf-8")
    else:
        print(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
