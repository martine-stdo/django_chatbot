from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
import openai
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone

openai_api_key = "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"
openai.api_key = openai_api_key
# 向openai发送提问的函数


def ask_openai(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # model = "gpt-4",
        # prompt=message,
        # max_tokens=150,
        # n=1,
        # stop=None,
        # temperature=0.7,
        messages=[
            {"role": "system", "content": "You are an helpful assistant."},
            {"role": "user", "content": message},
        ]
    )
    print(response)
    answer = response.choices[0].message.content.strip()
    return answer

# Create your views here.
# 聊天功能函数从前端获取用户提问


def chatbot(request):
    if not request.user.is_authenticated:
        return redirect("login")

    chats = Chat.objects.filter(user=request.user).order_by("-created_at")

    if request.method == "POST":
        message = request.POST.get("message")
        response = ask_openai(message)

        # 保存用户提问和openai回答
        chat = Chat(user=request.user, message=message,
                    response=response, created_at=timezone.now())
        # chatCount增加1
        chat.chatCount += 1
        chat.save()
        return JsonResponse({"message": message, "response": response})
    return render(request, "chatbot.html", {"chats": chats})


def login(request):
    if request.method == "POST":
        username = request.POST.get("Username")
        password = request.POST.get("password")
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("chatbot")
        else:
            error_message = "用户名或密码错误"
            return render(request, "login.html", {"error_message": error_message})

    return render(request, "login.html")

# 用户注册


def register(request):
    if request.method == "POST":
        username = request.POST.get("Username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("ConfirmPassword")
        if User.objects.filter(username=username).exists():
            error_message = "用户名已存在"
            return render(request, "register.html", {"error_message": error_message})

        elif password == confirm_password:
            try:
                user = User.objects.create_user(
                    username=username, password=password)
                user.save()
                auth.login(request, user)
                return redirect("chatbot")
            except:
                error_message = "用户创建失败"
                return render(request, "register.html", {"error_message": error_message})
        else:
            error_message = "Passwords do not match"
            return render(request, "register.html", {"error_message": error_message})

    return render(request, "register.html")

def forgot(request):
    return render(request, "forgot.html")


def logout(request):
    auth.logout(request)
    return redirect("login")
