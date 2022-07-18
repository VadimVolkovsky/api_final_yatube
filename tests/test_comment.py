import pytest

from posts.models import Comment


class TestCommentAPI:

    @pytest.mark.django_db(transaction=True)
    def test_comments_not_authenticated(self, client, post):
        response = client.get(f'/api/v1/posts/{post.id}/comments/')

        code = 200
        assert response.status_code == code, (
            'Анонимный пользователь при запросе `/api/v1/posts/{post.id}/comments/` '
            f'должен получать ответ с кодом {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_comment_single_not_authenticated(self, client, post, comment_1_post):
        response = client.get(f'/api/v1/posts/{post.id}/comments/{comment_1_post.id}/')

        code = 200
        assert response.status_code == code, (
            'Анонимный пользователь при запросе `/api/v1/posts/{post.id}/comments/{comment.id}` '
            f'должен получать ответ с кодом {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_comments_not_found(self, user_client, post):
        response = user_client.get(f'/api/v1/posts/{post.id}/comments/')

        assert response.status_code != 404, (
            'Страница `/api/v1/posts/{post.id}/comments/` не найдена, проверьте этот адрес в *urls.py*'
        )

    @pytest.mark.django_db(transaction=True)
    def test_comments_get(self, user_client, post, comment_1_post, comment_2_post, comment_1_another_post):
        response = user_client.get(f'/api/v1/posts/{post.id}/comments/')

        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/v1/posts/{post.id}/comments/` '
            'с токеном авторизации возвращаетсся статус 200'
        )
        test_data = response.json()
        assert type(test_data) == list, (
            'Проверьте, что при GET запросе на `/api/v1/posts/{post.id}/comments/` возвращается список'
        )
        assert len(test_data) == Comment.objects.filter(post=post).count(), (
            'Проверьте, что при GET запросе на `/api/v1/posts/{post.id}/comments/` '
            'возвращается весь список комментов статьи'
        )

        comment = Comment.objects.filter(post=post).first()
        test_comment = test_data[0]
        assert 'id' in test_comment, (
            'Проверьте, что добавили `id` в список полей `fields` сериализатора модели Comment'
        )
        assert 'text' in test_comment, (
            'Проверьте, что добавили `text` в список полей `fields` сериализатора модели Comment'
        )
        assert 'author' in test_comment, (
            'Проверьте, что добавили `author` в список полей `fields` сериализатора модели Comment'
        )
        assert 'post' in test_comment, (
            'Проверьте, что добавили `post` в список полей `fields` сериализатора модели Comment'
        )
        assert 'created' in test_comment, (
            'Проверьте, что добавили `created` в список полей `fields` сериализатора модели Comment'
        )
        assert test_comment['author'] == comment.author.username, (
            'Проверьте, что `author` сериализатора модели Comment возвращает имя пользователя'
        )
        assert test_comment['id'] == comment.id, (
            'Проверьте, что при GET запросе на `/api/v1/posts/{post.id}/comments/` возвращается весь список статей'
        )

    @pytest.mark.django_db(transaction=True)
    def test_comments_create(self, user_client, post, user, another_user):
        comments_count = Comment.objects.count()

        data = {}
        response = user_client.post(f'/api/v1/posts/{post.id}/comments/', data=data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе на `/api/v1/posts/{post.id}/comments/` '
            'с не правильными данными возвращается статус 400'
        )

        data = {'author': another_user.id, 'text': 'Новый коммент 1233', 'post': post.id}
        response = user_client.post(f'/api/v1/posts/{post.id}/comments/', data=data)
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе на `/api/v1/posts/{post.id}/comments/` '
            'с правильными данными возвращается статус 201'
        )

        test_data = response.json()
        msg_error = (
            'Проверьте, что при POST запросе на `/api/v1/posts/{post.id}/comments/` '
            'возвращается словарь с данными нового комментария'
        )
        assert type(test_data) == dict, msg_error
        assert test_data.get('text') == data['text'], msg_error

        assert test_data.get('author') == user.username, (
            'Проверьте, что при POST запросе на `/api/v1/posts/{post.id}/comments/` '
            'создается комментарий от авторизованного пользователя'
        )
        assert comments_count + 1 == Comment.objects.count(), (
            'Проверьте, что при POST запросе на `/api/v1/posts/{post.id}/comments/` создается комментарий'
        )

    @pytest.mark.django_db(transaction=True)
    def test_comment_get_current(self, user_client, post, comment_1_post, user):
        response = user_client.get(f'/api/v1/posts/{post.id}/comments/{comment_1_post.id}/')

        assert response.status_code == 200, (
            'Страница `/api/v1/posts/{post.id}/comments/{comment.id}/` не найдена, '
            'проверьте этот адрес в *urls.py*'
        )

        test_data = response.json()
        assert test_data.get('text') == comment_1_post.text, (
            'Проверьте, что при GET запросе `/api/v1/posts/{post.id}/comments/{comment.id}/` '
            'возвращаете данные сериализатора, не найдено или не правильное значение `text`'
        )
        assert test_data.get('author') == user.username, (
            'Проверьте, что при GET запросе `/api/v1/posts/{post.id}/comments/{comment.id}/` '
            'возвращаете данные сериализатора, не найдено или не правильное значение `author`, '
            'должно возвращать имя пользователя '
        )
        assert test_data.get('post') == post.id, (
            'Проверьте, что при GET запросе `/api/v1/posts/{post.id}/comments/{comment.id}/` '
            'возвращаете данные сериализатора, не найдено или не правильное значение `post`'
        )

    @pytest.mark.django_db(transaction=True)
    def test_comment_patch_current(self, user_client, post, comment_1_post, comment_2_post):
        response = user_client.patch(f'/api/v1/posts/{post.id}/comments/{comment_1_post.id}/',
                                     data={'text': 'Поменяли текст коммента'})

        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе `/api/v1/posts/{post.id}/comments/{comment.id}/` '
            'возвращаете статус 200'
        )

        test_comment = Comment.objects.filter(id=comment_1_post.id).first()

        assert test_comment, (
            'Проверьте, что при PATCH запросе `/api/v1/posts/{post.id}/comments/{comment.id}/` '
            'вы не удалили комментарий'
        )

        assert test_comment.text == 'Поменяли текст коммента', (
            'Проверьте, что при PATCH запросе `/api/v1/posts/{id}/` вы изменяете статью'
        )

        response = user_client.patch(f'/api/v1/posts/{post.id}/comments/{comment_2_post.id}/',
                                     data={'text': 'Поменяли текст статьи'})

        assert response.status_code == 403, (
            'Проверьте, что при PATCH запросе `/api/v1/posts/{post.id}/comments/{comment.id}/` '
            'для не своей статьи возвращаете статус 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_comment_delete_current(self, user_client, post, comment_1_post, comment_2_post):
        response = user_client.delete(f'/api/v1/posts/{post.id}/comments/{comment_1_post.id}/')

        assert response.status_code == 204, (
            'Проверьте, что при DELETE запросе `/api/v1/posts/{post.id}/comments/{comment.id}/` возвращаете статус 204'
        )

        test_comment = Comment.objects.filter(id=post.id).first()

        assert not test_comment, (
            'Проверьте, что при DELETE запросе `/api/v1/posts/{post.id}/comments/{comment.id}/` вы удалили комментарий'
        )

        response = user_client.delete(f'/api/v1/posts/{post.id}/comments/{comment_2_post.id}/')

        assert response.status_code == 403, (
            'Проверьте, что при DELETE запросе `/api/v1/posts/{post.id}/comments/{comment.id}/` '
            'для не своего комментария возвращаете статус 403'
        )
