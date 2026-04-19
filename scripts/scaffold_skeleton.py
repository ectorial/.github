# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Ectorial org scaffolding for v0.1.

Reads a ``scaffold_skeleton.{toml,json,txt}`` plan and executes each command
in sequence. Commands are composed of steps that provision GitHub repos,
seed baseline files, and set topics so the org is ready for v0.1 work.

The script shells out to the ``gh`` CLI — it does not talk to the GitHub
API directly. You must be authenticated (``gh auth status``) before running.

Usage
-----

    uv run scripts/scaffold_skeleton.py                 # use ./scaffold_skeleton.toml
    uv run scripts/scaffold_skeleton.py --plan plan.json
    uv run scripts/scaffold_skeleton.py --dry-run       # print actions, do nothing
    uv run scripts/scaffold_skeleton.py --only wsr,wit  # subset by command name

Plan format
-----------

TOML (canonical)::

    [defaults]
    owner = "ectorial"
    default_branch = "main"

    [[commands]]
    name = "wsr"
    summary = "Create ectorial/wsr (core execution engine)"

    [[commands.steps]]
    op = "ensure_repo"
    repo = "wsr"
    description = "WSR — the Wasm component CI runtime"
    private = false
    topics = ["wasm", "ci", "cd"]

    [[commands.steps]]
    op = "ensure_file"
    repo = "wsr"
    path = "README.md"
    content = "# wsr\\n"

