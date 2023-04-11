# from audioop import reverse
import json
import datetime as dt
from datetime import date
import base64
import requests
from requests import Session
from django.shortcuts import render, redirect
# from requests_ntlm import HttpNtlmAuth
from django.conf import settings as config
from django.contrib import messages
from django.views import View
from myRequest.views import UserObjectMixins
# Create your views here.


class UserObjectMixin(object):
    model = None
    session = Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

    def get_object(self, endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response


def CompanyJobs(request):
    try:
        session = requests.Session()
        session.auth = config.AUTHS

        Access_Point = config.O_DATA.format("/QyRecruitmentRequests")
        submitted = config.O_DATA.format("/QyApplicantJobApplied")

        todays_date = date.today()
        year = todays_date.year
        Job = []
        Sub = []
        try:
            response = session.get(Access_Point, timeout=10).json()
            submitted_res = session.get(submitted, timeout=10).json()
            for job in response['value']:
                if job['Submitted_To_Portal'] == True:
                    output_json = json.dumps(job)
                    Job.append(json.loads(output_json))
            for subs in submitted_res['value']:
                if subs['Application_No_'] == request.session['No_']:
                    output_json = json.dumps(subs)
                    Sub.append(json.loads(output_json))
        except requests.exceptions.ConnectionError as e:
            print(e)
        count = len(Job)
        counter = len(Sub)
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

        my_name = request.session['E_Mail']

        ctx = {"today": todays_date, "year": year,
               "count": count, "res": Job, "sub": Sub,
               "counter": counter, "my_name": my_name}
    except KeyError:
        messages.error(request, "Session has expired, Login Again")
        return redirect('login')
    return render(request, 'job.html', ctx)


def JobDetail(request, pk, no):
    try:
        session = requests.Session()
        session.auth = config.AUTHS

        Access_Point = config.O_DATA.format("/QyRecruitmentRequests")
        Qualifications = config.O_DATA.format("/QyJobAcademicQualifications")
        Experience = config.O_DATA.format("/QyJobExperienceQualifications")
        Industry = config.O_DATA.format("/QyJobIndustries")
        Memberships = config.O_DATA.format("/QyProfessionalMemberships")
        Responsibilities = config.O_DATA.format("/QyJobResponsibilities")
        Skills = config.O_DATA.format("/QyJobKnowledgeSkills")
        Courses = config.O_DATA.format("/QyProfessionalCourses")
        JobMembeships = config.O_DATA.format("/QyJobProfessionalMembeships")
        Positions = config.O_DATA.format("/QyJobPositionsSupervising")
        Attachments = config.O_DATA.format("/QyJobAttachments")
        res = ''
        E_response = ''

        try:
            response = session.get(Access_Point, timeout=10).json()
            Qualifications_res = session.get(Qualifications, timeout=10).json()
            Experience_res = session.get(Experience, timeout=10).json()
            Industry_res = session.get(Industry, timeout=10).json()
            Memberships_res = session.get(Memberships, timeout=10).json()
            Responsibilities_res = session.get(
                Responsibilities, timeout=10).json()
            Skills_res = session.get(Skills, timeout=10).json()
            Courses_res = session.get(Courses, timeout=10).json()
            JobMembeships_res = session.get(JobMembeships, timeout=10).json()
            Positions_res = session.get(Positions, timeout=10).json()
            Attachments_res = session.get(Attachments, timeout=10).json()

            RESPOs = []
            Skill = []
            Course = []
            Member = []
            Position = []
            Attachment = []

            All_Industry = Industry_res['value']
            All_Memberships = Memberships_res['value']
            for job in response['value']:
                if job['Job_ID'] == pk:
                    res = job
            for Qualifications in Qualifications_res['value']:
                if Qualifications['Job_ID'] == pk:
                    response = Qualifications
            for Experience in Experience_res['value']:
                if Experience['Job_ID'] == pk:
                    E_response = Experience
            for Responsibilities in Responsibilities_res['value']:
                if Responsibilities['Code'] == pk:
                    output_json = json.dumps(Responsibilities)
                    RESPOs.append(json.loads(output_json))
            for Skills in Skills_res['value']:
                if Skills['Code'] == pk:
                    output_json = json.dumps(Skills)
                    Skill.append(json.loads(output_json))
            for Courses in Courses_res['value']:
                if Courses['Job_ID'] == pk:
                    output_json = json.dumps(Courses)
                    Course.append(json.loads(output_json))
            for JobMembeship in JobMembeships_res['value']:
                if JobMembeship['Job_ID'] == pk:
                    output_json = json.dumps(JobMembeship)
                    Member.append(json.loads(output_json))
            for Positions in Positions_res['value']:
                if Positions['Job_ID'] == pk:
                    output_json = json.dumps(Positions)
                    Position.append(json.loads(output_json))
            for Attachments in Attachments_res['value']:
                if Attachments['Job_ID'] == pk:
                    output_json = json.dumps(Attachments)
                    Attachment.append(json.loads(output_json))
        except requests.exceptions.ConnectionError as e:
            print(e)

        my_name = request.session['E_Mail']
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": res,
               "Qualifications": response, "experience": E_response,
               "industry": All_Industry, "member": All_Memberships,
               "RESPOs": RESPOs, "Skill": Skill,
               "Course": Course, "JobMembeship": Member,
               "Position": Position, "Attach": Attachment,
               "my_name": my_name}
    except KeyError:
        messages.error(request, "Session has expired, Login Again")
        return redirect('login')
    return render(request, 'jobDetail.html', ctx)


