import os

import box
import yaml

def get_working():
    if 'SPLITTER_WORKING_PATH' in os.environ:
        env_working = os.environ["SPLITTER_WORKING_PATH"]
        print('working:', env_working)
        return env_working
    return '/working'

with open(get_working() + '/config.yml', 'r', encoding='utf8') as ymlfile:
    config = box.Box(yaml.safe_load(ymlfile))

    print('config:')
    for k, v in config.items():
        print(k, '=', v)


