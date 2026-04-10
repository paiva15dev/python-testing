def criar_tarefa(client, headers, title="Tarefa teste", description=""):
    res = client.post("/tasks", json={"title": title, "description": description}, headers=headers)
    assert res.status_code == 201
    return res.get_json()["task"]


class TestListTasks:

    def test_lista_vazia(self, client, auth_headers):
        res = client.get("/tasks", headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["total"] == 0

    def test_lista_com_tarefas(self, client, auth_headers):
        criar_tarefa(client, auth_headers, "Tarefa 1")
        criar_tarefa(client, auth_headers, "Tarefa 2")
        res = client.get("/tasks", headers=auth_headers)
        assert res.get_json()["total"] == 2

    def test_filtra_por_done(self, client, auth_headers):
        task = criar_tarefa(client, auth_headers, "Concluir")
        client.patch(f"/tasks/{task['id']}/toggle", headers=auth_headers)
        criar_tarefa(client, auth_headers, "Pendente")
        res = client.get("/tasks?done=true", headers=auth_headers)
        assert res.get_json()["total"] == 1

    def test_sem_token_retorna_401(self, client):
        res = client.get("/tasks")
        assert res.status_code == 401


class TestCreateTask:

    def test_cria_tarefa_sucesso(self, client, auth_headers):
        res = client.post("/tasks", json={"title": "Nova tarefa"}, headers=auth_headers)
        assert res.status_code == 201
        assert res.get_json()["task"]["done"] is False

    def test_cria_tarefa_sem_titulo(self, client, auth_headers):
        res = client.post("/tasks", json={"description": "sem titulo"}, headers=auth_headers)
        assert res.status_code == 400


class TestUpdateTask:

    def test_atualiza_titulo(self, client, auth_headers):
        task = criar_tarefa(client, auth_headers)
        res = client.put(f"/tasks/{task['id']}", json={"title": "Novo titulo"}, headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["task"]["title"] == "Novo titulo"

    def test_atualiza_done(self, client, auth_headers):
        task = criar_tarefa(client, auth_headers)
        res = client.put(f"/tasks/{task['id']}", json={"done": True}, headers=auth_headers)
        assert res.get_json()["task"]["done"] is True


class TestToggleTask:

    def test_toggle(self, client, auth_headers):
        task = criar_tarefa(client, auth_headers)
        res = client.patch(f"/tasks/{task['id']}/toggle", headers=auth_headers)
        assert res.get_json()["task"]["done"] is True

    def test_toggle_duplo(self, client, auth_headers):
        task = criar_tarefa(client, auth_headers)
        client.patch(f"/tasks/{task['id']}/toggle", headers=auth_headers)
        res = client.patch(f"/tasks/{task['id']}/toggle", headers=auth_headers)
        assert res.get_json()["task"]["done"] is False


class TestDeleteTask:

    def test_deleta_tarefa(self, client, auth_headers):
        task = criar_tarefa(client, auth_headers)
        res = client.delete(f"/tasks/{task['id']}", headers=auth_headers)
        assert res.status_code == 200
        get = client.get(f"/tasks/{task['id']}", headers=auth_headers)
        assert get.status_code == 404

    def test_nao_deleta_tarefa_de_outro(self, client, auth_headers):
        task = criar_tarefa(client, auth_headers)
        client.post("/auth/register", json={
            "username": "invasor", "email": "invasor@test.com", "password": "senha123"
        })
        login = client.post("/auth/login", json={"username": "invasor", "password": "senha123"})
        headers2 = {"Authorization": f"Bearer {login.get_json()['access_token']}"}
        res = client.delete(f"/tasks/{task['id']}", headers=headers2)
        assert res.status_code == 403