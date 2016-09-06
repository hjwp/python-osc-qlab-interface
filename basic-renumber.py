from qlab_interface import Interface

def _fix_simple_cue_numbers(interface):
    while True:
        cue_no = interface.get_cue_property('selected', 'number')
        print(cue_no)
        if cue_no:
            act = int(cue_no[:1])
            if act > 4:
                break
            scene = int(cue_no[1:3])
            number = int(cue_no[3:])
            new_no = '{}.{}.{}'.format(act, scene, number)
            interface.set_cue_property('selected', 'number', new_no)

        interface.client.send_message('/select/next')

if __name__ == '__main__':
    interface = Interface()
    interface.client.send_message('/select/40818')
    _fix_simple_cue_numbers(interface)

