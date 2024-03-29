from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from .models import *
from .forms import *

def index(request):
    if request.user.is_authenticated():
        chats = Link.objects.filter(user=request.user)
        users = list()
        for i in chats:
            r = i.room
            part = Link.objects.filter(room=r)
            users+= part
            myself = Link.objects.get(user=request.user,room=r)
            users.remove(myself)    
        context = {
        'users' : users,
        'chats' : chats,
        }
        return render(request,'chat/messages.html',context)
    else:
	   return render(request, 'chat/index.html')
    
def contacts(request):
    if request.method == 'POST':
        userimp = request.POST.get('user', '')
        user = User.objects.get(username=userimp)
        u1r = Link.objects.filter(user=request.user).values_list('room')
        u2r = Link.objects.filter(user=user).values_list('room')
        flag = False
        for i in u1r:
            if i in u2r:
                room_id = i[0]
                flag = True
                break
        if(flag==False):
            room_count = Room.objects.all().count()
            room_count +=1
            room_name = "R" + str(room_count)
            roomobj = Room.objects.create(
                room_name = room_name,
            )
            room = Room.objects.filter(room_name=room_name)[0]
            room_id = room.id
            linkobj = Link.objects.create(
            room = room,
            user =  user,
            )
            linkobj1 = Link.objects.create(
            room = room,
            user =  request.user,
            )
        return HttpResponseRedirect(reverse('chatroom' , kwargs={'room_id': room_id}))


    else:
        form = LinkForm(request.POST)
        users = User.objects.all()
        user_list=list()
        user_list+=users
        myself = User.objects.get(username=request.user.username)
        user_list.remove(myself)
        context = {
            'user_list' : user_list,
            'form' : form, 
        }
        return render(request, 'chat/contacts.html', context)

def messages(request):
    chats = Link.objects.filter(user=request.user)
    users = list()
    for i in chats:
    	r = i.room
    	part = Link.objects.filter(room=r)
    	users+= part
        myself = Link.objects.get(user=request.user,room=r)
        users.remove(myself)	
    context = {
	'users' : users,
	'chats' : chats,
    }
    return render(request,'chat/messages.html',context)

def chatroom(request,room_id):
    if request.method == 'POST':
        form = MsgForm(request.POST)
        link = Link.objects.get(room=room_id,user=request.user.id)
        if form.is_valid():
            msgobj = Message.objects.create(
                links = link,
                message = form.cleaned_data['message'],
            )
            return HttpResponseRedirect(reverse('chatroom' , kwargs={'room_id': room_id}))
        else :
            return HttpResponse("Input Invalid")
    else:
        form = MsgForm()
        room = Room.objects.get(pk=room_id)
        links = Link.objects.filter(room_id=room_id)
        users = list()
        for i in links:
            r = i.room
            part = Link.objects.filter(room=r)
            users+= part
            myself = Link.objects.get(user=request.user,room=r)
            users.remove(myself)
        users = users[0]
        messages = Message.objects.filter(links__room_id=room_id).order_by('timestamp')[:25]
        context = {
        'links' : links,
        'users' : users,
        'messages' : messages,
        'form': form
        }
        return render(request, 'chat/room.html', context)
    '''
def chatroom(request, label):
    room, created = Room.objects.get_or_create(label=label)

    messages = reversed(room.messages.order_by('-timestamp')[:50])

    return render(request, "chat/room.html", {
        'room': room,
        'messages': messages,
    })
'''
