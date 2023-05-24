import base64
import threading
from django.http import response
from django.shortcuts import redirect, render, HttpResponse
from django.conf import settings as config
import json
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import datetime
from datetime import date
from django.contrib import messages
from cryptography.fernet import Fernet
import re
import enum
import secrets
import string
from django.core.mail import EmailMessage
import threading
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from myRequest.views import UserObjectMixins
import asyncio
import aiohttp
from asgiref.sync import sync_to_async
from django.views import View
# Create your views here.


def get_object(endpoint):
    session = requests.Session()
    session.auth = config.AUTHS
    response = session.get(endpoint, timeout=10)
    return response


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


def send_mail(email, verificationToken, request):
    current_site = get_current_site(request)
    email_subject = 'Activate Your Account'
    email_body = render_to_string('activate.html', {
        'domain': current_site,
        'Secret': verificationToken,
    })

    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=config.EMAIL_HOST_USER, to=[email])

    EmailThread(email).start()


def profile_request(request):
    try:
        todays_date = date.today()
        year = todays_date.year
        session = requests.Session()
        session.auth = config.AUTHS

        citizenship = config.O_DATA.format("/CountryRegion")
        countyCode = config.O_DATA.format("/QyCounties")
        industry = config.O_DATA.format("/QyJobIndustries")
        Qualification = config.O_DATA.format("/QyQualificationCodes")
        ProfessionalBodies = config.O_DATA.format("/QyProfessionalBodies")
        Study = config.O_DATA.format("/QyFieldsOfStudy")
        Access_Point = config.O_DATA.format("/QyApplicants")
        Qualifications = config.O_DATA.format(
            "/QyApplicantAcademicQualifications")
        Experience = config.O_DATA.format("/QyApplicantJobExperience")
        Courses = config.O_DATA.format("/QyApplicantJobProfessionalCourses")
        Memberships = config.O_DATA.format(
            "/QyApplicantProfessionalMemberships")
        Hobbies = config.O_DATA.format("/QyApplicantHobbies")
        Referees = config.O_DATA.format("/QyApplicantReferees")
        res = ""
        My_Qualifications = []
        My_Experience = []
        My_Course = []
        My_Membership = []
        My_Hobby = []
        My_Referees = []
        try:
            response = session.get(citizenship, timeout=10).json()
            county_res = session.get(countyCode, timeout=10).json()
            industry_res = session.get(industry, timeout=10).json()
            Qualification_res = session.get(Qualification, timeout=10).json()
            ProfessionalBodies_res = session.get(
                ProfessionalBodies, timeout=10).json()

            Study_res = session.get(Study, timeout=10).json()
            App_response = session.get(Access_Point, timeout=10).json()
            Qualifications_res = session.get(Qualifications, timeout=10).json()
            Experience_res = session.get(Experience, timeout=10).json()
            Courses_res = session.get(Courses, timeout=10).json()
            Memberships_res = session.get(Memberships, timeout=10).json()
            Hobbies_res = session.get(Hobbies, timeout=10).json()
            Referees_Res = session.get(Referees, timeout=10).json()

            for applicant in App_response['value']:
                if applicant['No_'] == request.session['No_']:
                    fullname = applicant['First_Name'] + \
                        " " + applicant['Last_Name']

                    request.session['username'] = fullname
                    username = request.session['username']
                    res = applicant
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
            country = response['value']
            county = county_res['value']
            ind = industry_res['value']
            Quo = Qualification_res['value']
            Pro = ProfessionalBodies_res['value']
            FStudy = Study_res['value']
        except requests.exceptions.ConnectionError as e:
            print(e)

        my_name = request.session['E_Mail']

        todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {
            "year": year,
            "country": country,
            "county": county,
            "industry": ind,
            "Quo": Quo,
            "Pro": Pro,
            "Study": FStudy,
            "applicant": res,
            "fullname": fullname,
            "Qualify": My_Qualifications,
            "experience": My_Experience,
            "course": My_Course,
            "membership": My_Membership,
            "hobby": My_Hobby,
            "Referee": My_Referees,
            "today": todays_date,
            "my_name": my_name
        }
    except KeyError:
        messages.error(request, "Session has expired, Login Again")
        return redirect('login')

    return render(request, 'profile.html', ctx)


