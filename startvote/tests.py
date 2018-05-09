import block.model_block
from . import models
# Create your tests here.
article = models.Artivle.objects.get(pk=1)
print (article.title)