# CLI cheatsheet

All CLI programs listed here are included in `Brewfile`. Install them with:
`brew bundle install --no-upgrade --file=Brewfile`.
For shell integrations, apply the dotfiles and run `zsh -lic 'zimfw install'`.

## Alternatives to familiar commands

Run these alternatives explicitly: `ls`, `cat`, `grep`, `find`, `cd`,
`ps`, `top`, `du` and `df` are not overridden by aliases. Alternative tools may
use different flags from standard utilities; choose the tool explicitly in scripts.

| Familiar command / task | Installed alternative | Usage | Difference |
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
| `ps` | `procs` | `procs`; `procs node`; `procs --watch 2` | Process table, name filtering and updates every two seconds |
| `du` | `dust` | `dust .`; `dust -d 2 .` | Visual disk usage breakdown with a depth limit |
| `df` | `duf` | `duf`; `duf /` | Table of filesystems, capacity and available space |
| Viewing Git diffs | `delta` | `git diff`; `git show HEAD` | Already configured as the Git pager; use `git --no-pager diff` to bypass it |
| `curl` for HTTP APIs | `http` (HTTPie) | `http GET https://httpbin.org/get`; `http POST https://httpbin.org/post hello=world` | Readable output and simple JSON input; the second example sends test data |
| `curl -o`, downloading files | `wget` | `wget -O artifact.tgz https://example.com/artifact.tgz` | Saves to an explicit filename; replace the URL with your artifact URL |
| `vi` / `vim` | `nvim` (Neovim) | `nvim README.md` | Separate editor; EDITOR is not automatically changed to use it |
| `time` for command comparisons | `hyperfine` | `hyperfine --warmup 2 'rg TODO src' 'grep -R TODO src'` | Repeated runs with statistics; the example commands use different ignore rules |
| Repeated command execution | `watch`, `watchexec` | `watch -n 2 df -h`; `watchexec -e go -- go test ./...` | The first runs on a timer; the second runs when files change |

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
| fzf directory selection | Alt-C; your terminal may need Option configured as Alt |
| fzf-tab completion selection | Tab after a command or partial path |
| Accept an autosuggestion | Right arrow at the end of the line |
| Edit the command line in EDITOR | Ctrl-X, then Ctrl-E (Zim input module) |
| Install new modules after editing `.zimrc` | `zimfw install`, then open a new terminal tab |
| Update downloaded modules | `zimfw update` |
| List modules | `zimfw list` |
| Extract an archive | `unarchive archive.tar.gz` (Zim archive module) |

Zim Git uses an **uppercase `G` prefix**: `Gws` shows short status,
`Gwd` shows a diff, `Gia` stages files, `Gc` commits, and `Glg` shows the history graph.
For example: `Gia README.md`. The old `gst`, `ga`, `gc`, `ll`, `lt` and `please`
aliases are not defined. Inspect an alias with `alias Gws`.
The archive module also adds archive suffix aliases and uses pigz/pbzip2
instead of gzip/bzip2 when available.
[Zim documentation](https://zimfw.sh/docs/commands/), [Git aliases](https://github.com/zimfw/git).

## Other tools from Brewfile

| Task | Example |
| --- | --- |
| JSON | `jq '.scripts' package.json` |
| YAML | `yq '.services' compose.yaml` |
| GitHub CLI | `gh auth login`; `gh pr list`; `gh pr diff 1` |
| Git UI | Run `lazygit` inside a repository |
| Source code statistics | `tokei .` |
| Persistent terminal session | `tmux new -s work`; detach with Ctrl-B, D; reattach with `tmux attach -t work` |
| Project runtime versions | `mise use --pin node@lts`; `mise exec -- node --version` |
| Python dependencies | `uv add --dev ruff pre-commit`; `mise exec -- uv sync --locked --no-python-downloads` |
| Python formatting | `mise exec -- uv run --locked ruff format --check .` |
| Project tasks | `mise run test`; `just --list`; `just test` — when the corresponding task is defined |
| C/C++ builds | `cmake -S . -B build -G Ninja`; `cmake --build build` |
| GNU Make on macOS | `gmake` is the executable provided by the `make` formula |
| Compiler and linker flags for a library | `pkg-config --cflags --libs sqlite3` — when its metadata is available |
| Homebrew SQLite | `"$(brew --prefix sqlite)/bin/sqlite3" app.db '.tables'` |
| Go code from SQL | Run `sqlc generate` in a project with `sqlc.yaml` |
| SHA-256 with OpenSSL 3 | `"$(brew --prefix openssl@3)/bin/openssl" dgst -sha256 artifact.tgz` |
| File encryption | `age -r AGE_PUBLIC_RECIPIENT -o file.age file.txt` — substitute the recipient's public key |
| Editing encrypted YAML | `sops secrets.yaml` — after configuring the project's recipients and keys |
| Compare dotfiles before applying | `chezmoi diff`; `chezmoi apply`; `chezmoi verify` |

`sqlite` and `openssl@3` may be keg-only: using `brew --prefix FORMULA` in the path
selects the Homebrew version explicitly. System binaries remain available.
Keep age/SOPS keys and history databases out of the dotfiles repository.
