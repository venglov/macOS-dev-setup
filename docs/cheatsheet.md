# Читшит CLI

Все перечисленные здесь CLI-программы входят в `Brewfile`. Установка:
`brew bundle install --no-upgrade --file=Brewfile`.
Для интеграций shell примените dotfiles и выполните `zsh -lic 'zimfw install'`.

## Альтернативы привычным командам

Это команды для самостоятельного вызова: `ls`, `cat`, `grep`, `find`, `cd`,
`ps`, `top`, `du` и `df` не переопределяются aliases. Флаги альтернатив могут
отличаться от стандартных утилит; в скриптах выбирайте инструмент явно.

| Привычная команда / задача | Установленная альтернатива | Как использовать | Отличие |
| --- | --- | --- | --- |
| `ls` | `eza` | `eza -la --git --group-directories-first` | Подробный список с Git-статусом; `eza -T -L 2` показывает дерево |
| `cat`, просмотр исходника | `bat` | `bat README.md`; `bat --paging=never file.py` | Подсветка и номера строк; для побайтового объединения файлов используйте `cat` |
| `less`, постраничное чтение | `bat` или `less` | `bat file.py`; `less -R +G app.log` | `bat` удобен для кода; `less` остаётся pager для больших логов, `F` следит за дописыванием |
| `grep -R` | `rg` (ripgrep) | `rg -n 'TODO\|FIXME' src` | Рекурсивный поиск; по умолчанию учитывает ignore-файлы и пропускает скрытые файлы |
| `find` | `fd` | `fd --type f --extension go . src` | Поиск имён; учитывает ignore-файлы, по умолчанию пропускает скрытые файлы |
| Повторный `cd` в знакомые каталоги | `z`, `zi` (zoxide) | `z project`; `zi project` | Выбор из посещённых каталогов; `zi` открывает fzf; обычный `cd` работает по точному пути |
| `history`, поиск по Ctrl-R | `atuin` | Ctrl-R; `atuin search 'git rebase'` | Поиск по локальной базе; Enter возвращает выбранную команду для проверки, без запуска |
| Ручной выбор из списка | `fzf` | `fd --type f \| fzf` | Нечёткий интерактивный фильтр; Ctrl-T вставляет выбранные пути в строку shell |
| `top` | `btop` | `btop` | Интерактивные графики CPU, памяти, сети и процессов; выход — `q` |
| `ps` | `procs` | `procs`; `procs node`; `procs --watch 2` | Таблица процессов, фильтр по имени и обновление каждые две секунды |
| `du` | `dust` | `dust .`; `dust -d 2 .` | Наглядное распределение занятого места, ограничение глубины |
| `df` | `duf` | `duf`; `duf /` | Таблица файловых систем, ёмкости и свободного места |
| Просмотр Git diff | `delta` | `git diff`; `git show HEAD` | Уже подключён как Git pager; для вывода без pager — `git --no-pager diff` |
| `curl` для HTTP API | `http` (HTTPie) | `http GET https://httpbin.org/get`; `http POST https://httpbin.org/post hello=world` | Читаемый вывод и простой JSON-ввод; второй пример отправляет тестовые данные |
| `curl -o`, скачивание файлов | `wget` | `wget -O artifact.tgz https://example.com/artifact.tgz` | Явное сохранение в файл; замените URL адресом своего артефакта |
| `vi` / `vim` | `nvim` (Neovim) | `nvim README.md` | Отдельный редактор; EDITOR автоматически на него не переключается |
| `time` для сравнения команд | `hyperfine` | `hyperfine --warmup 2 'rg TODO src' 'grep -R TODO src'` | Несколько запусков со статистикой; команды в примере имеют разные правила ignore |
| Цикл повторного запуска | `watch`, `watchexec` | `watch -n 2 df -h`; `watchexec -e go -- go test ./...` | Первый запускает по таймеру, второй — при изменении файлов |

