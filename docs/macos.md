# Подготовка macOS

Этот шаг выполняется до общей конфигурации: именно он предоставляет Git,
chezmoi и mise. Работа в обычном аккаунте; системные установщики могут запросить
администратора через собственный интерфейс. Не запускайте весь bootstrap с sudo.

## Чистая система

1. Завершите обновления macOS и первичную настройку аккаунта.
2. В штатном Terminal выполните `xcode-select --install`, завершите диалог CLT.
   Затем проверьте `xcode-select -p` и `xcrun --find clang`.
   Если уже установлен полноценный Xcode, он также может предоставлять инструменты.
3. Склонируйте этот репозиторий с его GitHub-страницы по HTTPS или распакуйте ZIP.
   SSH-ключ для первоначального клонирования не требуется. Откройте каталог репозитория.
4. Установите Homebrew по [официальной инструкции](https://docs.brew.sh/Installation).
   Для просмотра перед выполнением можно скачать installer во временный каталог:

```sh
setup_download=$(mktemp -d "${TMPDIR:-/tmp}/homebrew-review.XXXXXXXX")
curl --fail --location --proto '=https' --tlsv1.2 \
  https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh \
  --output "$setup_download/install.sh"
less "$setup_download/install.sh"
# Выполните следующую строку только после успешного скачивания и просмотра:
/bin/bash "$setup_download/install.sh"
```

URL installer изменяемый: просмотр и TLS не делают его неизменяемым артефактом.
Для управляемого парка проверяйте и фиксируйте конкретную ревизию отдельно.
Не выполняйте повторно установку, если native Homebrew уже работает.

5. Выполните:

```sh
./bootstrap macos prepare
./bootstrap macos install terminal
./bootstrap common init
./bootstrap common diff
./bootstrap common apply
./bootstrap macos gui install ghostty
./verify macos terminal
```

На вопрос terminal UX ответьте `yes`. После применения откройте новую вкладку
Ghostty, затем выполните `./verify common`. В старой вкладке PATH мог ещё не измениться.
Bootstrap находит Homebrew по native пути сам, независимо от `.zshrc`.

## Архитектура и поддержка

Homebrew использует `/opt/homebrew` на Apple Silicon и `/usr/local` на Intel.
Этот репозиторий требует macOS 14+ и CLT/Xcode. Текущая официальная документация
относит Intel к Tier 3; Intel-ветка сохранена как best effort. Точную совместимость
пакетов проверяйте перед установкой. [Installation](https://docs.brew.sh/Installation),
[Support Tiers](https://docs.brew.sh/Support-Tiers).

Bootstrap отвергает shell, запущенный через Rosetta. Откройте native Terminal или
Ghostty и повторите. Rosetta не устанавливается автоматически: она нужна только
при конкретной зависимости от Intel-приложения. Тогда используйте запрос самой
macOS и [инструкцию Apple](https://support.apple.com/en-us/102527).

Системный `/bin/zsh` достаточен. Homebrew zsh, GNU coreutils и отдельный ssh-agent
не входят в базу. GNU Make из build-профиля вызывается как `gmake`; мы не ставим
его `gnubin` впереди системного PATH. Фоновым сервисам и login items bootstrap
не даёт разрешение на автоматический запуск.

## CLI и системная интеграция

`macos install` включает core и выбранные профили. Повторная установка использует
`brew bundle install --no-upgrade`; обычное обновление вынесено в `macos update`.
Это не полная фиксация бинарных версий: Homebrew может обновить зависимость ради
установки нового пакета. [Семантика Bundle](https://docs.brew.sh/Manpage#bundle-subcommand).

Следующие действия пользователь выполняет отдельно:

- [SSH/Keychain и signing](ssh.md), вход в Git-host и проверка fingerprints;
- первый запуск GUI, выдача Accessibility/Screen Recording только нужным приложениям;
- FileVault, Touch ID, Apple ID, резервное копирование и системные настройки;
- настройка контейнеров в OrbStack, только если он выбран;
- проектные runtimes через mise, а не глобальный перечень всех языков.

Bootstrap не меняет `defaults`, SIP, Gatekeeper, firewall или политику агентов.
Homebrew casks могут выполнять собственные installer scripts; перед установкой
GUI просмотрите источник и требования в [каталоге](../manifests/macos/gui.tsv).
