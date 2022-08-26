# routines to read the status of sbc (small board computer).
import subprocess
import json

def diskusage():
    result = subprocess.run(['df', '-h', '/dev/mmcblk0p2'], stdout=subprocess.PIPE)

    result = result.stdout.decode('utf-8')
    result = result.split('\n')
    r0 = result[0].split()
    r1 = result[1].split()
    r0 = r0[:5]
    r1 = r1[:5]
    result[0] = '\t'.join(r0)
    result[1] = '\t'.join(r1)
    result = '\n'.join(result)

    return result


def temperature(unit=False):
    result = subprocess.run(['sensors', '-j'], stdout=subprocess.PIPE)
    j = json.loads(result.stdout.decode('utf-8'))
    T = float(j['ddr_thermal-virtual-0']['temp1']['temp1_input'])

    if unit:
        return f'{T}°C'
    else:
        return T


if __name__ == "__main__":
    print (diskusage())
    print (temperature())

