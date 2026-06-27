_keeplog_preexec() {
    if [[ "$__KEEPLOG_READY" != "1" ]]; then
        return
    fi
    if [[ -z "$_keeplog_cmd" && -n "$KEEPLOG_CTRL_FD" ]]; then
        _keeplog_cmd="$1"
        print -rnu "$KEEPLOG_CTRL_FD" "C:${1::1024}"$'\n'
    fi
}

_keeplog_precmd() {
    if [[ "$__KEEPLOG_READY" != "1" ]]; then
        return
    fi
    local ec=$?
    if [[ -n "$_keeplog_cmd" && -n "$KEEPLOG_CTRL_FD" ]]; then
        print -rnu "$KEEPLOG_CTRL_FD" "E:$ec"$'\n'
        unset _keeplog_cmd
    fi
}

autoload -Uz add-zsh-hook
add-zsh-hook preexec _keeplog_preexec
add-zsh-hook precmd _keeplog_precmd
