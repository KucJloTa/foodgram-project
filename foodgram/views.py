from django.shortcuts import render


def author(request):
    """Страница об исполнителе проекта"""

    return render(request, 'about.html',)


def tech(request):
    """Страница о технологиях, используемых в проекте"""

    return render(request, 'tech.html',)