from django.urls import path
from . import views

urlpatterns = [
    path('job', views.CompanyJobs, name='job'),
    path('jobDetail/<str:pk>/<str:no>', views.JobDetail, name='jobDetail'),
    path('FnApplicantApplyJob/<str:pk>/<str:no>',
         views.FnApplicantApplyJob, name='FnApplicantApplyJob'),
    path('FnWithdrawJobApplication',
         views.FnWithdrawJobApplication, name='FnWithdrawJobApplication'),
    path('UploadAttachedDocument/<str:pk>/<str:no>',
         views.UploadAttachedDocument.as_view(), name='UploadAttachedDocument'),

    path('JobApplication/<str:pk>/<str:no>',
         views.JobApplication, name='JobApplication')
]
