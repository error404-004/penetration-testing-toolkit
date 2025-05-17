# tests/test_brute_forcer.py

import pytest
from unittest.mock import patch, MagicMock
from brute_forcer import brute_forcer


@pytest.mark.parametrize("input_word,expected_leets", [
    ("password", {"password", "p4ssword", "pa$$word", "p455word", "passw0rd"}),
    ("admin", {"4dm1n", "adm1n", "admin", "Admin", "ADMIN"}),
])
def test_generate_mutations_contains_expected(input_word, expected_leets):
    mutations = brute_forcer.generate_mutations(input_word)
    matches = set()
    for pwd in mutations:
        for expected in expected_leets:
            if expected in pwd:
                matches.add(expected)
    assert matches >= expected_leets


def test_generate_mutations_output_type():
    mutations = brute_forcer.generate_mutations("test")
    assert isinstance(mutations, list)
    assert all(isinstance(pwd, str) for pwd in mutations)


@patch("modules.brute_forcer.requests.post")
def test_http_brute_force_success(mock_post):
    # Simulate HTTP 200 response on valid login
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    url = "http://example.com/login"
    usernames = ["admin"]
    base_passwords = ["password"]

    result = brute_forcer.http_brute_force(url, usernames, base_passwords)
    assert result is True


@patch("modules.brute_forcer.requests.post")
def test_http_brute_force_fail(mock_post):
    # Simulate 403 response on invalid login
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_post.return_value = mock_response

    url = "http://example.com/login"
    usernames = ["admin"]
    base_passwords = ["wrongpass"]

    result = brute_forcer.http_brute_force(url, usernames, base_passwords)
    assert result is False


@patch("modules.brute_forcer.paramiko.SSHClient")
def test_ssh_brute_force_success(mock_ssh_client):
    # Simulate successful SSH login
    mock_ssh = MagicMock()
    mock_ssh.connect.return_value = True
    mock_ssh_client.return_value = mock_ssh

    host = "192.168.1.10"
    usernames = ["admin"]
    base_passwords = ["password"]

    result = brute_forcer.ssh_brute_force(host, usernames, base_passwords)
    assert result is True
    mock_ssh.connect.assert_called()


@patch("modules.brute_forcer.paramiko.SSHClient")
def test_ssh_brute_force_fail(mock_ssh_client):
    # Simulate SSH AuthenticationException
    from paramiko import AuthenticationException

    mock_ssh = MagicMock()
    mock_ssh.connect.side_effect = AuthenticationException()
    mock_ssh_client.return_value = mock_ssh

    host = "192.168.1.10"
    usernames = ["user"]
    base_passwords = ["wrong"]

    result = brute_forcer.ssh_brute_force(host, usernames, base_passwords)
    assert result is False