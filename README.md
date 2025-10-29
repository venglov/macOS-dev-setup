# macOS Developer Setup (2025)

Opinionated, repeatable bootstrap for a clean macOS machine. The quickstart below is meant for copy/paste on a fresh install.

---

## Quickstart (copy/paste)

Run the blocks in order. Commands that overwrite dotfiles (`~/.zprofile`, `~/.zshenv`, `~/.zshrc`, `~/.zimrc`, `~/.gitignore_global`) assume a clean setup—back up existing files if you care about them.

### Step 0 — Prerequisites

```bash
xcode-select --install
# Apple Silicon only: install Rosetta if you need x86 binaries
sudo softwareupdate --install-rosetta --agree-to-license
```

### Step 1 — Homebrew (CLI only)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### Step 2 — Core CLI stack

```bash
brew update && brew upgrade

brew install \
  zsh zsh-completions \
  fzf ripgrep fd eza bat \
  git gh jq yq git-delta \
  zoxide atuin \
  watch less \
  btop duf dust procs \
  openssl@3 age sops \
  make cmake ninja pkg-config \
  sqlite \
  httpie wget \
  tokei \
  mise uv \
  mas \
  docker \
  ollama
```

**Optional tooling** (only if you actively use these categories):

```bash
brew install postgresql@16 redis \
  kubectl k9s helm kubectx stern \
  dive cosign trivy oras
```

Install fzf key bindings and completions:

```bash
"$(brew --prefix)/opt/fzf/install" --key-bindings --completion --no-update-rc
```

Start installed services (optional):

```bash
brew services start postgresql@16   # Postgres
brew services start redis           # Redis
brew services start ollama          # Ollama API
brew services start atuin           # Atuin history daemon
```

(Optional but recommended for Spaceship prompt glyphs)

```bash
brew install --cask font-meslo-lg-nerd-font
```

### Step 3 — Zsh with Zimfw

#### 3.1 `~/.zprofile`

```bash
cat > ~/.zprofile <<'EOF'
# Homebrew (ARM)
eval "$(/opt/homebrew/bin/brew shellenv)"

# User tool paths (uv, Go, etc.)
export PATH="$HOME/.local/bin:$HOME/go/bin:$PATH"
EOF
```

#### 3.2 `~/.zshenv`

```bash
cat > ~/.zshenv <<'EOF'
export HOMEBREW_NO_ANALYTICS=1
export EDITOR="vim"
export MANPAGER="less -R"
EOF
```

#### 3.3 Install Zimfw

```bash
curl -fsSL https://raw.githubusercontent.com/zimfw/install/master/install.zsh | zsh
```

#### 3.4 `~/.zimrc`

```bash
cat >| ~/.zimrc <<'EOF'
zmodule zimfw/archive
zmodule zimfw/git
zmodule zimfw/input
zmodule zimfw/termtitle

# Theme (module options BEFORE init options)
zmodule spaceship-prompt/spaceship-prompt -n spaceship -s "spaceship.zsh"

# Plugins
zmodule zsh-users/zsh-autosuggestions
zmodule zdharma-continuum/fast-syntax-highlighting
zmodule Aloxaf/fzf-tab

# Build preferences
zstyle ':zim' build autoload
EOF

# 2) Install missing modules and build the init
zimfw install
zimfw build

# 3) Activate in current shell (or just open a new terminal)
source "${ZDOTDIR:-$HOME}/.zim/init.zsh" 2>/dev/null || true
```

#### 3.5 `~/.zshrc`

