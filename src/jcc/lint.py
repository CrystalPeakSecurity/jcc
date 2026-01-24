"""Source linting for JCC.

Provides pattern-based and structural lint rules that can be configured
per-project in jcc.toml.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jcc.config import LintConfig


@dataclass
class LintError:
    """A linting error found in source code."""

    file: Path
    line: int
    code: str
    message: str
    rule: str
    column: int | None = None

    def __str__(self) -> str:
        loc = f"{self.file.name}:{self.line}"
        if self.column:
            loc += f":{self.column}"
        return f"{loc}: {self.code}\n  ^ {self.message} [{self.rule}]"


class LintRule(ABC):
    """Base class for lint rules."""

    name: str

    @abstractmethod
    def check(self, path: Path, content: str) -> list[LintError]:
        """Check a file for violations.

        Args:
            path: Path to the file being checked
            content: File content

        Returns:
            List of errors found
        """
        ...


@dataclass
class PatternRule(LintRule):
    """A regex pattern-based lint rule."""

    name: str
    pattern: str
    message: str
    _compiled: re.Pattern[str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._compiled = re.compile(self.pattern)

    def check(self, path: Path, content: str) -> list[LintError]:
        errors = []
        for i, line in enumerate(content.splitlines(), 1):
            match = self._compiled.search(line)
            if match:
                # Skip if match is inside a comment
                comment_start = line.find("//")
                if comment_start != -1 and match.start() > comment_start:
                    continue
                errors.append(
                    LintError(
                        file=path,
                        line=i,
                        column=match.start() + 1,
                        code=line.strip(),
                        message=self.message,
                        rule=self.name,
                    )
                )
        return errors


class DeathPainStateRule(LintRule):
    """Verify that all initial death/pain states have ACT_NONE.

    NOTE: This is a DOOM-specific rule that parses data/mobjinfo.h.
    It won't do anything for non-DOOM projects.

    This is required because P_DamageMobj uses P_SetMobjStateRaw (not P_SetMobjState)
    to avoid stack overflow. P_SetMobjStateRaw skips action execution entirely,
    so if a death/pain state has a real action, it will be silently skipped.

    See combat.h P_DamageMobj for details.
    """

    name = "death_pain_state"

    def check(self, path: Path, content: str) -> list[LintError]:
        # Only check data/mobjinfo.h
        if not (path.name == "mobjinfo.h" and path.parent.name == "data"):
            return []

        errors = []

        # Parse state name -> index from #define statements
        state_indices: dict[str, int] = {}
        for match in re.finditer(r"#define\s+(S_\w+)\s+(\d+)", content):
            state_indices[match.group(1)] = int(match.group(2))

        # Parse states[] array to get action for each index
        state_actions: dict[int, str] = {}
        states_match = re.search(r"const struct state_t states\[.*?\]\s*=\s*\{(.*?)\};", content, re.DOTALL)
        if states_match:
            idx = 0
            for entry in re.finditer(r"\{[^}]*,\s*(ACT_\w+)\s*,", states_match.group(1)):
                state_actions[idx] = entry.group(1)
                idx += 1

        # Parse mobjinfo[] to get painstate/deathstate for each type
        mobjinfo_match = re.search(r"const struct mobjinfo_t mobjinfo\[.*?\]\s*=\s*\{(.*?)\};", content, re.DOTALL)
        if mobjinfo_match:
            entry_pattern = re.compile(
                r"//\s*(MT_\w+).*?\n"  # Comment with type name
                r"\s*\{[^}]+,\s*"  # First 6 fields (health through flags)
                r"(\w+),\s*"  # spawnstate
                r"(\w+),\s*"  # seestate
                r"(\w+),\s*"  # painstate
                r"(\w+),\s*"  # meleestate
                r"(\w+),\s*"  # missilestate
                r"(\w+)\s*\}",  # deathstate
                re.DOTALL,
            )

            for match in entry_pattern.finditer(mobjinfo_match.group(1)):
                type_name = match.group(1)
                painstate_name = match.group(4)
                deathstate_name = match.group(7)

                # Check painstate (if not S_NULL)
                if painstate_name != "S_NULL" and painstate_name in state_indices:
                    idx = state_indices[painstate_name]
                    action = state_actions.get(idx, "UNKNOWN")
                    if action != "ACT_NONE":
                        # Find line number of the mobjinfo entry
                        line_num = content[: match.start()].count("\n") + 1
                        errors.append(
                            LintError(
                                file=path,
                                line=line_num,
                                code=f"{type_name} painstate = {painstate_name}",
                                message=f"painstate {painstate_name} has {action}, must be ACT_NONE. "
                                f"P_DamageMobj uses P_SetMobjStateRaw which skips action execution.",
                                rule=self.name,
                            )
                        )

                # Check deathstate (if not S_NULL)
                if deathstate_name != "S_NULL" and deathstate_name in state_indices:
                    idx = state_indices[deathstate_name]
                    action = state_actions.get(idx, "UNKNOWN")
                    if action != "ACT_NONE":
                        line_num = content[: match.start()].count("\n") + 1
                        errors.append(
                            LintError(
                                file=path,
                                line=line_num,
                                code=f"{type_name} deathstate = {deathstate_name}",
                                message=f"deathstate {deathstate_name} has {action}, must be ACT_NONE. "
                                f"P_DamageMobj uses P_SetMobjStateRaw which skips action execution.",
                                rule=self.name,
                            )
                        )

        return errors


class Linter:
    """Runs lint rules against source files."""

    def __init__(self, rules: list[LintRule]) -> None:
        self.rules = rules

    def lint(self, paths: list[Path]) -> list[LintError]:
        """Run all rules against the given files.

        Args:
            paths: Files to check

        Returns:
            All errors found across all files and rules
        """
        errors: list[LintError] = []
        for path in paths:
            if not path.exists():
                continue
            content = path.read_text()
            for rule in self.rules:
                errors.extend(rule.check(path, content))
        return errors

    @classmethod
    def from_config(cls, config: "LintConfig") -> "Linter":
        """Create a linter from configuration.

        Args:
            config: Lint configuration from jcc.toml

        Returns:
            Configured Linter instance
        """
        rules: list[LintRule] = []

        # Add pattern rules from config
        for pattern_config in config.pattern_rules:
            rules.append(
                PatternRule(
                    name=pattern_config.name or f"pattern_{len(rules)}",
                    pattern=pattern_config.pattern,
                    message=pattern_config.message,
                )
            )

        # Add structural rules based on config flags
        if config.death_pain_state:
            rules.append(DeathPainStateRule())

        return cls(rules)
