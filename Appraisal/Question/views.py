# Create your views here.
from django.shortcuts import render_to_response
from django.contrib.sessions.models import Session
from django.http import HttpResponse
from forms import QuestionForm, OptionFrom
from Login.models import OptionHeader, Option, Question
from django.http import HttpResponseRedirect 
from django.core.context_processors import csrf
from django.utils import simplejson
from django.utils import timezone
from django.template.context import RequestContext
import pdb;

from Login.models import UserDetails, AppraisalContent, AppraisalContent, Appraisment, Answer

def questionCreateView(request):
    
    args={}
    args.update(csrf(request))
    args['error']=''
    objQuestionForm = QuestionForm(request.POST or None)
    objOptionForm = OptionFrom(request.POST or None)
    if request.method == 'POST':
        if request.POST['type_text'] == 'MCQ':
 #           objOptionForm.clean_optionheadertext(sOptionHeaderText=request.POST['option_header_text'],nOptionHeaderID=request.POST['option_header_id'])
            if objQuestionForm.is_valid() and objOptionForm.is_valid():
                flag=True
            else:
                flag=False
        else:
            objOptionForm = OptionFrom()
            if objQuestionForm.is_valid():
                flag=True   
            else:
                flag=False
             
        if flag == True:
            iOptionHeaderID = 0 
            i_UserId = UserDetails.objects.get(user_id=request.session['UserID'])
            if request.POST['type_text'] == 'MCQ':
                if request.POST['option_header_id']=='0':
                    objOptionHeader = OptionHeader.objects.create(title=request.POST['option_header_text'], modified_by=i_UserId, modified_on=timezone.now())
                    iOptionHeaderID = OptionHeader.objects.latest('option_header_id')
                    objOptionForm.save(commit=False, userId=i_UserId, optionHeaderId=iOptionHeaderID)
                    
                else:
                    iOptionHeaderID = OptionHeader.objects.get(option_header_id=request.POST['option_header_id'])
            objQuestionForm.save(commit=False, userId = i_UserId, optionHeaderId = iOptionHeaderID)
            args['successMsg']="Question created successfully"
            objOptionForm = OptionFrom()
            initial = {'type_text' : request.POST['type_text']}
            objQuestionForm = QuestionForm()
            args['questionCreateform']=objQuestionForm
            args['optionCreateform']=objOptionForm
            return render_to_response('Questions/CreateQuestion.html',args)
        else:
            args['questionCreateform']=objQuestionForm
            args['optionCreateform']=objOptionForm
            return render_to_response('Questions/CreateQuestion.html',args)
    else:
        args['questionCreateform']=objQuestionForm
        args['optionCreateform']=objOptionForm
        return render_to_response('Questions/CreateQuestion.html',args)

def OptionList(request):
    objOptions = OptionHeader.objects.all();
    result=''
    for optionheader in objOptions:
        result += '<div class=\"accordion\" id=\"accordion_'+str(optionheader.option_header_id)+'\" ><div class=\"accordion-group\"><div class=\"accordion-heading\"><a data-toggle=\"collapse\" data-parent=\"#accordion_'+str(optionheader.option_header_id)+'\" href=\"#accordionCollapse_'+str(optionheader.option_header_id)+'\" class=\"accordion-toggle\"><i class=\"icon-minus-sign icon-white\"></i>&nbsp;'+optionheader.title+' </a><a name=\"btnUseIt\" class=\"btn btn-primary\" data=\"'+ str(optionheader.option_header_id) +'\">Use it</a><a name=\"btnEditIt\" class=\"btn btn-primary\" data=\"'+ str(optionheader.option_header_id) +'\">Edit</a></div><div class=\"accordion-body collapse\" id=\"accordionCollapse_'+str(optionheader.option_header_id)+'\"><div class=\"accordion-inner\">' 
        for option in optionheader.option_set.filter():
            result+= option.option_text + '<br/>'
        result+='</div></div></div></div>'
    return HttpResponse(content=result, content_type='text/html')

