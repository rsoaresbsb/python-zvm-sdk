# Copyright 2017,2018 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import six
import time

from zvmsdk.tests.sdkwsgi import base
from zvmsdk.tests.sdkwsgi import test_utils
from zvmsdk.tests.sdkwsgi import test_sdkwsgi
from zvmsdk import config
from zvmsdk import monitor

CONF = config.CONF


class MonitorTestCase(base.ZVMConnectorBaseTestCase):

    @classmethod
    def setUpClass(cls):
        super(MonitorTestCase, cls).setUpClass()

        cls.client = test_sdkwsgi.TestSDKClient()
        cls.test_utils = test_utils.ZVMConnectorTestUtils()
        cls.userid1 = cls.test_utils.guest_deploy()[0]
        cls.userid2 = cls.test_utils.guest_deploy()[0]

    @classmethod
    def tearDownClass(cls):
        super(MonitorTestCase, cls).tearDownClass()
        cls.test_utils.guest_destroy(cls.userid1)
        cls.test_utils.guest_destroy(cls.userid2)

    def setUp(self):
        super(MonitorTestCase, self).setUp()
        self.record_logfile_position()

    def _inspect_stats(self, userid):
        body = None
        url = '/guests/stats?userid=%s' % userid
        resp = self.client.api_request(url=url, method='GET',
                                      body=body)
        return resp

    def _inspect_vnics(self, userid):
        body = None
        url = '/guests/interfacestats?userid=%s' % userid
        resp = self.client.api_request(url=url, method='GET',
                                      body=body)
        return resp

    def test_guest_inspect_stats(self):
        print("Test with a single uerid")
        test_id = self.userid1.upper()
        resp = self._inspect_stats(self.userid1)
        self.assertEqual(200, resp.status_code)
        results = json.loads(resp.content)
        self.assertEqual(0, results['overallRC'])
        result = results['output']
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 1)
        stats_keys = ['guest_cpus', 'used_cpu_time_us', 'elapsed_cpu_time_us',
                      'min_cpu_count', 'max_cpu_limit', 'samples_cpu_in_use',
                      'samples_cpu_delay', 'used_mem_kb', 'max_mem_kb',
                      'min_mem_kb', 'shared_mem_kb']
        self.assertListEqual(sorted(result[test_id].keys()),
                             sorted(stats_keys))
        self.assertTrue(isinstance(
                result[test_id].get('guest_cpus'), int))
        self.assertTrue(isinstance(
                result[test_id].get('used_cpu_time_us'), int))
        self.assertTrue(isinstance(
                result[test_id].get('elapsed_cpu_time_us'), int))
        self.assertTrue(isinstance(
                result[test_id].get('min_cpu_count'), int))
        self.assertTrue(isinstance(
                result[test_id].get('max_cpu_limit'), int))
        self.assertTrue(isinstance(
                result[test_id].get('samples_cpu_in_use'), int))
        self.assertTrue(isinstance(
                result[test_id].get('samples_cpu_delay'), int))
        self.assertTrue(isinstance(
                result[test_id].get('used_mem_kb'), int))
        self.assertTrue(isinstance(
                result[test_id].get('max_mem_kb'), int))
        self.assertTrue(isinstance(
                result[test_id].get('min_mem_kb'), int))
        self.assertTrue(isinstance(
                result[test_id].get('shared_mem_kb'), int))
        """
        print("Test with a userid list")
        test_id2 = self.userid2.upper()
        guest_list = [self.userid1, self.userid2]
        resp = self._inspect_stats(guest_list)
        self.assertEqual(200, resp.status_code)
        results = json.loads(resp.content)
        self.assertEqual(0, results['overallRC'])
        result = results['output']
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 2)
        self.assertListEqual(sorted(result[test_id].keys()),
                             sorted(stats_keys))
        self.assertListEqual(sorted(result[test_id2].keys()),
                             sorted(stats_keys))
        self.assertTrue(isinstance(
                result[test_id].get('guest_cpus'), int))
        self.assertTrue(isinstance(
                result[test_id].get('shared_mem_kb'), int))
        """
        print("Test with a nonexistent guest")
        resp = self._inspect_stats('FAKE_ID')
        self.assertEqual(200, resp.status_code)
        results = json.loads(resp.content)
        self.assertEqual(results['overallRC'], 0)
        self.assertEqual(results['output'], {})
        """
        print("Test with an empty user list")
        resp = self._inspect_stats([])
        self.assertEqual(200, resp.status_code)
        results = json.loads(resp.content)
        self.assertEqual(results['overallRC'], 0)
        self.assertEqual(results['output'], {})
        """

    def test_guest_inspect_vnics(self):
        print("To test with a single uerid")
        test_id = self.userid1.upper()
        resp = self._inspect_vnics(self.userid1)
        self.assertEqual(200, resp.status_code)
        results = json.loads(resp.content)
        self.assertEqual(0, results['overallRC'])
        result = results['output']
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 1)
        vnics_keys = ['vswitch_name', 'nic_vdev', 'nic_fr_rx', 'nic_fr_tx',
                      'nic_fr_rx_dsc', 'nic_fr_tx_dsc', 'nic_fr_rx_err',
                      'nic_fr_tx_err', 'nic_rx', 'nic_tx']
        self.assertListEqual(sorted(result[test_id][0].keys()),
                             sorted(vnics_keys))
        self.assertTrue(isinstance(result[test_id][0].get('vswitch_name'),
                                   six.string_types))
        self.assertTrue(isinstance(result[test_id][0].get('nic_vdev'),
                                   six.string_types))
        self.assertTrue(isinstance(
                result[test_id][0].get('nic_fr_rx'), int))
        self.assertTrue(isinstance(
                result[test_id][0].get('nic_fr_tx'), int))
        self.assertTrue(isinstance(
                result[test_id][0].get('nic_fr_rx_dsc'), int))
        self.assertTrue(isinstance(
                result[test_id][0].get('nic_fr_tx_dsc'), int))
        self.assertTrue(isinstance(
                result[test_id][0].get('nic_fr_rx_err'), int))
        self.assertTrue(isinstance(
                result[test_id][0].get('nic_fr_tx_err'), int))
        self.assertTrue(isinstance(
                result[test_id][0].get('nic_rx'), int))
        self.assertTrue(isinstance(
                result[test_id][0].get('nic_tx'), int))
        """
        print("To test with a userid list")
        test_id2 = self.userid2.upper()
        guest_list = [self.userid1, self.userid2]
        resp = self._inspect_vnics(guest_list)
        self.assertEqual(200, resp.status_code)
        results = json.loads(resp.content)
        self.assertEqual(0, results['overallRC'])
        result = results['output']
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 2)
        self.assertListEqual(sorted(result[test_id][0].keys()),
                             sorted(vnics_keys))
        self.assertListEqual(sorted(result[test_id2][0].keys()),
                             sorted(vnics_keys))
        self.assertTrue(isinstance(
                result[test_id][0].get('nic_vdev'), six.string_types))
        self.assertTrue(isinstance(
                result[test_id2][0].get('nic_tx'), int))
        """
        print("To test with a nonexistent guest")
        resp = self._inspect_vnics('FAKE_ID')
        self.assertEqual(200, resp.status_code)
        results = json.loads(resp.content)
        self.assertEqual(results['overallRC'], 0)
        self.assertEqual(results['output'], {})
        """
        print("To test with an empty user list")
        resp = self._inspect_vnics([])
        self.assertEqual(200, resp.status_code)
        results = json.loads(resp.content)
        self.assertEqual(results['overallRC'], 0)
        self.assertEqual(results['output'], {})
        """


