#!/bin/sh

dotfiles_ready() {
    need chezmoi
    [ -f "$CONFIG" ] || die 'Run ./bootstrap common init first.'
}

dotfiles_dependencies() {
    need git
    need mise
    git --version | awk 'BEGIN {ok=0} {split($3,v,"."); ok=(v[1]>2 || (v[1]==2 && v[2]>=35))} END {exit !ok}' || die 'Git 2.35+ is required.'
    if [ "$(cm execute-template '{{ .zsh }}')" = true ]; then
        need zsh
    fi
    if [ "$(cm execute-template '{{ .terminal }}')" = true ]; then
        for tool in starship atuin fzf fd rg zoxide delta; do need "$tool"; done
        fzf --zsh >/dev/null 2>&1 || die 'fzf 0.48+ is required for shell integration.'
    fi
}

managed_paths() { cm managed --include=files,symlinks --path-style=relative; }

check_targets() {
    while IFS= read -r path; do
        safe_relative "$path"
        check_parents "$HOME" "$path"
        if [ -e "$HOME/$path" ] && [ ! -f "$HOME/$path" ] && [ ! -L "$HOME/$path" ]; then
            die "Managed target is not a regular file: $path"
        fi
    done < "$1"
}

backup_targets() {
    mkdir -p "$STATE/backups"
    snapshot=$(mktemp -d "$STATE/backups/snapshot.XXXXXXXX")
    managed_paths > "$snapshot/paths"
    check_targets "$snapshot/paths"
    mkdir "$snapshot/files"
    : > "$snapshot/present"
    : > "$snapshot/absent"
    while IFS= read -r path; do
        if [ -e "$HOME/$path" ] || [ -L "$HOME/$path" ]; then
            mkdir -p "$snapshot/files/$(dirname -- "$path")"
            cp -pR -P "$HOME/$path" "$snapshot/files/$path"
            printf '%s\n' "$path" >> "$snapshot/present"
        else
            printf '%s\n' "$path" >> "$snapshot/absent"
        fi
    done < "$snapshot/paths"
    # Only a completed backup is eligible for restoration.
    : > "$snapshot/complete"
    printf 'Backup: %s\n' "$snapshot"
}

restore_targets() {
    case $1 in snapshot.*) ;; *) die 'Use the snapshot.NAME printed during apply.' ;; esac
    safe_relative "$1"
    case $1 in */*) die 'Pass a snapshot name, without directories.' ;; esac
    snapshot=$STATE/backups/$1
    [ -f "$snapshot/complete" ] || die 'No complete backup with that name.'
    for list in present absent; do
        [ -f "$snapshot/$list" ] || die 'Incomplete backup'
        check_targets "$snapshot/$list"
    done
    while IFS= read -r path; do
        check_parents "$snapshot/files" "$path"
        [ -f "$snapshot/files/$path" ] || [ -L "$snapshot/files/$path" ] || die "Missing backup: $path"
    done < "$snapshot/present"
    printf 'Restore these files (including original symlinks):\n'
    cat "$snapshot/present"
    printf 'Remove these files, which did not exist before apply:\n'
    cat "$snapshot/absent"
    confirm restore
    while IFS= read -r path; do
        mkdir -p "$HOME/$(dirname -- "$path")"
        rm -f "$HOME/$path"
        cp -pR -P "$snapshot/files/$path" "$HOME/$path"
    done < "$snapshot/present"
    while IFS= read -r path; do
        rm -f "$HOME/$path"
    done < "$snapshot/absent"
    printf 'Restored. Backup retained; empty directories and installed tools retained.\n'
}

dotfiles_command() {
    action=${1:-help}
    [ "$#" -gt 0 ] && shift
    case $action in
        init|diff|apply) [ "$#" -eq 0 ] || die 'Unexpected arguments' ;;
        restore) [ "$#" -eq 1 ] || die 'Usage: ./bootstrap common restore snapshot.NAME' ;;
        *) die 'Use common init, diff, apply or restore.' ;;
    esac
    umask 077
    check_parents "$HOME" .config/unix-setup/chezmoi.toml
    check_parents "$HOME" .local/state/unix-setup/backups/placeholder
    case $action in
        init)
            need chezmoi
            if [ -f "$CONFIG" ]; then
                printf 'Options already exist: %s\nEdit that file, then run common diff/apply.\n' "$CONFIG"
                return
            fi
            [ ! -e "$CONFIG" ] && [ ! -L "$CONFIG" ] || die 'Config path already exists.'
            mkdir -p "$(dirname -- "$CONFIG")" "$STATE"
            cm init
            printf 'Options saved. Next: ./bootstrap common diff\n'
            ;;
        diff) dotfiles_ready; cm diff --include=files,symlinks ;;
        apply)
            dotfiles_ready
            dotfiles_dependencies
            # Refuse unsafe targets before preview (e.g. a symlinked ~/.config).
            paths=$(managed_paths) || die 'Cannot enumerate managed paths.'
            printf '%s\n' "$paths" | while IFS= read -r path; do
                safe_relative "$path"
                check_parents "$HOME" "$path"
            done
            cm diff --include=files,symlinks
            if cm verify --include=files,symlinks >/dev/null 2>&1; then
                printf 'Already matches; no changes or backup needed.\n'
                return
            fi
            confirm apply
            backup_targets
            # Applying only files preserves permissions of existing directories.
            # Chezmoi requires their parents to exist in this mode.
            while IFS= read -r path; do
                mkdir -p "$HOME/$(dirname -- "$path")"
            done < "$snapshot/paths"
            cm apply --include=files,symlinks --force
            cm verify --include=files,symlinks
            printf 'Applied and verified. See docs/recovery.md for restoration.\n'
            ;;
        restore) restore_targets "$1" ;;
    esac
}
