from qlab_interface import Interface


def _fix_act_numbers(interface):
    last_cue_no = None
    while True:
        cue_no = interface.get_cue_property('selected', 'number')
        if cue_no:
            if cue_no == last_cue_no:
                return
            last_cue_no = cue_no

            act = int(cue_no[:1])
            assert cue_no[1] == '.'
            rest = cue_no[2:]
            new_no = '{}--{}'.format(act, rest)
            interface.set_cue_property('selected', 'number', new_no)

        interface.client.send_message('/select/next')

if __name__ == '__main__':
    interface = Interface()
    interface.client.send_message('/select/4.12.0')
    _fix_act_numbers(interface)