class MeteringCacheTestCase(base.ZVMConnectorBaseTestCase):

    def setUp(self):
        super(MeteringCacheTestCase, self).setUp()
        self.set_conf('monitor', 'cache_interval', 1000)
        self.mc = monitor.MeteringCache(('typeA', 'typeB'))
        self.mc.refresh('typeA', {})
        self.mc.refresh('typeB', {})
        self.record_logfile_position()

    def test_init(self):
        self.assertListEqual(sorted(self.mc._cache.keys()),
                             sorted(['typeA', 'typeB']))
        self.assertListEqual(sorted(self.mc._cache['typeA'].keys()),
                             sorted(['expiration', 'data']))
        self.assertListEqual(sorted(self.mc._cache['typeB'].keys()),
                             sorted(['expiration', 'data']))
        self.assertEqual(self.mc._cache['typeA']['data'], {})
        self.assertEqual(self.mc._cache['typeB']['data'], {})
        self.assertListEqual(sorted(self.mc._types),
                             sorted(['typeA', 'typeB']))

    def test_set_get_delete(self):
        self.mc.set('typeA', 'data1', 'value1')
        self.mc.set('typeA', 'data2', 'value2')
        self.mc.set('typeB', 'data1', 'value1')
        self.mc.set('typeB', 'data2', 'value2')
        self.assertListEqual(sorted(self.mc._cache['typeA']['data'].keys()),
                             sorted(['data1', 'data2']))
        self.assertListEqual(sorted(self.mc._cache['typeB']['data'].keys()),
                             sorted(['data1', 'data2']))
        self.assertEqual(self.mc._cache['typeA']['data']['data1'],
                         'value1')
        self.assertEqual(self.mc._cache['typeB']['data']['data1'],
                         'value1')
        # Test get
        self.assertEqual(self.mc.get('typeA', 'data1'), 'value1')
        self.assertEqual(self.mc.get('typeA', 'data2'), 'value2')
        # Delete
        self.mc.delete('typeA', 'data1')
        self.assertEqual(self.mc.get('typeA', 'data1'), None)
        self.assertEqual(self.mc.get('typeA', 'data2'), 'value2')

    def test_refresh_and_expire(self):
        data = {'data1': 'value1',
                'data2': 'value2'}
        # Test refresh
        self.mc.refresh('typeA', data)
        self.assertEqual(self.mc.get('typeA', 'data1'), 'value1')
        self.assertEqual(self.mc.get('typeA', 'data2'), 'value2')
        self.set_conf('monitor', 'cache_interval', 1)
        # Test expire
        self.mc.refresh('typeA', data)
        time.sleep(2)
        self.assertEqual(self.mc.get('typeA', 'data1'), None)
        self.assertEqual(self.mc.get('typeA', 'data2'), None)
