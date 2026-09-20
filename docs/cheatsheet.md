# CLI cheatsheet

Start with the [setup guide](../README.md). Tools marked **optional** come from
[Brewfile.optional](../Brewfile.optional): install a tool with `brew install NAME`
or the whole set with `brew bundle install --no-upgrade --file=Brewfile.optional`.
Project runtimes are installed by mise, separately from Homebrew.

## Alternatives to familiar commands

Run these alternatives explicitly: `ls`, `cat`, `grep`, `find`, `cd`,
`ps`, `top`, `du` and `df` are not overridden by aliases. Alternative tools may
use different flags from standard utilities; choose the tool explicitly in scripts.

| Familiar command / task | Alternative | Usage | Difference |
| --- | --- | --- | --- |
| `ls` | `eza` | `eza -la --git --group-directories-first` | Detailed listing with Git status; `eza -T -L 2` shows a tree |
| `cat`, viewing source files | `bat` | `bat README.md`; `bat --paging=never file.py` | Syntax highlighting and line numbers; use `cat` for byte-for-byte file concatenation |
| `less`, paged reading | `bat` or `less` | `bat file.py`; `less -R +G app.log` | `bat` is convenient for code; `less` handles large logs, and `F` follows appended output |
| `grep -R` | `rg` (ripgrep) | `rg -n 'TODO\|FIXME' src` | Recursive search; respects ignore files and skips hidden files by default |
| `find` | `fd` | `fd --type f --extension go . src` | Searches names; respects ignore files and skips hidden files by default |
| Repeated `cd` to familiar directories | `z`, `zi` (zoxide) | `z project`; `zi project` | Selects from visited directories; `zi` opens fzf; regular `cd` uses an exact path |
| `history`, Ctrl-R search | `atuin` | Ctrl-R; `atuin search 'git rebase'` | Searches a local database; Enter returns the selected command for review without executing it |
| Manual selection from a list | `fzf` | `fd --type f \| fzf` | Interactive fuzzy filter; Ctrl-T inserts selected paths into the shell command line |
| `top` | `btop` | `btop` | Interactive CPU, memory, network and process monitoring; press `q` to quit |
| `ps` | `procs` (optional) | `procs`; `procs node`; `procs --watch 2` | Process table, name filtering and updates every two seconds |
| `du` | `dust` | `dust .`; `dust -d 2 .` | Visual disk usage breakdown with a depth limit |
| `df` | `duf` (optional) | `duf`; `duf /` | Table of filesystems, capacity and available space |
| Viewing Git diffs | `delta` | `git diff`; `git show HEAD` | Already configured as the Git pager; use `git --no-pager diff` to bypass it |
| `curl` for HTTP APIs | `http` (HTTPie, optional) | `http GET https://httpbin.org/get`; `http POST https://httpbin.org/post hello=world` | Readable output and simple JSON input; the second example sends test data |
| `curl -o`, downloading files | `wget` (optional) | `wget -O artifact.tgz https://example.com/artifact.tgz` | Saves to an explicit filename; replace the URL with your artifact URL |
| `vi` / `vim` | `nvim` (Neovim, optional) | `nvim README.md` | Separate editor; EDITOR is not automatically changed to use it |
| `time` for command comparisons | `hyperfine` (optional) | `hyperfine --warmup 2 'rg TODO src' 'grep -R TODO src'` | Repeated runs with statistics; the example commands use different ignore rules |
| Repeated command execution | `watch`, `watchexec` (optional) | `watch -n 2 df -h`; `watchexec -e go -- go test ./...` | The first runs on a timer; the second runs when files change |

