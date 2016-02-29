#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import core


# -- Available Routines --

UPDATE = 131
BACKUP = 132
NOTIFY_EXPENSES = 133
NOTIFY_INCOMES = 134

ACTTIVE_ROUTINES = list()


# -- Routine Management functions --


def add_to_be_done(parent, to_be_done, routine_type, time=None):
    """
    Adiciona uma rotina a ser executada
    :param wx.Window parent: Frame de origem da Rotina
    :param to_be_done: Função que será executada
    :param int routine_type: Tipo da rotina (Executada no icício do programa, no fim, etc)
    :param str time: Hora em que deve ser executada
    :return:
    """
    my_routine = None

    for routine in ACTTIVE_ROUTINES:
        if routine_type != routine.routine_type or time != routine.time:
            continue
        my_routine = routine
        break

    if not my_routine:
        my_routine = Routine(parent, routine_type, time)

    my_routine.add(to_be_done)


def start_routines(routine_type):
    """
    Inicia todas as rotinas de um determinado tipo
    :param int routine_type: Tipo da rotina a ser inicializada
    :return bool: True caso alguma rotina tenha sido iniciada
    """
    activated = False
    for routine in ACTTIVE_ROUTINES:
        if routine.routine_type == routine_type:
            routine.start()
            activated = True

    return activated


def on_start():
    """
    Inicia todas as rotinas do tipo que são realizadas ao abrir o programa
    :return bool: True caso alguma rotina tenha sido iniciada
    """
    return start_routines(core.ON_START)


def on_close():
    """
    Inicia todas as rotinas do tipo que são realizadas ao fechar o programa
    :return bool: True caso alguma rotina tenha sido iniciada
    """
    return start_routines(core.ON_CLOSE)


def on_time():
    """
    Inicia todas as rotinas do tipo que são realizadas em um determinado horário
    :return bool: True caso alguma rotina tenha sido iniciada
    """
    return start_routines(core.ON_TIME)


def clear_routines():
    for routine in ACTTIVE_ROUTINES:
        routine.destroy()


def update_routines(parent=None):

    clear_routines()

    import settings as st
    import core_gui as gui
    notify_expenses = st.config2type(st.CONFIG.get(st.CONFIG_SECTION_NOTIFICATIONS, st.CONFIG_FIELD_NOTIFY_EXPENSES),
                                     bool)
    notify_incomes = st.config2type(st.CONFIG.get(st.CONFIG_SECTION_NOTIFICATIONS, st.CONFIG_FIELD_NOTIFY_INCOMES),
                                    bool)
    if notify_expenses or notify_incomes:
        transaction_frequency = st.config2type(st.CONFIG.get(st.CONFIG_SECTION_NOTIFICATIONS,
                                               st.CONFIG_FIELD_TRANSACTIONS_FREQUENCY), str)
        transaction_selections = gui.FrequencyPanel.get_selections_from_string(transaction_frequency)

        if notify_expenses:
            frequency2routine(parent, NOTIFY_EXPENSES, transaction_selections)
        if notify_incomes:
            frequency2routine(parent, NOTIFY_INCOMES, transaction_selections)

    on_time()


def frequency2routine(parent, to_be_done, selections):
    """
    Cria uma rotina a partir dos dados de um FrequencyPanel
    :param int to_be_done: Que tipo de rotina deve ser executada
    :param wx.Window parent: Frame pai
    :param core_gui.FrequencyPanel.FrequencySelections selections:
    :return:
    """
    if core.ON_START in selections.options:
        add_to_be_done(parent, to_be_done, core.ON_START)
    if core.ON_CLOSE in selections.options:
        add_to_be_done(parent, to_be_done, core.ON_CLOSE)
    if core.ON_TIME in selections.options:
        add_to_be_done(parent, to_be_done, core.ON_TIME, time=selections.time)


#  -- Routines Actions --


def notify_pendant_transactions(transaction_type, parent=None):
    import database
    import dialogs

    # TODO adicionar confifuração para selecionar quantos dias antes ser notificado

    today = core.datetime_today()[0]
    limit_day = core.int2date(core.date2int(today) + 3)

    db = database.TransactionsDB()
    transactions = db.pendant_transactions_list(up_to=limit_day)
    db.close()

    for exchange in transactions:
        if exchange.type == transaction_type:
            gui_line.open(dialogs.TransactionNotification, parent, exchange, title=exchange.description)


def notify_pendant_expenses(parent=None):
    from transaction import EXPENSE
    notify_pendant_transactions(EXPENSE, parent)


def notify_pendant_incomes(parent=None):
    from transaction import INCOME
    notify_pendant_transactions(INCOME, parent)


# -- Routine Class


class Routine(object):

    __actions = {
        NOTIFY_EXPENSES: notify_pendant_expenses,
        NOTIFY_INCOMES: notify_pendant_incomes
    }

    def __init__(self, parent, routine_type, time=None):

        self.routine_type = routine_type
        self.time = time
        self.parent = parent

        self.timer = None

        self.__to_be_done = list()

        ACTTIVE_ROUTINES.append(self)

    def add(self, to_be_done):
        self.__to_be_done.append(to_be_done)

    def start(self):
        if self.routine_type == core.ON_TIME:
            time_now = core.hour2int(core.datetime_today()[1][:-3])
            time_objective = core.hour2int(self.time)
            minutes_to_exec = time_objective - time_now

            if minutes_to_exec < 0:
                self.destroy()
                return

            self.timer = threading.Timer(60*minutes_to_exec, self.execute)
            self.timer.start()

        elif self.routine_type == core.ON_START:
            thread = threading.Timer(3, self.execute)
            thread.start()

        else:
            self.execute()

    def execute(self):
        for key in self.__actions:
            if key in self.__to_be_done:
                self.__actions[key](self.parent)

        gui_line.run_list()
        self.destroy()

    def destroy(self):
        ACTTIVE_ROUTINES.remove(self)
        if self.timer:
            self.timer.cancel()


class Gui(object):
    __line = list()
    opening = False

    def open(self, window, *args, **kwargs):
        self.__line.append((window, args, kwargs))

    def run_list(self):
        if not len(self.__line):
            return

        item = self.__line[0]

        self.__open(item[0], item[1], item[2])

        self.__line.remove(item)

        self.run_list()

    def __open(self, window, args, kwargs):
        self.opening = True
        window(*args, **kwargs)
        self.opening = False

gui_line = Gui()

update_routines()
