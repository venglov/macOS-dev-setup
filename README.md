# Unix setup

A CLI workstation: shared dotfiles, one macOS Brewfile, and the commands below.
No custom installer, package profiles, automatic services, or login-shell changes.

- `dotfiles/` — Git, zsh with Zimfw, mise, Starship and Atuin; Ghostty settings on macOS.
- `Brewfile` — the macOS CLI tools, including the previously optional tools.
- `.chezmoiroot` — tells chezmoi to manage only `dotfiles/` in this checkout.
- [CLI cheatsheet](docs/cheatsheet.md) — alternatives to standard commands and examples.

## Shared Unix base

| Purpose | Tools |
| --- | --- |
| Configuration and projects | Git, chezmoi, mise |
| Shell, prompt and history | Zimfw, Starship, Atuin |
| Search and navigation | fzf, fd, ripgrep, zoxide |
| Diffs and structured data | Delta, jq |

**On a fresh Mac, do [macOS preparation](#macos-preparation) first.** On Linux,
install these tools using your distribution's packages or their official releases,
then clone this repository. Homebrew and systemd are not required by the dotfiles.
Package names can differ: the shell expects `fd`, `rg` and `delta` on PATH.

Use Git 2.35+, chezmoi 2.x, a current mise and fzf 0.48+. The optional shell config
uses zsh 5.9; other shells can use the Git/mise configs without adopting zsh.
This setup uses standard `~/.config` paths and `ZDOTDIR=$HOME`. Run as your own
user, without sudo. Other BSD/Unix systems need tool compatibility checked first.

### Apply dotfiles

From your local checkout:

```sh
chezmoi init --source "$PWD"
chezmoi diff
```

Initialization saves this checkout as the source and asks whether to manage zsh.
It does not apply dotfiles. If you already use chezmoi, merge these files into your
existing source instead of replacing its configuration.

Review the diff and back up the existing files it lists before continuing.
Chezmoi is not a backup service; use your normal home backup or Time Machine.
Keep local changes you need by editing the source before applying.

```sh
chezmoi apply
chezmoi verify
```

Repeat `diff` → `apply` after changes. An unchanged source can be reapplied safely.
To undo a source change, revert it in Git, review the diff, and apply again.
To recover your pre-setup files, restore your backup. Disabling zsh in
`chezmoi edit-config` stops managing its files; it does not remove existing ones.
[Chezmoi's workflow](https://www.chezmoi.io/user-guide/command-overview/).

### Shell behavior

`.zshenv` sets only EDITOR/PAGER defaults. `.zprofile` handles login PATH and
Homebrew on macOS. `.zshrc` contains interactive integrations and completions.
Use the system zsh on macOS with Zimfw. Starship supplies the prompt; no patched font is required.

- **Ctrl-R:** Atuin history. Enter puts a selection on the command line for review.
- **Ctrl-T / Alt-C:** fzf file / directory selection. Its Ctrl-R binding is disabled.
- **`z project`:** jump with zoxide. `cd`, `ls`, `cat`, `grep`, etc. stay unchanged.
- Atuin is local-only by default: no sync, update check or daemon. Import old history
  with `atuin import auto` only if wanted; account creation and sync are separate.

Zim's Git module supplies uppercase aliases such as `G`, `Gws` and `Gwd`.
The old aliases replacing `ls`, `cat`, `grep`, `find`, etc. are not installed;
use the alternatives by name as shown in the [cheatsheet](docs/cheatsheet.md).
If your terminal's Option key produces
characters instead of Alt-C, adjust its modifier settings or use `fd` and `fzf` directly.
[Bindings: fzf](https://github.com/junegunn/fzf#setting-up-shell-integration),
[Atuin](https://docs.atuin.sh/latest/configuration/key-binding/).

### Zim setup

The Brewfile installs Zimfw, zsh-completions, autosuggestions and syntax highlighting.
After applying dotfiles, install the modules declared in `~/.zimrc`:

```sh
zsh -lic 'zimfw install'
```

Then open a new terminal tab. Zim provides archive helpers, Git aliases, input
bindings, terminal titles and fzf-tab completion. It loads the Homebrew copies of
autosuggestions and syntax highlighting on macOS. On Linux it downloads those
two plugins alongside the other modules. See [Zim installation](https://zimfw.sh/docs/install/).
If your Linux package manager does not provide Zim, install its manager first:

```sh
mkdir -p "$HOME/.zim"
curl --fail --location --output "$HOME/.zim/zimfw.zsh" \
  https://github.com/zimfw/zimfw/releases/download/v1.20.1/zimfw.zsh
```

Module installation needs network access. Run `zimfw install` after editing the
managed `.zimrc` and applying it; use `zimfw update` to update downloaded modules.
Ordinary shell startup only loads the generated `~/.zim/init.zsh`; it does not
download or update anything. Before the first install the base shell still works.
Homebrew updates the manager and the two packaged plugins on macOS.

## macOS preparation

Use a native terminal on Apple Silicon. Homebrew uses `/opt/homebrew` there and
`/usr/local` on Intel. This route targets macOS 14+; Intel is best effort under
[Homebrew's current support policy](https://docs.brew.sh/Installation).
Rosetta is only needed for an app that actually requires it.

1. Run `xcode-select --install` and finish the Command Line Tools dialog.
2. Install Homebrew using its [official instructions](https://docs.brew.sh/Installation).
   Review the installer before running it. Keep its installation separate from dotfiles.
3. Add Homebrew to the current terminal session:

```sh
eval "$(/opt/homebrew/bin/brew shellenv zsh)"  # Apple Silicon
# Intel: use /usr/local/bin/brew instead.
```

4. Get the repository and install the CLI tools:

```sh
git clone https://github.com/venglov/macOS-dev-setup.git
cd macOS-dev-setup
brew bundle install --no-upgrade --file=Brewfile
brew install --cask ghostty
```

Continue with [Apply dotfiles](#apply-dotfiles) and [Zim setup](#zim-setup), then open a new Ghostty tab.
`--no-upgrade` avoids routine upgrades on reruns; Homebrew can still update a
required dependency when installing a new package. [Bundle reference](https://docs.brew.sh/Brew-Bundle-and-Brewfile).

### Included CLI tools and optional apps

All tools in this table are installed by the Brewfile. There are no extra profiles.

| Tool | When useful |
| --- | --- |
| `uv` | Python environments and project dependencies; Python itself stays in mise |
| `bat`, `eza` | File previews and directory listings, called by their own names |
| `tmux` | SSH and long sessions; start it explicitly |
| `btop`, `duf`, `dust`, `procs`, `watch` | Processes, disk usage and repeated command output |
| `cmake`, `ninja`, `pkgconf`, `make` | Projects needing more than Apple CLT; GNU Make is `gmake` |
| `neovim`, `lazygit` | Terminal editor / Git UI |
| `hyperfine`, `watchexec`, `just` | Benchmarking, file watching, or a project with a Justfile |
| `zimfw`, `zsh-completions`, `zsh-autosuggestions`, `zsh-syntax-highlighting` | Shell modules, completion, suggestions and highlighting |
| `gh`, `age`, `sops` | GitHub CLI or a specific secrets workflow |
| `yq`, `httpie`, `wget` | YAML queries, HTTP APIs and downloads |
| `openssl@3`, `sqlite`, `sqlc`, `tokei`, `less` | Crypto/TLS tooling, SQL, code generation, source statistics and paging |

For GUI apps, the installation source is **Homebrew Cask**. Select apps separately
with `brew install --cask NAME`; the Brewfile contains no GUI apps.

| Cask | Manual setup |
| --- | --- |
| `ghostty` | Main terminal; config is `~/.config/ghostty/config` |
| `visual-studio-code` | Enable the `code` command; choose language extensions |
| `orbstack` | Review licensing, launch once and enable Docker integration |
| `raycast` | Choose hotkey and permissions; check architecture support |
| `obsidian` | Choose a vault and sync policy |

OrbStack provides Docker tooling: do not add a second Docker CLI by default.
After launching it, check `docker context show`, `docker version` and
`docker compose version`. [OrbStack documentation](https://docs.orbstack.dev/docker/).
For Ghostty, check for an older config in `~/Library/Application Support/com.mitchellh.ghostty/`
before keeping two competing files. [Config locations](https://ghostty.org/docs/config).

For VS Code, keep Workspace Trust and tool approvals enabled. Install extensions
per project/language instead of a large global list; let extension dependencies
supply companions such as Pylance. Do not copy old auto-approve, auto-reply or
auto-accept settings. [VS Code security](https://code.visualstudio.com/docs/agents/run/security).

## Git and SSH

Git defaults live in `~/.config/git/config`. Your existing `~/.gitconfig` has higher
priority and is not overwritten. Create or edit that exact file for your identity:

```sh
git config --file "$HOME/.gitconfig" user.name "Your Name"
git config --file "$HOME/.gitconfig" user.email "you@example.com"
git config --file "$HOME/.gitconfig" --edit
```

Keep private overrides there or in `~/.config/git/local`. On a fresh home,
`git config --global --edit` would open the managed `~/.config/git/config` instead
if `~/.gitconfig` does not exist; a later chezmoi apply could overwrite those edits.
[Git config file selection](https://git-scm.com/docs/git-config#Documentation/git-config.txt---global).

Delta is a pager, not a `diff.tool`. No global `core.ignorecase` or `core.fileMode`
is set; Git should detect these per repository. Global ignore covers only macOS
litter, leaving `.vscode`, dependencies and build outputs to each project's `.gitignore`.
If migrating old settings, use `git config --show-origin --get KEY` to find overrides.

For macOS SSH, reuse an existing key or create a passphrase-protected key with
`ssh-keygen -t ed25519`; never overwrite an existing key. Use the session's agent
instead of starting another one in every shell. In your own `~/.ssh/config`, add
or adjust a host block using your actual key path:

```sshconfig
Host github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    AddKeysToAgent yes
    UseKeychain yes
```

Use `UseKeychain` only on macOS. Load the key with
`/usr/bin/ssh-add --apple-use-keychain ~/.ssh/id_ed25519`, register its public key
as an authentication key, and test `ssh -T git@github.com`.
Verify a new host fingerprint against [GitHub's published fingerprints](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints).
GitHub returns exit code 1 even after successful authentication because it offers no shell.

SSH signing is a separate opt-in. Register a signing key with your Git host, then
set `gpg.format=ssh` and `user.signingKey` to its `.pub` path in your local Git config.
Keep the private key loaded in your agent. For local verification, set
`gpg.ssh.allowedSignersFile` to a file containing your real email and public key:
`EMAIL namespaces="git" ssh-ed25519 PUBLIC_KEY`. Test a signed commit with
`git log -1 --show-signature` in a scratch repository before enabling
`commit.gpgSign=true`. [Signing setup](https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key).

## Projects and CLI tips

### Runtimes, tasks and agents

Pin only the runtimes a project uses, e.g. `mise use --pin node@lts` in that project.
Review and commit its `mise.toml`. The shared config enables mise's paranoid mode:
inspect project tasks/configs before `mise trust ./mise.toml`, then `mise install`.
[Trust behavior](https://mise.jdx.dev/paranoid.html).

```sh
mise exec -- node --version  # Project runtime, no interactive shell needed
mise run test               # Run a task defined by the project
```

Agents and CI need mise on PATH and the project's working directory; they must
not depend on `.zshrc`. On Apple Silicon, `/opt/homebrew/bin/mise exec -- …` is an
explicit entry point. Use the installed path on other systems.

For Python, select Python with mise and dependencies with uv. Add pre-commit and
Ruff to the project's dev dependencies with `uv add --dev pre-commit ruff`, then
commit `pyproject.toml` and `uv.lock`. Use `uv run`, not a separate global tool install:

```sh
mise exec -- uv sync --locked --no-python-downloads
mise exec -- uv run --locked pre-commit install       # After reviewing the hooks
mise exec -- uv run --locked ruff format --check .    # CI: check without rewriting
mise exec -- uv run --locked ruff format .            # Local: explicitly reformat
```

Keep tokens, private keys, `.env` secrets and history databases out of Git and
chezmoi. Use Keychain or a secret manager; history filters and gitignore are not
security boundaries. [uv project workflow](https://docs.astral.sh/uv/concepts/projects/sync/).

### Everyday commands

```sh
rg -n 'TODO|FIXME' src                  # Search project contents
fd --type f --extension go             # Find files, respecting ignore rules
fd --type f --print0 | fzf --read0 --print0  # NUL-delimited selection for scripts
z project                             # Jump to a visited directory
zi                                    # Choose a visited directory with fzf
atuin search 'git rebase'              # Search local command history
jq '.scripts' package.json            # Inspect JSON
git diff                              # Delta renders the diff
git log --oneline --graph -20
```

Quote paths. Avoid splitting filenames with `awk -F:` or whitespace-based `xargs`;
for arbitrary filenames, keep NUL delimiters throughout a pipeline. In Ghostty,
Ctrl-T inserts selected paths into the command line; `z` never replaces `cd`.

More installed tools: `bat README.md`, `eza -la`, `btop`, `dust .`,
`hyperfine 'your-command'`, or `watchexec -e go -- go test ./...`.
For long sessions use `tmux new -s work`, detach with Ctrl-B then D, and return
with `tmux attach -t work`.

## Updates and checks

```sh
brew update
brew upgrade --formula                    # All installed CLI, no GUI
brew upgrade --cask --greedy ghostty        # Only the named GUI app; close it first
brew bundle check --no-upgrade --file=Brewfile
zimfw update                              # Downloaded Zim modules; in interactive zsh
chezmoi diff
chezmoi verify
```

App updaters may also update their own bundles; do not disable security updates.
Review repository changes before applying dotfiles again. Brewfile records the tool
set, not exact binary versions; pin project dependencies separately. No automatic
cleanup, service startup or OS preference changes are part of this setup.

CI renders and reapplies dotfiles in a temporary home on macOS and Linux. It checks
Git identity persistence, zsh syntax and login Homebrew initialization on macOS.
It does not install Zim modules or exercise GUI/Keychain integration.

## Later platforms

Steam Deck needs a SteamOS-specific plan: verify writable paths and persistence
across updates before system package changes; [Valve warns about packages outside Flatpak](https://help.steampowered.com/en/faqs/view/671A-4453-E8D2-323C).
A Proxmox hypervisor should get only necessary administration tools, not a desktop
stack. Ubuntu VM and LXC guests need separate provisioning and privilege checks.
No installers for these platforms are included, and user dotfiles are never meant
for automatic application to root.
