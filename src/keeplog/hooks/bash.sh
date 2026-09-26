# The DEBUG trap also fires for every command PROMPT_COMMAND runs, so a command
# is only recorded after __keeplog_arm (the last PROMPT_COMMAND entry) has run.
__keeplog_preexec() {
    if [[ "$__KEEPLOG_READY" != "1" || -z "$__keeplog_armed" || -z "$KEEPLOG_CTRL_FD" ]]; then
        return
    fi
    if [[ "$BASH_COMMAND" == __keeplog_precmd* ]]; then
        return
    fi
    __keeplog_armed=
    __keeplog_cmd="$BASH_COMMAND"
    printf 'C:%s\n' "${BASH_COMMAND::1024}" >&$KEEPLOG_CTRL_FD 2>/dev/null
}

__keeplog_precmd() {
    local ec=$?
    __keeplog_armed=
    if [[ "$__KEEPLOG_READY" == "1" && -n "$__keeplog_cmd" && -n "$KEEPLOG_CTRL_FD" ]]; then
        printf 'E:%s\n' "$ec" >&$KEEPLOG_CTRL_FD 2>/dev/null
        unset __keeplog_cmd
    fi
    return $ec
}

__keeplog_arm() {
    local ec=$?
    __keeplog_armed=1
    return $ec
}

trap '__keeplog_preexec' DEBUG
if [[ "$(declare -p PROMPT_COMMAND 2>/dev/null)" == "declare -a"* ]]; then
    PROMPT_COMMAND=(__keeplog_precmd "${PROMPT_COMMAND[@]}" __keeplog_arm)
else
    PROMPT_COMMAND="__keeplog_precmd"$'\n'"${PROMPT_COMMAND}"$'\n'"__keeplog_arm"
fi
