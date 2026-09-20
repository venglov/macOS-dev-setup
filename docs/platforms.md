# Other platforms

The [main setup](../README.md) targets macOS. Shared dotfiles can also be used on
Linux; the Brewfiles and macOS settings are not a Linux installer.

Install Git 2.35+, chezmoi 2.x and current versions of mise, Starship, Atuin, fzf
(0.48+), fd, ripgrep, zoxide, Delta and jq using distro packages or official releases.
The optional shell setup uses zsh 5.9 and Zimfw. Executable names on PATH must be
`fd`, `rg` and `delta`; some distributions use different package/binary names.

Clone the repository, then follow [Apply dotfiles](../README.md#4-apply-dotfiles-and-start-the-shell).
Choose whether to manage zsh. If your package manager does not provide Zim,
install its manager before running `zimfw install`:

```sh
mkdir -p "$HOME/.zim"
curl --fail --location --output "$HOME/.zim/zimfw.zsh" \
  https://github.com/zimfw/zimfw/releases/download/v1.20.1/zimfw.zsh
```

On Linux, Zim downloads autosuggestions and syntax highlighting with its other
modules. Ghostty config and Git's macOS credential helper are excluded by chezmoi.
Keep `UseKeychain` out of Linux SSH config. Homebrew and systemd are not required;
apply user dotfiles as your own user, without sudo.

Other BSD/Unix systems need compatibility checked first. Steam Deck needs a
SteamOS-specific plan for writable paths and update persistence;
[Valve warns about packages outside Flatpak](https://help.steampowered.com/en/faqs/view/671A-4453-E8D2-323C).
A Proxmox host should get only necessary administration tools. Ubuntu VM and LXC
guests need their own provisioning; these dotfiles are not intended for root.
