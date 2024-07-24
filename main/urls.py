from django.urls import path

from .views import user_view, post_view

urlpatterns = [
    path('register', user_view.register, name='register'),
    path('login', user_view.login, name='login'),
    path('logout', user_view.logout, name='logout'),
    path('get-user-profile', user_view.get_user_profile, name='get_user_profile'),

    ### post related urls
    path('', post_view.all_post_view, name='all_post'),
    path('create-post', post_view.post_create_view, name='post_create'),
    path('update-post/<int:post_id>', post_view.post_update_view, name='post_update'),
    path('delete-post/<int:post_id>', post_view.post_delete_view, name='post_delete'),
    path('single-post/<int:post_id>', post_view.singel_post_view, name='post_single'),
    path('post/tags', post_view.tags_post_view, name='post_tags'),
    path('suggestions', post_view.suggestions, name='suggestions'),
]