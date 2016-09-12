from qlab_interface import Interface

ROMANS = {
    1: 'I',
    2: 'II',
    3: 'III',
    4: 'IV',
    5: 'V',
    6: 'VI',
    7: 'VII',
    8: 'VIII',
    9: 'IX',
    10: 'X',
    11: 'XI',
    12: 'XII',
    13: 'XIII',
    14: 'XIV',
    15: 'XV',
    16: 'XVI',
}

def _fix_scene_numbers(interface):
    last_cue_no = None
    while True:
        cue_no = interface.select_next_cue()
        if cue_no and '--' in cue_no:
            if cue_no == last_cue_no:
                return
            last_cue_no = cue_no

            act, rest = cue_no.split('--')
            act = int(act)
            scene, rest = rest.split('.', 1)
            scene = int(scene)
            new_no = '{}-{}  {}'.format(act, ROMANS[scene], rest)
            interface.set_cue_property('selected', 'number', new_no)

if __name__ == '__main__':
    interface = Interface()
    interface.client.send_message('/select/4.12.0')
    _fix_scene_numbers(interface)

