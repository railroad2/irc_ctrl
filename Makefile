
CC=gcc -x c
FLAGS= -I/usr/include/opencv4 \
	   -I/usr/local/include \
	   -lmysqlclient -L/usr/local/lib \
	   -luvc -lopencv_core -lopencv_imgcodecs -lpthread \
	   -lconfig

LIBROOT=/usr/local
INC=-I$(LIBROOT)/include 
LIBLEP=-L$(LIBROOT)/lib -llepton -lm
LIBSOL=-L/usr/local/lib -lSolTrack -lm



daemon: src/irc_daemon.c
	$(CC) -o irc_daemon src/irc_daemon.c $(FLAGS) $(LIBSOL) $(LIBLEP) $(INC)

all: daemon module shutter sunpos checkshutter

module: src/irc_module.c
	$(CC) -o irc_module src/irc_module.c $(FLAGS)
	

single: src/singlecam.c
	$(CC) -o singlecam src/singlecam.c  $(FLAGS)


shutter: src/shutter.c
	$(CC) -o shutter src/shutter.c $(FLAGS) $(INC) $(LIBLEP) $(LIBSOL)


sunpos: src/sunpos.c
	$(CC) -o sunpos src/sunpos.c $(LIBSOL)
	
checkshutter: src/checkshutter.c
	$(CC) -o checkshutter src/checkshutter.c $(FLAGS) $(INC) $(LIBLEP) $(LIBSOL)
	
camstatus: src/camstatus.c
	$(CC) -o camstatus src/camstatus.c $(FLAGS) $(INC) $(LIBLEP) $(LIBSOL)

test:
	LD_LIBRARY_PATH=/storage/irc/GetThermal/source/libuvc/build/ ./singlecam 0015002c-5119-3038-3732-333700000000 1 &
	LD_LIBRARY_PATH=/storage/irc/GetThermal/source/libuvc/build/ ./singlecam 0013001c-5113-3437-3335-373400000000 2 &
	LD_LIBRARY_PATH=/storage/irc/GetThermal/source/libuvc/build/ ./singlecam 00070029-5102-3038-3835-393400000000 3 &
	LD_LIBRARY_PATH=/storage/irc/GetThermal/source/libuvc/build/ ./singlecam 8010800b-5113-3437-3335-373400000000 4 &

install:
	cp irc_daemon /home/gb/bin/
	mkdir log

install_service:
	cp services/*.service /etc/systemd/system/

clean:
	rm irc_module irc_daemon singlecam shutter sunpos checkshutter
