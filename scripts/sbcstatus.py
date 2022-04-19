# routines to read the status of sbc (small board computer).
import subprocess
import json

def diskusage():
    result = subprocess.run(['df', '-h', '/dev/mmcblk0p2'], stdout=subprocess.PIPE)

    return result.stdout.decode('utf-8')


def sbctemperature():
    result = subprocess.run(['sensors', '-j'], stdout=subprocess.PIPE)
    j = json.loads(result.stdout.decode('utf-8'))
    T = j['ddr_thermal-virtual-0']['temp1']['temp1_input']

    return T


if __name__ == "__main__":
    print (diskusage())
    print (sbctemperature())

