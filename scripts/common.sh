#!/bin/sh
# Shared POSIX helpers. No package manager or shell integration here.
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "Required command missing: $1"; }

setup_context() {
    [ "$(id -u)" -ne 0 ] || die 'Run as the target user, without sudo or root.'
    [ -z "${SUDO_USER:-}" ] || die 'Start a normal user session, without sudo.'
    case ${HOME:-} in /*) ;; *) die 'HOME must be an absolute directory' ;; esac
    [ "$HOME" != / ] && [ -d "$HOME" ] || die 'Invalid HOME'
    # This small setup deliberately supports the standard XDG locations only.
    [ "${XDG_CONFIG_HOME:-$HOME/.config}" = "$HOME/.config" ] || die 'Custom XDG_CONFIG_HOME is not supported; see docs/common.md.'
    [ "${XDG_DATA_HOME:-$HOME/.local/share}" = "$HOME/.local/share" ] || die 'Custom XDG_DATA_HOME is not supported.'
    [ "${XDG_STATE_HOME:-$HOME/.local/state}" = "$HOME/.local/state" ] || die 'Custom XDG_STATE_HOME is not supported.'
    [ "${XDG_CACHE_HOME:-$HOME/.cache}" = "$HOME/.cache" ] || die 'Custom XDG_CACHE_HOME is not supported.'
    [ "${ZDOTDIR:-$HOME}" = "$HOME" ] || die 'Custom ZDOTDIR is not supported.'
    CONFIG=$HOME/.config/unix-setup/chezmoi.toml
    STATE=$HOME/.local/state/unix-setup
}

confirm() {
    printf 'Type %s to continue: ' "$1"
    IFS= read -r answer || die 'No confirmation; stopped.'
    [ "$answer" = "$1" ] || die 'Cancelled; destination files unchanged.'
}

# All managed paths are repository-defined, simple relative filenames. Reject
# unfamiliar paths before backup/restore; do not split paths on whitespace.
safe_relative() {
    case $1 in
        ''|/*|../*|*/../*|*/..|..|./*|*/./*|*/.|*//*|*[!a-zA-Z0-9_./-]*)
            die "Unsupported managed path: $1" ;;
    esac
}

# Do not follow symlinked parent directories into another location. Leaf links
# are backed up as links; chezmoi owns replacement of the managed leaf itself.
check_parents() {
    check_base=$1
    check_rel=$2
    while [ "$check_rel" != . ]; do
        check_rel=$(dirname -- "$check_rel")
        [ ! -L "$check_base/$check_rel" ] || die "Symlinked parent: $check_base/$check_rel"
        if [ -e "$check_base/$check_rel" ] && [ ! -d "$check_base/$check_rel" ]; then
            die "Parent is not a directory: $check_base/$check_rel"
        fi
    done
}

cm() (
    # A dedicated config/state avoids adopting another chezmoi repository.
    # Keep target permissions identical for init, diff, apply and verification.
    umask 077
    chezmoi --source "$ROOT/dotfiles" --destination "$HOME" \
        --config "$CONFIG" --persistent-state "$STATE/chezmoi-state.boltdb" \
        --no-tty --color false "$@"
)
