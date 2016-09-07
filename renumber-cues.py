from qlab_interface import Interface

def process_group(interface, group_cue_no):
    group_cues = interface.get_cue_property(group_cue_no, 'children')
    subgroup_no = 0
    item_no = 0
    for cue_info in group_cues:
        cue_no = cue_info.get('number')
        item_no += 1
        new_no = '{}.{}'.format(group_cue_no, item_no)
        cue_name = interface.get_cue_property(cue_no, 'name')
        cue_type = interface.get_cue_property(cue_no, 'type')

        if cue_type == 'Fade':
            target = interface.get_cue_property(cue_no, 'cueTargetNumber')
            new_no = '{}.off'.format(target)

        interface.set_cue_property(cue_no, 'number', new_no)
        if cue_name:
            print(cue_no, new_no, cue_name)
        else:
            text = interface.get_cue_property(new_no, 'text')
            print(cue_no, new_no, repr(text))
        interface.client.send_message('/select/{}'.format(new_no))

        if cue_type == 'Group':
            process_group(interface, new_no)


def recursive_group_numbers(interface):
    current_group_cue_no = None
    last_act, last_scene = None, None
    while True:
        cue_no = interface.get_cue_property('selected', 'number')
        act, scene, _ = cue_no.split('.', 3)
        if act != last_act or scene != last_scene:
            item_no = 1
        else:
            item_no += 1
        last_act, last_scene = act, scene

        cue_name = interface.get_cue_property('selected', 'name')
        cue_type = interface.get_cue_property('selected', 'type')
        new_no  = '{act}.{scene}.{item_no}'.format(**locals())

        interface.set_cue_property(cue_no, 'number', new_no)
        if cue_name:
            print(cue_no, new_no, cue_name)
        else:
            text = interface.get_cue_property('selected', 'text')
            print(cue_no, new_no, repr(text))

        if cue_type == 'Group':
            process_group(interface, new_no)

        if cue_no == '41551':
            break

        interface.client.send_message('/select/next')


if __name__ == '__main__':
    interface = Interface()
    start_act = 4
    start_scene = 12
    interface.client.send_message('/select/{act}.{scene}.1'.format(act=start_act, scene=start_scene))
    recursive_group_numbers(interface)

