from abc import ABC, abstractmethod

class CarDirector:
    TIER_RANGES = {
        'economy': (0, 50),
        'standard': (51, 100),
        'premium': (101, 150),
        'luxury': (151, float('inf')),
    }

    def __init__(self, builder):
        self._builder = builder

    def construct_car(self, car_attributes):
        """
        Construct a car based on provided attributes and automatically determine the pricing tier.
        """
        # Set the basic attributes
        self._builder.set_model(car_attributes.get('model'))
        self._builder.set_year(car_attributes.get('year'))
        self._builder.set_mileage(car_attributes.get('mileage'))
        self._builder.set_availability_calendar(car_attributes.get('availability_calendar'))
        self._builder.set_pickup_location(car_attributes.get('pickup_location'))

        # Automatically determine and set the pricing tier
        pricing = car_attributes.get('rental_pricing')
        tier = self.determine_pricing_tier(pricing)
        self._builder.set_rental_pricing(pricing)

        return self._builder.get_result()

    def determine_pricing_tier(self, pricing):
        for tier, (low, high) in self.TIER_RANGES.items():
            if low <= pricing <= high:
                return tier
        raise ValueError("Pricing does not fit any defined tier")

    


class CarListingBuilder(ABC):
    @abstractmethod
    def set_model(self, model):
        pass

    @abstractmethod
    def set_year(self, year):
        pass
    
    @abstractmethod
    def set_mileage(self, mileage):
        pass
    
    @abstractmethod
    def set_availability_calendar(self, availability_calendar):
        pass
    
    @abstractmethod
    def set_pickup_location(self, pickup_location):
        pass
    
    @abstractmethod
    def set_rental_pricing(self, rental_pricing):
        pass
    
    @abstractmethod
    def get_result(self):
        pass

class ConcreteCarListingBuilder(CarListingBuilder):
    def __init__(self):
        self.car_listing = CarListing()

    def set_model(self, model):
        self.car_listing.model = model
        return self  # Returning self for chaining

    def set_year(self, year):
        self.car_listing.year = year
        return self

    def set_mileage(self, mileage):
        self.car_listing.mileage = mileage
        return self
    
    def set_availability_calendar(self, availability_calendar):
        self.car_listing.availability_calendar = availability_calendar
        return self
    
    def set_pickup_location(self, pickup_location):
        self.car_listing.pickup_location = pickup_location
        return self
    
    def set_rental_pricing(self, rental_pricing):
        self.car_listing.rental_pricing = rental_pricing
        return self

    def get_result(self):
        return self.car_listing

class CarListing:
    def __init__(self):
        self.model = None
        self.year = None
        self.mileage = None
        self.availability_calendar = None
        self.pickup_location = None
        self.rental_pricing = None
        
