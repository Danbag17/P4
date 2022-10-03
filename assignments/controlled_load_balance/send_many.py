#!/usr/bin/env python3
import random
import socket
import sys

from scapy.all import IP, UDP, Ether, Raw, get_if_hwaddr, get_if_list, sendp

data = bytes('''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut maximus, lectus lacinia tempor mollis, eros nisi accumsan orci, vel pellentesque purus erat vel lacus. Curabitur sed mollis quam. Donec nunc enim, auctor et faucibus nec, ullamcorper eget odio. Etiam lectus purus, eleifend a blandit quis, placerat sit amet leo. Cras vel erat tellus. Sed malesuada dui eget sem hendrerit, quis finibus ipsum pellentesque. Nam sed nulla posuere, pretium neque non, molestie diam. Morbi elementum sapien tortor, ut gravida risus bibendum a. Praesent elementum neque ut volutpat pulvinar. Aliquam fringilla risus quis venenatis facilisis. In et metus id purus sollicitudin hendrerit.

Donec lobortis laoreet metus, quis fringilla dui fermentum sed. Nam neque risus, mattis quis diam sed, auctor hendrerit lorem. Quisque interdum pellentesque luctus. Cras cursus eleifend arcu at ullamcorper. Sed maximus molestie massa, nec posuere mauris interdum sit amet. Aliquam tincidunt, diam ut lacinia interdum, leo est mattis ipsum, vitae dapibus tortor mi ac lorem. Aliquam ullamcorper et nisi blandit pulvinar. Duis facilisis eros nisl, non condimentum tortor porta non. Nam id luctus orci. Curabitur fringilla bibendum lorem in vehicula.

Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Maecenas odio quam, suscipit sit amet nisl in, iaculis lobortis ante. Nam purus est, pretium in ullamcorper eget, vestibulum id lectus. Morbi nunc risus, ultrices sit amet elit ac, lacinia vehicula odio. Aliquam eu tincidunt massa. Morbi id aliquam enim. Mauris aliquet eros non ultrices accumsan. Nulla laoreet orci non varius cursus. Nam justo nisi, hendrerit nec lacinia eget, convallis nec tellus.

Aenean metus velit, imperdiet non ligula a, tristique pharetra eros. Curabitur egestas aliquam turpis in facilisis. Praesent in nisl non mauris bibendum porttitor in eget arcu. Sed sit amet fermentum arcu. Fusce nec turpis eget nulla porttitor pulvinar. Sed semper augue id elementum semper. Vestibulum facilisis lacinia risus ac pharetra. Integer quis ullamcorper massa. Duis pulvinar augue eu turpis rutrum, vel varius mi facilisis. Vestibulum ac enim porttitor, tempor tellus id, tempus enim. Aliquam vitae ligula id justo cursus gravida lobortis sed lacus. In tempor hendrerit justo placerat dignissim.

Curabitur vitae lectus pretium purus molestie pharetra et vel risus. Nulla ac urna egestas, ultrices risus vel, venenatis massa. Donec ac est turpis. Phasellus elementum accumsan mi sed sodales. Ut auctor odio felis, sed varius augue elementum ac. Vivamus id lorem vitae est efficitur dapibus. Nam euismod nunc in tempor posuere. Etiam vestibulum ultrices nisl, sit amet euismod justo ultrices quis. Nam eget ultrices nulla. In consequat convallis ornare. Interdum et malesuada fames ac ante ipsum primis in faucibus. ''', "UTF-8")

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def main():

    if len(sys.argv)<3:
        print('pass at least 3 arguments: <destination> <amount>')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print("sending on interface %s to %s" % (iface, str(addr)))
    pkt_n = int(sys.argv[2])
    for _ in range(pkt_n):
        pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff') / IP(dst=addr)
        pkt /= UDP(dport=1234, sport=random.randint(49152,65535))
        load_size = 2**random.randint(4, 10)
        pkt /= Raw(load=data*(load_size//len(data)) + data[:(load_size%len(data))])
        pkt.show2()
        sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
