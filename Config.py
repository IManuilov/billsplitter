import os

import box
import yaml

with open('./config.yml', 'r', encoding='utf8') as ymlfile:
    config = box.Box(yaml.safe_load(ymlfile))

    print('config:')
    for k, v in config.items():
        print(k, '=', v)


