import pytest
from services.auth import hash_password, verify_password, generate_jwt, verify_jwt, JwtConfig


class TestPasswordHashing:
    def test_hash_returns_non_empty_string(self):
        h = hash_password("secret")
        assert isinstance(h, str)
        assert len(h) > 0
        assert h != "secret"

    def test_verify_correct_password(self):
        h = hash_password("mypassword")
        assert verify_password("mypassword", h) is True

    def test_verify_wrong_password(self):
        h = hash_password("mypassword")
        assert verify_password("wrong", h) is False

    def test_two_hashes_differ(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2


class TestJwt:
    def test_generate_and_verify(self, jwt_config):
        token = generate_jwt(42, jwt_config)
        assert isinstance(token, str)
        assert verify_jwt(token, jwt_config) == 42

    def test_wrong_secret(self, jwt_config):
        token = generate_jwt(42, jwt_config)
        bad = JwtConfig(secret="wrong", issuer=jwt_config.issuer, expires_in_seconds=3600)
        assert verify_jwt(token, bad) is None

    def test_wrong_issuer(self, jwt_config):
        token = generate_jwt(42, jwt_config)
        bad = JwtConfig(secret=jwt_config.secret, issuer="wrong", expires_in_seconds=3600)
        assert verify_jwt(token, bad) is None

    def test_expired_token(self):
        cfg = JwtConfig(secret="s", issuer="i", expires_in_seconds=-1)
        token = generate_jwt(1, cfg)
        assert verify_jwt(token, cfg) is None

    def test_garbage_token(self, jwt_config):
        assert verify_jwt("not.a.token", jwt_config) is None

    def test_empty_token(self, jwt_config):
        assert verify_jwt("", jwt_config) is None

    def test_different_user_ids(self, jwt_config):
        t1 = generate_jwt(1, jwt_config)
        t2 = generate_jwt(2, jwt_config)
        assert t1 != t2
        assert verify_jwt(t1, jwt_config) == 1
        assert verify_jwt(t2, jwt_config) == 2