def OptionDetails(request):
    if request.is_ajax():
        search_text = request.POST.get('search_txt')
        objOptions = OptionHeader.objects.get(option_header_id=search_text);
        result =''
        for option in objOptions.option_set.filter():
            result+= option.option_text + ','
        objDetails = {'OptionHeaderID':objOptions.option_header_id,
                      'OptionHeader' :objOptions.title,
                      'Options' : result[:-1]
                      }
        data = simplejson.dumps(objDetails)
        return HttpResponse(content=data, content_type='json')    

def QuestionList(request):
    objQuestion = Question.objects.all();
    #for objOption in objOptions:
    #    objJsonOptions = {'option_header':objOption.option_header,
    #                      'question_id' : objOption.question_id,
    #                       'question' : objOption.question,
    #                       'level' : objOption.level,
    #                       'weight' : objOption.weight,
    #                       'type' : objOption.type,
    #                       'intent' : objOption.intent
    #                      }
    args={}
    args.update(csrf(request))
    args['error']=''
    args['QuestionList']=objQuestion
    return render_to_response('Questions/QuestionList.html',args)

def validateOptionHeader(request):
    if request.is_ajax():
        stitle = request.POST.get('stitle')
        nOptionHeaderID = request.POST.get('nOptionHeaderID')
        error_msg=''
        objOptions = OptionHeader.objects.filter(title=stitle).exclude(option_header_id=nOptionHeaderID).count()
        if objOptions> 0 :
            error_msg='Option header already exists'
        data = simplejson.dumps({'error':error_msg})
        return HttpResponse(content=data, content_type='json')      
    
def updateOption(request):
      if request.is_ajax():
            objOptionForm = OptionFrom(request.POST or None)
            iOptionHeaderID= OptionHeader.objects.get(option_header_id=request.POST.get('option_header_id'))
            OptionHeader.objects.filter(option_header_id=request.POST.get('option_header_id')).update(title=request.POST.get('option_header_text'))
            i_UserId = UserDetails.objects.get(user_id=request.session['UserID'])
            Option.objects.filter(option_header=iOptionHeaderID).delete()
            objOptionForm.save(commit=False, userId=i_UserId, optionHeaderId=iOptionHeaderID)
      success_msg='Record updated successfully'
      data = simplejson.dumps({'success':success_msg})
      return HttpResponse(content=data, content_type='json')   
  
  
def deleteQuestion(request):
      if request.is_ajax():
          Question.objects.filter(question_id=request.POST.get('QuestionID')).delete()
      success_msg='Record deleted successfully'    
      data = simplejson.dumps({'success':success_msg})
      return HttpResponse(content=data, content_type='json')   
      
      
def editQuestion(request, questionId):
    args={}
    args.update(csrf(request))
    objQuestionForm = QuestionForm(request.POST or None)
    objOptionForm = OptionFrom(request.POST or None)
    if request.method == 'POST':
        flag=False
        
        if request.POST['type_text'] == 'MCQ':
 #           objOptionForm.clean_optionheadertext(sOptionHeaderText=request.POST['option_header_text'],nOptionHeaderID=request.POST['option_header_id'])
            if objQuestionForm.is_valid() and objOptionForm.is_valid():
                flag=True
        else:
            objOptionForm = OptionFrom()
            if objQuestionForm.is_valid():
                flag=True   
                
        if flag == True:
            iOptionHeaderID = None 
            i_UserId = UserDetails.objects.get(user_id=request.session['UserID'])
            if request.POST['type_text'] == 'MCQ':
                if request.POST['option_header_id']=='0':
                    objOptionHeader = OptionHeader.objects.create(title=request.POST['option_header_text'], modified_by=i_UserId, modified_on=timezone.now())
                    iOptionHeaderID = OptionHeader.objects.latest('option_header_id')
                    objOptionForm.save(commit=False, userId=i_UserId, optionHeaderId=iOptionHeaderID)
                    
                else:
                    iOptionHeaderID = OptionHeader.objects.get(option_header_id=request.POST['option_header_id'])
            Question.objects.filter(question_id=request.POST['questionID']).update(question=request.POST['question'],level=request.POST['level'],weight=request.POST['weight'],info=request.POST['info'],intent=request.POST['intent'],type=request.POST['type_text'],option_header=iOptionHeaderID)
            return HttpResponseRedirect("/question/QuestionList")
        else:
            args['optionCreateform']=objOptionForm
            args['questionCreateform']=objQuestionForm         
    else:    
        objQuestion=Question.objects.get(question_id=int(questionId))
        
        if objQuestion.type=='MCQ':
            objOptionHeader=OptionHeader.objects.get(option_header_id=objQuestion.option_header_id)
            objOption=Option.objects.filter(option_header=objOptionHeader.option_header_id)
            optionText=''
            for option in objOption:
                optionText+=option.option_text + ','
            optionText=optionText[:-1]
            objOptionForm = OptionFrom(initial={'option_header_id':str(objOptionHeader.option_header_id),'option_text':optionText,'option_header_text':objOptionHeader.title})
            
        args['optionCreateform']=objOptionForm
        
        objQuestionForm = QuestionForm(initial={'questionID':questionId,'question':objQuestion.question,'level':objQuestion.level,'weight':objQuestion.weight,'info':objQuestion.info,'intent':objQuestion.intent,'type_text':objQuestion.type})
        args['questionCreateform']=objQuestionForm
    
    return render_to_response('Questions/CreateQuestion.html',args)
    
