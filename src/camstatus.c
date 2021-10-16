#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <pthread.h>

#include "camserial.h"
#include "irc_ctrl.c"
#include "libuvc/libuvc.h"
#include "LEPTON_SDK.h"
#include "LEPTON_SYS.h"
#include "LEPTON_RAD.h"

struct Irc_str cam;
static char* shutterPosition2string(LEP_SYS_SHUTTER_POSITION_E shutterPosition);

void exiting()
{
    if (detect_irc(cam)){
        uvc_unref_device(cam.dev);
    }
    uvc_exit(cam.ctx);
    printf("Device closed\n");

    exit(0);
}


void INThandler(int sig)
{
    signal(sig, SIG_IGN);
    exiting();
}

int checkshutter(int i)
{
    int idCam[4] = {1, 2, 3, 4};
    uvc_error_t              res;
    uvc_device_descriptor_t *desc;
    uvc_device_handle_t     *devh;

    LEP_CAMERA_PORT_DESC_T m_portDesc;

    signal (SIGINT, INThandler);

    cam.serial = (char*)serial[i];
    cam.idcam = idCam[i];

    res = uvc_init(&cam.ctx, NULL);
    if (res < 0) {
        uvc_perror(res, "uvc_init");
    }

    res = uvc_find_device(cam.ctx, &cam.dev, 0x1e4e, 0x0100, cam.serial);
    if (res < 0) {
        uvc_perror(res, "uvc_find_device");
        return -1;
    }

    uvc_get_device_descriptor(cam.dev, &desc);
    printf("Using %s %s with firmware %s\n", desc->manufacturer, desc->product, desc->serialNumber);

    res = uvc_open(cam.dev, &devh);
    if (res < 0) {
        uvc_perror(res, "uvc_open");
        uvc_unref_device(cam.dev);
        return -1;
    }

    m_portDesc.portID = 0;
    m_portDesc.portType = LEP_CCI_UVC;
    m_portDesc.userPtr = (void*) devh;
    //LEP_OpenPort(m_portDesc.portID, m_portDesc.portType, 0, &m_portDesc);
                
    //printf("LEPTON port opened\n");

    const uvc_extension_unit_t *units = uvc_get_extension_units(devh);

    uvc_device_t* dev_test;
    int bus, addr;

    dev_test = uvc_get_device(devh);
    bus = uvc_get_bus_number(dev_test);
    addr = uvc_get_device_address(dev_test);

    dev_test = uvc_get_device((uvc_device_handle_t*) m_portDesc.userPtr);
    bus = uvc_get_bus_number(dev_test);
    addr = uvc_get_device_address(dev_test);
    
    LEP_RESULT lres;
    LEP_SYS_SHUTTER_POSITION_E shutterPosition;
    LEP_SYS_FFC_SHUTTER_MODE_OBJ_T shutterModeObj;
    LEP_STATUS_T sysStatus;
    LEP_SYS_FFC_STATES_E ffcState;
    LEP_SYS_GAIN_MODE_E gainMode;
    LEP_SYS_GAIN_MODE_OBJ_T gainModeObj;
    
    lres = LEP_GetSysFfcShutterModeObj(&m_portDesc, &shutterModeObj);
    printf("shutter mode : %d\n", shutterModeObj.shutterMode);

    lres = LEP_GetSysShutterPosition(&m_portDesc, &shutterPosition);
    printf("shutter position : %s\n", shutterPosition2string(shutterPosition));
    
    lres = LEP_GetSysStatus(&m_portDesc, &sysStatus);
    printf("status : %d\t%d\n", sysStatus.camStatus, sysStatus.commandCount);

    lres = LEP_GetSysFFCStates(&m_portDesc, &ffcState);
    printf("ffcState : %d\n", ffcState);

    lres = LEP_GetSysGainMode(&m_portDesc, &gainMode);
    printf("gain mode : %d\n", gainMode);

    lres = LEP_GetSysGainModeObj(&m_portDesc, &gainModeObj);
    //printf("gain mode : %d\n", gainModeObj.sysGainModeROI);


    //lres = LEP_RunSysFFCNormalization(&m_portDesc);
    lres = LEP_RunRadFFC(&m_portDesc);

    if (detect_irc(cam)){
        uvc_unref_device(cam.dev);
    }
    uvc_exit(cam.ctx);
    puts ("");
}

int main()
{

    int i;

    for (i=0; i<4; i++) {
        checkshutter(i);
    }

    return 0;
}


static char* shutterPosition2string(LEP_SYS_SHUTTER_POSITION_E shutterPosition)
{
    static char* pos;

    printf("%d\n", shutterPosition);

    switch (shutterPosition) {
        case -1:
            pos = (char*)"UNKNOWN";
            break;
        case 0:
            pos = (char*)"IDLE";
            break;
        case 1:
            pos = (char*)"OPEN";
            break;
        case 2:
            pos = (char*)"CLOSED";
            break;
        case 3:
            pos = (char*)"BREAK_ON";
            break;
        case 4:
            pos = (char*)"END";
            break;
        default:
            pos = (char*)"DEFAULT?";
            break;
    }

    return pos;
}
