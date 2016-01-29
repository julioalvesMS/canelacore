#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webbrowser
NEW_TAB = 2     # open in a new tab, if possible

GOOGLE_MAPS_SEARCH = "https://www.google.com.br/maps?q="


def search_in_maps(address):
    """
    Busca um endereço no google maps
    :param address: Endereço a ser buscado
    :type address: str
    :rtype: None
    """
    url = GOOGLE_MAPS_SEARCH + address.replace(' ', '+')
    webbrowser.open(url, new=NEW_TAB)
