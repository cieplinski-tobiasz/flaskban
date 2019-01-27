"""
The module serves as an entry point
for uWSGI. It creates the application
using factory method and runs it.
"""
from app import create_app

APP = create_app('dev')

if __name__ == '__main__':
    APP.run()
