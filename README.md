# taskwarrior-effort-tracker
Hook for Taskwarrior that records a log of time spent each day on each task
[![Code Health](https://landscape.io/github/jhmartin/taskwarrior-time-report/master/landscape.svg?style=flat)](https://landscape.io/github/jhmartin/taskwarrior-time-report/master)

# Installation
Place the file in ~/.task/hooks/
Set a LEDGERFILE environmental variable where the output file should be written.

Output format is:
Date,UID,Seconds effort, Project name (or 'no project'), task description

Example:
`2015/03/22,e28087e9-525e-403c-9c4b-1aed53809092,9,no project,test3`