```bash
cat >| ~/.zshrc <<'EOF'
setopt HIST_IGNORE_DUPS HIST_IGNORE_SPACE HIST_VERIFY SHARE_HISTORY
setopt AUTO_CD EXTENDED_GLOB INTERACTIVE_COMMENTS
bindkey -v
export KEYTIMEOUT=1

# Completions: add Homebrew dirs then init (cached)
if command -v brew >/dev/null 2>&1; then
  fpath=("$(brew --prefix)/share/zsh-completions" "$(brew --prefix)/share/zsh/site-functions" $fpath)
fi
autoload -Uz compinit
compinit -C

# Load Zim
source "${ZDOTDIR:-$HOME}/.zim/init.zsh"

# Prompt: Spaceship (inline overrides)
export SPACESHIP_PROMPT_ADD_NEWLINE=true
export SPACESHIP_CHAR_SYMBOL="❯ "
export SPACESHIP_PROMPT_ORDER=(time user dir host git node golang docker venv python exec_time line_sep char)

# Tooling hooks
eval "$(zoxide init zsh)"
eval "$(atuin init zsh)"
# Global mise shims & env
eval "$(mise activate zsh)"

# fzf defaults
export FZF_DEFAULT_COMMAND='rg --files --hidden --follow --glob "!.git"'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND='fd -t d .'

# Pager & bat
export BAT_THEME="OneHalfDark"
export PAGER="bat -p"

# Aliases
alias ll='eza -l --git'
alias lt='eza -T -L 2 --git'
alias la='eza -la --git'
alias rgp='rg --hidden --glob "!.git"'
alias g=git
alias please='sudo $(fc -ln -1)'

zmodload zsh/complist 2>/dev/null
EOF
```

### Step 4 — Languages & toolchains (mise)

```bash
mise use -g python@3.14
mise use -g golang@1.25
```

### Step 5 — Go tools (built with mise’s Go)

```bash
go install golang.org/x/tools/gopls@latest
go install golang.org/x/tools/gopls/internal/analysis/modernize/cmd/modernize@latest
go install github.com/go-delve/delve/cmd/dlv@latest
go install honnef.co/go/tools/cmd/staticcheck@latest
go install mvdan.cc/gofumpt@latest
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@latest
go install golang.org/x/vuln/cmd/govulncheck@latest
```

### Step 6 — Python fast path (`uv`)

```bash
uv tool install ruff
uv tool install pre-commit
```

Reshim:

```bash
mise reshim
```

### Step 7 — Git sane defaults

```bash
git config --global init.defaultBranch main
git config --global pull.rebase true
git config --global rebase.autosquash true
git config --global rebase.autoStash true
git config --global fetch.prune true
git config --global push.autoSetupRemote true
git config --global core.fileMode false
git config --global core.ignorecase false
git config --global color.ui auto
git config --global merge.conflictstyle zdiff3
git config --global diff.tool delta
git config --global credential.helper osxkeychain

cat > ~/.gitignore_global <<'EOF'
.DS_Store
.idea/
.vscode/
venv/
__pycache__/
*.pyc
dist/
node_modules/
coverage/
EOF
git config --global core.excludesfile ~/.gitignore_global
```

#### 7.1 — SSH keys and commit signing (recommended)

Generate an SSH key, store the passphrase in Keychain, and enable SSH-based commit signing.

```bash
# Generate key (ed25519)
ssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519 -C "$USER@$(scutil --get ComputerName)"

# Start agent and store key in macOS Keychain
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/id_ed25519

# Git: sign commits with SSH
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true

# Add your public key to your Git host (GitHub, GitLab, etc.)
pbcopy < ~/.ssh/id_ed25519.pub  # copies the key to clipboard (macOS)
open https://github.com/settings/ssh/new || true

# Authenticate GitHub CLI (optional)
gh auth login
```

### Step 8 — GUI apps (Homebrew Cask + MAS)

Install GUI apps available via Homebrew Cask:

```bash
brew install --cask \
  visual-studio-code \
  ghostty \
  warp \
  raycast \
  beekeeper-studio \
  insomnia \
  stats \
  orbstack \
  google-chrome \
  telegram \
  discord \
  github \
  chatgpt \
  chatgpt-atlas \
  ledger-live \
  steam \
  prismlauncher \
  logi-options+ \
  applite \
  orcaslicer \
  codex


# After launching VS Code once, enable the `code` shell command from the Command Palette
```

