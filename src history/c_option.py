#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shelve

s = shelve.open("options.txt")

s["umoney"] = u"Dinheiro"
s["ucard"] = u"Cartão"

s.close()