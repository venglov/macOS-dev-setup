#!/bin/sh
# Sourced by bootstrap/verify. All Homebrew assumptions stay in this file.

macos_environment() {
    [ "$(uname -s)" = Darwin ] || die 'This command is macOS-only.'
    need sysctl
    mac_version=$(sw_vers -productVersion)
    mac_major=${mac_version%%.*}
    case $mac_major in ''|*[!0-9]*) die 'Cannot determine macOS version.' ;; esac
    [ "$mac_major" -ge 14 ] || die 'This setup requires macOS 14 or newer; see docs/macos.md.'
    if [ "$(sysctl -in sysctl.proc_translated 2>/dev/null || :)" = 1 ]; then
        die 'Quit the Rosetta terminal and use a native Apple Silicon session.'
    fi
    case $(uname -m) in
        arm64) BREW=/opt/homebrew/bin/brew ;;
        x86_64)
            printf 'Intel: best effort only; Homebrew classifies it as Tier 3.\n' >&2
            BREW=/usr/local/bin/brew ;;
        *) die 'Unsupported macOS architecture' ;;
    esac
    if ! xcode-select -p >/dev/null 2>&1 || ! xcrun --find clang >/dev/null 2>&1; then
        die 'Install Command Line Tools with xcode-select --install, finish the dialog, then retry.'
    fi
    [ -x "$BREW" ] || die "Homebrew missing at $BREW. Follow docs/macos.md, then retry."
    # This affects this process and its children only; no startup file writes.
    brew_environment=$("$BREW" shellenv sh) || die 'Homebrew shellenv failed.'
    eval "$brew_environment"
    export HOMEBREW_NO_ANALYTICS=1 HOMEBREW_NO_AUTO_UPDATE=1
    export HOMEBREW_NO_INSTALL_CLEANUP=1 HOMEBREW_NO_INSTALL_UPGRADE=1
}

select_profiles() {
    profiles=core
    for profile in "$@"; do
        case $profile in ''|*[!a-z0-9-]*) die "Invalid profile: $profile" ;; esac
        [ -f "$ROOT/manifests/macos/cli/$profile.Brewfile" ] || die "Unknown profile: $profile"
        case " $profiles " in *" $profile "*) ;; *) profiles="$profiles $profile" ;; esac
    done
}

cli_packages() {
    action=$1
    shift
    select_profiles "$@"
    macos_environment
    printf 'CLI profiles: %s\n' "$profiles"
    [ "$action" != update ] || "$BREW" update
    for profile in $profiles; do
        manifest=$ROOT/manifests/macos/cli/$profile.Brewfile
        case $action in
            install) "$BREW" bundle install --no-upgrade --file="$manifest" ;;
            check) "$BREW" bundle check --no-upgrade --file="$manifest" ;;
            update)
                formulae=$("$BREW" bundle list --brews --file="$manifest")
                printf '%s\n' "$formulae" | while IFS= read -r formula; do
                    [ -n "$formula" ] || continue
                    if "$BREW" list --formula --versions "$formula" >/dev/null 2>&1; then
                        "$BREW" upgrade --formula "$formula"
                    else
                        printf 'Not installed; skipped: %s\n' "$formula"
                    fi
                done
                ;;
        esac
    done
}

gui_packages() {
    action=${1:-list}
    [ "$#" -eq 0 ] || shift
    catalog=$ROOT/manifests/macos/gui.tsv
    case $action in
        list) [ "$#" -eq 0 ] || die 'gui list takes no arguments'; cat "$catalog"; return ;;
        install|update) [ "$#" -gt 0 ] || die 'Name the apps explicitly; use macos gui list.' ;;
        *) die 'Use macos gui list, install or update.' ;;
    esac
    # Validate the whole request before any installation starts.
    for app in "$@"; do
        case $app in ''|*[!a-z0-9-]*) die "Invalid app: $app" ;; esac
        awk -F '\t' -v app="$app" 'NR > 1 && $1 == app {found=1} END {exit !found}' "$catalog" || die "Unknown app: $app"
    done
    macos_environment
    [ "$action" != update ] || "$BREW" update
    for app in "$@"; do
        cask=$(awk -F '\t' -v app="$app" '$1 == app {print $2}' "$catalog")
        if [ "$action" = install ]; then
            if "$BREW" list --cask --versions "$cask" >/dev/null 2>&1; then
                printf 'Already installed: %s\n' "$app"
            else
                "$BREW" install --cask "$cask"
            fi
        elif "$BREW" list --cask --versions "$cask" >/dev/null 2>&1; then
            # Explicitly named apps only; includes casks with vendor updaters.
            "$BREW" upgrade --cask --greedy "$cask"
        else
            printf 'Not installed; skipped: %s\n' "$app"
        fi
    done
}

macos_command() {
    action=${1:-help}
    [ "$#" -eq 0 ] || shift
    case $action in
        prepare) [ "$#" -eq 0 ] || die 'prepare takes no arguments'; macos_environment; printf 'macOS prerequisites available.\n' ;;
        install|update) cli_packages "$action" "$@" ;;
        gui) gui_packages "$@" ;;
        *) die 'Use macos prepare, install, update or gui.' ;;
    esac
}