Documentation and additional flags: [eza](https://github.com/eza-community/eza),
[bat](https://github.com/sharkdp/bat), [ripgrep](https://github.com/BurntSushi/ripgrep),
[fd](https://github.com/sharkdp/fd), [zoxide](https://github.com/ajeetdsouza/zoxide),
[procs](https://github.com/dalance/procs), [dust](https://github.com/bootandy/dust),
[duf](https://github.com/muesli/duf).

## Search, hidden files and paths with spaces

```sh
rg -n --hidden --glob '!.git' 'TODO|FIXME' .
fd --hidden --exclude .git --type f --extension toml
fd --type f --print0 | fzf --read0 --print0   # NUL delimiters for path handling
```

`--hidden` includes hidden files while preserving ignore rules. Add `--no-ignore`
when you explicitly want to search ignored directories. Add `--follow` only when
you want to traverse symbolic links. Quote paths and preserve NUL delimiters
throughout pipelines that process lists of filenames.

## Keyboard shortcuts and Zimfw

| Action | Shortcut / command |
| --- | --- |
| Atuin history | Ctrl-R; Enter inserts the command, then another Enter executes it |
| fzf file selection | Ctrl-T |
| fzf directory selection | Left Option-C in Ghostty (Alt-C) |
| fzf-tab completion selection | Tab after a command or partial path |
| Accept an autosuggestion | Right arrow at the end of the line |
| Edit the command line in EDITOR | Ctrl-X, then Ctrl-E (Zim input module) |
| Install new modules after editing `.zimrc` | `zimfw install`, then open a new terminal tab |
| Update downloaded modules | `zimfw update` |
| List modules | `zimfw list` |

Zim loads input bindings, fzf-tab, autosuggestions and syntax highlighting.
Use full Git commands; Ghostty's shell integration handles terminal titles.
[Zim documentation](https://zimfw.sh/docs/commands/).

## Ghostty and SSH

| Action | Default macOS shortcut |
| --- | --- |
| New tab / close pane or tab | Cmd-T / Cmd-W |
| Next / previous tab | Ctrl-Tab / Ctrl-Shift-Tab |
| Split right / below | Cmd-D / Cmd-Shift-D |
| Next / previous split | Cmd-] / Cmd-[ |
| Zoom current split | Cmd-Shift-Enter |
| Command palette | Cmd-Shift-P |

Left Option acts as Alt for shell shortcuts; right Option keeps character input.
Adjust `macos-option-as-alt` in the managed config if you prefer another mapping.
[Ghostty options](https://ghostty.org/docs/config/reference#macos-option-as-alt).

If SSH reports `unknown terminal: xterm-ghostty`, copy terminfo from a Ghostty tab
to a host you manage (replace `user@host`):

```sh
infocmp -x xterm-ghostty | ssh user@host 'mkdir -p ~/.terminfo && tic -x -o ~/.terminfo -'
```

For a one-off connection to a host you cannot configure, use
`TERM=xterm-256color ssh user@host`; keep Ghostty's normal TERM locally.
[Terminfo reference](https://ghostty.org/docs/help/terminfo).

## First projects

Run each recipe in its own new directory. Pin only the runtimes the project uses.
Review existing project configs before `mise trust ./mise.toml`, then `mise install`;
review and trust again after edits. `mise exec -- …` also works in scripts and CI
without `.zshrc`; mise itself must be on PATH (on Apple Silicon,
`/opt/homebrew/bin/mise`).

### Python: mise + uv

```sh
mkdir hello-python
cd hello-python
mise use --pin python@3.14
```

Keep the generated `[tools]` section in `mise.toml` and add:

```toml
[env]
UV_PYTHON = { value = "{{ tools.python.path }}/bin/python", tools = true }
UV_PYTHON_DOWNLOADS = "never"
```

This selects mise's actual interpreter and disables uv's Python downloads for the
project. Run uv through mise so both settings apply:

```sh
mise trust ./mise.toml
mise exec -- uv init --app --no-package --no-pin-python
mise exec -- uv add --dev ruff pre-commit
mise exec -- uv run --locked main.py
mise exec -- uv run --locked ruff check .
mise exec -- uv run --locked ruff format --check .
mise exec -- uv run --locked python -c 'import sys; print(sys.executable); print(sys.base_prefix)'
```

The executable should be in `.venv`; the base prefix should match `mise where python`.
Commit `mise.toml`, `pyproject.toml`, `uv.lock` and source files; ignore `.venv/`.
On another machine, review/trust the config, run `mise install`, then
`mise exec -- uv sync --locked`. After adding and reviewing `.pre-commit-config.yaml`,
run `mise exec -- uv run --locked pre-commit install`.
[Mise + uv](https://mise.jdx.dev/lang/python.html), [uv projects](https://docs.astral.sh/uv/guides/projects/).

### Node: mise + npm

```sh
mkdir hello-node
cd hello-node
git init
mise use --pin node@lts
mise trust ./mise.toml
mise exec -- npm init -y
mise exec -- npm install --save-dev typescript
mise exec -- npm exec -- tsc --version
mise exec -- node --version
```

Commit `mise.toml`, `package.json` and `package-lock.json`; ignore `node_modules/`.
On another machine, review/trust the config, run `mise install`, then `mise exec -- npm ci`.

### Go: mise + Go modules

```sh
mkdir hello-go
cd hello-go
git init
mise use --pin go@latest
mise trust ./mise.toml
mise exec -- go mod init example.com/hello-go
```

Create `main.go`:

```go
package main

import "fmt"

func main() { fmt.Println("Hello, Go!") }
```

```sh
mise exec -- go run .
mise exec -- go test ./...
```

Commit `mise.toml`, `go.mod`, source files and `go.sum` when dependencies create it.
Use your repository's module path for a real project.

## VS Code and project runtimes

1. In the Command Palette, run **Shell Command: Install 'code' command in PATH**,
   open a new terminal, then run `code .` from the project directory.
2. Keep Workspace Trust and tool approvals enabled; choose extensions per language.
3. **Python:** finish the uv recipe, install Microsoft's Python extension and select
   `.venv/bin/python` via **Python: Select Interpreter**. Run/debug `main.py` with that
   interpreter; do not create a second environment in VS Code.
4. **Node:** use `mise exec -- node --version` in the integrated terminal. For the
   debugger, select the executable printed by `mise which node` as `runtimeExecutable`
   in your local launch configuration; recheck it after changing Node versions.
5. **Go:** install the Go extension. If it selects another SDK, set the `go` entry
   in `go.alternateTools` to the executable printed by `mise which go` in your local
   workspace settings.

The shell's runtime and the debugger's runtime are separate choices. Check the
integrated terminal with `mise current`; avoid committing machine-specific absolute
SDK paths. [macOS setup](https://code.visualstudio.com/docs/setup/mac),
[Python environments](https://code.visualstudio.com/docs/python/environments),
[Go SDK selection](https://github.com/golang/vscode-go/wiki/advanced#choosing-a-different-version-of-go).

## Git and optional signing

```sh
git status --short --branch
git diff
git add README.md
git commit
git log --oneline --graph -20
gh pr list
```

### SSH commit signing

Signing is separate from SSH authentication. Register your public key as a
**signing key** on GitHub, even if it is already registered for authentication.
Set these in your local `~/.gitconfig`:

```gitconfig
[gpg]
    format = ssh
[user]
    signingKey = ~/.ssh/id_ed25519.pub
```

Keep the private key loaded in your agent. For local verification, set
`gpg.ssh.allowedSignersFile` to a file containing your real email and public key:
`EMAIL namespaces="git" ssh-ed25519 PUBLIC_KEY`. Test a signed commit with
`git commit -S` and `git log -1 --show-signature` in a scratch repository before
enabling `commit.gpgSign=true` in your local config.
[Signing setup](https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key).

## More tools

| Task | Example | Install set |
| --- | --- | --- |
| JSON / YAML | `jq '.scripts' package.json`; `yq '.services' compose.yaml` | Base |
| Dotfiles | `chezmoi diff`; `chezmoi apply`; `chezmoi verify` | Base |
| Project tasks | `mise run test` — if the project defines it | Base |
| Git UI | `lazygit` inside a repository | Optional |
| Source statistics | `tokei .` | Optional |
| Persistent session | `tmux new -s work`; Ctrl-B, D to detach; `tmux attach -t work` | Optional |
| Justfile tasks | `just --list`; `just test` — if defined | Optional |
| C/C++ builds | `cmake -S . -B build -G Ninja`; `cmake --build build` | Optional |
| GNU Make | `gmake` — Apple's `make` stays unchanged | Optional |
| Library flags | `pkg-config --cflags --libs sqlite3` — if metadata is available | Optional |
| Homebrew SQLite | `"$(brew --prefix sqlite)/bin/sqlite3" app.db '.tables'` | Optional |
| Go code from SQL | `sqlc generate` in a project with `sqlc.yaml` | Optional |
| OpenSSL 3 digest | `"$(brew --prefix openssl@3)/bin/openssl" dgst -sha256 artifact.tgz` | Optional |
| File encryption | `age -r AGE_PUBLIC_RECIPIENT -o file.age file.txt` — use your recipient | Optional |
| Encrypted YAML | `sops secrets.yaml` — after configuring recipients and keys | Optional |

`brew --prefix FORMULA` selects keg-only binaries explicitly. Keep private keys
and history databases out of the dotfiles repository.
