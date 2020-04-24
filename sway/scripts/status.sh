#!/usr/bin/env sh
date_formatted=$(date "+%F")
time_formatted=$(date "+%H:%M")

clock=$(case $(date "+%I") in
    01    ) echo "🕐";;
    02    ) echo "🕑";;
    03    ) echo "🕒";;
    04    ) echo "🕓";;
    05    ) echo "🕔";;
    06    ) echo "🕕";;
    07    ) echo "🕖";;
    08    ) echo "🕗";;
    09    ) echo "🕘";;
    10    ) echo "🕙";;
    11    ) echo "🕚";;
    12    ) echo "🕛";;
    *     ) echo "  ";;
esac)

cpu_temp=$(sensors k10temp-pci-00c3 -j | jq ".[].Tdie.temp1_input")
cpu_temp=$(echo "$cpu_temp/1" | bc)

gpu_sensors=$(sensors amdgpu-pci-0600 -j)
gpu_temp=$(echo $gpu_sensors | jq ".[].edge.temp1_input")
gpu_fan_max=$(echo $gpu_sensors | jq ".[].fan1.fan1_max")
gpu_fan_cur=$(echo $gpu_sensors | jq ".[].fan1.fan1_input")
gpu_fan_percent=$(echo "100*$gpu_fan_cur/$gpu_fan_max" | bc)

echo "🌡️" CPU:$cpu_temp GPU:$gpu_temp FAN:$gpu_fan_percent% "📅" $date_formatted $clock $time_formatted
