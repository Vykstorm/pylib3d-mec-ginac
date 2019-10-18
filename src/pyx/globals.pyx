'''
Author: Víctor Ruiz Gómez
Description:
This file implements global function helpers
'''




######## Change gravity direction ########


def set_gravity_direction(state):
    '''set_gravity(state: int | str)
    Toggle gravity down or up.

    :param state:
        * If its True, 1 or "up", gravity is turned up.
        * If its False, 0 or "down", gravity is turned down.

    '''
    global c_gravity

    if not isinstance(state, (int, str)):
        raise TypeError('Input argument must be str or int')

    if isinstance(state, str):
        if state not in ('up', 'down'):
            raise TypeError('Possible values for gravity state are "up" and "down"')
        state = state == 'up'
    else:
        state = bool(state)

    c_gravity = state



def set_gravity_up():
    '''
    Toggle gravity up.
    '''
    set_gravity_direction(1)


def set_gravity_down():
    '''
    Toggle gravity down.
    '''
    set_gravity_direction(0)




def get_gravity_direction():
    '''get_gravity_direction() -> int
    Get the gravity direction. Returns 1 if it is turned up, and 0 if its down.

    :rtype: int

    '''
    return int(c_gravity)






######## Change atomization ########


def set_atomization_state(state):
    '''set_gravity(state: int | str)
    Toggle atomization on or off

    :param state:
        * If its True, 1 or "on", atomization is enabled
        * If its False, 0 or "off", atomization is disabled

    '''
    global c_atomization

    if not isinstance(state, (int, str)):
        raise TypeError('Input argument must be str or int')

    if isinstance(state, str):
        if state not in ('on', 'off'):
            raise TypeError('Possible values for atomization state are "on" and "off"')
        state = state == 'on'
    else:
        state = bool(state)

    c_atomization = state



def enable_atomization():
    '''
    Toggle atomization on
    '''
    set_atomization_state(1)


def disable_atomization():
    '''
    Toggle atomization off
    '''
    set_atomization_state(0)



def get_atomization_state():
    '''
    Returns 1 if atomization is enabled. 0 othwerwise.

    :rtype: int

    '''
    return int(c_atomization)
