#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libconfig.h>

struct Camconfig 
{
    int ncam;
    int saverate;
    int showrate;
    char *logpath;
    char *latestpath;

    int camid[4];
    char *serial[4];
};


void print_config(struct Camconfig camcfg) 
{
    puts("============================================================");
    puts(" Configurations");
    puts("============================================================");
    printf ("ncam       = %d\n", camcfg.ncam);
    printf ("saverate   = %d\n", camcfg.saverate);
    printf ("showrate   = %d\n", camcfg.showrate);
    printf ("logpath    = %s\n", camcfg.logpath);
    printf ("latestpath = %s\n", camcfg.latestpath);
    for (int i=0; i<4; i++) {
        puts("------------------------------------------------------------");
        printf ("%d\t camid      = %d\n", i, camcfg.camid[i]);
        printf ("%d\t serial     = %s\n", i, camcfg.serial[i]);
    }
    puts("============================================================");
    puts(" The End");
    puts("============================================================");
}


int load_config(char *fname, struct Camconfig *camcfg)
{
    config_t cfg;
    config_setting_t *setting;
    const char *str;
    int num;
    int saverate;
    int showrate;
    const char *logpath;
    const char *latestpath;
    //struct Camconfig camcfg[4];

    config_init(&cfg);

    int res = config_read_file(&cfg, fname);
  
    if (!res) {
        fprintf(stderr, "%s:%d - %s\n", config_error_file(&cfg),
                config_error_line(&cfg), config_error_text(&cfg));
        config_destroy(&cfg);

        return -1; //(EXIT_FAILURE);
    }

    if (config_lookup_int(&cfg, "Ncam", &num))
        printf ("number of cams : %d\n", num);
    else
        printf ("Ncam not found\n");

    if (config_lookup_int(&cfg, "saverate", &saverate))
        printf ("saverate : %d\n", saverate);
    else
        printf ("saverate not found\n");

    if (config_lookup_int(&cfg, "showrate", &showrate))
        printf ("showrate : %d\n", showrate);
    else
        printf ("showrate not found\n");

    if (config_lookup_string(&cfg, "logpath", &logpath))
        printf ("logpath : %s\n", logpath);

    if (config_lookup_string(&cfg, "latestpath", &latestpath))
        printf ("latestpath : %s\n", latestpath);

    puts("Configuration file loading finished.");

    int camid;
    const char *serial;
    int count; 
    int i;

    camcfg->ncam = num;
    camcfg->saverate = saverate;
    camcfg->showrate = showrate;
    camcfg->logpath = (char*) logpath;
    camcfg->latestpath = (char*) latestpath;

    setting = config_lookup(&cfg, "caminfo");
    if (setting != NULL) {
        count = config_setting_length(setting);

        for (i=0; i<count; i++) {
            config_setting_t *cam = config_setting_get_elem(setting, i);
            config_setting_lookup_int(cam, "camid", &camid);
            config_setting_lookup_string(cam, "serial", &serial);

            camcfg->camid[i] = camid;
            camcfg->serial[i] = (char*) serial;
        }
    }

    return 0;
}



int main1()
{
    struct Camconfig camcfg;

    const char *fname = "../ku.cfg";

    load_config((char*) fname, &camcfg);

    print_config(camcfg);
}

