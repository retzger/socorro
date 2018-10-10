import json
import urllib

import pyquery

from django.core.urlresolvers import reverse

from crashstats.crashstats import models
from crashstats.crashstats.tests.test_views import BaseTestViews
from crashstats.supersearch.models import SuperSearchUnredacted


DUMB_SIGNATURE = 'hang | mozilla::wow::such_signature(smth*)'


class TestViews(BaseTestViews):

    def test_signature_report(self):
        url = reverse('signature:signature_report')
        response = self.client.get(url, {'signature': DUMB_SIGNATURE})
        assert response.status_code == 200
        assert DUMB_SIGNATURE in response.content
        assert 'Loading' in response.content

    def test_signature_reports(self):

        def mocked_supersearch_get(**params):
            assert '_columns' in params

            assert 'uuid' in params['_columns']

            assert 'signature' in params
            assert params['signature'] == ['=' + DUMB_SIGNATURE]

            if 'product' in params:
                results = {
                    "hits": [
                        {
                            "date": "2017-01-31T23:12:57",
                            "uuid": "aaaaaaaaaaaaa1",
                            "product": "WaterWolf",
                            "version": "1.0",
                            "platform": "Linux",
                            "build_id": 888981,
                            "cpu_info": "FakeAMD family 20 model 42",
                        },
                        {
                            "date": "2017-01-31T23:12:57",
                            "uuid": "aaaaaaaaaaaaa2",
                            "product": "WaterWolf",
                            "version": "1.0",
                            "platform": "Linux",
                            "build_id": 888981,
                            "cpu_info": "AuthenticAMD family 20 model 1",
                        },
                        {
                            "date": "2017-01-31T23:12:57",
                            "uuid": "aaaaaaaaaaaaa3",
                            "product": "WaterWolf",
                            "version": "1.0",
                            "platform": "Linux",
                            "build_id": None
                        },
                        {
                            "date": "2017-01-31T23:12:57",
                            "uuid": "aaaaaaaaaaaaa4",
                            "product": "WaterWolf",
                            "version": "1.0",
                            "platform": "Linux",
                            "build_id": None
                        }
                    ],
                    "total": 4
                }
                results['hits'] = self.only_certain_columns(
                    results['hits'],
                    params['_columns']
                )
                return results

            return {"hits": [], "total": 0}

        SuperSearchUnredacted.implementation().get.side_effect = (
            mocked_supersearch_get
        )

        url = reverse('signature:signature_reports')

        # Test with no results.
        response = self.client.get(url, {
            'signature': DUMB_SIGNATURE,
            'date': '2012-01-01',
        })
        assert response.status_code == 200
        assert 'table id="reports-list"' not in response.content
        assert 'No results were found' in response.content

        # Test with results.
        response = self.client.get(url, {
            'signature': DUMB_SIGNATURE,
            'product': 'WaterWolf'
        })
        assert response.status_code == 200
        assert 'table id="reports-list"' in response.content
        assert 'aaaaaaaaaaaaa1' in response.content
        assert '888981' in response.content
        assert 'Linux' in response.content
        assert '2017-01-31 23:12:57' in response.content
        assert 'AMD' in response.content
        assert 'Cpu info' not in response.content

        # Test with a different columns list.
        response = self.client.get(url, {
            'signature': DUMB_SIGNATURE,
            'product': 'WaterWolf',
            '_columns': ['build_id', 'platform'],
        })
        assert response.status_code == 200
        assert 'table id="reports-list"' in response.content
        # The build and platform appear
        assert '888981' in response.content
        assert 'Linux' in response.content
        # The crash id is always shown
        assert 'aaaaaaaaaaaaa1' in response.content
        # The version and date do not appear
        assert '1.0' not in response.content
        assert '2017' not in response.content

        # Test missing parameter.
        response = self.client.get(url)
        assert response.status_code == 400

        response = self.client.get(url, {
            'signature': '',
        })
        assert response.status_code == 400

    def test_parameters(self):

        def mocked_supersearch_get(**params):
            # Verify that all expected parameters are in the URL.
            assert 'product' in params
            assert 'WaterWolf' in params['product']
            assert 'NightTrain' in params['product']

            assert 'address' in params
            assert '0x0' in params['address']
            assert '0xa' in params['address']

            assert 'reason' in params
            assert '^hello' in params['reason']
            assert '$thanks' in params['reason']

            assert 'java_stack_trace' in params
            assert 'Exception' in params['java_stack_trace']

            return {
                "hits": [],
                "facets": "",
                "total": 0
            }

        SuperSearchUnredacted.implementation().get.side_effect = (
            mocked_supersearch_get
        )

        url = reverse('signature:signature_reports')

        response = self.client.get(
            url, {
                'signature': DUMB_SIGNATURE,
                'product': ['WaterWolf', 'NightTrain'],
                'address': ['0x0', '0xa'],
                'reason': ['^hello', '$thanks'],
                'java_stack_trace': 'Exception',
            }
        )
        assert response.status_code == 200

    def test_signature_reports_pagination(self):
        """Test that the pagination of results works as expected.
        """

        def mocked_supersearch_get(**params):
            assert '_columns' in params

            # Make sure a negative page does not lead to negative offset value.
            # But instead it is considered as the page 1 and thus is not added.
            assert params.get('_results_offset') == 0

            hits = []
            for i in range(140):
                hits.append({
                    "signature": "nsASDOMWindowEnumerator::GetNext()",
                    "date": "2017-01-31T23:12:57",
                    "uuid": i,
                    "product": "WaterWolf",
                    "version": "1.0",
                    "platform": "Linux",
                    "build_id": 888981
                })
            return {
                "hits": self.only_certain_columns(hits, params['_columns']),
                "facets": "",
                "total": len(hits)
            }

        SuperSearchUnredacted.implementation().get.side_effect = (
            mocked_supersearch_get
        )

        url = reverse('signature:signature_reports')

        response = self.client.get(
            url,
            {
                'signature': DUMB_SIGNATURE,
                'product': ['WaterWolf'],
                '_columns': ['platform']
            }
        )

        assert response.status_code == 200
        assert '140' in response.content

        # Check that the pagination URL contains all three expected parameters.
        doc = pyquery.PyQuery(response.content)
        next_page_url = str(doc('.pagination a').eq(0))
        assert 'product=WaterWolf' in next_page_url
        assert '_columns=platform' in next_page_url
        assert 'page=2' in next_page_url

        # Verify white spaces are correctly encoded.
        # Note we use `quote` and not `quote_plus`, so white spaces are
        # turned into '%20' instead of '+'.
        assert urllib.quote(DUMB_SIGNATURE) in next_page_url

        # Test that a negative page value does not break it.
        response = self.client.get(url, {
            'signature': DUMB_SIGNATURE,
            'page': '-1',
        })
        assert response.status_code == 200

    def test_signature_aggregation(self):

        def mocked_supersearch_get(**params):
            assert 'signature' in params
            assert params['signature'] == ['=' + DUMB_SIGNATURE]

            assert '_facets' in params

            if 'product' in params['_facets']:
                return {
                    "hits": [],
                    "facets": {
                        "product": [
                            {
                                "term": "windows",
                                "count": 42,
                            },
                            {
                                "term": "linux",
                                "count": 1337,
                            },
                            {
                                "term": "mac",
                                "count": 3,
                            },
                        ]
                    },
                    "total": 1382
                }

            # the default
            return {
                "hits": [],
                "facets": {
                    "platform": []
                },
                "total": 0
            }

        SuperSearchUnredacted.implementation().get.side_effect = (
            mocked_supersearch_get
        )

        # Test with no results.
        url = reverse(
            'signature:signature_aggregation',
            args=('platform',)
        )

        response = self.client.get(url, {'signature': DUMB_SIGNATURE})
        assert response.status_code == 200
        assert 'Product' not in response.content
        assert 'No results were found' in response.content

        # Test with results.
        url = reverse(
            'signature:signature_aggregation',
            args=('product',)
        )

        response = self.client.get(url, {'signature': DUMB_SIGNATURE})
        assert response.status_code == 200
        assert 'Product' in response.content
        assert '1337' in response.content
        assert 'linux' in response.content
        assert str(1337 / 1382 * 100) in response.content
        assert 'windows' in response.content
        assert 'mac' in response.content

    def test_signature_graphs(self):

        def mocked_supersearch_get(**params):
            assert 'signature' in params
            assert params['signature'] == ['=' + DUMB_SIGNATURE]

            assert '_histogram.date' in params
            assert '_facets' in params

            if 'product' in params['_facets']:
                return {
                    "hits": [],
                    "total": 4,
                    "facets": {
                        "product": [
                            {
                                "count": 4,
                                "term": "WaterWolf"
                            }
                        ],
                        "histogram_date": [
                            {
                                "count": 2,
                                "term": "2015-08-05T00:00:00+00:00",
                                "facets": {
                                    "product": [
                                        {
                                            "count": 2,
                                            "term": "WaterWolf"
                                        }
                                    ]
                                }
                            },
                            {
                                "count": 2,
                                "term": "2015-08-06T00:00:00+00:00",
                                "facets": {
                                    "product": [
                                        {
                                            "count": 2,
                                            "term": "WaterWolf"
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }

            return {
                "hits": [],
                "total": 0,
                "facets": {
                    "platform": [],
                    "signature": [],
                    "histogram_date": []
                }
            }

        SuperSearchUnredacted.implementation().get.side_effect = (
            mocked_supersearch_get
        )

        # Test with no results
        url = reverse(
            'signature:signature_graphs',
            args=('platform',)
        )

        response = self.client.get(url, {'signature': DUMB_SIGNATURE})
        assert response.status_code == 200
        assert 'application/json' in response['content-type']
        struct = json.loads(response.content)
        assert 'aggregates' in struct
        assert len(struct['aggregates']) == 0
        assert 'term_counts' in struct
        assert len(struct['term_counts']) == 0

        # Test with results
        url = reverse(
            'signature:signature_graphs',
            args=('product',)
        )

        response = self.client.get(url, {'signature': DUMB_SIGNATURE})
        assert response.status_code == 200
        assert 'application/json' in response['content-type']
        struct = json.loads(response.content)
        assert 'aggregates' in struct
        assert len(struct['aggregates']) == 2
        assert 'term_counts' in struct
        assert len(struct['term_counts']) == 1

    def test_signature_comments(self):

        def mocked_supersearch_get(**params):
            assert '_columns' in params

            assert 'signature' in params
            assert params['signature'] == ['=' + DUMB_SIGNATURE]

            assert 'user_comments' in params
            assert params['user_comments'] == ['!__null__']

            if 'product' in params:
                results = {
                    "hits": [
                        {
                            "date": "2017-01-31T23:12:57",
                            "uuid": "aaaaaaaaaaaaa1",
                            "product": "WaterWolf",
                            "version": "1.0",
                            "platform": "Linux",
                            "user_comments": "hello there people!",
                            "useragent_locale": "locale1"
                        },
                        {
                            "date": "2017-01-31T23:12:57",
                            "uuid": "aaaaaaaaaaaaa2",
                            "product": "WaterWolf",
                            "version": "1.0",
                            "platform": "Linux",
                            "user_comments": "I love Mozilla",
                            "useragent_locale": "locale2"
                        },
                        {
                            "date": "2017-01-31T23:12:57",
                            "uuid": "aaaaaaaaaaaaa3",
                            "product": "WaterWolf",
                            "version": "1.0",
                            "platform": "Linux",
                            "user_comments": "this product is awesome",
                            "useragent_locale": "locale3"
                        },
                        {
                            "date": "2017-01-31T23:12:57",
                            "uuid": "aaaaaaaaaaaaa4",
                            "product": "WaterWolf",
                            "version": "1.0",
                            "platform": "Linux",
                            "user_comments": "WaterWolf Y U SO GOOD?",
                            "useragent_locale": "locale4"
                        }
                    ],
                    "total": 4
                }
                results['hits'] = self.only_certain_columns(
                    results['hits'],
                    params['_columns']
                )
                return results

            return {"hits": [], "total": 0}

        SuperSearchUnredacted.implementation().get.side_effect = (
            mocked_supersearch_get
        )

        url = reverse('signature:signature_comments')

        # Test with no results.
        response = self.client.get(url, {
            'signature': DUMB_SIGNATURE,
        })
        assert response.status_code == 200
        assert 'Crash ID' not in response.content
        assert 'No comments were found' in response.content

        # Test with results.
        response = self.client.get(url, {
            'signature': DUMB_SIGNATURE,
            'product': 'WaterWolf'
        })
        assert response.status_code == 200
        assert 'aaaaaaaaaaaaa1' in response.content
        assert 'Crash ID' in response.content
        assert 'hello there' in response.content
        assert 'WaterWolf Y U SO GOOD' in response.content
        assert 'locale1' in response.content

    def test_signature_comments_pagination(self):
        """Test that the pagination of comments works as expected. """

        def mocked_supersearch_get(**params):
            assert '_columns' in params

            if params.get('_results_offset') != 0:
                hits_range = range(100, 140)
            else:
                hits_range = range(100)

            hits = []
            for i in hits_range:
                hits.append({
                    "date": "2017-01-31T23:12:57",
                    "uuid": i,
                    "user_comments": "hi",
                })

            return {
                'hits': self.only_certain_columns(hits, params['_columns']),
                'total': 140
            }

        SuperSearchUnredacted.implementation().get.side_effect = (
            mocked_supersearch_get
        )

        url = reverse('signature:signature_comments')

        response = self.client.get(
            url,
            {
                'signature': DUMB_SIGNATURE,
                'product': ['WaterWolf'],
            }
        )

        assert response.status_code == 200
        assert '140' in response.content
        assert '99' in response.content
        assert '139' not in response.content

        # Check that the pagination URL contains all expected parameters.
        doc = pyquery.PyQuery(response.content)
        next_page_url = str(doc('.pagination a').eq(0))
        assert 'product=WaterWolf' in next_page_url
        assert 'page=2' in next_page_url

        response = self.client.get(url, {
            'signature': DUMB_SIGNATURE,
            'page': '2',
        })
        assert response.status_code == 200
        assert '140' in response.content
        assert '99' not in response.content
        assert '139' in response.content

    def test_signature_summary(self):
        models.GraphicsDevice.objects.create(
            vendor_hex='0x0086',
            adapter_hex='0x1234',
            vendor_name='Intel',
            adapter_name='Device'
        )
        models.GraphicsDevice.objects.create(
            vendor_hex='0x0086',
            adapter_hex='0x1239',
            vendor_name='Intel',
            adapter_name='Other'
        )

        def mocked_supersearch_get(**params):
            assert 'signature' in params
            assert params['signature'] == ['=' + DUMB_SIGNATURE]

            res = {
                "hits": [],
                "total": 4,
                "facets": {
                    "platform_pretty_version": [
                        {
                            "count": 4,
                            "term": "Windows 7"
                        }
                    ],
                    "cpu_name": [
                        {
                            "count": 4,
                            "term": "x86"
                        }
                    ],
                    "process_type": [
                        {
                            "count": 4,
                            "term": "browser"
                        }
                    ],
                    "product": [
                        {
                            "count": 4,
                            "term": "WaterWolf",
                            "facets": {
                                "version": [
                                    {
                                        "term": "2.1b99",
                                        "count": 2,
                                        "facets": {
                                            "cardinality_install_time": {
                                                "value": 2
                                            }
                                        }
                                    },
                                    {
                                        "term": "1.0",
                                        "count": 2,
                                        "facets": {
                                            "cardinality_install_time": {
                                                "value": 2
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ],
                    "flash_version": [
                        {
                            "count": 4,
                            "term": "1.1.1.14"
                        }
                    ],
                    "adapter_vendor_id": [
                        {
                            "term": "0x0086",
                            "count": 4,
                            "facets": {
                                "adapter_device_id": [
                                    {
                                        "term": "0x1234",
                                        "count": 2,
                                    },
                                    {
                                        "term": "0x1239",
                                        "count": 2,
                                    }
                                ]
                            }
                        }
                    ],
                    "android_cpu_abi": [
                        {
                            "term": "armeabi-v7a",
                            "count": 4,
                            "facets": {
                                "android_manufacturer": [
                                    {
                                        "term": "ZTE",
                                        "count": 4,
                                        "facets": {
                                            "android_model": [
                                                {
                                                    "term": "roamer2",
                                                    "count": 4,
                                                    "facets": {
                                                        "android_version": [
                                                            {
                                                                "term": "15",
                                                                "count": 4,
                                                            }
                                                        ]
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    ],
                    "histogram_uptime": [
                        {
                            "count": 2,
                            "term": 0,
                        },
                        {
                            "count": 2,
                            "term": 60,
                        }
                    ],
                }
            }

            if '_histogram.date' in params:
                res['facets']['histogram_date'] = [
                    {
                        "count": 2,
                        "term": "2015-08-05T00:00:00+00:00",
                        "facets": {
                            "exploitability": [
                                {
                                    "count": 2,
                                    "term": "high"
                                }
                            ]
                        }
                    },
                    {
                        "count": 2,
                        "term": "2015-08-06T00:00:00+00:00",
                        "facets": {
                            "exploitability": [
                                {
                                    "count": 2,
                                    "term": "low"
                                }
                            ]
                        }
                    }
                ]

            return res

        SuperSearchUnredacted.implementation().get.side_effect = (
            mocked_supersearch_get
        )

        # Test with no results
        url = reverse('signature:signature_summary')

        response = self.client.get(url, {
            'signature': DUMB_SIGNATURE,
            'product': 'WaterWolf',
            'version': '1.0',
        })
        assert response.status_code == 200

        # Make sure all boxes are there.
        assert 'Operating System' in response.content
        assert 'Uptime Range' in response.content
        assert 'Product' in response.content
        assert 'Architecture' in response.content
        assert 'Process Type' in response.content
        assert 'Mobile Devices' in response.content
        assert 'Graphics Adapter' in response.content
        assert 'Flash&trade; Version' in response.content

        # Logged out users can't see no exploitability
        assert 'Exploitability' not in response.content

        # Check that some of the expected values are there.
        assert 'Windows 7' in response.content
        assert 'x86' in response.content
        assert 'WaterWolf' in response.content
        assert '2.1b99' in response.content
        assert 'browser' in response.content
        assert '1.1.1.14' in response.content
        assert '&lt; 1 min' in response.content
        assert '1-5 min' in response.content
        assert 'ZTE' in response.content
        assert 'Intel (0x0086)' in response.content

        user = self._login()

        response = self.client.get(url, {'signature': DUMB_SIGNATURE})
        assert response.status_code == 200

        # Logged in users without the permission can't see no exploitability
        assert 'Exploitability' not in response.content

        group = self._create_group_with_permission('view_exploitability')
        user.groups.add(group)
        assert user.has_perm('crashstats.view_exploitability')

        response = self.client.get(url, {'signature': DUMB_SIGNATURE})
        assert response.status_code == 200

        # Logged in users with the permission can see exploitability
        assert 'Exploitability' in response.content

    def test_signature_summary_with_many_hexes(self):
        def mocked_supersearch_get(**params):
            assert 'signature' in params
            assert params['signature'] == ['=' + DUMB_SIGNATURE]

            adapters = [
                {
                    'term': '0x{0:0>4}'.format(i),
                    'count': 1
                }
                for i in range(50)
            ]
            vendors = [
                {
                    'term': '0x{0:0>4}'.format(i),
                    'count': 50,
                    'facets': {
                        'adapter_device_id': adapters
                    }
                }
                for i in range(3)
            ]

            res = {
                'hits': [],
                'total': 4,
                'facets': {
                    'adapter_vendor_id': vendors,
                }
            }

            return res

        SuperSearchUnredacted.implementation().get.side_effect = mocked_supersearch_get

        # Test with no results
        url = reverse('signature:signature_summary')

        response = self.client.get(url, {
            'signature': DUMB_SIGNATURE,
            'product': 'WaterWolf',
            'version': '1.0',
        })
        assert response.status_code == 200

    def test_signature_bugzilla(self):
        models.BugAssociation.objects.create(
            bug_id=111111,
            signature='Something'
        )
        models.BugAssociation.objects.create(
            bug_id=111111,
            signature='OOM | small'
        )
        models.BugAssociation.objects.create(
            bug_id=123456789,
            signature='Something'
        )

        # Test with signature that has no bugs
        url = reverse('signature:signature_bugzilla')
        response = self.client.get(url, {
            'signature': 'hang | mozilla::wow::such_signature(smth*)'
        })
        assert response.status_code == 200
        assert 'There are no bugs' in response.content

        # Test with signature that has bugs and related bugs
        response = self.client.get(url, {
            'signature': 'Something',
        })
        assert response.status_code == 200
        assert '123456789' in response.content
        assert '111111' in response.content

        # because bug id 123456789 is > than 111111 we expect that order
        # in the rendered output
        assert (
            response.content.find('123456789') <
            response.content.find('111111') <
            response.content.find('Related Crash Signatures') <
            response.content.find('Bugs for <code>OOM | small</code>')
        )
