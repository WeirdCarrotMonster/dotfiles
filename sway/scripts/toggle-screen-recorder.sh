#!/bin/bash

pid=`pgrep wf-recorder`
status=$?

if [ $status != 0 ]
then
  wf-recorder --muxer=v4l2 --codec=rawvideo --pixel-format=yuv420p --file=/dev/video2
else
  pkill --signal SIGINT wf-recorder
fi;
