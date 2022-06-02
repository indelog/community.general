# -*- coding: utf-8 -*-
# Copyright: (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import json
import yaml

from unittest.mock import mock_open

from ansible_collections.community.general.plugins.modules.files.yaml_file import YamlFile
from ansible_collections.community.general.tests.unit.plugins.module_utils.test_data_merge_utils import (
    DICT_CURRENT,
    DICT_MODIF,
    DICT_EXPECTED_PRESENT,
    DICT_EXPECTED_ABSENT)

DEFAULT_MODULE_ARGS = dict([
    [key, val.get('default')]
    for key, val in YamlFile.module['argument_spec'].items()
    if val.get('default') is not None])

FAKE_PATH = '/path/to/fake/file.yaml'
YAML_CURRENT = yaml.safe_dump(
    DICT_CURRENT,
    indent=DEFAULT_MODULE_ARGS['indent'],
    explicit_start=DEFAULT_MODULE_ARGS['explicit_start'],
    explicit_end=DEFAULT_MODULE_ARGS['explicit_end'],
    sort_keys=DEFAULT_MODULE_ARGS['sort_keys'],
    default_flow_style=DEFAULT_MODULE_ARGS.get('default_flow_style'),
    canonical=DEFAULT_MODULE_ARGS['canonical'],
    width=DEFAULT_MODULE_ARGS['width'],
)


TEST_CASE_EXEC = [
    [
        {'path': FAKE_PATH, 'value': DICT_CURRENT},
        {
            'id': 'test_dest_not_changed',
            'expected_value': DICT_CURRENT,
            'read_data': YAML_CURRENT,
            'expected_changed': False,
        },
    ],
    [
        {'path': FAKE_PATH, 'value': DICT_MODIF, 'state': 'present'},
        {
            'id': 'test_changed_present',
            'expected_value': DICT_EXPECTED_PRESENT,
            'read_data': YAML_CURRENT,
            'expected_changed': True,
        },
    ],
    [
        {'path': FAKE_PATH, 'value': DICT_MODIF, 'state': 'absent'},
        {
            'id': 'test_changed_absent',
            'expected_value': DICT_EXPECTED_ABSENT,
            'read_data': YAML_CURRENT,
            'expected_changed': True,
        },
    ],
    [
        {'path': FAKE_PATH, 'value': DICT_MODIF, 'state': 'identic'},
        {
            'id': 'test_changed_identic',
            'expected_value': DICT_MODIF,
            'read_data': YAML_CURRENT,
            'expected_changed': True,
        },
    ],
    [
        {'path': FAKE_PATH, 'value': DICT_CURRENT,
            'indent': 8, 'diff_on_value': False},
        {
            'id': 'test_reformat_on_indent',
            'expected_value': yaml.safe_dump(
                DICT_CURRENT,
                indent=8,
                explicit_start=DEFAULT_MODULE_ARGS['explicit_start'],
                explicit_end=DEFAULT_MODULE_ARGS['explicit_end'],
                sort_keys=DEFAULT_MODULE_ARGS['sort_keys'],
                default_flow_style=DEFAULT_MODULE_ARGS.get('default_flow_style'),
                canonical=DEFAULT_MODULE_ARGS['canonical'],
                width=DEFAULT_MODULE_ARGS['width'],
            ).splitlines(keepends=True),
            'read_data': YAML_CURRENT,
            'expected_changed': True,
        },
    ],
    [
        {'path': FAKE_PATH, 'value': DICT_CURRENT,
            'sort_keys': True, 'diff_on_value': False},
        {
            'id': 'test_reformat_on_sort_keys',
            'expected_value': yaml.safe_dump(
                DICT_CURRENT,
                indent=DEFAULT_MODULE_ARGS['sort_keys'],
                explicit_start=DEFAULT_MODULE_ARGS['explicit_start'],
                explicit_end=DEFAULT_MODULE_ARGS['explicit_end'],
                sort_keys=True,
                default_flow_style=DEFAULT_MODULE_ARGS.get('default_flow_style'),
                canonical=DEFAULT_MODULE_ARGS['canonical'],
                width=DEFAULT_MODULE_ARGS['width'],
            ).splitlines(keepends=True),
            'read_data': YAML_CURRENT,
            'expected_changed': True,
        },
    ],
    [
        {'path': FAKE_PATH, 'value': DICT_CURRENT,
            'explicit_end': True, 'diff_on_value': False},
        {
            'id': 'test_reformat_on_explicit_end',
            'expected_value': yaml.safe_dump(
                DICT_CURRENT,
                indent=DEFAULT_MODULE_ARGS['sort_keys'],
                explicit_start=DEFAULT_MODULE_ARGS['explicit_start'],
                explicit_end=True,
                sort_keys=DEFAULT_MODULE_ARGS['sort_keys'],
                default_flow_style=DEFAULT_MODULE_ARGS.get('default_flow_style'),
                canonical=DEFAULT_MODULE_ARGS['canonical'],
                width=DEFAULT_MODULE_ARGS['width'],
            ).splitlines(keepends=True),
            'read_data': YAML_CURRENT,
            'expected_changed': True,
        },
    ],
    [
        {'path': FAKE_PATH, 'value': DICT_CURRENT, 'diff_on_value': True},
        {
            'id': 'empty_file_diff_on_value',
            'expected_value': DICT_CURRENT,
            'read_data': None,
            'expected_changed': True,
        },
    ],
    [
        {'path': FAKE_PATH, 'value': DICT_CURRENT, 'diff_on_value': False},
        {
            'id': 'empty_file_no_diff_on_value',
            'expected_value': YAML_CURRENT.splitlines(keepends=True),
            'read_data': None,
            'expected_changed': True,
        },
    ],
    [
        {'path': FAKE_PATH, 'value': DICT_CURRENT, 'diff_on_value': True},
        {
            'id': 'blank_file_diff_on_value',
            'expected_value': DICT_CURRENT,
            'read_data': '\n\t\n   ',
            'expected_changed': True,
        },
    ],
    [
        {'path': FAKE_PATH, 'value': DICT_CURRENT, 'diff_on_value': False},
        {
            'id': 'blank_file_no_diff_on_value',
            'expected_value': YAML_CURRENT.splitlines(keepends=True),
            'read_data': '\n\t\n   ',
            'expected_changed': True,
        },
    ],
    [
        {'path': FAKE_PATH, 'value': 'Z'},
        {
            'id': 'test_scalar_value',
            'expected_value': ['Z'],
            'read_data': YAML_CURRENT,
            'expected_changed': True,
        },
    ],
    [
        {'path': FAKE_PATH, 'value': '{"Z": 1}', 'state': 'identic'},
        {
            'id': 'test_json_string_value',
            'expected_value': {'Z': 1},
            'read_data': YAML_CURRENT,
            'expected_changed': True,
        },
    ],
]
TEST_CASES_EXEC_IDS = [item[1]['id'] for item in TEST_CASE_EXEC]


