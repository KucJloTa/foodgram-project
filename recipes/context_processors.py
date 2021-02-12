from taggit.models import Tag

def tags_con(request):
    tags = Tag.objects.all()
    return {'tags': tags}