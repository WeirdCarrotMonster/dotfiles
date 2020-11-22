#!/usr/bin/env fish

set options "Suspend
Reboot
Poweroff"

set choice (echo $options | wofi --dmenu --lines 3 --prompt "" --cache-file /dev/null --insensitive)

switch $choice
    case Suspend
        systemctl suspend
    case Reboot
        systemctl reboot
    case Poweroff
        systemctl poweroff
end