Install App Store apps via `mas` (sign in to App Store first):

```bash
# Ensure you are signed in to the Mac App Store app
open -a "App Store"  # Sign in if needed, then close

# Apple iWork (Office) apps
mas install 409201541  # Pages
mas install 409203825  # Numbers
mas install 409183694  # Keynote
```

### Step 9 — Verify the toolchain

```bash
zsh --version
brew doctor
zimfw --version
docker version
mise doctor
python --version
go version
fzf --version
zoxide --version
atuin --version
btop --version
```

## VS Code setup

```bash
# AI
code --install-extension openai.chatgpt --profile "main"
code --install-extension GitHub.copilot --profile "main"
code --install-extension GitHub.copilot-chat --profile "main"

# Git (lightweight)
code --install-extension mhutchie.git-graph --profile "main"

# Diagnostics / UX
code --install-extension usernamehw.errorlens --profile "main"
code --install-extension Gruntfuggly.todo-tree --profile "main"
code --install-extension streetsidesoftware.code-spell-checker --profile "main"

# Web + lint/format
code --install-extension dbaeumer.vscode-eslint --profile "main"
code --install-extension esbenp.prettier-vscode --profile "main"

# Python + Jupyter
code --install-extension ms-python.python --profile "main"
code --install-extension ms-python.vscode-pylance --profile "main"
code --install-extension ms-toolsai.jupyter --profile "main"
code --install-extension ms-toolsai.jupyter-renderers --profile "main"
code --install-extension ms-toolsai.jupyter-keymap --profile "main"

# Go / YAML / Markdown
code --install-extension golang.go --profile "main"
code --install-extension redhat.vscode-yaml --profile "main"
code --install-extension yzhang.markdown-all-in-one --profile "main"
code --install-extension DavidAnson.vscode-markdownlint --profile "main"

# Remote & Containers
code --install-extension ms-vscode-remote.remote-ssh --profile "main"
code --install-extension ms-vscode-remote.remote-containers --profile "main"
code --install-extension ms-vscode.remote-server --profile "main"
code --install-extension ms-vscode.remote-explorer --profile "main"
code --install-extension ms-azuretools.vscode-docker --profile "main"

# Icons (keep Material; drop vscode-icons)
code --install-extension PKief.material-icon-theme --profile "main"
code --install-extension PKief.material-product-icons --profile "main"

# Build tools (Makefile not used; skip Makefile Tools)

# IntelliCode API Usage Examples (real-world API snippets in-editor)
code --install-extension VisualStudioExptTeam.intellicode-api-usage-examples --profile "main"

# Code Runner (one-shot run scripts across many langs)
code --install-extension formulahendry.code-runner --profile "main"

# Rainbow CSV (colorized columns + CSV helpers)
code --install-extension mechatroner.rainbow-csv --profile "main"

# Mermaid for Markdown/Notebooks (keeps Mermaid current)
code --install-extension bierner.markdown-mermaid --profile "main"

# Image preview (inline gutter/hover previews of image links)
code --install-extension kisstkondoros.vscode-gutter-preview --profile "main"

# Paths & imports QoL (tiny, useful)
code --install-extension christian-kohler.path-intellisense --profile "main"
code --install-extension christian-kohler.npm-intellisense --profile "main"

# Python: fast lint/format (ruff) – replaces/augments black/flake8/isort
code --install-extension charliermarsh.ruff --profile "main"

# TOML (pyproject/go toolchains use TOML a lot)
code --install-extension tamasfe.even-better-toml --profile "main"

# HTML tag QoL (IntelliJ-like paired tag ops)
code --install-extension formulahendry.auto-rename-tag --profile "main"
code --install-extension formulahendry.auto-close-tag --profile "main"

# GitHub PRs/Issues panel (JetBrains-like VCS integration)
code --install-extension GitHub.vscode-pull-request-github --profile "main"

```

