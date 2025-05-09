import logging
import os

from google.cloud import translate_v3

logger = logging.getLogger(__name__)

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")

client = translate_v3.TranslationServiceClient()


def detect_language(text: str) -> str:
    parent = f"projects/{PROJECT_ID}/locations/global"

    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = client.detect_language(
        content=text,
        parent=parent,
        mime_type="text/plain",
    )

    for language in response.languages:
        logger.debug(
            f"Language code: {language.language_code}, Confidence: {language.confidence}"
        )

    return response.languages[0].language_code


def translate_text(
    text: str,
    source_language_code: str = "en",
    target_language_code: str = "zh",
) -> str:
    parent = f"projects/{PROJECT_ID}/locations/global"

    # Translate text from English to chosen language
    # Supported mime types: # https://cloud.google.com/translate/docs/supported-formats
    response = client.translate_text(
        contents=[text],
        source_language_code=source_language_code,
        target_language_code=target_language_code,
        parent=parent,
        mime_type="text/plain",
    )

    # Display the translation for each input text provided
    for translation in response.translations:
        logger.debug(f"Translated text: {translation.translated_text}")

    return response.translations[0].translated_text
