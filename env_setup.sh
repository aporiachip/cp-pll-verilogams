#!/bin/bash
export CADHOME=/opt/cadence
export CDS=$CADHOME/IC618
export MMSIMHOME=$CADHOME/SPECTRE231
export CDS_LIC_FILE=$CDS/share/license/license.dat
export CDS_LIC_ONLY=1
export CDS_AUTO_64BIT=ALL
export LANG=C
export CDS_Netlisting_Mode=Analog
export PATH=$PATH:$CADHOME/XCELIUM2309/bin:$CADHOME/XCELIUM2309/tools/bin:$MMSIMHOME/bin:$MMSIMHOME/tools/bin
export LD_LIBRARY_PATH=$CADHOME/XCELIUM2309/tools/lib/64bit:$CADHOME/XCELIUM2309/tools/lib
