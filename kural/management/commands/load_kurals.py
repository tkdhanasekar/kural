from django.core.management.base import BaseCommand, no_translations
from kural.models import Tirukkural

import json

class Command(BaseCommand):
    """
        This command loads the tirukural loads data into table
        {
          "Number": 1,
          "Line1": "அகர முதல எழுத்தெல்லாம் ஆதி",
          "Line2": "பகவன் முதற்றே உலகு.",
          "Translation": "'A' leads letters; the Ancient Lord Leads and lords the entire world",
          "mv": "எழுத்துக்கள் எல்லாம் அகரத்தை அடிப்படையாக கொண்டிருக்கின்றன. அதுபோல உலகம் கடவுளை அடிப்படையாக கொண்டிருக்கிறது.",
          "sp": "எழுத்துக்கள் எல்லாம் அகரத்தில் தொடங்குகின்றன; (அது போல) உலகம் கடவுளில் தொடங்குகிறது.",
          "mk": "அகரம் எழுத்துக்களுக்கு முதன்மை; ஆதிபகவன், உலகில் வாழும் உயிர்களுக்கு முதன்மை",
          "explanation": "As the letter A is the first of all letters, so the eternal God is first in the world",
          "couplet": "A, as its first of letters, every speech maintains;The \"Primal Deity\" is first through all the world's domains",
          "transliteration1": "Akara Mudhala Ezhuththellaam Aadhi",
          "transliteration2": "Pakavan Mudhatre Ulaku"
        }
    """

    def handle(self, *args, **options):
        """
        ALTER DATABASE tirukkural CHARACTER SET utf8 COLLATE utf8_general_ci;

        ALTER TABLE `kural_tirukkural` CHANGE `line_1` `line_1` VARCHAR(1024) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

        ALTER TABLE `kural_tirukkural` CHANGE `line_2` `line_2` VARCHAR(1024) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

        ALTER TABLE `kural_tirukkural` CHANGE `transliteration1` `transliteration1` VARCHAR(1024) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

        ALTER TABLE `kural_tirukkural` CHANGE `transliteration2` `transliteration2` VARCHAR(1024) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
        """
        file_path ="kural/thirukkural.json"

        data = json.loads(open(file_path).read())
        for item in data["kural"]:
            t = Tirukkural()
            t.kural_id = item["Number"]
            t.line_1 = item["Line1"]
            t.line_2 = item["Line2"]
            t.explanation = item["explanation"]
            t.transliteration1 = item["transliteration1"]
            t.transliteration2 = item["transliteration2"]
            t.translation = item["Translation"]
            t.munnurai = item['mv']
            t.save()
