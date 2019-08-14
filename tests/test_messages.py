import pytest
from hamcrest import *

from encrypio.messages import check_connection_client


"""
Dummy tests for CI integration
"""


@pytest.mark.parametrize('input', [
    (
        'Message'
    )
])
def test_check_connection_client(input):
    check_connection_client(input)


def test_check_connection_client_error():
    with pytest.raises(SystemExit):
        check_connection_client(None)