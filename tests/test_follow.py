import pytest

from posts.models import Follow


class TestFollowAPI:

    @pytest.mark.django_db(transaction=True)
    def test_follow_not_found(self, client, follow_1, follow_2):
        response = client.get('/api/v1/follow/')

        assert response.status_code != 404, (
            'Страница `/api/v1/follow/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code != 500, (
            'Страница `/api/v1/follow/` не может быть обработана вашим сервером, проверьте view-функцию в *views.py*'
        )

    @pytest.mark.django_db(transaction=True)
    def test_follow_not_auth(self, client, follow_1, follow_2):
        response = client.get('/api/v1/follow/')
        assert response.status_code == 401, (
            'Проверьте, что `/api/v1/follow/` при GET запросе без токена возвращает статус 401'
        )

        data = {}
        response = client.post('/api/v1/follow/', data=data)
        assert response.status_code == 401, (
            'Проверьте, что `/api/v1/follow/` при POST запросе без токена возвращает статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_follow_get(self, user_client, user, follow_1, follow_2, follow_3):
        response = user_client.get('/api/v1/follow/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/v1/follow/` с токеном авторизации возвращается статус 200'
        )

        test_data = response.json()

        assert type(test_data) == list, (
            'Проверьте, что при GET запросе на `/api/v1/follow/` возвращается список'
        )

        assert len(test_data) == Follow.objects.filter(following__username=user.username).count(), (
            'Проверьте, что при GET запросе на `/api/v1/follow/` возвращается список всех подписчиков пользователя'
        )

        follow = Follow.objects.filter(user=user)[0]
        test_group = test_data[0]
        assert 'user' in test_group, (
            'Проверьте, что добавили `user` в список полей `fields` сериализатора модели Follow'
        )
        assert 'following' in test_group, (
            'Проверьте, что добавили `following` в список полей `fields` сериализатора модели Follow'
        )

        assert test_group['user'] == follow.user.username, (
            'Проверьте, что при GET запросе на `/api/v1/follow/` возвращается список подписок текущего пользователя, '
            'в поле `user` должен быть `username`'
        )
        assert test_group['following'] == follow.following.username, (
            'Проверьте, что при GET запросе на `/api/v1/follow/` возвращается весь список подписок, '
            'в поле `following` должен быть `username`'
        )

    @pytest.mark.django_db(transaction=True)
    def test_follow_create(self, user_client, follow_2, follow_3, user, user_2, another_user):
        follow_count = Follow.objects.count()

        data = {}
        response = user_client.post('/api/v1/follow/', data=data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе на `/api/v1/follow/` с неправильными данными возвращается статус 400'
        )

        data = {'following': another_user.username}
        response = user_client.post('/api/v1/follow/', data=data)
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе на `/api/v1/follow/` с правильными данными возвращается статус 201'
        )

        test_data = response.json()

        msg_error = (
            'Проверьте, что при POST запросе на `/api/v1/follow/` возвращается словарь с данными новой подписки'
        )
        assert type(test_data) == dict, msg_error
        assert test_data.get('user') == user.username, msg_error
        assert test_data.get('following') == data['following'], msg_error

        assert follow_count + 1 == Follow.objects.count(), (
            'Проверьте, что при POST запросе на `/api/v1/follow/` создается подписка'
        )

        response = user_client.post('/api/v1/follow/', data=data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе на `/api/v1/follow/` '
            'на уже подписанного автора возвращается статус 400'
        )

        data = {'following': user.username}
        response = user_client.post('/api/v1/follow/', data=data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе на `/api/v1/follow/` '
            'при попытке подписаться на самого себя возвращается статус 400'
        )

    @pytest.mark.django_db(transaction=True)
    def test_follow_search_filter(self, user_client, follow_1, follow_2,
                                  follow_3, follow_4, follow_5,
                                  user, user_2, another_user):

        follow_user = Follow.objects.filter(user=user)
        follow_user_cnt = follow_user.count()

        response = user_client.get('/api/v1/follow/')
        assert response.status_code != 404, (
            'Страница `/api/v1/follow/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            'Страница `/api/v1/follow/` не работает, проверьте view-функцию'
        )

        test_data = response.json()
        assert len(test_data) == follow_user_cnt, (
            'Проверьте, что при GET запросе на `/api/v1/follow/` возвращается список всех подписок пользователя'
        )

        response = user_client.get(f'/api/v1/follow/?search={user_2.username}')
        assert len(response.json()) == follow_user.filter(following=user_2).count(), (
            'Проверьте, что при GET запросе с параметром `search` на `/api/v1/follow/` '
            'возвращается результат поиска по подписке'
        )

        response = user_client.get(f'/api/v1/follow/?search={another_user.username}')
        assert len(response.json()) == follow_user.filter(following=another_user).count(), (
            'Проверьте, что при GET запросе с параметром `search` на `/api/v1/follow/` '
            'возвращается результат поиска по подписке'
        )
