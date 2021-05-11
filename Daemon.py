"""
Tetelezzuk fel, hogy ezt a fajl meghivodik 20 percenkent automatikusan egy cron
vagy barmilyen futtato segitsegevel.
"""

from CarService import CarService

driver = CarService()

driver.order_delete_completed()
