# Проекты, языки и работа агентов

Bootstrap устанавливает mise, но не устанавливает все языки глобально.
Каждый проект выбирает поддерживаемые им версии и фиксирует их в Git.
Проверьте compatibility проекта и официальные release notes нужного runtime.
Команды ниже выполняются в **вашем проекте**, а не в репозитории настройки.

## mise

После просмотра `mise.toml`, task scripts и источников инструментов выполните
`mise trust ./mise.toml`, затем `mise install`. Здесь включён `paranoid=true`:
доверие привязано к содержимому non-global конфигурации. Не используйте
`MISE_TRUSTED_CONFIG_PATHS=/`, `mise trust --all` или отключение проверок для
неизвестных checkout. В текущем обычном режиме mise некоторые execute-команды
сами доверяют активной конфигурации, поэтому прежнего совета «mise всегда спросит»
недостаточно. [Trust](https://mise.jdx.dev/cli/trust.html),
[paranoid mode](https://mise.jdx.dev/paranoid.html).

Для нового проекта выбирайте только нужный runtime, например
`mise use --pin node@lts` или `mise use --pin python@3` или `mise use --pin go@1`.
Эти команды разрешают актуальную версию **в момент запуска**, устанавливают её
и записывают точную версию в конфигурацию. Просмотрите diff и закоммитьте его.
Дальнейшие установки используют этот выбор; обновление — отдельный осознанный diff.
Включайте lockfile mise, если выбранные backend и версия mise его поддерживают,
и проверяйте его вместе с manifest. [mise use](https://mise.jdx.dev/cli/use.html).

Агентам не нужна интерактивная shell activation:

```sh
# Запуск из каталога проверенного проекта:
mise exec -- node --version
mise run test
```

Сам `mise` должен быть в явно переданном PATH. На Apple Silicon можно вызывать
`/opt/homebrew/bin/mise exec -- …`, на Intel — `/usr/local/bin/mise exec -- …`.
В Linux путь определяется установкой пользователя/платформы. Укажите рабочий
каталог проекта в настройках агента. `zsh -c` читает только `.zshenv`, а `mise
activate` действует на prompt; не используйте загрузку `.zshrc` для CI.
[Non-interactive mise](https://mise.jdx.dev/faq.html).

`mise run check` в этом репозитории вызывает `./verify repo`: системные тестовые
зависимости должны уже быть доступны. Сам task не устанавливает ничего.

## Python / uv

Профиль `python-uv` предоставляет uv через Homebrew; Python выбирается через mise.
`uv` также умеет управлять Python, но здесь один владелец runtime — mise.
В Python-проекте добавьте `ruff`, `pre-commit` и нужный test runner в группу dev
командой `uv add --dev …`, просмотрите и сохраните `pyproject.toml` и `uv.lock`.
Если проект не пакет, настройте его как non-package в соответствии с документацией uv.

При создании `.venv` можно явно выбрать уже установленный Python:
`mise exec -- uv venv --python python --no-python-downloads`.
При повторной настройке достаточно `mise exec -- uv sync --locked --no-python-downloads`;
не пересоздавайте существующее окружение без причины.

Пример задач для такого **подготовленного Python-проекта**:

```toml
[tasks.test]
run = "uv run --locked --no-python-downloads pytest"

[tasks.format]
description = "Explicitly rewrite formatting"
run = "uv run --locked --no-python-downloads ruff format ."

[tasks.format-check]
run = "uv run --locked --no-python-downloads ruff format --check ."

[tasks.lint]
run = "uv run --locked --no-python-downloads ruff check ."

[tasks.ci]
run = "mise run format-check && mise run lint && mise run test"
```

Один механизм для pre-commit: проектная dev dependency и
`mise exec -- uv run --locked --no-python-downloads pre-commit …`.
Глобальная установка `uv tool install pre-commit` здесь не нужна.
Hooks устанавливаются отдельно через `pre-commit install` после просмотра
`.pre-commit-config.yaml`; не используйте `-f` поверх существующих hooks.
Некоторые hooks форматируют файлы — запускайте их локально. В CI используйте
non-mutating команды, а не автоматическую правку с последующим коммитом.
[uv dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/),
[locked sync](https://docs.astral.sh/uv/concepts/projects/sync/).

Для Go по тому же принципу закрепите инструменты и их совместимость с версией
Go в проекте; `gofumpt -w`/`modernize -w` — явные write-задачи, не CI-check.
Go/npm/uv команды могут обновлять caches и зависимости; «не изменяет исходники»
не означает запрет любых локальных записей. Lockfiles не прячутся в global ignore.

## Секреты и история

Токены, приватные SSH/age-ключи, `.env` с credentials, Atuin DB, ключ синхронизации,
cloud config и cookies не должны попадать в source chezmoi. Храните их в Keychain
или отдельном password/secret manager. В repo допустим только безопасный пример
имён переменных без значений; gitignore не защищает уже отслеживаемые файлы.

Atuin настроен локально: sync/update check/daemon выключены. Импорт старой истории,
создание аккаунта и sync требуют отдельного решения. Фильтр секретов не гарантирует,
что пароль не окажется в истории; не передавайте токены в command line. При утечке
сначала отзовите секрет, затем удаляйте следы из истории и Git.
[Atuin configuration](https://docs.atuin.sh/latest/configuration/config/).

age/sops из optional-профиля не создают ключи и не расшифровывают файлы сами.
Устанавливайте получателей шифрования и recovery key по задаче. Не используйте
постоянный `secrets.clear.yaml` как промежуточный файл. Резервные копии dotfiles
тоже могут содержать старые секреты: они локальные и закрыты umask 077, но не
зашифрованы. Внешнее резервное хранение должно быть зашифрованным.
