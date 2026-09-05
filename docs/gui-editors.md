# GUI и редакторы

Единственный установочный каталог GUI — [gui.tsv](../manifests/macos/gui.tsv):
короткий id, Homebrew cask, официальный источник, способ обновления, ручные шаги.
Для включённых приложений выбран Homebrew Cask; CLI-профили их не устанавливают.
Наличие в каталоге — возможность выбора, а не рекомендация установить всё.

```sh
./bootstrap macos gui list
./bootstrap macos gui install ghostty vscode
# Отдельное обновление только названных приложений:
./bootstrap macos gui update ghostty vscode
```

Установка повторно пропускает зарегистрированные casks. При приложении, ранее
установленном вручную, Homebrew может отказаться из-за существующего app bundle.
Не используйте force/adopt автоматически: проверьте версии и выберите одного
владельца установки. Для обновления закройте приложение; его собственный updater
может обновить bundle независимо от Homebrew. Мы не отключаем обновления безопасности.
Команда GUI update использует `--greedy` только для явно названных casks.
`macos update` никогда не обновляет GUI.

Ghostty основной. Его конфигурация хранится в `~/.config/ghostty/config`.
На macOS также возможен файл в `~/Library/Application Support/com.mitchellh.ghostty/`;
если он уже существует, проверьте порядок загрузки и уберите конфликт вручную
после backup. Repo не создаёт вторую копию. Тема и шрифт штатные, Starship не
требует Nerd Font. [Ghostty config](https://ghostty.org/docs/config),
[options](https://ghostty.org/docs/config/reference).

OrbStack нужен только при контейнерах или локальных Linux-машинах. Он предоставляет
Docker tooling; отдельная formula `docker` в CLI-профилях отсутствует.
После первого запуска проверьте `command -v docker`, `docker context show`,
`docker version` и `docker compose version`. Доступ к engine требует запуска
OrbStack; это осознанный ручной шаг. Не удаляйте чужой Docker CLI или contexts
автоматически. [OrbStack Docker](https://docs.orbstack.dev/docker/).

Raycast, Obsidian, Chrome, Stats и Beekeeper — варианты под конкретную работу.
Raycast в проверенном cask требует ARM64; Intel-пользователь должен отдельно
проверять текущую поддержку. Права Accessibility, login items, лицензии, sync
и plugins выдаются пользователем после первого запуска.

Другие приложения прежнего README (мессенджеры, игровые клиенты, кошельки,
слайсеры, Logi Options+, несколько AI-клиентов) не являются частью dev bootstrap.
Устанавливайте нужные через официальный сайт или добавляйте проверенную запись
в каталог отдельным изменением. Pages/Numbers/Keynote остаются ручной установкой
через App Store; автоматизации Apple ID и зависимости от `mas` нет.

## VS Code

VS Code — отдельный cask `vscode`, Neovim — отдельный optional CLI-профиль.
Ни один редактор не обязателен. После запуска VS Code включите команду `code`
через Command Palette, если она ещё не доступна.

[settings.json](../config/editors/vscode/settings.json) — небольшой образец для
осознанного переноса в настройку выбранного профиля редактора; bootstrap его
не копирует поверх существующих пользовательских настроек. Сначала сравните
свою конфигурацию. Для дальнейшего управления личным полным файлом добавьте его
в свой chezmoi source и продолжайте diff/apply, сохраняя только одного владельца.
Проектные formatters и language settings должны согласовываться с проектом.

Образец сохраняет Workspace Trust и подтверждение Git Sync, отключает Smart
Commit, не назначает неизвестную тему/formatter и не вводит agent auto-approval.
Если в старом профиле уже были auto-approve, auto-reply или auto-accept настройки,
одного нового образца недостаточно: просмотрите и сбросьте их в User, Workspace
и Remote Settings. Не переносите старые AI-настройки по названию без проверки.
[Workspace Trust](https://code.visualstudio.com/docs/editing/workspaces/workspace-trust),
[tool approvals](https://code.visualstudio.com/docs/agents/run/approvals).

[Каталог extensions](../manifests/editors/vscode-extensions.txt) разделён комментариями
по задачам; выбирайте отдельные строки. Например, для Go можно вызвать
`code --install-extension golang.go --profile main` после создания профиля.
Не запускайте массовую установку всего файла.

Python может подтянуть Pylance как зависимость, Jupyter — companion extensions:
их не нужно перечислять повторно как обязательные. Auto Close/Rename Tag
не добавлены поверх встроенного linked editing. AI extensions, remote-server,
Code Runner, наборы иконок и formatter для каждого файла не навязываются.
Проверяйте publisher, dependency list и разрешения выбранного расширения.
[Python extension](https://code.visualstudio.com/docs/python/python-tutorial).
