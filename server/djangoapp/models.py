
# - Any other fields you would like to include in car make model
class CarMake(models.Model):
    names = models.CharField(max_length=20)
    description = models.CharField(max_length=20)
  
    def __str__(self):
        return f"{self.name} {self.description}"


# - Type (CharField with a choices argument to provide limited choices
# such as Sedan, SUV, WAGON, etc.)
# - Year (IntegerField) with min value 2015 and max value 2023
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    SEDAN = "Sedan"
    SUV = "SUV"
    WAGON = "WAGON"
  
    CAR_MODEL_CHOICES = {
        SEDAN: "Sedan",
        SUV: "SUV",
        WAGON: "WAGON",
    }
  
    type = models.CharField(max_length=20, choices=CAR_MODEL_CHOICES)
    year = models.IntegerField(validators=[MinValueValidator(2015), MaxValueValidator(2023)])
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.type} {self.car_make} {self.year}"