def userwiseQuestionList(request,requestUserID):   
    args={}
    args.update(csrf(request))
    objAppraisment=None
    objAppraisalContent=None
    errMessage=''
    i_UserId = UserDetails.objects.get(user_id=request.session['UserID'])
    flag=True
    if int(request.session['UserID'])!=int(requestUserID):
        objAppraisment1=None
        try:
            objAppraisment1 = Appraisment.objects.get(appraiser=i_UserId,appraisee=i_UserId)
        except Appraisment.DoesNotExist:
            errMessage= "First complete appraising youself"
            
        if objAppraisment1.status == "Completed":
            flag=True
        else :
            flag=False
            errMessage='First complete appraising youself'
    if flag:
        try:
            objAppraisment = Appraisment.objects.get(appraiser=request.session['UserID'],appraisee=requestUserID)
        except Appraisment.DoesNotExist:
            errMessage= "You are not authorised to appraise this user"
        
        if objAppraisment:
            if objAppraisment.status == 'Initial':
                value= objAppraisment.appraiser.user_level
                if objAppraisment.appraisee.user_level <= objAppraisment.appraiser.user_level :
                    value= objAppraisment.appraisee.user_level
                objQuestion = Question.objects.filter(level__lte=value).order_by('level')
                index=0
                for question in objQuestion:
                    index=index+1
                    AppraisalContent.objects.create( appresment = objAppraisment, question = question ,question_order = index,modified_by = i_UserId,modified_on=timezone.now() )
                objAppraisment.status = 'Created'
                objAppraisment.save()#Appraisment.objects.filter(appraisment_id=objAppraisment.appraisment_id).update(status='Created')    
            objAppraisalContent = AppraisalContent.objects.filter(appresment=objAppraisment).order_by('question_order');
            request.session['appraisee']= objAppraisment.appraisee     
        else:
            errMessage="You are not authorised to appraise this user"
        args['Question']= objAppraisalContent
    args['error']=errMessage
    return render_to_response('Questions/UserWiseQuestionList.html', args)

