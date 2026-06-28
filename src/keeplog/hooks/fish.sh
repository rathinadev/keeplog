function _keeplog_preexec --on-event fish_preexec
    if test "$__KEEPLOG_READY" != "1"
        return
    end
    if test -z "$_keeplog_cmd" -a -n "$KEEPLOG_CTRL_FD"
        set -g _keeplog_cmd $argv[1]
        printf 'C:%s\n' (string sub -l 1024 -- $argv[1]) >&$KEEPLOG_CTRL_FD 2>/dev/null
    end
end

function _keeplog_postexec --on-event fish_postexec
    if test "$__KEEPLOG_READY" != "1"
        return
    end
    if test -n "$_keeplog_cmd"
        printf 'E:%s\n' $status >&$KEEPLOG_CTRL_FD 2>/dev/null
        set -e _keeplog_cmd
    end
end
