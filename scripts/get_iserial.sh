#!/bin/bash
lsusb -d 1e4e:0100 -v |  grep iSerial 2>null | grep Serial