def login_request(request):
    todays_date = date.today()
    year = todays_date.year
    session = requests.Session()
    session.auth = config.AUTHS

    if request.method == 'POST':
        try:
            email = request.POST.get('email').strip()
            password = request.POST.get('password')

            Access_Point = config.O_DATA.format(
                f"/QyApplicants?$filter=E_Mail%20eq%20%27{email}%27")
            response = session.get(Access_Point, timeout=10)

            if response.status_code != 200:
                messages.error(
                    request, f'Failed with status code: {response.status_code}')
                return redirect('login')
            cleanData = response.json()
            for applicant in cleanData['value']:
                Portal_Password = base64.urlsafe_b64decode(
                    applicant['Portal_Password'])
                request.session['No_'] = applicant['No_']
                request.session['E_Mail'] = applicant['E_Mail']
                # applicant_no = request.session['No_']
                # mail = request.session['E_Mail']

                cipher_suite = Fernet(config.ENCRYPT_KEY)
                decoded_text = cipher_suite.decrypt(
                    Portal_Password).decode("ascii")
                if decoded_text == password:
                    return redirect('dashboard')
                messages.error(
                    request, "Invalid Credentials")
                return redirect('login')

            messages.error(request, "Email does not exist")
            return redirect('login')
        except Exception as e:
            print(e)
            messages.error(request, e)
            return redirect('login')

    ctx = {"year": year}
    return render(request, 'login.html', ctx)


def register_request(request):
    todays_date = date.today()
    year = todays_date.year
    email = ''
    password = ''
    confirm_password = ''
    try:
        if request.method == 'POST':

            email = request.POST.get('email').strip()
            my_password = str(request.POST.get('password'))
            confirm_password = str(
                request.POST.get('confirm_password')).strip()

            if len(my_password) < 6:
                messages.error(
                    request, "Password should be at least 6 characters")
                return redirect('register')

            if my_password != confirm_password:
                messages.error(request, "Password mismatch")
                return redirect('register')

            if not email:
                messages.error(request, "Kindly provide your email")
                return redirect('register')

            nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                                for i in range(5))
            verificationToken = str(nameChars)

            cipher_suite = Fernet(config.ENCRYPT_KEY)
            encrypted_text = cipher_suite.encrypt(my_password.encode('ascii'))
            password = base64.urlsafe_b64encode(encrypted_text).decode("ascii")

            # except ValueError:
            #     messages.error(request, "Invalid credentials, try again")
            #     return redirect('register')

            try:
                response = config.CLIENT.service.FnApplicantRegister(
                    email, password)
                print(response)

                if response == True:
                    send_mail(email, verificationToken, request)
                messages.success(
                    request, "'We sent you an email to verify your account")
                return redirect('login')

            except Exception as e:
                print(e)
                messages.error(request, e)
    except Exception as e:
        print(e)
        messages.error(request, e)
        return redirect('register')

    ctx = {"year": year}
    return render(request, "register.html", ctx)