Источники и дополнительные флаги: [eza](https://github.com/eza-community/eza),
[bat](https://github.com/sharkdp/bat), [ripgrep](https://github.com/BurntSushi/ripgrep),
[fd](https://github.com/sharkdp/fd), [zoxide](https://github.com/ajeetdsouza/zoxide),
[procs](https://github.com/dalance/procs), [dust](https://github.com/bootandy/dust),
[duf](https://github.com/muesli/duf).

## Поиск, скрытые файлы и имена с пробелами

```sh
rg -n --hidden --glob '!.git' 'TODO|FIXME' .
fd --hidden --exclude .git --type f --extension toml
fd --type f --print0 | fzf --read0 --print0   # NUL-разделители для обработки путей
```

`--hidden` включает скрытые файлы, но сохраняет правила ignore. Для осознанного
поиска в игнорируемых каталогах добавьте `--no-ignore`. `--follow` добавляйте,
только если хотите обходить симлинки. Заключайте пути в кавычки, а при обработке
списков файлов сохраняйте NUL-разделители до конца цепочки.

## Клавиши и Zimfw

| Действие | Клавиша / команда |
| --- | --- |
| История Atuin | Ctrl-R; Enter вставляет команду, следующий Enter выполняет её |
| Выбор файлов fzf | Ctrl-T |
| Выбор каталога fzf | Alt-C; в терминале может потребоваться настройка Option как Alt |
| Дополнение с выбором fzf-tab | Tab после команды или части пути |
| Принять подсказку autosuggestions | Стрелка вправо в конце строки |
| Отредактировать командную строку в EDITOR | Ctrl-X, затем Ctrl-E (модуль Zim input) |
| Установить новые модули после изменения `.zimrc` | `zimfw install`, затем открыть новую вкладку |
| Обновить загруженные модули | `zimfw update` |
| Посмотреть модули | `zimfw list` |
| Распаковать архив | `unarchive archive.tar.gz` (модуль Zim archive) |

Zim Git использует префикс **`G` в верхнем регистре**: `Gws` — короткий статус,
`Gwd` — diff, `Gia` — добавление файлов, `Gc` — commit, `Glg` — граф истории.
Например: `Gia README.md`. Старые `gst`, `ga`, `gc`, `ll`, `lt`, `please`
не определены. Проверить реальное раскрытие можно командой `alias Gws`.
Модуль archive также добавляет aliases для расширений архивов и при наличии
pigz/pbzip2 использует их вместо gzip/bzip2.
[Справка Zim](https://zimfw.sh/docs/commands/), [Git aliases](https://github.com/zimfw/git).

## Остальные инструменты из Brewfile

| Задача | Пример |
| --- | --- |
| JSON | `jq '.scripts' package.json` |
| YAML | `yq '.services' compose.yaml` |
| GitHub CLI | `gh auth login`; `gh pr list`; `gh pr diff 1` |
| Git UI | `lazygit` в репозитории |
| Счётчик исходного кода | `tokei .` |
| Отдельная терминальная сессия | `tmux new -s work`; отсоединиться Ctrl-B, D; вернуться `tmux attach -t work` |
| Версии языка в проекте | `mise use --pin node@lts`; `mise exec -- node --version` |
| Python-зависимости | `uv add --dev ruff pre-commit`; `mise exec -- uv sync --locked --no-python-downloads` |
| Форматирование Python | `mise exec -- uv run --locked ruff format --check .` |
| Задачи проекта | `mise run test`; `just --list`; `just test` — если соответствующая задача определена |
| Сборка C/C++ | `cmake -S . -B build -G Ninja`; `cmake --build build` |
| GNU Make на macOS | `gmake` — имя программы из формулы `make` |
| Флаги библиотеки для компилятора | `pkg-config --cflags --libs sqlite3` — если её metadata доступна |
| SQLite от Homebrew | `"$(brew --prefix sqlite)/bin/sqlite3" app.db '.tables'` |
| Go-код из SQL | `sqlc generate` в проекте с `sqlc.yaml` |
| SHA-256 через OpenSSL 3 | `"$(brew --prefix openssl@3)/bin/openssl" dgst -sha256 artifact.tgz` |
| Шифрование файла | `age -r AGE_PUBLIC_RECIPIENT -o file.age file.txt` — подставьте публичного получателя |
| Редактирование зашифрованного YAML | `sops secrets.yaml` — после настройки получателей и ключей проекта |
| Сравнить dotfiles перед применением | `chezmoi diff`; `chezmoi apply`; `chezmoi verify` |

`sqlite` и `openssl@3` могут быть keg-only: путь через `brew --prefix FORMULA`
выбирает именно установленную Homebrew-версию. Системные бинарники остаются доступны.
Ключи age/SOPS и базы истории не добавляйте в репозиторий dotfiles.
