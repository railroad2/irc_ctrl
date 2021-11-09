#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <sys/stat.h>
#include <string.h>

#include "libuvc/libuvc.h"
#include "detect_sun.c"
#include "shutter_ctrl.c"

const int nCam = 4;

struct Imginfo {
    int ncam;
    char isotstr[20];
    int camstat;
    int sunflag;
    int moonflag;
};

struct Irc_str {
    int idcam;
    char* serial;
    uvc_context_t* ctx;
    uvc_device_t* dev;

    int saverate;
    int showrate;
    char *logpath;
    char *latestpath;
    double sun_alt_threshold; 
    int debug;
};

char* get_isot() 
{
    char *isotstr = malloc(20);
    time_t rawtime = time(NULL);
    struct tm *nowtm = localtime(&rawtime);

    int year = nowtm->tm_year + 1900;
    int month = nowtm->tm_mon + 1;
    int day = nowtm->tm_mday;
    int hour = nowtm->tm_hour;
    int min = nowtm->tm_min;
    int sec = nowtm->tm_sec;

    snprintf(isotstr, 20, "%04d-%02d-%02dT%02d:%02d:%02d", year, month, day, hour, min, sec);

    return isotstr;
}

int fwrite_header(struct Imginfo *info, FILE *file)
{
    return 0; 
}

int detect_irc(struct Irc_str cam)
{
    uvc_error_t res;
    uvc_device_t* tmp;
    int stat;

    res = uvc_find_device(cam.ctx, &cam.dev, 0x1e4e, 0x0100, cam.serial);
    if (res < 0) {
        uvc_perror(res, "uvc_find_device");
        stat = 0;
    }
    else{
        stat = 1;
    }

    return stat;
}


int do_nuc(LEP_CAMERA_PORT_DESC_T *m_portDesc)
{
    LEP_RESULT lres;
    LEP_RunSysFFCNormalization(m_portDesc);
    return 0;
}


void cb(uvc_frame_t *frame, void *ptr)
{
    int seq = frame->sequence;
    struct Irc_str cam = *((struct Irc_str *) ptr);
    int showrate = cam.showrate;
    int saverate = cam.saverate;
    int showflg = 0;
    int saveflg = 0;

    //printf("%d ", seq);
    /* capture every 9 frame */
	//if (seq % 90 != 0)
    if (seq % saverate == 0) {
        saveflg = 1;
        showflg = 1;
    }
    else if (seq % showrate == 0) {
        showflg = 1;
    }
    else {
        return;
    }

    const int len    = frame->data_bytes;
    const int width  = frame->width;
    const int height = frame->height;

    unsigned short *pix = (unsigned short*) frame->data;
    int i;

    char fileName[200];
    char dirName[150]; 
    char datestr[20];
    char isotstr[20];
    struct Imginfo info;
    //int ncam = *(int*) ptr;
    int ncam = cam.idcam;
    char *logpath = cam.logpath;
    char *latestpath = cam.latestpath;
    
    char *isottmp = get_isot();
    char hour[3];
    strcpy(isotstr, get_isot());
    hour[0] = isottmp[11];
    hour[1] = isottmp[12];
    hour[2] = '\0';
    free (isottmp);

    strncpy(datestr, isotstr, 10);
    datestr[10] = '\0';

    strncpy(info.isotstr, isotstr, strlen(isotstr));
    info.ncam = ncam;
    info.camstat = 0;
    info.sunflag = 0;
    info.moonflag = 0;

    /* debug  */
    if (cam.debug) {
        printf ("%s\n", info.isotstr);
        printf ("%d\n", info.camstat);
        printf ("%d\n", info.ncam);
        printf ("%d\n", info.sunflag);
        printf ("%d\n", info.moonflag);
        printf ("%s\n", logpath);
        printf ("%s\n", latestpath);
    }

    if (saveflg) {
        snprintf(dirName, 150, "%s", logpath);
        mkdir(dirName, 0777);
        snprintf(dirName, 150, "%s/%s", logpath, datestr);
        mkdir(dirName, 0777);
        snprintf(dirName, 150, "%s/%s/%s", logpath, datestr, hour);
        mkdir(dirName, 0777);
        snprintf(fileName, 200, "%s/%s-cam%d", dirName, isotstr, ncam);

        FILE *file  = fopen(fileName, "w+");
        if (file == NULL)
        {
            printf ("[Error] Cannot open logging file\n");
            return ; 
        }

        fwrite(pix, len , 1, file);
        fclose(file);
    }

    if (showflg) {
        char fileName1[64];
        snprintf(fileName1, 64, "%s/latest_cam%d", latestpath, ncam);

        FILE *file1  = fopen(fileName1, "w");
        if (file1 == NULL)
        {
            printf ("[Error] Cannot open logging file\n");
            return ; 
        }

        fwrite(pix, len , 1, file1);
        fclose(file1);
    }
}


