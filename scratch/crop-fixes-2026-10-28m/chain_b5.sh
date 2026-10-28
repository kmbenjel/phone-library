#!/usr/bin/env bash
# wait for bench-b4-b to end, then launch the B5 bench in the memory pen (one analysis at a time)
cd /home/k/projects/phone-library/scratch/crop-fixes-2026-10-28m
while systemctl --user is-active -q bench-b4-b; do sleep 15; done
echo "bench-b4-b ended $(date -u +%T)"; cat bench-b4.log
systemd-run --user --slice=crop.slice --unit=bench-b5-a --nice=10 --working-directory=$PWD --setenv=PATH="$PATH" /usr/bin/bash -c "python3 bplan.py 064846139175 lbb5 > bench-b5.log 2>&1"
sleep 3; systemctl --user is-active bench-b5-a
