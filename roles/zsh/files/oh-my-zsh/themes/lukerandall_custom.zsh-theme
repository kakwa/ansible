# ZSH Theme - Preview: https://cl.ly/f701d00760f8059e06dc
# Thanks to gallifrey, upon whose theme this is based

local return_code="%(?..%{$fg_bold[red]%}%? ↵%{$reset_color%})"

# 64 hostname colors from 256 palette (no black/white/blue)
local -a HOSTNAME_COLORS=(
  17 18 19 22 23 24 25 28 29 30 31 32 33 34 35 38
  39 40 41 44 46 52 53 54 55 58 70 76 82 88 89 90
  91 92 93 94 106 112 118 124 125 126 127 128 129 130 142 148
  154 160 161 162 163 164 165 166 178 184 196 197 198 199 200 202
)
# Hostname-based color: pick from HOSTNAME_COLORS by hostname hash
function set_hostname_color() {
  local hash=0 i
  for ((i = 1; i <= ${#HOST}; i++)); do
    hash=$(( hash + $(printf '%d' "'${HOST[$i]}") ))
  done
  hostname_color=${HOSTNAME_COLORS[$(( (hash % 64) + 1 ))]}
}
precmd_functions+=(set_hostname_color)

function my_git_prompt_info() {
  ref=$(git symbolic-ref HEAD 2> /dev/null) || return
  GIT_STATUS=$(git_prompt_status)
  [[ -n $GIT_STATUS ]] && GIT_STATUS=" $GIT_STATUS"
  echo "$ZSH_THEME_GIT_PROMPT_PREFIX${ref#refs/heads/}$GIT_STATUS$ZSH_THEME_GIT_PROMPT_SUFFIX"
}

# Use %F{15} (256-color white) so hostname 256-color does not leak; @, space, > and input are white
PROMPT='%{$fg_bold[green]%}%n%F{15}@%F{$hostname_color}%m%F{15} %{$fg_bold[blue]%}%2~%F{15} $(my_git_prompt_info)%F{15}%B>%b '
RPS1="${return_code}"

ZSH_THEME_GIT_PROMPT_PREFIX="%{$fg[yellow]%}("
ZSH_THEME_GIT_PROMPT_SUFFIX=") %{$reset_color%}"
ZSH_THEME_GIT_PROMPT_UNTRACKED="%%"
ZSH_THEME_GIT_PROMPT_ADDED="+"
ZSH_THEME_GIT_PROMPT_MODIFIED="*"
ZSH_THEME_GIT_PROMPT_RENAMED="~"
ZSH_THEME_GIT_PROMPT_DELETED="!"
ZSH_THEME_GIT_PROMPT_UNMERGED="?"

