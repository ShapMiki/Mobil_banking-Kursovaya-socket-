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
def get_name(data):
    print(data)



@router('post', 'get_balance')
def get_balance(data):
    print(data)

@router('post', 'registration')
def registrate(data):
    print(data)

@router('post', 'login')
def login(data):
    print(data)



@router('SECURITY_POST', 'set_balance')
def set_balance(data):
    print(data)

# Test the functions
router_dir['get']['get_name'](3435)
router_dir['post']['get_balance'](3435)
router_dir['SECURITY_POST']['set_balance'](3435)