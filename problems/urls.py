# problems/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.start_page, name='start_page'),
    path('problem_list/', views.ProblemListView.as_view(), name='problem_list'),
    path('problem/<int:pk>/', views.ProblemDetailView.as_view(), name='problem_detail'),
    path('problem/<int:pk>/delete/', views.ProblemDeleteView.as_view(), name='problem_delete'),
    path('add_problem/', views.add_problem, name='add_problem'),
    path('problem/<int:pk>/edit/', views.ProblemUpdateView.as_view(), name='problem_edit'),
    path('thought_process_list/', views.ThoughtProcessListView.as_view(), name='thoughtprocess_list'),
    path('thought_process/<int:pk>/', views.ThoughtProcessDetailView.as_view(), name='thoughtprocess_detail'),
    path('thought_process/<int:pk>/delete/', views.ThoughtProcessDeleteView.as_view(), name='thoughtprocess_delete'),
    path('add_thought_process/', views.add_thought_process, name='add_thought_process'),
    path('thought_process/<int:pk>/edit/', views.ThoughtProcessUpdateView.as_view(), name='thoughtprocess_edit'),
    path('visualization/', views.visualization_page, name='visualization_page'),
    path('problem_list/', views.ProblemListView.as_view(), name='problem_list'),
    path('export_csv/', views.ExportProblemCSV.as_view(), name='export_problem_csv'),
]

