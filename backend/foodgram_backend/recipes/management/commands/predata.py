import json
from django.core.management.base import BaseCommand
from django.db import transaction
from recipes.models import Ingredient


class Command(BaseCommand):

    def load_data(self):
        with open('data/ingredients.json', encoding='utf-8') as f:
            ingredients_data = json.load(f)
            Ingredient.objects.bulk_create(
                Ingredient(**i) for i in ingredients_data)

    @transaction.atomic
    def handle(self, *args, **options):
        self.load_data()
        self.stdout.write(self.style.SUCCESS(
            'Predata with ingredients loaded!'))