def QuestionAnswer(request, questionId):
    #pdb.set_trace()
    
    Appraisment_Id = Appraisment.objects.get(appraiser=request.session['UserID'],appraisee=request.session['appraisee']).appraisment_id
    pages = AppraisalContent.objects.filter(appresment=Appraisment_Id)
    
    if(questionId == '1'):
        previousPageNumber = '#'
    else:
        previousPageNumber =  int(questionId) - 1    
    
    nextPageNumber =  int(questionId) + 1
    
    
    if request.method == 'POST' :
        print request.POST
        useranswer = request.POST.get('appAnswer')
        
        #Saving answer
        #try:    
        questionNumber = request.POST.get('qustnNmbr')
        print "Question Id : " + questionNumber
        print "Appresment Id : "  
        print Appraisment_Id
        
        try:
            exitingAnswer = AppraisalContent.objects.get(question_order = questionNumber, appresment = Appraisment_Id)
            print "Answer after query............."
            print exitingAnswer
        except AppraisalContent.DoesNotExist:
            print "Exception.........."
            
        if exitingAnswer.answer != None:
            print "Existing answer : ==============="
            print exitingAnswer.answer
        else:
            print "Inside else]]]]]]]]]]]]]]]"    
        
        if exitingAnswer.answer != None:
            print "Inside if"
            Answer.objects.filter(answer_id=exitingAnswer.answer.answer_id).update(answer=useranswer, modified_on = timezone.now(), modified_by = UserDetails.objects.get(user_id = request.session['UserID']))
        else:
            answer = Answer.objects.create( answer = useranswer, modified_on = timezone.now(), modified_by = UserDetails.objects.get(user_id = request.session['UserID']))
            print "Creating answer --------------------"
            print answer.answer_id
            AppraisalContent.objects.filter(question_order = questionNumber).filter(appresment = Appraisment_Id).update(answer=answer.answer_id ,modified_on = timezone.now(), modified_by = UserDetails.objects.get(user_id = request.session['UserID']))
        #except :
            #print "ERROR............."
        
        # Data for next question
        AppraisalContents = AppraisalContent.objects.get(appresment=Appraisment_Id, question_order=questionId)
        
        if AppraisalContents.question.type == 'Subjective':
            return render_to_response('Questions/Subjective.html', { 'AppraisalContents' : AppraisalContents, 'pages' : pages, 'nextPageNumber' : nextPageNumber, 'previousPageNumber' : previousPageNumber }, context_instance = RequestContext( request))
        if AppraisalContents.question.type == 'MCQ':
            options = Option.objects.filter(option_header=AppraisalContents.question.option_header)
            return render_to_response('Questions/MCQ.html', { 'AppraisalContents' : AppraisalContents, 'options' : options, 'pages' : pages, 'nextPageNumber' : nextPageNumber, 'previousPageNumber' : previousPageNumber }, context_instance = RequestContext( request))    
        if AppraisalContents.question.type == 'Scale':
            return render_to_response('Questions/Scale.html', { 'AppraisalContents' : AppraisalContents, 'pages' : pages, 'nextPageNumber' : nextPageNumber, 'previousPageNumber' : previousPageNumber }, context_instance = RequestContext( request))
        
    else:    
        
        print Appraisment_Id
        AppraisalContents = AppraisalContent.objects.get(appresment=Appraisment_Id, question_order=questionId)
        
        if AppraisalContents.question.type == 'Subjective':
            return render_to_response('Questions/Subjective.html', { 'AppraisalContents' : AppraisalContents, 'pages' : pages, 'nextPageNumber' : nextPageNumber, 'previousPageNumber' : previousPageNumber }, context_instance = RequestContext( request))
        if AppraisalContents.question.type == 'MCQ':
            options = Option.objects.filter(option_header=AppraisalContents.question.option_header)
            return render_to_response('Questions/MCQ.html', { 'AppraisalContents' : AppraisalContents, 'options' : options, 'pages' : pages, 'nextPageNumber' : nextPageNumber, 'previousPageNumber' : previousPageNumber }, context_instance = RequestContext( request))    
        if AppraisalContents.question.type == 'Scale':
            return render_to_response('Questions/Scale.html', { 'AppraisalContents' : AppraisalContents, 'pages' : pages, 'nextPageNumber' : nextPageNumber, 'previousPageNumber' : previousPageNumber }, context_instance = RequestContext( request))    
        
def demo(request):
    obj_searchResult = UserDetails.objects.get(user_id=1)
    initial = {    "error" : '',
                    "firstname": obj_searchResult.firstname,
                    "lastname": obj_searchResult.lastname, 
                    "emailid": obj_searchResult.emailid, 
                    "user_level": obj_searchResult.user_level, 
                    "user_weight": obj_searchResult.user_weight, 
                    "type": obj_searchResult.type,
                    "user_id" : obj_searchResult.user_id
                }
        
    data = simplejson.dumps(initial)
    return HttpResponse(content=data, content_type='json')    
    #return render_to_response('test.html', {'data' : data})