def FnApplicantApplyJob(request, pk, no):
    applicantNo = request.session['No_']
    needCode = ""

    if request.method == 'POST':
        try:
            needCode = request.POST.get('needCode')
        except ValueError:
            messages.error(request, "Invalid credentials, try again")
            return redirect('JobApplication', pk=pk, no=no)
    try:
        response = config.CLIENT.service.FnApplicantApplyJob(
            applicantNo, needCode)
        print(response)
        messages.success(request, "Application Sent successfully")
        return redirect('JobApplication', pk=pk, no=no)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('JobApplication', pk=pk, no=no)


def FnWithdrawJobApplication(request):
    applicantNo = request.session['No_']
    needCode = ""

    if request.method == 'POST':
        try:
            needCode = request.POST.get('needCode')
        except ValueError:
            messages.error(request, "Invalid credentials, try again")
            return redirect('job')
    try:
        response = config.CLIENT.service.FnWithdrawJobApplication(
            applicantNo, needCode)
        print(response)
        messages.success(request, "Application Cancelled successfully")
        return redirect('job')
    except Exception as e:
        url = redirect('profile')
        messages.error(request, e)
        print(e)
    return redirect('job')


def UploadAttachedDocument(request, pk, no):
    docNo = request.session['No_']
    response = ""
    fileName = ""
    attachment = ""
    tableID = 52177558  #52177607

    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            print("Not Working")
            return redirect('JobApplication', pk=pk, no=no)
        
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())

            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    docNo, fileName, attachment, tableID)
                print(response)
            except Exception as e:
                messages.error(request, e)
                print(e)

        if response == True:
            messages.success(request, "Successfully Sent !!")
            return redirect('JobApplication', pk=pk, no=no)
        else:
            messages.error(request, "OooPs!!! something went Wrong.")
            return redirect('JobApplication', pk=pk, no=no)

    return redirect('JobApplication', pk=pk, no=no)


# class JobApplication(UserObjectMixins, View):

