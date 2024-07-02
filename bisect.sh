#!/bin/bash

PADIR=$(dirname $(readlink -f $0))
. $PADIR/utils

which apply > /dev/null 2>&1
if [ "$?" != "0" ]; then
    source $PADIR/pa.init
fi

WORK_DIR=`pwd`

ARCH=arm64
CROSS=aarch64-wrs-linux-
KERNEL_DIR=`find $WORK_DIR/tmp-glibc/work-shared/ -maxdepth 2 -name "kernel-source"`
OUT_DIR=$WORK_DIR/obj_out
THREADs=-j96
CONFIG_F=config

set_env() {
    if [ -f bisect.conf ]; then
	echo_c SC_GREEN "Read ppre from config."
	PPRE=`cat bisect.conf`
    else
	echo_c SC_GREEN "Try to find a ppre..."
	PPRE=`find tmp-glibc/work -maxdepth 4 -name "recipe-sysroot-native" | grep linux-yocto`
	if [ "x$PPRE" == "x" ] ; then
	    echo_c SC_RED "I can't found recipe-sysroot-native dir..."
	    exit 1
	fi
	echo $PPRE > bisect.conf
    fi
    export PATH=$PATH:$WORK_DIR/$PPRE/usr/bin/aarch64-wrs-linux
}


allyesmake() {
    rm -rf $OUT_DIR
    make -C $KERNEL_DIR ARCH=$ARCH CROSS_COMPILE=$CROSS O=$OUT_DIR allyesconfig
    make $THREADs -C $KERNEL_DIR ARCH=$ARCH CROSS_COMPILE=$CROSS O=$OUT_DIR > /dev/null
    if [ "$?" != "0" ]; then
	echo_c SC_RED "failed."
	exit 1
    fi
    exit 0
}

menuconfig() {
    make $THREADs -C $KERNEL_DIR ARCH=$ARCH CROSS_COMPILE=$CROSS O=$OUT_DIR menuconfig
    if [ "$?" != "0" ]; then
	echo_c SC_RED "failed."
	exit 1
    else 
	cp $OUT_DIR/.config $CONFIG_F 
    fi
    exit 0
}

make() {
    cp $CONFIG_F $OUT_DIR/.config
    make $THREADs -C $KERNEL_DIR ARCH=$ARCH CROSS_COMPILE=$CROSS O=$OUT_DIR
    make $THREADs -C $KERNEL_DIR ARCH=$ARCH CROSS_COMPILE=$CROSS O=$OUT_DIR modules_install INSTALL_MOD_PATH=$OUT_DIR/__mod/
    if [ "$?" != "0" ]; then
	echo_c SC_RED "failed."
	exit 1
    fi
    exit 0
}

bisect(){

    patches_tmp=""
    patches_failed=0
    while true
    do
	pushd $KERNEL_DIR
	apply 1
	if [ "$?" != "0" ]; then
	    break
	fi
	popd

	cp $CONFIG_F $OUT_DIR/.config
	make $THREADs -C $KERNEL_DIR ARCH=$ARCH CROSS_COMPILE=$CROSS O=$OUT_DIR
	if [ "$?" != "0" ]; then
	    echo_c SC_RED "failed."
	    patches_tmp="$patches_tmp $curr"
	    patches_failed=$(($patches_failed + 1))
	else
	    cp $OUT_DIR/.config $CONFIG_F 
	    patches_tmp=""
	    patches_failed=0
	fi

	if [ $patches_failed -gt 1 ]; then
	    echo_c SC_RED "2 patches failed. exit"
	    echo "$patches_tmp"
	    exit 1
	fi
    done
}

set_env

case "$1" in
    "make")
	make
	;;
    "menuconfig")
	menuconfig
	;;
    "allyesmake")
	allyesmake
	;;
    *)
	echo_c SC_B_CYAN "Usage1: $0"
	echo_c SC_B_CYAN "\tbisect Verify"
	echo
	echo_c SC_B_CYAN "Usage2: $0 [cmd]"
	echo_c SC_B_CYAN "cmd:"
	echo_c SC_B_CYAN "\tmake menuconfig allyesmake"
	exit -1
esac
