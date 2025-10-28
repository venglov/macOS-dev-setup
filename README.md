# macOS Developer Setup (2025)

Opinionated, repeatable bootstrap for a clean macOS machine. The quickstart below is meant for copy/paste on a fresh install.

## Contents
- [Quickstart (copy/paste)](#quickstart-copy-paste)
- [Reference: Notes & Snippets](#reference-notes--snippets)

---

## Quickstart (copy/paste)

Run the blocks in order. Commands that overwrite dotfiles (`~/.zshenv`, `~/.zshrc`, `~/.zimrc`, `~/.gitignore_global`) assume a clean setup—back up existing files if you care about them.

### Step 0 — Prerequisites

```bash
xcode-select --install || true
sudo xcodebuild -license accept 2>/dev/null || true
# Apple Silicon only: install Rosetta if you need x86 binaries
sudo softwareupdate --install-rosetta --agree-to-license || true
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
  zoxide atuin direnv \
  gnu-sed coreutils gnu-tar findutils gawk watch less \
  btop duf dust procs \
  openssl@3 gnupg age sops pinentry-mac \
  make cmake ninja pkg-config \
  sqlite \
  httpie wget \
  tokei \
  mise uv \
  mas \
  codex-cli \
  ollama
```

**Optional tooling** (only if you actively use these categories):

```bash
brew install postgresql@16 redis \
  kubectl k9s helm kubectx stern \
  dive cosign trivy oras
```

Finalize `fzf` bindings:

```bash
"$(brew --prefix)/opt/fzf/install" --key-bindings --completion --no-update-rc
```

### Step 3 — Zsh with Zimfw

#### 3.1 `~/.zshenv`

```bash
cat > ~/.zshenv <<'EOF'
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
export HOMEBREW_NO_ANALYTICS=1
export EDITOR="vim"
export MANPAGER="less -R"
EOF
```

#### 3.2 Install Zimfw

```bash
curl -fsSL https://raw.githubusercontent.com/zimfw/install/master/install.zsh | zsh
```

#### 3.3 `~/.zimrc`

```bash
cat > ~/.zimrc <<'EOF'
zmodule zimfw/archive
zmodule zimfw/git
zmodule zimfw/input
zmodule zimfw/termtitle
zmodule zimfw/completion

# Theme
zmodule spaceship-prompt/spaceship-prompt --source "spaceship.zsh" --name "spaceship"

# Plugins
zmodule zsh-users/zsh-autosuggestions
zmodule zdharma-continuum/fast-syntax-highlighting kind:defer
zmodule Aloxaf/fzf-tab

zstyle ':zim' build autoload
EOF

zimfw install
zimfw build
```

#### 3.4 `~/.zshrc`

```bash
cat > ~/.zshrc <<'EOF'
setopt HIST_IGNORE_DUPS HIST_IGNORE_SPACE HIST_VERIFY SHARE_HISTORY
setopt AUTO_CD EXTENDED_GLOB INTERACTIVE_COMMENTS
bindkey -v
export KEYTIMEOUT=1

# Paths (include uv tools and Go binaries)
eval "$(/opt/homebrew/bin/brew shellenv)"
export PATH="$HOME/.local/bin:$HOME/go/bin:$PATH"

# Load Zim (static init)
source "${ZDOTDIR:-$HOME}/.zim/init.zsh"

# Prompt: Spaceship (inline overrides)
export SPACESHIP_PROMPT_ADD_NEWLINE=true
export SPACESHIP_CHAR_SYMBOL="❯ "
export SPACESHIP_PROMPT_ORDER=(time user dir host git node golang docker venv python exec_time line_sep char)

# fzf / zoxide / atuin / direnv
eval "$(zoxide init zsh)"
eval "$(atuin init zsh)"
eval "$(direnv hook zsh)"
export FZF_DEFAULT_COMMAND='rg --files --hidden --follow --glob "!.git"'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND='fd -t d .'
export BAT_THEME="OneHalfDark"
export PAGER="bat -p"

# Aliases (tree via eza -T)
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
go install github.com/go-delve/delve/cmd/dlv@latest
go install honnef.co/go/tools/cmd/staticcheck@latest
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
go install golang.org/x/vuln/cmd/govulncheck@latest
```

### Step 6 — Python fast path (`uv`)

```bash
uv tool install ruff
uv tool install pre-commit
```

### Step 7 — Git sane defaults

```bash
git config --global init.defaultBranch main
git config --global pull.rebase true
git config --global rebase.autosquash true
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
direnv --version
btop --version
```

---

## Reference: Notes & Snippets

### Ruff instead of Black

Use Ruff for both linting *and* formatting to keep the Python toolchain fast and simple. Configure it per repository in `pyproject.toml`.

### Install locations worth knowing

- **mise** selects language/tool versions; it does not host packages itself.
- **Go** `go install …` drops binaries in `~/go/bin` (or `$GOBIN`), compiled with Go **1.25** (managed by mise).
- **uv (global tools)** installs shims in `~/.local/bin` with tool data in `~/Library/Application Support/uv/tools/...`.
- **uv (per-project)** uses `uv venv` + `uv pip install` in `./.venv`, leveraging Python **3.14** from mise.

### Per-project bootstrap (mise + direnv + uv)

```bash
# .mise.toml
[tools]
python = "3.14"
golang = "1.25"

[env]
PIP_DISABLE_PIP_VERSION_CHECK = "1"
```

```bash
# .envrc
use mise
```

```bash
direnv allow
uv venv
uv pip install -e .
uv pip install ruff pytest mypy
pre-commit install
```

### SSH commit signing (no Touch ID required)

Generate an ed25519 key, store the passphrase in the macOS Keychain, and configure Git to sign with SSH.

```bash
ssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519 -C "$USER@$(scutil --get ComputerName)"
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/id_ed25519

git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

Add the public key to your Git host for verified signatures.

### Fonts for Spaceship prompt

Install a Nerd Font (e.g. **MesloLGS NF**) in your terminal profile to render prompt symbols correctly.

### Copy/paste snippets

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
select = ["E","F","I","UP","B","C90","PERF"]
```

#### `Makefile` (Go + Python helpers)

```make
.PHONY: help lint test fmt
help: ; @grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed -E 's/:.*?##/ –/'

fmt: ## format code
	@command -v ruff >/dev/null && ruff format .
	@command -v gofumpt >/dev/null && gofumpt -w .

lint: ## lint (py+go)
	@command -v ruff >/dev/null && ruff check .
	@command -v golangci-lint >/dev/null && golangci-lint run

test: ## run tests
	@command -v pytest >/dev/null && pytest -q
	@command -v go >/dev/null && go test ./...
```

#### `.golangci.yml` (compact defaults)

```yaml
run:
  timeout: 3m
linters:
  enable: [govet, staticcheck, gofumpt, revive]
issues:
  exclude-use-default: false
```