def verifyRequest(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            secret = request.POST.get('secret')
            verified = True
            Access_Point = config.O_DATA.format(
                f"/QyApplicants?$filter=E_Mail%20eq%20%27{email}%27")
            response = get_object(Access_Point)

            if response.status_code != 200:
                messages.error(
                    request, f"Failed with status code: {response.status_code}")
                return redirect('login')
            cleanedData = response.json()
            for res in cleanedData['value']:
                if res['Verification_Token'] == secret:
                    response = config.CLIENT.service.FnVerified(
                        verified, email)
                    messages.success(request, "Verification Successful")
                    return redirect('login')
        except requests.exceptions.RequestException as e:
            print(e)
            messages.error(
                request, "Not Verified. check Credentials or Register")
            return redirect('verify')
        except ValueError:
            messages.error(request, 'Wrong Input')
            return redirect('verify')
    return render(request, "verify.html")


def FnApplicantDetails(request):
    applicantNo = request.session['No_']
    firstName = ""
    middleName = ""
    lastName = ""
    idNumber = ""
    genders = ""
    citizenship = ""
    countyCode = ""
    maritalStatus = ""
    ethnicOrigin = ""
    disabled = ""
    dob = ""
    phoneNumber = ""
    postalAddress = ""
    postalCode = ""
    residentialAddress = ""
    disabilityGrade = ''
    areYouKenyan = ""
    citizenshipBy = ""
    certificateNo = ""
    stateNationality = ""
    country = ""
    subCounty = ""
    constituency = ""
    termsOfService = ""
    currentMonthlySalary = ""
    expectedSalary = ""
    howSoonCanYouTakeThisAppointment = ""
    haveYouEverBeenRemovedOrDismissedFromEmployment = ""
    giveDetails = ""
    haveYouBeenChargedInACourtOfLaw = ""
    offence = ""
    dateOfOffence = ""
    placeOfOffence = ""
    sentenceImposed = ""
    if request.method == 'POST':
        try:
            firstName = request.POST.get('firstName')
            middleName = request.POST.get('middleName')
            lastName = request.POST.get('lastName')
            idNumber = request.POST.get('idNumber')
            genders = request.POST.get('gender')
            citizenship = request.POST.get('citizenship')
            countyCode = request.POST.get('countyCode')
            maritalStatus = int(request.POST.get('maritalStatus'))
            ethnicOrigin = int(request.POST.get('ethnicOrigin'))
            disabled = int(request.POST.get('disabled'))
            dob = request.POST.get('dob')
            phoneNumber = request.POST.get('phoneNumber')
            postalAddress = request.POST.get('postalAddress')
            postalCode = request.POST.get('postalCode')
            residentialAddress = request.POST.get('residentialAddress')
            disabilityGrade = request.POST.get('disabilityGrade')
            areYouKenyan = request.POST.get('areYouKenyan')
            citizenshipBy = request.POST.get('citizenshipBy')
            certificateNo = request.POST.get('certificateNo')
            stateNationality = request.POST.get('stateNationality')
            country = request.POST.get('country')
            subCounty = request.POST.get('subCounty')
            constituency = request.POST.get('constituency')
            termsOfService = request.POST.get('termsOfService')
            currentMonthlySalary = request.POST.get('currentMonthlySalary')
            expectedSalary = request.POST.get('expectedSalary')
            howSoonCanYouTakeThisAppointment = request.POST.get(
                'howSoonCanYouTakeThisAppointment')
            haveYouEverBeenRemovedOrDismissedFromEmployment = request.POST.get(
                'haveYouEverBeenRemovedOrDismissedFromEmployment')
            giveDetails = request.POST.get('giveDetails')
            haveYouBeenChargedInACourtOfLaw = request.POST.get(
                'haveYouBeenChargedInACourtOfLaw')
            offence = request.POST.get('offence')
            dateOfOffence = request.POST.get('dateOfOffence')
            placeOfOffence = request.POST.get('placeOfOffence')
            sentenceImposed = request.POST.get('sentenceImposed')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('profile')
    if not countyCode:
        countyCode = " "

    class Data(enum.Enum):
        values = genders
    gender = (Data.values).value
    try:
        response = config.CLIENT.service.FnApplicantDetails(
            applicantNo, firstName, middleName, lastName, idNumber, gender, citizenship,
            countyCode, maritalStatus, ethnicOrigin, disabled, dob, phoneNumber, postalAddress, postalCode, residentialAddress, disabilityGrade,
            areYouKenyan, citizenshipBy, certificateNo, stateNationality, country, subCounty, constituency, termsOfService, currentMonthlySalary,
            expectedSalary, howSoonCanYouTakeThisAppointment, haveYouEverBeenRemovedOrDismissedFromEmployment, giveDetails,
            haveYouBeenChargedInACourtOfLaw, offence, dateOfOffence, placeOfOffence, sentenceImposed
        )
        print(response)
        messages.success(request, "Successfully Added.")
        return redirect('profile')
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('profile')


def JobExperience(request):
    applicantNo = request.session['No_']
    lineNo = 0
    startDate = ""
    endDate = ""
    employer = ""
    industry = ""
    hierarchyLevels = ""
    functionalArea = ""
    jobTitle = ""
    isPresentEmployment = ""
    country = ""
    description = ""
    location = ""
    employerEmail = ""
    employerPostalAddress = ""
    myAction = ""

    if request.method == 'POST':
        try:
            startDate = request.POST.get('startDate')
            endDate = request.POST.get('endDate')
            employer = request.POST.get('employer')
            industry = request.POST.get('industry')
            hierarchyLevels = request.POST.get('hierarchyLevel')
            functionalArea = request.POST.get('functionalArea')
            jobTitle = request.POST.get('jobTitle')
            isPresentEmployment = request.POST.get('isPresentEmployment')
            country = request.POST.get('country')
            description = request.POST.get('description')
            location = request.POST.get('location')
            employerEmail = request.POST.get('employerEmail')
            employerPostalAddress = request.POST.get('employerPostalAddress')
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('profile')

    class Data(enum.Enum):
        values = hierarchyLevels

    hierarchyLevel = (Data.values).value
    try:
        response = config.CLIENT.service.FnApplicantJobExperience(applicantNo, lineNo, startDate, endDate, employer, industry, hierarchyLevel, functionalArea, jobTitle,
                                                                  isPresentEmployment, country, description, location, employerEmail, employerPostalAddress, myAction)
        print(response)
        messages.success(request, "Successfully Added.")
        return redirect('profile')
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('profile')


def FnApplicantProfessionalCourse(request):
    applicantNo = request.session['No_']
    lineNo = 0
    qualificationCode = ""
    sectionLevel = ""
    myAction = "insert"
    otherQualification = ''
    if request.method == 'POST':
        try:
            qualificationCode = request.POST.get('qualificationCode')
            sectionLevel = int(request.POST.get('sectionLevel'))
            otherQualification = request.POST.get('otherQualification')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('profile')
        try:
            response = config.CLIENT.service.FnApplicantProfessionalCourse(
                applicantNo, lineNo, qualificationCode, sectionLevel, myAction, otherQualification)
            print(response)
            messages.success(request, "Successfully Added.")
            return redirect('profile')
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('profile')


def FnApplicantAcademicQualification(request):
    # applicantNo = request.session['No_']
    # lineNo = ""
    # startDate = ""
    # endDate = ""
    # educationTypes = ""
    # educationLevels = ""
    # fieldOfStudy = ""
    # qualificationCode = ""
    # institutionName = ""
    # proficiencyLevels = ""
    # country = ""
    # region = ""
    # isHighestLevel = ""
    # description = ""
    # grade = ""
    # myAction = "insert"
    # otherQualification = ""
    try:
        if request.method == 'POST':
            applicantNo = request.session['No_']
            lineNo = request.POST.get('lineNo')
            startDate = request.POST.get('startDate')
            endDate = request.POST.get('endDate')
            educationTypes = request.POST.get('educationType')
            educationLevels = request.POST.get('educationLevel')
            fieldOfStudy = request.POST.get('fieldOfStudy')
            qualificationCode = request.POST.get('qualificationCode')
            institutionName = request.POST.get('institutionName')
            proficiencyLevels = request.POST.get('proficiencyLevel')
            country = request.POST.get('country')
            region = request.POST.get('region')
            isHighestLevel = request.POST.get('isHighestLevel')
            description = request.POST.get('description')
            grade = request.POST.get('grade')
            otherQualification = request.POST.get('otherQualification')
            myAction = request.POST.get('myAction')
    
            print(lineNo)
            class Data(enum.Enum):
                values = educationTypes
                education = educationLevels
                proficiency = proficiencyLevels

            educationType = (Data.values).value
            educationLevel = (Data.education).value
            proficiencyLevel = (Data.proficiency).value

            try:
                response = config.CLIENT.service.FnApplicantAcademicQualification(applicantNo, lineNo, startDate, endDate, educationType, educationLevel, fieldOfStudy, qualificationCode, institutionName,
                                                                                proficiencyLevel, country, region, isHighestLevel, description, grade, myAction, otherQualification)
                print(response)
                print(response)
                messages.success(request, "Request Successfully")
                return redirect('profile')
            except Exception as e:
                messages.error(request, e)
                print(e)
    except ValueError:
        messages.error(request, "Not sent. Invalid Input, Try Again!!")
        return redirect('profile')
    return redirect('profile')


def FnApplicantProfessionalMembership(request):
    applicantNo = request.session['No_']
    lineNo = 0
    professionalBody = ""
    membershipNo = ""
    myAction = "insert"
    otherProfessionalBody = ''
    if request.method == 'POST':
        try:
            professionalBody = request.POST.get('professionalBody')
            membershipNo = request.POST.get('membershipNo')
            otherProfessionalBody = request.POST.get('otherProfessionalBody')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('profile')

        try:
            response = config.CLIENT.service.FnApplicantProfessionalMembership(
                applicantNo, lineNo, professionalBody, membershipNo, myAction, otherProfessionalBody)
            print(response)
            messages.success(request, "Successfully Added.")
            return redirect('profile')
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('profile')


def FnApplicantHobby(request):
    applicantNo = request.session['No_']
    # print(request.session['No_'])
    lineNo = ""
    hobby = ""
    myAction = ""
    if request.method == 'POST':
        try:
            lineNo = request.POST.get('lineNo')
            hobby = request.POST.get('hobby')
            myAction = request.POST.get('myAction')

        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('profile')

    try:
        response = config.CLIENT.service.FnApplicantHobby(
            applicantNo, lineNo, hobby, myAction)
        print(response)
        messages.success(request, "Successfully Added.")
        return redirect('profile')
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('profile')


def FnApplicantReferee(request):
    applicantNo = request.session['No_']
    lineNo = ""
    names = ""
    company = ""
    telephoneNo = ""
    email = ""
    myAction = ""
    if request.method == 'POST':
        try:
            lineNo = request.POST.get('lineNo')
            names = request.POST.get('names')
            designation = request.POST.get('designation')
            company = request.POST.get('company')
            address = request.POST.get('address')
            telephoneNo = request.POST.get('telephoneNo')
            email = request.POST.get('email')
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('profile')
        try:
            response = config.CLIENT.service.FnApplicantReferee(
                applicantNo, lineNo, names, designation, company, address, telephoneNo, email, myAction)
            print(response)
            messages.success(request, "Successfully Added.")
            return redirect('profile')
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('profile')


def logout(request):
    try:
        del request.session['No_']
        del request.session['E_Mail']
        messages.success(request, 'Logged out successfully')
    except KeyError:
        print(False)
    return redirect('login')