@pytest.mark.parametrize('patch_ansible_module, testcase',
                         TEST_CASE_EXEC,
                         ids=TEST_CASES_EXEC_IDS,
                         indirect=['patch_ansible_module'])
@pytest.mark.usefixtures('patch_ansible_module')
def test_execute(testcase, capfd, mocker):
    mocker.patch(
        'ansible_collections.community.general.plugins.module_utils.mh.module_helper.AnsibleModule.set_fs_attributes_if_different',
        side_effect=lambda file_args, changed: changed)
    mocker.patch('ansible_collections.community.general.plugins.module_utils.mh.module_helper_dest_file.dest_file_sanity_check',
                 return_value=False)
    if testcase['read_data'] is None:
        mocker.patch('builtins.open', mock_open())
    else:
        mocker.patch('builtins.open', mock_open(read_data=testcase['read_data']))
    mocker.patch('os.write')
    mocker.patch('os.close')
    mocker.patch('tempfile.mkstemp', return_value=(1234, '/fake/temp/file'))
    mocker.patch.multiple(YamlFile,
                          __make_backup__=mocker.DEFAULT,
                          __move_temp__=mocker.DEFAULT)
    with pytest.raises(SystemExit):
        YamlFile().execute()
    result = json.loads(capfd.readouterr().out)
    assert(result['failed'] is False)
    assert(result['changed'] == testcase['expected_changed'])
    assert(result['result'] == testcase['expected_value'])
