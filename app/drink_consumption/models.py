from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=200)
    style = models.CharField(max_length=200, blank=True, default="")
    producer = models.CharField(max_length=200, blank=True, default="")
    abv = models.FloatField(help_text="Alcohol By Volume.", default=0)
    def __str__(self):
        return self.name


class Container(models.Model):
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    capacity = models.FloatField(help_text="Capacity of the container in Liters.")
    initial_content = models.FloatField(help_text="Content of the container at the begining, in Liters.", null=True, blank=True)
    cost = models.FloatField(help_text="Cost of the keg, in your desired unit.")

    def __str__(self):
        return self.product.name + " (" + str(round(self.remaining(), 2)) + " L)"

    def remaining(self):
        refills = Refill.objects.all().filter(product=self)
        consumed = 0
        for refill in refills:
            consumed += refill.container.capacity
        if  self.initial_content == None:
            initial_content = self.capacity
        else:
            initial_content = self.initial_content
        return initial_content - consumed


class PersonalContainer(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    capacity = models.FloatField(help_text="Capacity of the container in Liters.")
    def __str__(self):
        return self.name + " (" + str(self.capacity) + " L)"


class Tag(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    linked_container = models.ForeignKey(PersonalContainer, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=200, blank=True, default="**Auto-created Tag**")
    uid = models.CharField(max_length=200, unique=True)
    def __str__(self):
        if self.description is not None and self.description != "":
            return self.uid + " (" + self.description + ")"
        if self.owner is not None:
            return self.uid + " (" + self.owner.username + ")"
        return self.uid


class Refill(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT )
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(Container, on_delete=models.RESTRICT )
    container = models.ForeignKey(PersonalContainer, on_delete=models.RESTRICT, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " - " + self.product.product.name + " - " + str(self.cost()) + "$"

    def cost(self):
        return round(self.product.cost/self.product.capacity*self.container.capacity, 2)


class Tap(models.Model):
    name = models.CharField(max_length=200, unique=True)
    onTap = models.OneToOneField(Container, on_delete=models.SET_NULL, blank=True, null=True, unique=True)
    def __str__(self):
        return self.name


class Reader(models.Model):
    name = models.CharField(max_length=200, default="**Auto-created Reader**")
    physical_id = models.CharField(max_length=200, unique=True)
    forTap = models.ForeignKey(Tap, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    def __str__(self):
        return self.name
