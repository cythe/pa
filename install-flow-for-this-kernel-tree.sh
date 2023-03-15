#!/bin/bash

PDIR=$(dirname $(readlink -f $0))

ln -sf $PDIR/flow/* .
