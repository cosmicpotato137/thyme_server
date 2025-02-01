from django.shortcuts import render


# Create your views here.
def index(request):
    from django.template import engines

    print(engines["django"].engine.dirs)  # Show global template directories

    return render(request, "index.html")
