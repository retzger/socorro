import ujson

from crashstats.crashstats.tests.test_models import Response


SUPERSEARCH_FIELDS_MOCKED_RESULTS = {
    'signature': {
        'name': 'signature',
        'query_type': 'string',
        'namespace': 'processed_crash',
        'form_field_choices': None,
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'signature',
    },
    'product': {
        'name': 'product',
        'query_type': 'enum',
        'namespace': 'processed_crash',
        'form_field_choices': None,
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'product',
    },
    'version': {
        'name': 'version',
        'query_type': 'enum',
        'namespace': 'processed_crash',
        'form_field_choices': None,
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'version',
    },
    'platform': {
        'name': 'platform',
        'query_type': 'enum',
        'namespace': 'processed_crash',
        'form_field_choices': None,
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'os_name',
    },
    'process_type': {
        'name': 'process_type',
        'query_type': 'enum',
        'namespace': 'processed_crash',
        'form_field_choices': ['browser', 'content'],
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'process_type',
    },
    'dump': {
        'name': 'dump',
        'query_type': 'string',
        'namespace': 'processed_crash',
        'form_field_choices': None,
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': False,
        'is_mandatory': False,
        'in_database_name': 'dump',
    },
    'release_channel': {
        'name': 'release_channel',
        'query_type': 'enum',
        'namespace': 'processed_crash',
        'form_field_choices': None,
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'release_channel',
    },
    'date': {
        'name': 'date',
        'query_type': 'date',
        'namespace': 'processed_crash',
        'form_field_choices': None,
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'date_processed',
    },
    'address': {
        'name': 'address',
        'query_type': 'string',
        'namespace': 'processed_crash',
        'form_field_choices': None,
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'address',
    },
    'build_id': {
        'name': 'build_id',
        'query_type': 'number',
        'namespace': 'processed_crash',
        'form_field_choices': None,
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'build',
    },
    'reason': {
        'name': 'reason',
        'query_type': 'string',
        'namespace': 'processed_crash',
        'form_field_choices': None,
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'reason',
    },
    'java_stack_trace': {
        'name': 'java_stack_trace',
        'query_type': 'enum',
        'namespace': 'processed_crash',
        'form_field_choices': None,
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'java_stack_trace',
    },
    'email': {
        'name': 'email',
        'query_type': 'string',
        'namespace': 'processed_crash',
        'form_field_choices': None,
        'permissions_needed': ['crashstats.view_pii'],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'email',
    },
    'url': {
        'name': 'url',
        'query_type': 'string',
        'namespace': 'processed_crash',
        'form_field_choices': None,
        'permissions_needed': ['crashstats.view_pii'],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'url',
    },
    'exploitability': {
        'name': 'exploitability',
        'query_type': 'string',
        'namespace': 'processed_crash',
        'form_field_choices': [
            'high', 'normal', 'low', 'none', 'unknown', 'error'
        ],
        'permissions_needed': ['crashstats.view_exploitability'],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'exploitability',
    },
    'user_comments': {
        'name': 'user_comments',
        'query_type': 'string',
        'namespace': 'processed_crash',
        'form_field_choices': [],
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'user_comments',
    },
    'winsock_lsp': {
        'name': 'winsock_lsp',
        'query_type': 'enum',
        'namespace': 'raw_crash',
        'form_field_choices': [],
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': True,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'Winsock_LSP',
    },
    'SecondsSinceLastCrash': {
        'name': 'SecondsSinceLastCrash',
        'query_type': 'enum',
        'namespace': 'raw_crash',
        'form_field_choices': [],
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': False,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'SecondsSinceLastCrash',
    },
    'a_test_field': {
        'name': 'a_test_field',
        'query_type': 'string',
        'namespace': 'processed_crash',
        'form_field_choices': [],
        'permissions_needed': [],
        'default_value': None,
        'is_exposed': False,
        'is_returned': True,
        'is_mandatory': False,
        'in_database_name': 'a_test_field',
    },
}


class SuperSearchResponse(Response):
    def __init__(self, content=None, status_code=200, columns=None):
        if isinstance(content, basestring):
            content = ujson.loads(content)

        if columns is None:
            columns = []

        assert 'hits' in content
        for i, hit in enumerate(content['hits']):
            content['hits'][i] = dict(
                (key, val)
                for key, val in hit.items()
                if key in columns
            )

        super(SuperSearchResponse, self).__init__(content, status_code)
