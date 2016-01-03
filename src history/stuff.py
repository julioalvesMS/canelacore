#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shelve
import time

try:
    current_dir = os.path.realpath(os.curdir)


    s = shelve.open(current_dir + "\\options.txt")
    for root, folder, files in os.walk("saves"):
        for i in files:
            print i
            if len(i) == 14:
                a = shelve.open(current_dir + "\\saves\\" + i)
                for j in a["sales"]:
                    print j
                    u = a["sales"]
                    if u[j]["payment"] == s["card"]:
                        u[j]["payment"] = u"Cartão"
                        print 2
                    elif u[j]["payment"] == s["money"]:
                        u[j]["payment"] = u"Dinheiro"
                        print 1
                    else:
                        print 0
                    a["sales"] = u
                    print a["sales"][j]["payment"]
                a.close()
    s.close()
except Exception, e:
    print e
    time.sleep(100)