import os


# @property
def run_integration_tests():
    return 'INTEGRATION_TESTS' in os.environ