//int stream_proc(struct Irc_str cam)
void *stream_proc(void *camptr)
{ 
    int stat;
    struct Irc_str cam = *((struct Irc_str *) camptr);
    uvc_error_t res; 
    uvc_device_handle_t* devh;
    uvc_stream_ctrl_t ctrl;

    stat = detect_irc(cam);

    res = uvc_open(cam.dev, &devh);
    if (res < 0) {
        uvc_perror(res, "uvc_open");
        uvc_unref_device(cam.dev);
        return (void*)-1;
    }

    res = uvc_get_stream_ctrl_format_size(
            devh, &ctrl, UVC_FRAME_FORMAT_Y16, 
            160, 120, 9);
    if (res < 0) {
        uvc_perror(res, "get_mode");
        uvc_close(devh);
        uvc_unref_device(cam.dev);
        return (void*)-1;
    }

    res = uvc_start_streaming(devh, &ctrl, cb, (void*) &cam.idcam, 0);
    if (res < 0) {
        uvc_perror(res, "start_streaming");
        printf("Error with Cam %d\n", cam.idcam);
        uvc_stop_streaming(devh);
        uvc_close(devh);
        uvc_unref_device(cam.dev);
        return (void*)-1;
    }

    while (1) {
        sleep(5);
        stat = detect_irc(cam);
        if (stat == 0){
            puts("Device not found");
            uvc_stop_streaming(devh);
            uvc_close(devh);
            uvc_unref_device(cam.dev);
            return (void*)-1;
        }
    }

    uvc_close(devh);
    uvc_unref_device(cam.dev);
    return (void*) 0;
}


void *stream_proc_shutter(void *camptr)
{ 
    int stat;
    int sunflag = 0;
    int sunwait = 0 ;

    struct Irc_str cam = *((struct Irc_str *) camptr);
    uvc_error_t res; 
    uvc_device_handle_t* devh;
    uvc_stream_ctrl_t ctrl;

    LEP_RESULT lres;
    LEP_CAMERA_PORT_DESC_T m_portDesc;

    stat = detect_irc(cam);

    res = uvc_open(cam.dev, &devh);
    if (res < 0) {
        uvc_perror(res, "uvc_open");
        uvc_unref_device(cam.dev);
        return (void*)-1;
    }
    shutter_ctrl(devh, 0);
    shutter_ctrl(devh, 1);

    m_portDesc.portID = 0;
    m_portDesc.portType = LEP_CCI_UVC;
    m_portDesc.userPtr = (void*) devh;
    
    do_nuc(&m_portDesc);

STARTSTREAMING:
    res = uvc_get_stream_ctrl_format_size(
            devh, &ctrl, UVC_FRAME_FORMAT_Y16, 
            160, 120, 9);
    if (res < 0) {
        uvc_perror(res, "get_mode");
        uvc_close(devh);
        uvc_unref_device(cam.dev);
        return (void*)-1;
    }

    //uvc_set_ae_mode(devh, 2);
    //res = uvc_start_streaming(devh, &ctrl, cb, (void*) &cam.idcam, 0);
    res = uvc_start_streaming(devh, &ctrl, cb, camptr, 0);
    if (res < 0) {
        uvc_perror(res, "start_streaming");
        printf("Error with Cam %d\n", cam.idcam);
        uvc_stop_streaming(devh);
        uvc_close(devh);
        uvc_unref_device(cam.dev);
        return (void*)-1;
    }

    while (1) {
        sleep(5);
        stat = detect_irc(cam);
        if (stat == 0){
            puts("Device not found");
            uvc_stop_streaming(devh);
            uvc_close(devh);
            uvc_unref_device(cam.dev);
            return (void*)-1;
        }
        
        sunflag = detect_sun(cam.idcam, cam.sun_alt_threshold);

        if (sunflag == 1) {
            puts("Sun detected");
            uvc_stop_streaming(devh);
            shutter_ctrl(devh, 0);
            sunwait = 1;
        }
        else if (sunflag == 0) {
            if (sunwait == 1) {
                puts("Sun is gone");
                sunwait = 0;
                shutter_ctrl(devh, 1);
                goto STARTSTREAMING;
            }
        }

    }

    uvc_close(devh);
    uvc_unref_device(cam.dev);
    return (void*) 0;
}


