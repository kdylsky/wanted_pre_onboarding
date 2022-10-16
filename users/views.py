import json
import jwt
import bcrypt

from django.http    import JsonResponse
from django.views   import View
from django.conf    import settings

from users.models   import User
from core.models    import Region
from core.utils     import check_email, duplicate_check_email

class SignUpView(View):
    def post(self, request):
        try:
            data            = json.loads(request.body)
            name            = data["name"]
            email           = data["email"]
            password        = data["password"]
            region          = Region.objects.get(name__startswith = data["region"])

            check_email(email)
            duplicate_check_email(email)
            
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            User.objects.create(
                        name        = name,
                        email       = email,
                        password    = hashed_password,
                        regions     = region
            )
            return JsonResponse({"message": "success"}, status = 201)
        
        except KeyError:
            return JsonResponse({"mssage":"key_error"}, status=400)
        
        except Region.DoesNotExist:
            return JsonResponse({"message" :"region_does_not_exist"}, status=400)

        except ValueError as e :
            return JsonResponse({"message": f"{e}"}, status=400)

class SignInView(View):
    def post(self, request):
        try:
            data             = json.loads(request.body)
            user             = User.objects.get(email = data["email"])
            hashed_password  = user.password.encode('utf-8')

            if not bcrypt.checkpw(data['password'].encode('utf-8'), hashed_password):
                return JsonResponse({"message":"invaild_user"}, status=400)

            access_token     = jwt.encode({'id' : user.id}, settings.SECRET_KEY, settings.ALGORITHM)

            return JsonResponse(
                {
                "message"       : "login_success",
                "access_token"  : access_token
                },
                status= 200
            )

        except KeyError:
            return JsonResponse({"message":"key_error"},status=400)

        except User.DoesNotExist:
            return JsonResponse({"message" :"user_does_not_exist"}, status=400)