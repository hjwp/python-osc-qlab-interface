from pythonosc import osc_message_builder
from pythonosc import udp_client
import time

'''
[{"surfaceID":665967233,"surfaceName":"SR (FOHL) Over Office"}
{"surfaceID":376297370,"surfaceName":"ACT 3+4 SL (FOHR) Movable Wall"}
{"surfaceID":1365308873,"surfaceName":"Gauze"}
{"surfaceID":409960254,"surfaceName":"ACT 4 CSR (FOHL) Side wall"}
{"surfaceID":1807921094,"surfaceName":"ACT 4 Greenscreen"}
{"surfaceID":1274214856,"surfaceName":"ACT 1 SL (FOHR) Movable Wall"}
{"surfaceID":697728266,"surfaceName":"ACT 1 CS Back of greenscreen"}
{"surfaceID":614508151,"surfaceName":"ACT 1 CSR (FOHL) Movable wall"}
{"surfaceID":1680566531,"surfaceName":"ACT 2 TV Screen"}
{"surfaceID":1228735564,"surfaceName":"ACT 2 White Set Bottom"}
{"surfaceID":553983330,"surfaceName":"ACT 2 White Set Top"}
{"surfaceID":972709665,"surfaceName":"ACT 3 CSL (FOHR) Movable Wall"}
{"surfaceID":1092165396,"surfaceName":"ACT 3 CS Side of greenscreen"}
{"surfaceID":485575375,"surfaceName":"ACT 3 CSR (FOHL) Movable wall"}
{"surfaceID":334013770,"surfaceName":"ACT 3 Corner of greenscreen and movable wall (wood only)"}
{"surfaceID":1025656445,"surfaceName":"ACT 3 CS Grey bits of greenroom"}
{"surfaceID":948552935,"surfaceName":"Caracan roof"}
{"surfaceID":489520998,"surfaceName":"Act 4 SL donwstage flat"}]
'''

client = udp_client.UDPClient('localhost', 53000)

import markdown
from bs4 import BeautifulSoup

def load_titles(act_number):
    # all_titles = list(filter(bool, [quote.strip() for quote in open('act2.md.titles-only').read().replace('> ', '').split('\n\n')]))
    raw = open('captions/act{}.md'.format(act_number)).read()
    html = markdown.markdown(raw)
    soup = BeautifulSoup(html)
    quotes = soup.find_all('blockquote')
    captions = [q.get_text().strip().replace('\n', ' ') for q in quotes]
    #print('\n\n'.join(captions))
    return captions
 


def import_titles(titles):
    for i, text in enumerate(titles):
        add_cues(i, text)


def add_cues(i, text):
    cueno = 3 * i + 1
    select_msg1 = osc_message_builder.OscMessageBuilder(address='/select/{}'.format(cueno - 1))
    client.send(select_msg1.build())
    group_msg = osc_message_builder.OscMessageBuilder(address='/new')
    group_msg.add_arg('group')
    client.send(group_msg.build())
    fix_title_msg = osc_message_builder.OscMessageBuilder(address='/cue/selected/name')
    fix_title_msg.add_arg('Group: ' + text)
    client.send(fix_title_msg.build())

    select_msg2 = osc_message_builder.OscMessageBuilder(address='/select/{}'.format(cueno))
    client.send(select_msg2.build())

    new_msg = osc_message_builder.OscMessageBuilder(address='/new')
    new_msg.add_arg('titles')
    client.send(new_msg.build())
    # fix_text_msg = osc_message_builder.OscMessageBuilder(address='/cue/{}/text'.format(cueno))
    fix_text_msg = osc_message_builder.OscMessageBuilder(address='/cue/selected/text')
    fix_text_msg.add_arg(text)
    client.send(fix_text_msg.build())
    print(cueno, text)

    fade_msg = osc_message_builder.OscMessageBuilder(address='/new')
    fade_msg.add_arg('fade')
    client.send(fade_msg.build())

    fix_fade_target_msg = osc_message_builder.OscMessageBuilder(address='/cue/selected/cueTargetNumber')
    fix_fade_target_msg.add_arg(cueno) # this should be cueno once we manage to put texts inside groups
    client.send(fix_fade_target_msg.build())
    # select_msg3 = osc_message_builder.OscMessageBuilder(address='/select/{}'.format(cueno + 2))
    # client.send(select_msg3.build())
    fix_fade_timing_msg = osc_message_builder.OscMessageBuilder(address='/cue/selected/duration')
    fix_fade_timing_msg.add_arg(0) 
    client.send(fix_fade_timing_msg.build())
    fix_fade_stop_target_msg = osc_message_builder.OscMessageBuilder(address='/cue/selected/stopTargetWhenDone')
    fix_fade_stop_target_msg.add_arg(1) 
    client.send(fix_fade_stop_target_msg.build())
    fix_fade_opacity_msg = osc_message_builder.OscMessageBuilder(address='/cue/selected/opacity')
    fix_fade_opacity_msg.add_arg(0) 
    client.send(fix_fade_opacity_msg.build())
    time.sleep(0.1)

    
                    
        
if __name__ == '__main__':
    titles = []
    for i in range(1, 5):
        titles += load_titles(i)
    import_titles(titles)


