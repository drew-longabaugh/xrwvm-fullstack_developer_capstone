from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# Car Make model
class CarMake(models.Model):

    name = models.CharField(max_length=20)  # Renamed from 'models'
    description = models.CharField
    (max_length:=100)  # Increased length for better descriptions

    def __str__(self):
        return f"{self.name} - {self.description}"


# Car Model model
class CarModel(models.Model):
    SEDAN = "Sedan"
    SUV = "SUV"
    WAGON = "Wagon"

    CAR_MODEL_CHOICES = [
        (SEDAN, "Sedan"),
        (SUV, "SUV"),
        (WAGON, "Wagon"),
    ]

    type= models.CharField(max_length=20, choices=CAR_MODEL_CHOICES)
    year= models.IntegerField
    validators= ([MinValueValidator(2015), MaxValueValidator(2023)])
