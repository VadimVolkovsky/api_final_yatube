import pytest

from posts.models import Post


class TestPostAPI:

    @pytest.mark.django_db(transaction=True)
    def test_post_not_found(self, client, post):
        response = client.get('/api/v1/posts/')

        assert response.status_code != 404, (
            'Страница `/api/v1/posts/` не найдена, проверьте этот адрес в *urls.py*'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_list_not_auth(self, client, post):
        response = client.get('/api/v1/posts/')

        assert response.status_code == 200, (
            'Проверьте, что на `/api/v1/posts/` при запросе без токена возвращаете статус 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_single_not_auth(self, client, post):
        response = client.get(f'/api/v1/posts/{post.id}/')

        assert response.status_code == 200, (
            'Проверьте, что на `/api/v1/posts/{post.id}/` при запросе без токена возвращаете статус 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_posts_get_not_paginated(self, user_client, post, another_post):
        response = user_client.get('/api/v1/posts/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/v1/posts/` с токеном авторизации возвращается статус 200'
        )

        test_data = response.json()

        # response without pagination must be a list type
        assert type(test_data) == list, (
            'Проверьте, что при GET запросе на `/api/v1/posts/` без пагинации, возвращается список'
        )

        assert len(test_data) == Post.objects.count(), (
            'Проверьте, что при GET запросе на `/api/v1/posts/` без пагинации возвращается весь список статей'
        )

        post = Post.objects.all()[0]
        test_post = test_data[0]
        assert 'id' in test_post, (
            'Проверьте, что добавили `id` в список полей `fields` сериализатора модели Post'
        )
        assert 'text' in test_post, (
            'Проверьте, что добавили `text` в список полей `fields` сериализатора модели Post'
        )
        assert 'author' in test_post, (
            'Проверьте, что добавили `author` в список полей `fields` сериализатора модели Post'
        )
        assert 'pub_date' in test_post, (
            'Проверьте, что добавили `pub_date` в список полей `fields` сериализатора модели Post'
        )
        assert test_post['author'] == post.author.username, (
            'Проверьте, что `author` сериализатора модели Post возвращает имя пользователя'
        )

        assert test_post['id'] == post.id, (
            'Проверьте, что при GET запросе на `/api/v1/posts/` возвращается весь список статей'
        )

    @pytest.mark.django_db(transaction=True)
    def test_posts_get_paginated(self, user_client, post, post_2, another_post):
        base_url = '/api/v1/posts/'
        limit = 2
        offset = 2
        url = f'{base_url}?limit={limit}&offset={offset}'
        response = user_client.get(url)
        assert response.status_code == 200, (
            f'Проверьте, что при GET запросе `{url}` с токеном авторизации возвращается статус 200'
        )

        test_data = response.json()

        # response with pagination must be a dict type
        assert type(test_data) == dict, (
            f'Проверьте, что при GET запросе на `{url}` с пагинацией, возвращается словарь'
        )
        assert "results" in test_data.keys(), (
            f'Убедитесь, что при GET запросе на `{url}` с пагинацией, ключ `results` присутствует в ответе'
        )
        assert len(test_data.get('results')) == Post.objects.count() - offset, (
            f'Проверьте, что при GET запросе на `{url}` с пагинацией, возвращается корректное количество статей'
        )
        assert test_data.get('results')[0].get('text') == another_post.text, (
            f'Убедитесь, что при GET запросе на `{url}` с пагинацией, '
            'в ответе содержатся корректные статьи'
        )

        post = Post.objects.get(text=another_post.text)
        test_post = test_data.get('results')[0]
        assert 'id' in test_post, (
            'Проверьте, что добавили `id` в список полей `fields` сериализатора модели Post'
        )
        assert 'text' in test_post, (
            'Проверьте, что добавили `text` в список полей `fields` сериализатора модели Post'
        )
        assert 'author' in test_post, (
            'Проверьте, что добавили `author` в список полей `fields` сериализатора модели Post'
        )
        assert 'pub_date' in test_post, (
            'Проверьте, что добавили `pub_date` в список полей `fields` сериализатора модели Post'
        )
        assert test_post['author'] == post.author.username, (
            'Проверьте, что `author` сериализатора модели Post возвращает имя пользователя'
        )

        assert test_post['id'] == post.id, (
            f'Проверьте, что при GET запросе на `{url}` возвращается корректный список статей'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_create(self, user_client, user, another_user, group_1):
        post_count = Post.objects.count()

        data = {}
        response = user_client.post('/api/v1/posts/', data=data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе на `/api/v1/posts/` с не правильными данными возвращается статус 400'
        )

        data = {'text': 'Статья номер 3'}
        response = user_client.post('/api/v1/posts/', data=data)
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе на `/api/v1/posts/` с правильными данными возвращается статус 201'
        )
        assert (
                response.json().get('author') is not None
                and response.json().get('author') == user.username
        ), (
            'Проверьте, что при POST запросе на `/api/v1/posts/` автором указывается пользователь,'
            'от имени которого сделан запрос'
        )

        # post with group
        data = {'text': 'Статья номер 4', 'group': group_1.id}
        response = user_client.post('/api/v1/posts/', data=data)
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе на `/api/v1/posts/`'
            ' можно создать статью с сообществом и возвращается статус 201'
        )
        assert response.json().get('group') == group_1.id, (
            'Проверьте, что при POST запросе на `/api/v1/posts/`'
            ' создается публикация с указанием сообщества'
        )

        test_data = response.json()
        msg_error = (
            'Проверьте, что при POST запросе на `/api/v1/posts/` возвращается словарь с данными новой статьи'
        )
        assert type(test_data) == dict, msg_error
        assert test_data.get('text') == data['text'], msg_error

        assert test_data.get('author') == user.username, (
            'Проверьте, что при POST запросе на `/api/v1/posts/` создается статья от авторизованного пользователя'
        )
        assert post_count + 2 == Post.objects.count(), (
            'Проверьте, что при POST запросе на `/api/v1/posts/` создается статья'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_get_current(self, user_client, post, user):
        response = user_client.get(f'/api/v1/posts/{post.id}/')

        assert response.status_code == 200, (
            'Страница `/api/v1/posts/{id}/` не найдена, проверьте этот адрес в *urls.py*'
        )

        test_data = response.json()
        assert test_data.get('text') == post.text, (
            'Проверьте, что при GET запросе `/api/v1/posts/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `text`'
        )
        assert test_data.get('author') == user.username, (
            'Проверьте, что при GET запросе `/api/v1/posts/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `author`, должно возвращать имя пользователя '
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_patch_current(self, user_client, post, another_post):
        response = user_client.patch(f'/api/v1/posts/{post.id}/',
                                     data={'text': 'Поменяли текст статьи'})

        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе `/api/v1/posts/{id}/` возвращаете статус 200'
        )

        test_post = Post.objects.filter(id=post.id).first()

        assert test_post, (
            'Проверьте, что при PATCH запросе `/api/v1/posts/{id}/` вы не удалили статью'
        )

        assert test_post.text == 'Поменяли текст статьи', (
            'Проверьте, что при PATCH запросе `/api/v1/posts/{id}/` вы изменяете статью'
        )

        response = user_client.patch(f'/api/v1/posts/{another_post.id}/',
                                     data={'text': 'Поменяли текст статьи'})

        assert response.status_code == 403, (
            'Проверьте, что при PATCH запросе `/api/v1/posts/{id}/` для не своей статьи возвращаете статус 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_delete_current(self, user_client, post, another_post):
        response = user_client.delete(f'/api/v1/posts/{post.id}/')

        assert response.status_code == 204, (
            'Проверьте, что при DELETE запросе `/api/v1/posts/{id}/` возвращаете статус 204'
        )

        test_post = Post.objects.filter(id=post.id).first()

        assert not test_post, (
            'Проверьте, что при DELETE запросе `/api/v1/posts/{id}/` вы удалили статью'
        )

        response = user_client.delete(f'/api/v1/posts/{another_post.id}/')

        assert response.status_code == 403, (
            'Проверьте, что при DELETE запросе `/api/v1/posts/{id}/` для не своей статьи возвращаете статус 403'
        )
