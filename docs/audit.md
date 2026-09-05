# Проверенный аудит и источники

Проверка выполнена 2026-09-05 по реальному checkout. Исходный HEAD: `d641112`.
В репозитории был только README: отдельных scripts/configs/CI не существовало.
Поэтому «код» старого процесса — исполняемые блоки README, а пример CI не был
действующим GitHub Actions workflow. Незакоммиченные изменения также учтены.

| Гипотеза | Что действительно найдено | Решение |
| --- | --- | --- |
| Перезапись через `>` | `cat >`/`cat >|` для startup files и global ignore; предупреждение о backup было | Реальный source chezmoi, diff, подтверждение, backup/restore |
| core.ignorecase/fileMode | Оба глобально установлены в false | Не задаются; verify указывает на старые глобальные overrides |
| Лишний ssh-agent | Безусловный `eval "$(ssh-agent -s)"` в SSH-шаге, не в каждом startup | Текущий macOS agent, проверка сокета, системный ssh-add |
| SSH authentication/signing | Ключ и signingKey были, но без host config, allowed signers и отдельных proof tests | Неактивный host-фрагмент, ручное включение, отдельные проверки authentication/signing |
| Delta | `diff.tool=delta` не делает Delta pager для `git diff` | `core.pager`, `interactive.diffFilter`; проверка effective values |
| uv/pre-commit | `uv tool install` сочетался с `uv run`; проектный pre-commit не объявлен | Один проектный dev dependency и `uv run --locked` |
| Форматирование CI | В примере mise task `ci` вызывал пишущий `fmt` | Отдельный format-check; новый CI только проверяет source |
| fzf/Ctrl-R | Старый installer не обязательно сломан; подключения актуального `--zsh` не было. В working-file Atuin уже удалён, поэтому фактический конфликт Atuin не подтверждён | fzf integration при запуске shell, его Ctrl-R отключён заранее, Atuin возвращён по новому заданию |
| Quoting/filenames | Связка `awk -F:` + `xargs -r ${EDITOR:-vim}` ломает пробелы/двоеточия и непереносима | Удалена; NUL-пример, quoted пути, тесты пробелов и symlinks |
| Docker/OrbStack | В списках одновременно formula docker и cask orbstack | Отдельной formula нет; OrbStack выбирается вручную |
| Global ignore | Прятал `.vscode`, `.idea`, build/dependency-файлы всех проектов | Только OS litter, остальные правила проектные |
| Агентские разрешения VS Code | enableAutoApprove, autoReplyToPrompts и autoAcceptDelay с широким воздействием | Не поставляются; инструкции сбросить старые настройки в каждом scope |
| VS Code drift | Указаны GitHub theme/markdownlint formatter без соответствующей установки; tag extensions при linkedEditing; Jupyter companions/Pylance перечислены отдельно | Минимальный образец без обязательных внешних formatters, каталог расширений по задачам |
| Rosetta/services | Rosetta сопровождалась «if needed», Ollama service был optional; безусловность гипотезы не подтверждена | Явно отделены от bootstrap; нет запуска сервисов и Rosetta |
| Shell aliases | Есть подмены `cd`, `ls`, `cat`, `less`, `grep`, `find`, `ps`, `du`, `df`, alias-модули Zim | В поставляемых файлах aliases/подмен нет; системный zsh, Starship |
| Все инструменты сразу | Большой brew install и глобальный набор runtime/Go-tools | Минимальная база + выбираемые CLI/GUI/языковые профили |

Удаление ключа настройки из нового образца не сбрасывает ранее применённый ключ
в реальном User/Workspace Settings. Аналогично `~/.gitconfig` сохраняет приоритет.
Миграция намеренно требует просмотра конфликтов, не массового удаления.

## Проверка меняющихся сведений

Ниже — официальные источники, проверенные при реализации. Списки версий и поддержка
меняются; повторно проверяйте их при обновлении manifests. Repo не утверждает
неподтверждённые названия или даты выпуска macOS.

- [Homebrew Installation](https://docs.brew.sh/Installation) и
  [Support Tiers](https://docs.brew.sh/Support-Tiers): native prefixes, CLT, нижняя
  граница macOS и Tier 3 для Intel. [Manpage](https://docs.brew.sh/Manpage):
  Bundle no-upgrade, списки formulae, cask greedy update.
- [Homebrew formula API](https://formulae.brew.sh/docs/api/): проверены все
  32 formulae и 8 casks; на дату проверки не deprecated/disabled. В cask Raycast
  обнаружено ограничение ARM64. API не заменяет приёмку фактической установки.
- [chezmoi setup](https://www.chezmoi.io/user-guide/setup/),
  [managed](https://www.chezmoi.io/reference/commands/managed/),
  [apply](https://www.chezmoi.io/reference/commands/apply/): source, config,
  списки targets и управление типами. Реальные тесты используют chezmoi 2.72.1.
- [fzf](https://github.com/junegunn/fzf#setting-up-shell-integration),
  [Atuin bindings](https://docs.atuin.sh/latest/configuration/key-binding/),
  [Atuin configuration](https://docs.atuin.sh/latest/configuration/config/):
  порядок интеграции, Ctrl-R, local history без daemon/sync.
- [Starship](https://starship.rs/guide/),
  [zoxide](https://github.com/ajeetdsouza/zoxide#installation),
  [Delta](https://dandavison.github.io/delta/get-started.html): init и pager configuration.
- [mise trust](https://mise.jdx.dev/cli/trust.html),
  [paranoid](https://mise.jdx.dev/paranoid.html),
  [use --pin](https://mise.jdx.dev/cli/use.html),
  [uv dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/):
  проектное доверие, versions, dependency groups; без старых закреплений из README.
- [Git config](https://git-scm.com/docs/git-config) и
  [GitHub signing](https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key):
  приоритет config, public signingKey и allowed signers.
- [OrbStack Docker](https://docs.orbstack.dev/docker/),
  [Ghostty config](https://ghostty.org/docs/config),
  [VS Code approvals](https://code.visualstudio.com/docs/agents/run/approvals):
  системная интеграция и осознанные пользовательские разрешения.
- [Valve SteamOS FAQ](https://help.steampowered.com/en/faqs/view/671A-4453-E8D2-323C),
  [Proxmox guide](https://pve.proxmox.com/pve-docs/pve-admin-guide.pdf):
  сохранность системных изменений и разделение host/guest.

SHA actions/checkout и actions/setup-python разрешены через официальный GitHub API,
тестовый chezmoi закреплён версией и checksum release artifacts. CI не использует
bootstrap для установки рабочего стека, не форматирует файлы и имеет read-only
permissions на содержимое репозитория.

## Выполненная проверка

Локально прошли 15 тестов на macOS ARM64 с системными Bash 3.2 и zsh 5.9,
Git 2.55.0 и временным chezmoi 2.72.1. Проверены также синтаксис workflow YAML
и отсутствие whitespace-ошибок в diff. Инсталляторы и shell-интеграции в тестах
заменены заглушками; реальные chezmoi и Git работают только в scratch directories.
Стек, GUI и пользовательские настройки машины выполнения не устанавливались
и не менялись. Workflow для Linux/macOS добавлен, но удалённый CI ещё не запускался;
чистая установка ОС и внешняя SSH authentication не проверялись.
