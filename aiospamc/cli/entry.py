import sys


def run():
    try:
        from .commands import app
    except ImportError:
        print("The optional 'cli' needed")
        sys.exit(-1)

    app()