def JobApplication(request, pk, no):
    try:
        todays_date = date.today()
        year = todays_date.year
        session = requests.Session()
        session.auth = config.AUTHS

        Access_point = config.O_DATA.format("/QyRecruitmentRequests")

        Applicant = config.O_DATA.format("/QyApplicants")
        citizenship = config.O_DATA.format("/CountryRegion")
        countyCode = config.O_DATA.format("/QyCounties")
        industry = config.O_DATA.format("/QyJobIndustries")
        Qualification = config.O_DATA.format("/QyQualificationCodes")
        ProfessionalBodies = config.O_DATA.format("/QyProfessionalBodies")
        Study = config.O_DATA.format("/QyFieldsOfStudy")
        Qualifications = config.O_DATA.format(
            "/QyApplicantAcademicQualifications")
        Experience = config.O_DATA.format("/QyApplicantJobExperience")
        Courses = config.O_DATA.format(
            "/QyApplicantJobProfessionalCourses")
        Memberships = config.O_DATA.format(
            "/QyApplicantProfessionalMemberships")
        Hobbies = config.O_DATA.format("/QyApplicantHobbies")
        Referees = config.O_DATA.format("/QyApplicantReferees")
        Attachments = config.O_DATA.format("/QyJobAttachments")
        
        res = ''
        My_Qualifications = []
        My_Experience = []
        My_Course = []
        My_Membership = []
        My_Hobby = []
        My_Referees = []

    
        Job_response = session.get(Access_point, timeout=10).json()
        
        App_response = session.get(Applicant, timeout=10).json()
        response = session.get(citizenship, timeout=10).json()
        county_res = session.get(countyCode, timeout=10).json()
        industry_res = session.get(industry, timeout=10).json()
        Qualification_res = session.get(
            Qualification, timeout=10).json()
        ProfessionalBodies_res = session.get(
            ProfessionalBodies, timeout=10).json()
        Study_res = session.get(Study, timeout=10).json()
        Qualifications_res = session.get(
            Qualifications, timeout=10).json()
        Experience_res = session.get(Experience, timeout=10).json()
        Courses_res = session.get(Courses, timeout=10).json()
        Memberships_res = session.get(Memberships, timeout=10).json()
        Hobbies_res = session.get(Hobbies, timeout=10).json()
        Referees_Res = session.get(Referees, timeout=10).json()
        Attachments_res = session.get(Attachments, timeout=10).json()

        Attachment = []

        for job in Job_response['value']:
            if job['No_'] == pk:
                res = job
                
        for applicant in App_response['value']:
            if applicant['No_'] == request.session['No_']:
                fullname = applicant['First_Name'] + \
                    " " + applicant['Last_Name']

                request.session['username'] = fullname
                username = request.session['username']
                res_app = applicant
                

        for Qualifications in Qualifications_res['value']:
            if Qualifications['Applicant_No_'] == request.session['No_']:
                output_json = json.dumps(Qualifications)
                My_Qualifications.append(json.loads(output_json))

        for Experience in Experience_res['value']:
            if Experience['Applicant_No_'] == request.session['No_']:
                output_json = json.dumps(Experience)
                My_Experience.append(json.loads(output_json))

        for course in Courses_res['value']:
            if course['Applicant_No_'] == request.session['No_']:
                output_json = json.dumps(course)
                My_Course.append(json.loads(output_json))

        for membership in Memberships_res['value']:
            if membership['Applicant_No_'] == request.session['No_']:
                output_json = json.dumps(membership)
                My_Membership.append(json.loads(output_json))

        for hobby in Hobbies_res['value']:
            if hobby['No_'] == request.session['No_']:
                output_json = json.dumps(hobby)
                My_Hobby.append(json.loads(output_json))

        for ref in Referees_Res['value']:
            if ref['No'] == request.session['No_']:
                output_json = json.dumps(ref)
                My_Referees.append(json.loads(output_json))

        for Attachments in Attachments_res['value']:
            if Attachments['Job_ID'] == pk:
                output_json = json.dumps(Attachments)
                Attachment.append(json.loads(output_json))

        country = response['value']
        county = county_res['value']
        ind = industry_res['value']
        Quo = Qualification_res['value']
        Pro = ProfessionalBodies_res['value']
        FStudy = Study_res['value']

    

        my_name = request.session['E_Mail']
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

       
        ctx = {
            'res': res,
            'res_app': res_app,
            "year": year,
            "country": country,
            "county": county,
            "industry": ind,
            "Quo": Quo,
            "Pro": Pro,
            "Study": FStudy,
            "applicant": res_app,
            "fullname": fullname,
            "Qualify": My_Qualifications,
            "experience": My_Experience,
            "course": My_Course,
            "membership": My_Membership,
            "hobby": My_Hobby,
            "Referee": My_Referees,
            "today": todays_date,
            "my_name": my_name,
            "Attach": Attachment,
        }

    except Exception as e:
        print(f'{e}')
        messages.info(request, f'{e}')
        return redirect('JobApplication', pk=pk, no=no)

    return render(request, 'jobApplication.html', ctx)
