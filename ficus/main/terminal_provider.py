import platform

from ficus.metatrader.MacTerminal import MacTerminal
from ficus.metatrader.MetatraderTerminal import MetatraderTerminal


def provide_trading_terminal():
    if platform.system() == 'Darwin':
        return MacTerminal()
    else:
        return MetatraderTerminal()