and settings.json:

```json
{
  // Theme & Icons
  "workbench.colorTheme": "GitHub Dark Default",
  "workbench.iconTheme": "material-icon-theme",
  "workbench.productIconTheme": "material-product-icons",

  // Layout / UX
  "workbench.activityBar.location": "top",
  "editor.minimap.enabled": false,
  "editor.inlayHints.enabled": "on",
  "editor.smoothScrolling": true,
  "editor.stickyScroll.enabled": true,
  "breadcrumbs.enabled": true,

  // Save / format
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 700,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit",
    "source.fixAll.eslint": "explicit"
  },

  // Python / Jupyter
  "python.analysis.typeCheckingMode": "basic",
  "python.testing.pytestEnabled": true,
  "notebook.lineNumbers": "on",
  "notebook.output.textLineLimit": 2000,
  "notebook.output.scrolling": true,

  // Go
  "gopls": {
    "ui.semanticTokens": true,
    "ui.completion.usePlaceholders": true
  },

  // YAML
  "yaml.schemaStore.enable": true,
  "yaml.format.enable": true,
  "yaml.validate": true,

  // Markdown
  "markdown.updateLinksOnFileMove.enabled": "always",

  // Git (built-in)
  "git.autoStash": true,
  "git.autofetch": true,
  "git.pruneOnFetch": true,
  "git.enableSmartCommit": true,
  "git.confirmSync": false,
  "git.mergeEditor": true,
  "git.blame.editorDecoration.enabled": true,
  "git.blame.statusBarItem.enabled": true,

  // Terminal & files
  "terminal.integrated.scrollback": 10000,
  "search.useIgnoreFiles": true,
  "files.exclude": {
    "**/.DS_Store": true,
    "**/.idea": true,
    "**/node_modules": true,
    "**/dist": true,
    "**/build": true,
    "**/.pytest_cache": true,
    "**/__pycache__": true,
    "**/.mypy_cache": true,
    "**/.ruff_cache": true,
    "**/.venv": true
  },

  // Tag rename/close without extensions
  "editor.linkedEditing": true,

  // Error Lens
  "errorLens.enabledDiagnosticLevels": ["warning", "info", "error"],
  "errorLens.messageEnabled": false,

  // --- IntelliJ-ish editor behavior ---
  "workbench.editor.enablePreview": false, // open files as real tabs, not preview
  "editor.inlineSuggest.enabled": true, // lightweight inline hints (pairs well with Copilot)
  "editor.cursorSurroundingLines": 5,
  "editor.guides.bracketPairs": "active",
  "editor.bracketPairColorization.enabled": true,

  // --- Save / format (language-scoped defaults) ---
  "[javascript]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[typescript]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[json]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[jsonc]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[markdown]": { "editor.defaultFormatter": "DavidAnson.vscode-markdownlint" },
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },

  // --- Explorer: file nesting ---
  "explorer.fileNesting.enabled": true,
  "explorer.fileNesting.patterns": {
    "*.ts": "${capture}.test.ts, ${capture}.spec.ts, ${capture}.d.ts, ${capture}.map",
    "*.tsx": "${capture}.test.tsx, ${capture}.spec.tsx, ${capture}.map",
    "*.js": "${capture}.test.js, ${capture}.spec.js, ${capture}.map",
    "*.go": "${capture}_test.go",
    "README.md": "CHANGELOG.md, CONTRIBUTING.md, LICENSE*",
    "package.json": "package-lock.json, yarn.lock, pnpm-lock.yaml, .npmrc",
    "go.mod": "go.sum"
  },

  // --- Project hygiene ---
  "files.insertFinalNewline": true,
  "files.trimTrailingWhitespace": true,

  // Completions
  "github.copilot.enable": {
    "*": true,
    "plaintext": true,
    "markdown": true,
    "scminput": true
  },
  "github.copilot.nextEditSuggestions.enabled": true,
  "editor.inlineSuggest.minShowDelay": 1000,
  "editor.inlineSuggest.edits.allowCodeShifting": "always",

  // Agent Mode: on + bigger budget
  "chat.agent.enabled": true,
  "chat.agent.maxRequests": 200,
  "github.copilot.chat.agent.autoFix": true,

  "chat.tools.terminal.enableAutoApprove": true,
  "chat.tools.terminal.autoApprove": {
    // Keep these blocked
    "curl": false,
    "wget": false,
    "chmod": false,
    "chown": false,
    "git": false
  },

  // Let Copilot answer terminal prompts on its own
  "chat.tools.terminal.autoReplyToPrompts": true,

  // Auto-accept edit suggestions after a short delay (ms)
  "chat.editing.autoAcceptDelay": 100,

  // Give Copilot more context for better autonomous changes
  "github.copilot.chat.codesearch.enabled": true,
  "github.copilot.chat.codeGeneration.useInstructionFiles": true,
  "chat.useAgentsMdFile": true,
  "github.copilot.chat.editor.temporalContext.enabled": true
}
```

