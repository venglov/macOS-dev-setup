# SSH, Keychain и подпись Git

Аутентификация на Git-host и подпись коммитов — разные проверки. Bootstrap
не создаёт ключи, не регистрирует их в аккаунтах и не включает signing заранее.
Не копируйте приватные ключи в репозиторий или вывод агента.

## macOS: authentication

1. Проверьте существующие ключи, выбранную identity и менеджер ключей. Если ключ
   уже есть, используйте его. Для нового ключа ниже имя специально отличается от
   стандартного; проверьте оба пути, чтобы исключить перезапись:

```sh
(
    umask 077
    mkdir -p "$HOME/.ssh"
    setup_key="$HOME/.ssh/id_ed25519_github"
    if [ -e "$setup_key" ] || [ -L "$setup_key" ] ||
       [ -e "$setup_key.pub" ] || [ -L "$setup_key.pub" ]; then
        printf '%s\n' 'Key path already exists; inspect it instead of overwriting.' >&2
        exit 1
    fi
    /usr/bin/ssh-keygen -t ed25519 -a 100 -f "$setup_key"
)
```

Введите passphrase в интерактивном запросе. При аппаратном ключе или password
manager используйте его отдельную официальную инструкцию; не переключайте
`SSH_AUTH_SOCK` глобально поверх уже работающего агента.

2. `./verify ssh` проверяет текущий сокет и список загруженных ключей. Обычный
   macOS-сеанс предоставляет агент; отдельный `eval "$(ssh-agent -s)"` на каждый
   shell не нужен. Если сокета нет, сначала откройте нормальный login-сеанс и
   проверьте интеграцию менеджера ключей. Не запускайте новый агент наугад.
3. Для системного Keychain загрузите ключ **системной** командой:

```sh
/usr/bin/ssh-add --apple-use-keychain "$HOME/.ssh/id_ed25519_github"
```

4. Chezmoi доставляет `~/.ssh/config.d/unix-setup-github.conf`. Это неактивный
   фрагмент, пока вы не добавите его в собственный `~/.ssh/config`. Откройте этот
   файл редактором и добавьте один `Include ~/.ssh/config.d/unix-setup-github.conf`
   в начало, вне существующих блоков Host/Match. Повторно строку не добавляйте.
   SSH использует первое полученное значение: проверьте порядок относительно
   ваших других host-блоков. При другом ключе оставьте собственный Host-блок с
   нужным IdentityFile перед Include, либо измените source фрагмента и посмотрите diff.
5. Зарегистрируйте публичный ключ как **authentication key** в своём Git-host.
   На GitHub используйте [SSH keys](https://github.com/settings/keys).
   Приватный файл не загружайте.
6. Повторите `./verify ssh`: проверьте identityfile, identitiesonly и usekeychain.
   Затем отдельно выполните `/usr/bin/ssh -T git@github.com`. При первом подключении
   сверьте fingerprint с [официальными ключами GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints).
   Не отключайте StrictHostKeyChecking. Успешный ответ GitHub сообщает об
   аутентификации, но завершает команду кодом **1**, поскольку shell не предоставляется.

`verify ssh` не подключается к серверу. Как и обычный `ssh -G`, он читает вашу
SSH-конфигурацию; пользовательские `Match exec` могут исполнять свои проверки.
Результат проверки сокета сам по себе не доказывает доступ к Git-host.
[Keychain и SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent),
[проверка соединения](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection).

## SSH signing

Git 2.34+ поддерживает SSH signing, а эта конфигурация требует Git 2.35+.
Нужны OpenSSH с `ssh-keygen -Y`, настроенные user.name/user.email и работающий ключ.
Один ключ технически может служить обеим целям; отдельный signing key упрощает
раздельную ротацию. Публичный ключ необходимо отдельно зарегистрировать как
**signing key**, даже если он уже зарегистрирован для authentication.
[Настройка GitHub signing](https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key).

В локальном `~/.config/git/local` (или существующем `~/.gitconfig`) настройте:

```gitconfig
[gpg]
    format = ssh
[user]
    signingKey = ~/.ssh/id_ed25519_github.pub
[gpg "ssh"]
    allowedSignersFile = ~/.config/git/allowed_signers
```

На macOS при нескольких OpenSSH дополнительно можно задать
`gpg.ssh.program = /usr/bin/ssh-keygen`. Публичный signingKey означает, что
приватный ключ должен быть доступен агенту; загрузите его предыдущим шагом.

Создайте или аккуратно дополните `~/.config/git/allowed_signers` редактором:
одна строка из вашего настоящего email, `namespaces="git"` и первых двух полей
публичного ключа (`ssh-ed25519 BASE64…`). Например, формат строки:

```text
your-actual-email@example.org namespaces="git" ssh-ed25519 YOUR_ACTUAL_PUBLIC_KEY
```

Замените оба значения своими; это схема, не готовая identity. Не добавляйте
wildcard principal. Локальный allowed_signers — явное доверие проверенным ключам,
а не автоматическое доверие любому автору коммита.
[Git allowedSignersFile](https://git-scm.com/docs/git-config#Documentation/git-config.txt-gpgsshallowedSignersFile).

Выполните `./verify signing`. Команда создаёт временный репозиторий, подписывает
пустой commit и проверяет подпись через ваш allowed_signers; удаляет временные
файлы при завершении. Она не пишет коммит в проект, не запускает project hooks
и не публикует данные. После успешной проверки включите `[commit] gpgSign = true`
в локальной Git-конфигурации. Подпись опубликованного коммита проверьте отдельно
в интерфейсе Git-host; локальная проверка не подтверждает регистрацию в аккаунте.

На других Unix Keychain-фрагмент не устанавливается. Используйте агент своей
сессии или менеджера ключей и обычный `ssh-add`; автоматического systemd-unit
или изменения login shell нет.
