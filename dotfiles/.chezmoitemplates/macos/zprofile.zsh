export HOMEBREW_NO_ANALYTICS=1
# Select the native prefix; this file never installs Homebrew or Rosetta.
if [[ "$MACHTYPE" == arm64 && -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv zsh)"
elif [[ "$MACHTYPE" == x86_64 && -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv zsh)"
fi
