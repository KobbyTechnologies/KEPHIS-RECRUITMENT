from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_request, name='login'),
    path('register', views.register_request, name='register'),
    path("verify", views.verifyRequest,name='verify'),
    path('logout', views.logout, name='logout'),

    path('profile', views.profile_request, name="profile"),
    path('FnApplicantDetails', views.FnApplicantDetails, name="FnApplicantDetails"),
    path('JobExperience', views.JobExperience, name="JobExperience"),
    path('FnApplicantProfessionalCourse', views.FnApplicantProfessionalCourse,
         name="FnApplicantProfessionalCourse"),
    path('FnApplicantAcademicQualification', views.FnApplicantAcademicQualification,
         name='FnApplicantAcademicQualification'),
    path('FnApplicantProfessionalMembership', views.FnApplicantProfessionalMembership,
         name='FnApplicantProfessionalMembership'),
    path('FnApplicantHobby', views.FnApplicantHobby, name='FnApplicantHobby'),
    path('FnApplicantReferee', views.FnApplicantReferee, name='FnApplicantReferee'),
]
