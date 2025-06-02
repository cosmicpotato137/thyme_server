from rest_framework import serializers
from .models import Word, Synonym, Languages


class SynonymSerializer(serializers.ModelSerializer):
    synonym = serializers.StringRelatedField()

    class Meta:
        model = Synonym
        fields = "__all__"


class WordSerializer(serializers.ModelSerializer):
    synonyms = serializers.SerializerMethodField()
    language_display = serializers.CharField(
        source="get_language_display", read_only=True
    )

    class Meta:
        model = Word
        fields = "__all__"

    def get_synonyms(self, obj):
        # Return a list of synonym words (as strings)
        return [syn.word for syn in obj.get_synonyms()]


class LanguagesSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()
