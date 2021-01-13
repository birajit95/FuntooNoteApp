from django.shortcuts import redirect
class CantAccessAfterLogin(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            return redirect('/notes/')
        response = self.get_response(request)
        return response
