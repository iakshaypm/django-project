from django.urls import path, include
from exchange import views

app_name = 'exchange'

urlpatterns = [
    path('question/add/', views.QuestionView.as_view(), name='create-question'),
    path('questions/show/', views.QuestionListView.as_view(), name='list-question'),
    path('question/<int:pk>/show', views.QuestionRetrieveView.as_view(), name='show-question'),
    path('question/<int:pk>/edit', views.QuestionUpdateView.as_view(), name='edit-question'),
    path('question/<int:pk>/delete', views.QuestionDeleteView.as_view(), name='delete-question'),

    path('comment/add/', views.CommentView.as_view(), name='add-comment'),
    path('comment/show/', views.CommentListView.as_view(), name='list-comment'),
    path('comment/<int:pk>/show', views.CommentRetrieveView.as_view(), name='show-comment'),
    path('comment/<int:pk>/delete', views.CommentDeleteView.as_view(), name='delete-comment'),

    path('upvote/add/', views.CommentView.as_view(), name='add-upvote'),
    path('upvote/<int:pk>/delete', views.CommentDeleteView.as_view(), name='delete-upvote'),

]
