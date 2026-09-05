#!/usr/bin/env python3
"""Offline tests. Only scratch homes/repos change; all installers are mocked."""
import csv
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which("chezmoi")
GIT = shutil.which("git")
ZSH = "/bin/zsh" if Path("/bin/zsh").exists() else shutil.which("zsh")
FILES = [p for p in ROOT.rglob("*") if p.is_file() and not
         any(x in {".git", "__pycache__", ".test-output"} for x in p.relative_to(ROOT).parts)]


def run(args, *, env=None, cwd=None, stdin="", ok=True):
    result = subprocess.run(args, env=env, cwd=cwd, input=stdin, text=True,
                            capture_output=True, timeout=60)
    if ok and result.returncode:
        raise AssertionError(f"{args}: {result.returncode}\n{result.stdout}\n{result.stderr}")
    return result


class StaticTests(unittest.TestCase):
    def test_syntax_and_format_check(self):
        for path in FILES:
            data = path.read_bytes()
            self.assertTrue(data.endswith(b"\n"), str(path))
            self.assertNotIn(b"\r", data, str(path))
            for line in data.splitlines():
                self.assertEqual(line, line.rstrip(b" \t"), str(path))
            if path.suffix == ".sh" or path.name in {"bootstrap", "verify"}:
                for shell in ["/bin/sh", "/bin/bash"]:
                    run([shell, "-n", str(path)])
            if path.suffix == ".toml":
                tomllib.loads(data.decode())
            if path.suffix == ".json":
                json.loads(data)

    def test_manifests_are_unique_and_scoped(self):
        owners = {}
        for path in (ROOT / "manifests/macos/cli").glob("*.Brewfile"):
            for line in path.read_text().splitlines():
                if not line or line.startswith("#"):
                    continue
                match = re.fullmatch(r'brew "([a-z0-9@+-]+)"', line)
                self.assertIsNotNone(match, line)
                name = match[1]
                self.assertNotIn(name, owners, name)
                owners[name] = path.stem
        self.assertEqual({n for n, p in owners.items() if p == "core"}, {"git", "chezmoi", "mise"})
        self.assertNotIn("docker", owners)
        self.assertNotIn("zsh", owners)
        with (ROOT / "manifests/macos/gui.tsv").open() as stream:
            apps = list(csv.DictReader(stream, delimiter="\t"))
        self.assertEqual(len({a["id"] for a in apps}), len(apps))
        self.assertEqual(len({a["cask"] for a in apps}), len(apps))
        self.assertTrue(all(a["source"].startswith("https://") for a in apps))

    def test_no_aliases_or_unsafe_defaults(self):
        for path in FILES:
            if "dotfiles" not in path.relative_to(ROOT).parts:
                continue
            text = path.read_text()
            self.assertIsNone(re.search(r"^\s*(alias\s|\[alias\])", text, re.M), str(path))
            self.assertIsNone(re.search(r"^\s*(cat|ls|cd|grep|find|ps|du|df)\s*\(\)", text, re.M), str(path))
            for pattern in ["ssh-agent -s", "compinit -C\n", "PAGER=\"bat", "core.ignorecase", "core.fileMode"]:
                self.assertNotIn(pattern, text, str(path))
        settings = json.loads((ROOT / "config/editors/vscode/settings.json").read_text())
        self.assertTrue(settings["security.workspace.trust.enabled"])
        self.assertFalse(any("autoApprove" in key or "autoAccept" in key for key in settings))

    def test_document_links_exist(self):
        for path in FILES:
            if path.suffix == ".md":
                for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                    if "://" not in target and not target.startswith("#"):
                        self.assertTrue((path.parent / target.split("#")[0]).exists(), f"{path}: {target}")


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="unix setup tests ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "checkout with spaces"
        self.home = self.base / "home with spaces"
        self.bin = self.base / "bin"
        for path in [self.repo, self.home, self.bin]:
            path.mkdir()
        for path in FILES:
            target = self.repo / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        for name, executable in [("chezmoi", CHEZMOI), ("git", GIT)]:
            (self.bin / name).symlink_to(executable)
        self.stub("mise", 'printf "mise %s\\n" "$*" >> "$CALLS"\nexit 91\n')
        self.env = {
            "HOME": str(self.home), "PATH": f"{self.bin}:/usr/bin:/bin:/usr/sbin:/sbin",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_DATA_HOME": str(self.home / ".local/share"),
            "XDG_STATE_HOME": str(self.home / ".local/state"),
            "XDG_CACHE_HOME": str(self.home / ".cache"), "ZDOTDIR": str(self.home),
            "GIT_CONFIG_NOSYSTEM": "1", "TERM": "xterm-256color", "LC_ALL": "C",
            "CALLS": str(self.base / "calls"), "TMPDIR": str(self.base),
        }
        run([GIT, "init", "-q", str(self.repo)], env=self.env)

    def stub(self, name, body):
        path = self.bin / name
        path.write_text("#!/bin/sh\nset -eu\n" + body)
        path.chmod(0o755)

    def bootstrap(self, *args, stdin="", ok=True, shell="/bin/sh"):
        return run([shell, str(self.repo / "bootstrap"), *args], env=self.env,
                   cwd=self.repo, stdin=stdin, ok=ok)

    def init(self, zsh=False, terminal=False, tmux=False, ghostty=False):
        answers = "".join("yes\n" if flag else "no\n" for flag in [zsh, terminal, tmux, ghostty])
        return self.bootstrap("common", "init", stdin=answers)

    def cm(self, *args):
        return run([CHEZMOI, "--source", str(self.repo / "dotfiles"), "--destination", str(self.home),
                    "--config", str(self.home / ".config/unix-setup/chezmoi.toml"),
                    "--persistent-state", str(self.home / ".local/state/unix-setup/chezmoi-state.boltdb"),
                    "--no-tty", *args], env=self.env, cwd=self.repo)

    def test_apply_decline_idempotence_backup_restore(self):
        self.init(zsh=True)
        original = b"# user's existing config\nexport ORIGINAL=kept\n"
        (self.home / ".zshrc").write_bytes(original)
        (self.home / ".zshrc").chmod(0o640)
        (self.home / ".gitconfig").write_text('[user]\n name = Existing\n email = existing@example.org\n')
        self.bootstrap("common", "diff")
        self.assertEqual((self.home / ".zshrc").read_bytes(), original)
        declined = self.bootstrap("common", "apply", stdin="no\n", ok=False)
        self.assertNotEqual(declined.returncode, 0)
        self.assertEqual((self.home / ".zshrc").read_bytes(), original)
        self.assertFalse((self.home / ".config/git/config").exists())
        applied = self.bootstrap("common", "apply", stdin="apply\n", shell="/bin/bash")
        self.assertIn("Backup:", applied.stdout)
        backups = list((self.home / ".local/state/unix-setup/backups").glob("snapshot.*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].stat().st_mode & 0o777, 0o700)
        self.assertEqual((backups[0] / "files/.zshrc").read_bytes(), original)
        self.assertIn("Existing", (self.home / ".gitconfig").read_text())
        self.assertIn("Already matches", self.bootstrap("common", "apply").stdout)
        self.assertEqual(len(list(backups[0].parent.glob("snapshot.*"))), 1)
        self.assertFalse((self.base / "calls").exists())
        self.bootstrap("common", "restore", backups[0].name, stdin="restore\n")
        self.assertEqual((self.home / ".zshrc").read_bytes(), original)
        self.assertEqual((self.home / ".zshrc").stat().st_mode & 0o777, 0o640)
        self.assertFalse((self.home / ".config/git/config").exists())
        self.assertTrue(backups[0].exists())

    def test_leaf_symlink_backup_restore_and_parent_rejection(self):
        self.init(zsh=True)
        outside = self.base / "original zshrc"
        outside.write_text("# do not change the symlink target\n")
        (self.home / ".zshrc").symlink_to(outside)
        self.bootstrap("common", "apply", stdin="apply\n")
        self.assertEqual(outside.read_text(), "# do not change the symlink target\n")
        snapshot = next((self.home / ".local/state/unix-setup/backups").glob("snapshot.*"))
        self.bootstrap("common", "restore", snapshot.name, stdin="restore\n")
        self.assertEqual(os.readlink(self.home / ".zshrc"), str(outside))
        target = self.base / "external git"
        target.mkdir()
        gitdir = self.home / ".config/git"
        gitdir.rmdir()
        gitdir.symlink_to(target, target_is_directory=True)
        result = self.bootstrap("common", "apply", stdin="apply\n", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(target.iterdir()), [])

    def test_options_stay_and_platform_templates(self):
        self.init()
        config = self.home / ".config/unix-setup/chezmoi.toml"
        before = config.read_bytes()
        self.init(zsh=True, terminal=True)
        self.assertEqual(config.read_bytes(), before)
        managed = self.cm("managed", "--include=files,symlinks").stdout
        for path in [".zshrc", "atuin", "ghostty"]:
            self.assertNotIn(path, managed)
        data = json.dumps({"chezmoi": {"os": "linux"}, "zsh": True, "terminal": True, "tmux": True, "ghostty": True})
        linux = self.cm("--override-data", data, "managed", "--include=files,symlinks").stdout
        for path in ["ghostty", ".ssh/", "git/macos"]:
            self.assertNotIn(path, linux)
        self.assertIn(".zshrc", linux)
        profile = self.cm("--override-data", data, "cat", str(self.home / ".zprofile")).stdout
        self.assertNotIn("brew", profile)

    def test_shell_startup_and_no_standard_command_replacements(self):
        self.init(zsh=True, terminal=True)
        for tool in ["starship", "atuin", "fzf", "fd", "rg", "zoxide", "delta"]:
            self.stub(tool, "exit 0\n")
        self.bootstrap("common", "apply", stdin="apply\n")
        for path in [".zshenv", ".zprofile", ".zshrc"]:
            run([ZSH, "-n", str(self.home / path)], env=self.env)
        result = run([ZSH, "-c", "printf 'noninteractive-ok'"], env=self.env, cwd=self.home)
        self.assertEqual(result.stdout, "noninteractive-ok")
        self.assertEqual(result.stderr, "")
        self.assertFalse((self.base / "calls").exists())
        # Stubs expose ordering without executing integrations or networking.
        self.stub("mise", 'printf "# mise activation stub\\n"\n')
        self.stub("fzf", "[ \"$1\" = --zsh ]\ncat <<'EOF'\nif [[ \"${FZF_CTRL_R_COMMAND-unset}\" != '' ]]; then\n    bindkey '^R' fzf-history-widget\nfi\nEOF\n")
        self.stub("atuin", "[ \"$*\" = 'init zsh --disable-up-arrow' ]\nprintf \"bindkey '^R' atuin-search\\n\"\n")
        self.stub("starship", 'printf "# starship stub\\n"\n')
        self.stub("zoxide", "[ \"$*\" = 'init zsh --cmd z' ]\nprintf 'function z() { builtin cd \"$@\"; }\\n'\n")
        code = "bindkey '^R'; (( ${+aliases[cat]} + ${+aliases[cd]} + ${+aliases[ls]} == 0 )) || exit 8; for name in cat cd ls grep find ps du df; do (( ! ${+functions[$name]} )) || exit 9; done"
        result = run([ZSH, "-d", "-i", "-c", code], env=self.env, cwd=self.home)
        self.assertIn("atuin-search", result.stdout)

    def test_missing_dependencies_fail_before_destination_changes(self):
        self.init(terminal=True)
        result = self.bootstrap("common", "apply", stdin="apply\n", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Required command missing", result.stderr)
        self.assertFalse((self.home / ".config/git/config").exists())

    def test_verify_common_and_preserve_directory_modes(self):
        self.init()
        gitdir = self.home / ".config/git"
        gitdir.mkdir(mode=0o755)
        self.bootstrap("common", "apply", stdin="apply\n")
        self.assertEqual(gitdir.stat().st_mode & 0o777, 0o755)
        result = run(["/bin/sh", str(self.repo / "verify"), "common"], env=self.env, cwd=self.repo)
        self.assertIn("OK dotfiles", result.stdout)
        run([GIT, "config", "--global", "core.ignorecase", "false"], env=self.env)
        result = run(["/bin/sh", str(self.repo / "verify"), "common"], env=self.env, cwd=self.repo, ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("REVIEW global core.ignorecase", result.stderr)

    def test_partial_apply_failure_remains_recoverable(self):
        self.init(zsh=True)
        original = "# original before failure\n"
        (self.home / ".zshenv").write_text(original)
        (self.bin / "chezmoi").unlink()
        self.env["REAL_CHEZMOI"] = CHEZMOI
        self.stub("chezmoi", 'for arg in "$@"; do if [ "$arg" = apply ]; then printf "partial write\\n" > "$HOME/.zshenv"; exit 9; fi; done\nexec "$REAL_CHEZMOI" "$@"\n')
        self.assertNotEqual(self.bootstrap("common", "apply", stdin="apply\n", ok=False).returncode, 0)
        snapshot = next((self.home / ".local/state/unix-setup/backups").glob("snapshot.*"))
        self.assertTrue((snapshot / "complete").exists())
        self.bootstrap("common", "restore", snapshot.name, stdin="restore\n")
        self.assertEqual((self.home / ".zshenv").read_text(), original)
        (snapshot / "complete").unlink()
        self.assertNotEqual(self.bootstrap("common", "restore", snapshot.name, stdin="restore\n", ok=False).returncode, 0)

    def test_platform_preflight_rejects_wrong_os_rosetta_and_missing_clt(self):
        self.stub("uname", 'case "$1" in -s) printf "%s\\n" "$TEST_OS" ;; -m) printf "arm64\\n" ;; esac\n')
        self.stub("sw_vers", 'printf "%s\\n" "$TEST_VERSION"\n')
        self.stub("sysctl", 'printf "%s\\n" "$TEST_TRANSLATED"\n')
        self.stub("xcode-select", "exit 1\n")
        self.env.update(TEST_OS="Linux", TEST_VERSION="14.0", TEST_TRANSLATED="0")
        self.assertIn("macOS-only", self.bootstrap("macos", "prepare", ok=False).stderr)
        self.env["TEST_OS"] = "Darwin"
        self.env["TEST_VERSION"] = "13.0"
        self.assertIn("14 or newer", self.bootstrap("macos", "prepare", ok=False).stderr)
        self.env.update(TEST_VERSION="14.0", TEST_TRANSLATED="1")
        self.assertIn("Rosetta", self.bootstrap("macos", "prepare", ok=False).stderr)
        self.env["TEST_TRANSLATED"] = "0"
        self.assertIn("Command Line Tools", self.bootstrap("macos", "prepare", ok=False).stderr)

    def test_refuse_root_custom_xdg_and_invalid_requests(self):
        self.stub("id", "printf '0\\n'\n")
        self.assertIn("without sudo", self.bootstrap("common", "init", ok=False).stderr)
        (self.bin / "id").unlink()
        self.env["XDG_CONFIG_HOME"] = str(self.base / "custom config")
        self.assertNotEqual(self.bootstrap("common", "init", ok=False).returncode, 0)
        self.env["XDG_CONFIG_HOME"] = str(self.home / ".config")
        for args in [("macos", "install", "../bad"), ("macos", "gui", "install", "ghostty", "bad"), ("steamdeck",)]:
            self.assertNotEqual(self.bootstrap(*args, ok=False).returncode, 0)
        self.assertFalse((self.home / ".config").exists())

    def test_macos_manifests_with_mock_package_manager(self):
        self.stub("mock-brew", "printf '%s\\n' \"$*\" >> \"$CALLS\"\ncase \"$*\" in\n'bundle list --brews --file='*) for arg in \"$@\"; do case $arg in --file=*) sed -n 's/^brew \"\\([^\"]*\\)\"$/\\1/p' \"${arg#--file=}\" ;; esac; done ;;\nesac\n")
        code = 'set -eu; ROOT=$1; . "$ROOT/scripts/common.sh"; . "$ROOT/platforms/macos/bootstrap.sh"; macos_environment() { BREW=mock-brew; }; shift; macos_command "$@"'
        run(["/bin/sh", "-c", code, "test", str(self.repo), "install", "terminal"], env=self.env)
        calls = (self.base / "calls").read_text()
        self.assertEqual(calls.count("bundle install --no-upgrade"), 2)
        self.assertNotIn("cask", calls)
        self.assertFalse(any(line.startswith("upgrade ") for line in calls.splitlines()))
        (self.base / "calls").unlink()
        run(["/bin/sh", "-c", code, "test", str(self.repo), "update"], env=self.env)
        calls = (self.base / "calls").read_text()
        self.assertIn("upgrade --formula git", calls)
        self.assertNotIn("install", calls)
        self.assertNotIn("--cask", calls)

    def test_local_signing_without_project_changes(self):
        key = self.home / "test signing key"
        run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)], env=self.env)
        allowed = self.home / "allowed signers"
        allowed.write_text('test@example.org namespaces="git" ' + " ".join(key.with_suffix(".pub").read_text().split()[:2]) + "\n")
        for setting, value in {"user.name": "Test Signer", "user.email": "test@example.org", "user.signingkey": str(key), "gpg.format": "ssh", "gpg.ssh.allowedSignersFile": str(allowed)}.items():
            run([GIT, "config", "--global", setting, value], env=self.env)
        result = run(["/bin/sh", str(self.repo / "verify"), "signing"], env=self.env, cwd=self.repo)
        self.assertIn("OK: local signing", result.stdout)
        self.assertEqual(list(self.base.glob("unix-setup-signing.*")), [])
        # An untrusted key must fail, even if signing itself succeeds.
        allowed.write_text("# no trusted keys\n")
        result = run(["/bin/sh", str(self.repo / "verify"), "signing"], env=self.env, cwd=self.repo, ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.base.glob("unix-setup-signing.*")), [])


if __name__ == "__main__":
    if not all([CHEZMOI, GIT, ZSH]):
        raise SystemExit("Tests require existing chezmoi, Git and zsh; no tools will be installed.")
    if os.getuid() == 0:
        raise SystemExit("Run repository tests as a non-root user.")
    unittest.main(verbosity=2)
