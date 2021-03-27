from openapi.utils import extend_schema_tags

tag = 'authorization_server'
path = tag
name = '身份源服务'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'list': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_server/',
            'method': 'get'
        },
        'create': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_server/',
            'method': 'post'
        },
        'update': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_server/{id}/',
            'method': 'put'
        },
        'delete': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/authorization_server/{id}/',
            'method': 'delete'
        }
    }
)
