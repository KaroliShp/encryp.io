import json

import pytest
from pytest_mock import mocker
from hamcrest import *

from encrypio.messages import check_connection_client, send_json_message, receive_json_message


@pytest.mark.parametrize('data,data_str,expected_length', [
    (
        { 'x' : 'y' }, '{"x":"y"}', format(9, '032b').encode()
    ), (
        {}, '{}', format(2, '032b').encode()
    )
])
def test_send_json_message(mocker, data, data_str, expected_length):
    # Assign
    mocker.patch('json.dumps')
    json.dumps.return_value = data_str
    socket = mocker.Mock()

    # Act
    send_json_message(socket, data)

    # Assert
    assert_that(socket.send.call_count, equal_to(2))
    assert_that(socket.send.call_args_list[0][0][0], equal_to(expected_length))
    assert_that(socket.send.call_args_list[1][0][0].decode("utf-8"), equal_to(data_str))


@pytest.mark.parametrize('data_length,data_bytes,expected_output', [
    (
        format(9, '032b').encode(), b'{"x":"y"}', { 'x' : 'y' }
    ), (
        format(2, '032b').encode(), b'{}', {}
    )
])
def test_receive_json_message(mocker, data_length, data_bytes, expected_output):
    # Assign
    socket = mocker.Mock()
    count = 0

    def side_effect(msg):
        if socket.recv.call_count == 1:
            return data_length
        elif socket.recv.call_count == 2:
            return data_bytes

    socket.recv.side_effect = side_effect

    # Act
    output = receive_json_message(socket)

    # Assert
    assert_that(output, equal_to(expected_output))


@pytest.mark.parametrize('input', [
    (
        'Message'
    ), (
        ''
    )
])
def test_check_connection_client(input):
    check_connection_client(input)


def test_check_connection_client_error():
    # Hamcrest doesnt work with SystemExit for some reason
    with pytest.raises(SystemExit):
        check_connection_client(None)