# macOS development setup

A manual setup for development, everyday use and terminal work. Follow the steps
in order on a fresh Mac; use the [cheatsheet](docs/cheatsheet.md) afterwards.

- [Brewfile](Brewfile) — everyday CLI tools; [Brewfile.optional](Brewfile.optional) — extras.
- `dotfiles/` — Git, zsh/Zimfw, mise, Starship, Atuin and Ghostty configurations.
- `.chezmoiroot` — limits chezmoi to `dotfiles/` in this checkout.
- [Other platforms](docs/platforms.md) — shared dotfiles on Linux and platform limits.

## 1. Prepare macOS

Use a native terminal on Apple Silicon and check
[Homebrew's supported macOS versions](https://docs.brew.sh/Installation).
Intel support is best effort. Install Rosetta only when an app requires it.

Review these settings manually; choose the comfort settings to suit you.

| Where | Setup |
| --- | --- |
| General → Software Update | Install updates; keep automatic security updates enabled |
| Privacy & Security → FileVault | Enable it and keep the recovery method accessible outside this Mac |
| Touch ID & Password; Lock Screen | Register a fingerprint; require a password immediately after locking |
| Apple Account → iCloud | Enable Find My Mac; choose what to sync |
| General → Sharing; Login Items & Extensions | Enable only services and startup apps you use |
| Keyboard | Choose layouts, language-switch shortcut and key-repeat speed; avoid hotkey conflicts |
| Trackpad; Desktop & Dock | Set gestures, scrolling and Dock behavior to taste |
| Finder → Settings → Advanced; View menu | Show filename extensions and the path bar |

[FileVault reference](https://support.apple.com/guide/mac-help/protect-data-on-your-mac-with-filevault-mh11785/mac).

### Optional: Touch ID for sudo

On macOS 14+ with Touch ID configured, use Apple's local PAM file:

```sh
sudo cp -n /etc/pam.d/sudo_local.template /etc/pam.d/sudo_local
sudoedit /etc/pam.d/sudo_local
```

`cp -n` preserves an existing file. Uncomment this line (or add it once if absent):

```text
auth       sufficient     pam_tid.so
```

Test in a local terminal, outside tmux or SSH:

```sh
sudo -k
sudo -v
```

Touch ID should be offered when available; password authentication remains the
fallback. `sudo_local` survives system updates. To undo, comment out the same
line. Leave `/etc/pam.d/sudo` unchanged; the shipped `sudo_local.template` explains
this mechanism.

## 2. Install Homebrew and CLI tools

Run `xcode-select --install` and finish the Command Line Tools dialog. Then install
Homebrew using its [official instructions](https://docs.brew.sh/Installation),
reviewing the installer first. Add it to this terminal session:

```sh
eval "$(/opt/homebrew/bin/brew shellenv zsh)"  # Apple Silicon
# Intel: use /usr/local/bin/brew instead.
```

Clone the repository and install the base tools as your own user:

```sh
git clone https://github.com/venglov/macOS-dev-setup.git
cd macOS-dev-setup
brew bundle install --no-upgrade --file=Brewfile
```

The base covers Git/GitHub, dotfiles, runtime management, shell integrations, search,
navigation, file/data inspection and basic monitoring. Both Brewfiles explain
each package. For extras, install individual tools or the whole optional set:

```sh
brew install tmux                         # Example: just one extra
# Or install all optional tools:
brew bundle install --no-upgrade --file=Brewfile.optional
```

Optional tools include terminal editors/UIs, HTTP clients, SQL tools, age/SOPS,
build tools and project automation. Removing a package from a Brewfile does not
uninstall it. `--no-upgrade` avoids routine upgrades on reruns; new dependencies
can still require upgrades. [Bundle reference](https://docs.brew.sh/Brew-Bundle-and-Brewfile).

## 3. Install applications

Install the terminal, then choose any other apps you need:

```sh
brew install --cask ghostty
# Example: brew install --cask visual-studio-code orbstack
```

| Cask | Manual setup |
| --- | --- |
| `ghostty` | Main terminal; configured in the next step |
| `visual-studio-code` | Enable the `code` command; see [IDE setup](docs/cheatsheet.md#vs-code-and-project-runtimes) |
| `orbstack` | Review licensing, launch once and enable Docker integration |
| `raycast` | Choose a hotkey and grant the permissions its features need |
| `obsidian` | Choose a vault and sync policy |

OrbStack supplies Docker tooling. After launching it, check `docker context show`,
`docker version` and `docker compose version`.
[OrbStack documentation](https://docs.orbstack.dev/docker/).

## 4. Apply dotfiles and start the shell

From the repository checkout:

```sh
chezmoi init --source "$PWD"
chezmoi diff
```

Initialization saves this checkout as the source and asks whether to manage zsh;
choose yes for the shell setup below. If you already use chezmoi, merge these files
into your existing source instead of replacing its configuration.

Review the diff and back up the files it lists with Time Machine or your usual
backup. Keep local changes you need by editing the source before applying.
For Ghostty, check for an older config in
`~/Library/Application Support/com.mitchellh.ghostty/` to avoid competing settings.
[Config locations](https://ghostty.org/docs/config).

```sh
chezmoi apply
chezmoi verify
zsh -lic 'zimfw install'    # If you chose to manage zsh; needs network access
```

Open a new Ghostty tab. The setup uses system zsh, standard `~/.config` paths and
`ZDOTDIR=$HOME`. `.zshenv` sets EDITOR/PAGER defaults, `.zprofile` handles login PATH,
and `.zshrc` loads interactive integrations.

| Action | Behavior |
| --- | --- |
| Ctrl-R | Atuin history; Enter inserts a selection for review, another Enter runs it |
| Ctrl-T / left Option-C | fzf file / directory selection |
| Tab | fzf-tab completion |
| Right arrow at end of line | Accept an autosuggestion |
| Ctrl-X, then Ctrl-E | Edit the command line in EDITOR |
| `z project` / `zi` | Jump to a visited directory / choose one interactively |

Zim manages input bindings, fzf-tab, autosuggestions and syntax highlighting.
Homebrew owns the two packaged plugins on macOS. Ghostty handles terminal titles;
Git commands and standard utilities keep their normal names. Starship needs no
patched font. Right Option retains macOS character input.

Atuin stays local: no sync, update check or daemon. Import previous history with
`atuin import auto` if wanted. Ordinary shell startup does not install or update
Zim modules; run `zimfw install` after changing `.zimrc` and applying it.
[Zim documentation](https://zimfw.sh/docs/commands/).

For tabs, panes and SSH terminal compatibility, see
[Ghostty in the cheatsheet](docs/cheatsheet.md#ghostty-and-ssh).

## 5. Connect Git and GitHub

Keep your identity in `~/.gitconfig`; it takes precedence over the shared config:

```sh
git config --file "$HOME/.gitconfig" user.name "Your Name"
git config --file "$HOME/.gitconfig" user.email "you@example.com"
git config --show-origin --get user.email
```

Private overrides can also live in `~/.config/git/local`. Avoid editing the managed
`~/.config/git/config` directly; chezmoi can overwrite those changes.

Choose one authentication route. **HTTPS** is the shorter setup:

```sh
gh auth login --hostname github.com --git-protocol https --web
# Answer yes when asked to authenticate Git with your GitHub credentials.
gh auth status
```

For **SSH**, reuse a key or run `ssh-keygen -t ed25519` to create a passphrase-protected
key; never overwrite an existing one. Add or adjust this block in `~/.ssh/config`,
using your actual key path:

```sshconfig
Host github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    AddKeysToAgent yes
    UseKeychain yes
```

Load it into macOS's existing agent, then sign in and upload the **public** key
when prompted:

```sh
/usr/bin/ssh-add --apple-use-keychain ~/.ssh/id_ed25519
gh auth login --hostname github.com --git-protocol ssh --web
gh auth status
ssh -T git@github.com
```

Verify new host fingerprints against [GitHub's list](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints).
Success says you authenticated; exit code 1 is normal because GitHub offers no
shell. `UseKeychain` is macOS-only. [GitHub authentication](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git).

Existing clones keep their remote protocol. For this repository, switch to SSH
only if you chose that route:

```sh
git remote -v
git remote set-url origin git@github.com:venglov/macOS-dev-setup.git
```

Shared Git defaults use fast-forward-only pulls, `zdiff3` conflicts and Delta as
the pager. Identity stays local; ignore rules cover only macOS litter.
[Optional SSH commit signing](docs/cheatsheet.md#ssh-commit-signing).

## 6. Start a project and verify the setup

Use mise for project runtimes and uv for Python dependencies. The
[project recipes](docs/cheatsheet.md#first-projects) cover Python, Node and Go,
including a small Python config that makes uv use mise's interpreter.

Review project configs before `mise trust ./mise.toml`, then run `mise install`.
Paranoid mode requires renewed trust after config changes.
[Trust behavior](https://mise.jdx.dev/paranoid.html).
Keep tokens, private keys, `.env` secrets and history databases out of Git and
chezmoi; use Keychain or a secret manager.

Check once in a fresh Ghostty tab. Run Brewfile commands from this repository:

- [ ] `brew bundle check --no-upgrade --file=Brewfile` succeeds; `chezmoi verify` reports no differences.
- [ ] The shell opens without errors; Ctrl-R, Ctrl-T, left Option-C and Tab behave as above.
- [ ] `git config --show-origin --get user.email` shows your email; `gh auth status` succeeds.
- [ ] Your chosen project recipe runs; its runtime matches `mise.toml`. For Python, check the interpreter as shown in the recipe.
- [ ] If installed, VS Code uses the project's runtime and OrbStack passes the Docker checks above.
- [ ] If enabled, `sudo -k` followed by `sudo -v` offers Touch ID when available.

## Updates and dotfile changes

Run from this repository:

```sh
brew update
brew upgrade --formula                    # Installed CLI tools
brew upgrade --cask --greedy ghostty       # Close the named app first
brew bundle check --no-upgrade --file=Brewfile
# If you installed the complete optional set:
# brew bundle check --no-upgrade --file=Brewfile.optional
zimfw update                              # Downloaded modules; in interactive zsh
chezmoi diff
chezmoi verify
```

Review source changes, then repeat `chezmoi diff` → `chezmoi apply` → `chezmoi verify`.
To undo a source change, revert it in Git and apply again; to recover pre-setup
files, restore your backup. Disabling zsh in `chezmoi edit-config` stops managing
its files without removing them. [Chezmoi workflow](https://www.chezmoi.io/user-guide/command-overview/).

Brewfiles record the tool set, not exact binary versions. Pin project dependencies
separately and keep app security updates enabled. CI checks dotfile rendering,
repeat application, Git identity and zsh syntax on macOS/Linux; GUI, Keychain and
interactive integrations use the manual checklist above.
