#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <pthread.h>

#include "irc_ctrl.c"
//#include "camserial.h"
#include "irc_config.c"
#include "libuvc/libuvc.h"

struct Irc_str cams[4];

char *config_fname = "./configs/gb.cfg";

void exiting()
{
    for (int i=0; i<4; i++) {
        if (detect_irc(cams[i])){
            uvc_unref_device(cams[i].dev);
        }
        uvc_exit(cams[i].ctx);
        printf("Device #%d closed\n", i);
    }
    exit(0);
}


void INThandler(int sig)
{
    signal(sig, SIG_IGN);
    exiting();
}

int main(int argc, char* argv[])
{

    int i;

    int idCam[4] = {1, 2, 3, 4};

    int irc_flag[4]  = {0, };
    int proc_flag[4] = {0, };

    pid_t pid[4];
    pthread_t pthread[4];

    uvc_error_t          res;

    signal (SIGINT, INThandler);

    struct Camconfig camcfg;
    if (argc == 2)
        config_fname = argv[1];

    load_config(config_fname, &camcfg);
    print_config(camcfg);

    for (i=0; i<4; i++) {
        cams[i].serial = (char*) camcfg.serial[i];
        cams[i].idcam = camcfg.camid[i];
        cams[i].saverate = camcfg.saverate;
        cams[i].showrate = camcfg.showrate;
        cams[i].logpath = camcfg.logpath;
        cams[i].latestpath = camcfg.latestpath;
        cams[i].sun_alt_threshold = camcfg.sun_alt_threshold;
        cams[i].debug = camcfg.debug;

        res = uvc_init(&cams[i].ctx, NULL);
        if (res < 0) {
            uvc_perror(res, "uvc_init");
        }
    }
    puts ("UVC initialized");


    long int logcnt = 0;
    int strmlogflg = 1;
    while (1) {

        for (i=0; i<4; i++) {
            res = uvc_find_device(cams[i].ctx, &cams[i].dev, 0x1e4e, 0x0100, cams[i].serial);
            if (res < 0) {
                uvc_perror(res, "uvc_find_device");
                irc_flag[i] = 0;
                proc_flag[i] = 0;
            }
            else {
                if (irc_flag[i] == 0) {
                    res = uvc_init(&cams[i].ctx, NULL);
                    res = uvc_find_device(cams[i].ctx, &cams[i].dev, 0x1e4e, 0x0100, cams[i].serial);
                    irc_flag[i] = 1;
                    proc_flag[i] = 0;
                }
            }
        }

        for (i=0; i<4; i++) {
            if (irc_flag[i] == 1) {
                if (proc_flag[i] == 0) {
                    printf("starting process for device #%d\n", i);
                    pid[i] = pthread_create(&pthread[i], NULL, stream_proc_shutter, (void*) &cams[i]);
                    if (pid[i] < 0) {
                        perror("process create error");
                        proc_flag[i] = 0;
                    }
                    else {
                        printf("process %d created \n", pid[i]);
                        proc_flag[i] = 1;
                        pthread_detach(pthread[i]);
                        strmlogflg = 1;
                    }
                    //sleep(2);
                }
                else {
                    if (strmlogflg) {  
                        printf("streaming for device #%d\n", i);
                    }
                }
            }
            else if (irc_flag[i] == 0) {
                if (proc_flag[i] == 1) {
                    printf("stopping process for device #%d\n", i);
                    proc_flag[i] = 0;
                }
                else {
                    printf("waiting for device #%d\n", i);
                    proc_flag[i] = 0;
                }
            }
        }
        //printf("\n");
        if (logcnt == 200) {
            logcnt = 0;
            strmlogflg = 1;
        }
        else {
            logcnt++;
            strmlogflg = 0;
        }

        sleep (3);
    }

    atexit(exiting);

    return 0;
}

