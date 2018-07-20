import logging
from json import load
from os.path import isdir
from time import time

import pandas as pd
from ete3 import Tree
from ete3 import TreeStyle


def get_setting(arg_setting_name, arg_settings):
    if arg_setting_name in arg_settings.keys():
        result = arg_settings[arg_setting_name]
        return result
    else:
        logger.warning('required key %s is not in the settings. Quitting.' % arg_setting_name)
        quit()


def check_existree_style(arg_folder_name, arg_descriptor):
    folder_existree_style = isdir(arg_folder_name)
    if folder_existree_style:
        logger.debug('using %s as the %s folder' % (arg_folder_name, arg_descriptor))
    else:
        logger.warning('%s %s does not exist. Quitting.' % (arg_descriptor, arg_folder_name))
        quit()


if __name__ == '__main__':
    start_time = time()

    formatter = logging.Formatter('%(asctime)s : %(name)s :: %(levelname)s : %(message)s')
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    console_handler.setLevel(logging.DEBUG)
    logger.debug('started')

    with open('./settings-example.json') as settings_fp:
        settings = load(settings_fp)
        logger.debug(settings)

    input_folder = get_setting('input_folder', settings)
    check_existree_style(input_folder, 'input')
    input_file = get_setting('input_file', settings)
    separator = get_setting('separator', settings)
    data = pd.read_csv(input_folder + input_file, sep=separator)
    logger.debug('initial data has shape %d rows x %d columns' % data.shape)

    data['first'] = data['AFSC'].apply(lambda x: x[:1])
    data['second'] = data['AFSC'].apply(lambda x: x[:2])
    data['third'] = data['AFSC'].apply(lambda x: x[:3])
    logger.debug('after parsing data has shape %d rows x %d columns' % data.shape)
    logger.debug('\n%s' % data.head(10))

    tree = Tree()
    for first in data['first'].unique():
        t0 = tree.add_child(name=first)
        for second in data[data['first'] == first]['second'].unique():
            t1 = t0.add_child(name=second)
            for third in data[data['second'] == second]['third'].unique():
                t2 = t1.add_child(name=third)
                afsc = data[data['third'] == third]['AFSC'].values[0]
                description = data[data['third'] == third]['Description'].values[0]
                t2.name = '{}: {}'.format(afsc, description)

    logger.debug(tree)
    tree_style = TreeStyle()
    tree_style.show_leaf_name = True
    tree_style.mode = "c"
    tree.show(tree_style=tree_style)
    # tree.show()

    logger.debug('done')
    finish_time = time()
    elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
    elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
    logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
    console_handler.close()
    logger.removeHandler(console_handler)
