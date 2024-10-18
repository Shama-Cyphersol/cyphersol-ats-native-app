import datetime

def get_license_info():
    # This is a dummy implementation. In a real-world scenario,
    # you would implement actual license checking logic here.
    return {
        'status': 'Active',
        'expiry': (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    }
