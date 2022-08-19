import sys
from json import load
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Upload read only data in database from data .json'

    def handle(self, *args, **options):
        models = {
            'ingredients.json': Ingredient,
            'tags.json': Tag
        }
        for file in Path(settings.DATA_ROOT).iterdir():
            if file.suffix != '.json':
                continue
            with open(file, 'r') as data:
                data_obj = load(data)
            for row in data_obj:
                instance = (
                    models.get(file.name)() if
                    models.get(file.name) is not None else None
                )
                if not instance:
                    raise CommandError('File name doesn`t match any model')
                for key, value in row.items():
                    setattr(instance, key, value)
                instance.save()
        self.stdout.write(self.style.SUCCESS('Successfully imported!'))
