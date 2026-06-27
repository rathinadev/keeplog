__keeplog_preexec() {
    if [[ "$__KEEPLOG_READY" != "1" ]]; then
        return
    fi
    if [[ -z "$__keeplog_cmd" && -n "$KEEPLOG_CTRL_FD" ]]; then
        __keeplog_cmd="$BASH_COMMAND"
        printf 'C:%s\n' "${BASH_COMMAND::1024}" >&$KEEPLOG_CTRL_FD 2>/dev/null
    fi
}

__keeplog_precmd() {
    if [[ "$__KEEPLOG_READY" != "1" ]]; then
        return
    fi
    local ec=$?
    if [[ -n "$__keeplog_cmd" && -n "$KEEPLOG_CTRL_FD" ]]; then
        printf 'E:%s\n' "$ec" >&$KEEPLOG_CTRL_FD 2>/dev/null
        unset __keeplog_cmd
    fi
}

trap '__keeplog_preexec' DEBUG
PROMPT_COMMAND="__keeplog_precmd${PROMPT_COMMAND:+;}$PROMPT_COMMAND"
