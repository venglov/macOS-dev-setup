# Unix environment setup

Повторно запускаемая настройка пользовательского окружения после чистой установки.
Общая конфигурация + платформенные операции macOS. Имя репозитория сохранено.

## Общая часть

Начните с [правил и ограничений](docs/common.md), затем выберите
[профили](docs/profiles.md). Git, dotfiles и mise общие; zsh и terminal UX опциональны.
Полноценный bootstrap сейчас поддерживает macOS на Apple Silicon. На других Unix
общая часть требует заранее установленных инструментов; установщика ОС-пакетов нет.

```sh
./bootstrap plan
# После установки Git, chezmoi и mise средствами вашей платформы:
./bootstrap common init
./bootstrap common diff
./bootstrap common apply
./verify common
```

`apply` повторно показывает diff, ждёт слово `apply`, сохраняет резервную копию и
применяет файлы через chezmoi. При совпадении ничего не меняет.
[Восстановление и миграция](docs/recovery.md).

## Дополнения macOS

На чистой системе сначала выполните [подготовку macOS](docs/macos.md): CLT,
получение репозитория, Homebrew. Этот шаг **предшествует** общей конфигурации,
поскольку устанавливает её зависимости.

```sh
./bootstrap macos prepare
./bootstrap macos install terminal  # core + выбранный terminal UX
# Теперь common init/diff/apply из раздела выше; выберите terminal=true.
./bootstrap macos gui install ghostty
./verify macos terminal
```

Ghostty — основной терминал, системный zsh — shell, Starship — prompt,
Atuin — Ctrl-R. Стандартные команды и login shell не подменяются.
Языки, GUI, редакторы и дополнительные CLI устанавливаются только по выбору.

- [SSH authentication, Keychain и подпись Git](docs/ssh.md)
- [Проекты, mise, uv, агенты и секреты](docs/projects.md)
- [GUI и редакторы](docs/gui-editors.md)
- [Обновления и восстановление](docs/recovery.md)
- [Будущие Steam Deck, Proxmox host, Ubuntu VM/LXC](docs/platforms.md)
- [Проверенный аудит и официальные источники](docs/audit.md)

Для проверки самого репозитория: `./verify repo` (Python 3.11+, chezmoi, Git,
zsh; без установки стека и применения к реальному домашнему каталогу).
