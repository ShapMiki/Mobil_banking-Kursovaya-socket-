router_dir = {
    'get': {},
    'post': {},
    'SECURITY_POST': {}
}

def router(method, route):
    def decorator(func):
        router_dir[method][route] = func
        return func
    return decorator


@router('get', 'get_name')
def get_name(id):
    print(id)

@router('post', 'get_balance')
def get_balance(id):
    print(id)

@router('SECURITY_POST', 'set_balance')
def set_balance(id):
    print(id)

# Test the functions
router_dir['get']['get_name'](3435)
router_dir['post']['get_balance'](3435)
router_dir['SECURITY_POST']['set_balance'](3435)