---

## Reference: Notes & Snippets

### Install locations worth knowing

- **mise** selects language/tool versions; it does not host packages itself.
- **Go** `go install …` drops binaries in `~/go/bin` (or `$GOBIN`), compiled with Go **1.25** (managed by mise).
- **uv (global tools)** installs shims in `~/.local/bin` with tool data in `~/Library/Application Support/uv/tools/...`.
- **uv (per-project)** uses `uv venv` + `uv sync` in `./.venv`, leveraging Python from mise.

### Go modernization (optional)

Modernize analyzes code and suggests adopting newer Go idioms and features.

- Review suggestions: `modernize ./...`
- Apply in place: `modernize -w ./...`
- Via tasks: `mise run modernize` or `mise run modernize-apply`

#### mise.toml

```toml
# mise.toml
[tools]
python = "3.14"
golang = "1.25"

[env]
# Put simple env vars here
PIP_DISABLE_PIP_VERSION_CHECK = "1"

[tasks.bootstrap]
description = "First-time setup: venv + deps + git hooks"
run = '''
if [ ! -d ".venv" ]; then
  uv venv
fi
uv sync
uv run pre-commit install -f --install-hooks
'''

[tasks.test]
description = "Run Python tests (pytest)"
run = "uv run pytest -q"

[tasks.test-go]
description = "Run Go tests"
run = "go test ./..."

[tasks.precommit]
run = "uv run pre-commit run --all-files"

[tasks.fmt]
description = "Format code (ruff + gofumpt)"
run = '''
ruff format .
gofumpt -w .
'''

[tasks.lint]
description = "Lint (ruff + golangci-lint)"
run = '''
ruff check .
golangci-lint run
'''

[tasks.modernize]
description = "Suggest Go modernizations"
run = "modernize ./..."

[tasks.modernize-apply]
description = "Apply Go modernizations (writes)"
run = "modernize -w ./..."

[tasks.sync]
description = "Sync Python deps (uv)"
run = "uv sync"

[tasks.ci]
run = '''
mise run fmt
mise run lint
mise run test
mise run test-go
'''
```

Usage:

- First time: `mise install` then `mise run bootstrap`
- Later: `mise run test` and `mise run precommit`
- If you use hooks: you may need `mise trust` once to allow hooks
- Go modernization: `mise run modernize` (review) or `mise run modernize-apply` (apply)

#### `pyproject.toml` (Ruff formatting & linting)

```toml
[project]
name = "yourpkg"
version = "0.1.0"
requires-python = ">=3.14"

[tool.ruff]
line-length = 100
target-version = "py314"

[tool.ruff.format]
quote-style = "double"

[tool.ruff.lint]
select = ["E","F","I","UP","B","C90","PERF","N","RUF"]
ignore = []
```

#### .pre-commit-config.yaml

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.0
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: https://github.com/golangci/golangci-lint
    rev: v2.6.0
    hooks:
      - id: golangci-lint

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.3
    hooks:
      - id: gitleaks

