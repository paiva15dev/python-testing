class TestRegister:

    def test_register_sucesso(self, client, user_payload):
        res = client.post("/auth/register", json=user_payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["user"]["username"] == user_payload["username"]
        assert "password" not in data["user"]
        assert "password_hash" not in data["user"]

    def test_register_username_duplicado(self, client, user_payload, registered_user):
        res = client.post("/auth/register", json=user_payload)
        assert res.status_code == 409

    def test_register_email_duplicado(self, client, user_payload, registered_user):
        payload = {**user_payload, "username": "outro"}
        res = client.post("/auth/register", json=payload)
        assert res.status_code == 409

    def test_register_sem_campos_obrigatorios(self, client):
        res = client.post("/auth/register", json={"username": "joao"})
        assert res.status_code == 400

    def test_register_senha_curta(self, client, user_payload):
        payload = {**user_payload, "password": "123"}
        res = client.post("/auth/register", json=payload)
        assert res.status_code == 400


class TestLogin:

    def test_login_sucesso(self, client, user_payload, registered_user):
        res = client.post("/auth/login", json={
            "username": user_payload["username"],
            "password": user_payload["password"]
        })
        assert res.status_code == 200
        assert "access_token" in res.get_json()

    def test_login_senha_errada(self, client, user_payload, registered_user):
        res = client.post("/auth/login", json={
            "username": user_payload["username"],
            "password": "senhaerrada"
        })
        assert res.status_code == 401

    def test_login_usuario_inexistente(self, client):
        res = client.post("/auth/login", json={
            "username": "naoexiste",
            "password": "qualquer"
        })
        assert res.status_code == 401


class TestMe:

    def test_me_autenticado(self, client, user_payload, auth_headers):
        res = client.get("/auth/me", headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["user"]["username"] == user_payload["username"]

    def test_me_sem_token(self, client):
        res = client.get("/auth/me")
        assert res.status_code == 401

    def test_me_token_invalido(self, client):
        res = client.get("/auth/me", headers={"Authorization": "Bearer tokeninvalido"})
        assert res.status_code == 422