JSON is the same shape. TXT is JSON Lines: one command object per line.
"""

from __future__ import annotations

import argparse
import base64
import json
import logging
import shlex
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

log = logging.getLogger("scaffold")


# ---------------------------------------------------------------------------
# Plan loading
# ---------------------------------------------------------------------------


@dataclass
class Step:
    op: str
    args: dict[str, Any]


@dataclass
class Command:
    name: str
    summary: str
    steps: list[Step] = field(default_factory=list)


@dataclass
class Plan:
    defaults: dict[str, Any]
    commands: list[Command]


def _coerce_command(raw: dict[str, Any]) -> Command:
    name = raw.get("name")
    if not name:
        raise ValueError(f"command missing 'name': {raw!r}")
    steps_raw = raw.get("steps") or []
    steps: list[Step] = []
    for i, s in enumerate(steps_raw):
        op = s.get("op")
        if not op:
            raise ValueError(f"command {name!r} step[{i}] missing 'op'")
        args = {k: v for k, v in s.items() if k != "op"}
        steps.append(Step(op=op, args=args))
    return Command(name=name, summary=raw.get("summary", ""), steps=steps)


def load_plan(path: Path) -> Plan:
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")

    if suffix == ".toml":
        data = tomllib.loads(text)
    elif suffix == ".json":
        data = json.loads(text)
    elif suffix in {".txt", ".jsonl", ".ndjson"}:
        commands_raw = [json.loads(line) for line in text.splitlines() if line.strip()]
        data = {"defaults": {}, "commands": commands_raw}
    else:
        raise ValueError(
            f"unsupported plan file extension {suffix!r}; use .toml, .json, or .txt"
        )

    defaults = data.get("defaults", {}) or {}
    commands = [_coerce_command(c) for c in data.get("commands", [])]
    return Plan(defaults=defaults, commands=commands)


def default_plan_path(cwd: Path) -> Path | None:
    for name in (
        "scaffold_skeleton.toml",
        "scaffold_skeleton.json",
        "scaffold_skeleton.txt",
    ):
        p = cwd / name
        if p.exists():
            return p
    return None


# ---------------------------------------------------------------------------
# gh CLI helpers
# ---------------------------------------------------------------------------


class GhError(RuntimeError):
    pass


class Gh:
    """Thin wrapper around the `gh` CLI."""

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self._binary = shutil.which("gh")

    def require(self) -> None:
        if self._binary is None:
            raise GhError(
                "`gh` CLI not found on PATH — install it from https://cli.github.com/"
            )
        # Check auth
        r = subprocess.run(
            [self._binary, "auth", "status"],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            raise GhError(
                "`gh` is not authenticated. Run `gh auth login` and retry.\n"
                + (r.stderr or r.stdout)
            )

    def run(
        self,
        *args: str,
        check: bool = True,
        capture: bool = True,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        if self.dry_run:
            log.info("   [dry-run] would run: gh %s", shlex.join(args))
            return subprocess.CompletedProcess(list(args), 0, stdout="", stderr="")
        assert self._binary is not None
        cmd = [self._binary, *args]
        log.debug("exec: %s", shlex.join(cmd))
        r = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            input=input_text,
        )
        if check and r.returncode != 0:
            raise GhError(
                f"gh {shlex.join(args)} failed ({r.returncode}):\n"
                f"stdout: {r.stdout}\nstderr: {r.stderr}"
            )
        return r


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------


class Runner:
    def __init__(self, gh: Gh, defaults: dict[str, Any]) -> None:
        self.gh = gh
        self.defaults = defaults
        self.owner: str = defaults.get("owner") or "ectorial"
        self.default_branch: str = defaults.get("default_branch") or "main"

    # --- utilities -------------------------------------------------------

    def _full(self, repo: str) -> str:
        return repo if "/" in repo else f"{self.owner}/{repo}"

    def _repo_exists(self, full: str) -> bool:
        if self.gh.dry_run:
            return False
        r = self.gh.run("repo", "view", full, "--json", "name", check=False)
        return r.returncode == 0

    def _get_file_sha(self, full: str, path: str, branch: str) -> str | None:
        if self.gh.dry_run:
            return None
        r = self.gh.run(
            "api",
            f"repos/{full}/contents/{path}",
            "-f",
            f"ref={branch}",
            "--jq",
            ".sha",
            check=False,
        )
        if r.returncode == 0:
            sha = (r.stdout or "").strip()
            return sha or None
        return None

    # --- ops -------------------------------------------------------------

    def ensure_repo(self, args: dict[str, Any]) -> None:
        repo = args["repo"]
        full = self._full(repo)
        description = args.get("description", "")
        private = bool(args.get("private", False))
        topics = args.get("topics") or []

        if self._repo_exists(full):
            log.info("  • repo %s already exists — skipping create", full)
        else:
            visibility = "--private" if private else "--public"
            cli_args = [
                "repo",
                "create",
                full,
                visibility,
                "--description",
                description or repo,
            ]
            log.info("  ✚ creating repo %s (%s)", full, "private" if private else "public")
            self.gh.run(*cli_args)

        if topics:
            self._set_topics(full, topics)

    def _set_topics(self, full: str, topics: list[str]) -> None:
        log.info("  • syncing topics on %s: %s", full, ", ".join(topics))
        payload = json.dumps({"names": topics})
        self.gh.run(
            "api",
            "-X",
            "PUT",
            f"repos/{full}/topics",
            "-H",
            "Accept: application/vnd.github.mercy-preview+json",
            "--input",
            "-",
            input_text=payload,
        )

    def ensure_topics(self, args: dict[str, Any]) -> None:
        full = self._full(args["repo"])
        self._set_topics(full, args.get("topics") or [])

    def ensure_file(self, args: dict[str, Any]) -> None:
        repo = args["repo"]
        full = self._full(repo)
        path = args["path"]
        branch = args.get("branch") or self.default_branch
        content = args.get("content")
        if content is None:
            source = args.get("source")
            if not source:
                raise ValueError(
                    f"ensure_file on {full}:{path} needs 'content' or 'source'"
                )
            content = Path(source).read_text(encoding="utf-8")

        overwrite = bool(args.get("overwrite", False))
        existing_sha = self._get_file_sha(full, path, branch)
        if existing_sha and not overwrite:
            log.info("  • %s:%s already exists — skipping (use overwrite=true to replace)", full, path)
            return

        action = "updating" if existing_sha else "creating"
        log.info("  ✚ %s %s:%s on %s", action, full, path, branch)

        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        message = args.get("message") or f"scaffold: {action} {path}"
        payload: dict[str, Any] = {
            "message": message,
            "content": encoded,
            "branch": branch,
        }
        if existing_sha:
            payload["sha"] = existing_sha

        self.gh.run(
            "api",
            "-X",
            "PUT",
            f"repos/{full}/contents/{path}",
            "--input",
            "-",
            input_text=json.dumps(payload),
        )

    def ensure_label(self, args: dict[str, Any]) -> None:
        full = self._full(args["repo"])
        name = args["name"]
        color = args.get("color", "ededed").lstrip("#")
        description = args.get("description", "")

        if not self.gh.dry_run:
            r = self.gh.run(
                "api",
                f"repos/{full}/labels/{name}",
                check=False,
            )
            if r.returncode == 0:
                log.info("  • label %r on %s already exists — skipping", name, full)
                return

        log.info("  ✚ creating label %r on %s", name, full)
        payload = json.dumps(
            {"name": name, "color": color, "description": description}
        )
        self.gh.run(
            "api",
            "-X",
            "POST",
            f"repos/{full}/labels",
            "--input",
            "-",
            input_text=payload,
        )

    # --- dispatch --------------------------------------------------------

    OPS = {
        "ensure_repo": "ensure_repo",
        "ensure_file": "ensure_file",
        "ensure_topics": "ensure_topics",
        "ensure_label": "ensure_label",
    }

    def run_step(self, step: Step) -> None:
        method_name = self.OPS.get(step.op)
        if method_name is None:
            raise ValueError(f"unknown op {step.op!r}")
        method = getattr(self, method_name)
        method(step.args)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        stream=sys.stdout,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="scaffold_skeleton",
        description="Scaffold the ectorial org for v0.1.",
    )
    p.add_argument(
        "--plan",
        type=Path,
        default=None,
        help="path to the plan file (.toml/.json/.txt); defaults to ./scaffold_skeleton.*",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="print what would happen; do not call gh",
    )
    p.add_argument(
        "--only",
        type=str,
        default=None,
        help="comma-separated list of command names to run (others are skipped)",
    )
    p.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="verbose logging (shows every gh call)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    _configure_logging(args.verbose)

    cwd = Path.cwd()
    plan_path = args.plan or default_plan_path(cwd)
    if plan_path is None:
        log.error(
            "no plan file found. Pass --plan PATH or create scaffold_skeleton.toml"
        )
        return 2
    plan_path = plan_path.resolve()

    log.info("▶ scaffold_skeleton starting")
    log.info("  plan:    %s", plan_path)
    log.info("  dry-run: %s", args.dry_run)

    plan = load_plan(plan_path)
    log.info("  owner:   %s", plan.defaults.get("owner", "ectorial"))
    log.info("  commands loaded: %d", len(plan.commands))

    only: set[str] | None = None
    if args.only:
        only = {s.strip() for s in args.only.split(",") if s.strip()}
        log.info("  filter:  only=%s", sorted(only))

    gh = Gh(dry_run=args.dry_run)
    try:
        if not args.dry_run:
            gh.require()
    except GhError as e:
        log.error("✖ %s", e)
        return 1

    runner = Runner(gh=gh, defaults=plan.defaults)

    ran = 0
    skipped = 0
    for cmd in plan.commands:
        if only is not None and cmd.name not in only:
            log.info("↷ skipping command %r (filtered out)", cmd.name)
            skipped += 1
            continue

        log.info("")
        log.info("━━ %s — %s", cmd.name, cmd.summary or "(no summary)")
        log.info("   steps: %d", len(cmd.steps))

        for i, step in enumerate(cmd.steps, 1):
            log.info("  [%d/%d] %s", i, len(cmd.steps), step.op)
            try:
                runner.run_step(step)
            except (GhError, ValueError) as e:
                log.error("    ✖ step failed: %s", e)
                return 1
        ran += 1

    log.info("")
    log.info("✔ done. ran=%d skipped=%d", ran, skipped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