```

#### `.golangci.yml` (compact defaults)

```yaml
version: "2"

run:
  tests: true
  modules-download-mode: readonly
  go: "1.25"

linters:
  default: none
  enable:
    - govet
    - staticcheck
    - errcheck
    - ineffassign
    - unused
    - revive
  exclusions:
    generated: lax
    presets:
      - std-error-handling
      - common-false-positives

issues:
  new: true
  new-from-merge-base: main
  max-issues-per-linter: 0
  max-same-issues: 0

formatters:
  enable:
    - gofumpt
  # Optional: uncomment and set your module for stricter formatting
  # settings:
  #   gofumpt:
  #     module-path: github.com/yourorg/yourrepo
```

### Cheatsheet

```bash
# =========
# Navigation & history — zoxide, atuin, fzf
# =========
z foo                # jump to a directory you've visited matching "foo" (zoxide)
zi proj              # interactive dir jump (zoxide) with fzf UI
# history: fuzzy search across all shells (atuin). Try: Ctrl-R, then type
atuin search "docker run"    # non-interactive history search

# =========
# Find & search — ripgrep, fd, fzf
# =========
rg -n "TODO|FIXME"                    # fast code search with line numbers
fd -t d src                           # list directories under ./src
# open a ripgrep match in $EDITOR via fzf (preview on the right)
rg --line-number --no-heading --color=always 'TODO|FIXME' \
| fzf --ansi --delimiter : \
      --preview 'bat --style=numbers --color=always --highlight-line {2} {1}' \
| awk -F: '{print "+"$2" "$1}' \
| xargs -r ${EDITOR:-vim}

# =========
# Listing & viewing — eza, bat, less
# =========
ll                                   # long view with git info (alias to eza)
lt                                   # small tree (alias to eza -T -L 2)
bat README.md                        # pretty file view with syntax highlighting
less -R +G big.log                   # open at end, keep ANSI colors

# =========
# JSON/YAML — jq, yq
# =========
curl -s https://httpbin.org/get | jq '.headers."User-Agent"'
yq '.spec.template.spec.containers[].image' k8s/deploy.yaml

# =========
# Git & GitHub — git, delta, gh
# =========
git log --oneline --graph --decorate -20 | less -R
git diff                              # rendered with delta (pager config)
gh repo clone owner/repo
gh pr create --fill --draft && gh pr view --web

# =========
# Per-project env & tools — mise, uv
# =========
mise use -g python@3.14 golang@1.25  # set global toolchains
mise run bootstrap                   # project setup (venv + deps + hooks)
mise run fmt && mise run lint        # format and lint via tasks

# uv basics (project-local Python)
uv venv                              # create .venv in the project
uv sync                              # install/update deps from pyproject/lock into .venv
uv run pytest -q                     # run in the project's .venv
ruff check .                         # use global ruff (via mise or brew)
source .venv/bin/activate            # optional: activate venv for interactive shell

# =========
# System monitors — btop, duf, dust, procs
# =========
btop                                  # interactive CPU/Mem/Proc/Net dashboard
duf                                   # mounted disks usage (human-friendly)
dust -r . | head                      # "du" but readable, largest dirs first
procs --watch 2                       # modern 'ps' with live refresh

# =========
# HTTP & downloads — httpie, wget, openssl
# =========
http GET https://api.github.com/repos/owner/repo
http POST https://httpbin.org/post hello=world
wget -qO artifact.tgz https://example.com/build.tgz
openssl dgst -sha256 artifact.tgz     # verify checksum

# =========
# Secrets — age, sops (with age)
# =========
age-keygen -o ~/.config/age/key.txt
export SOPS_AGE_KEY_FILE=~/.config/age/key.txt
sops -e -i secrets.yaml               # edit+encrypt in place
sops -d secrets.yaml > secrets.clear.yaml
```
