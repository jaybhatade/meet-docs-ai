"""
Translator module for MeetDocs AI automation system.
Handles language detection and translation of non-English content to English.
"""

import logging
import re
from typing import Optional
from googletrans import Translator as GoogleTranslator, LANGUAGES


logger = logging.getLogger(__name__)


class Translator:
    """
    Manages translation operations for multilingual transcripts.
    
    Detects Hindi, Marathi, and English content and translates
    non-English text to English using Google Translate API.
    """
    
    def __init__(self):
        """Initialize the Translator with Google Translate client."""
        self.translator = GoogleTranslator()
        self.supported_languages = {'hi', 'mr', 'en'}  # Hindi, Marathi, English
        logger.info("Translator initialized")
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., 'hi', 'mr', 'en') or 'unknown'
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for language detection")
            return 'unknown'
        
        try:
            detection = self.translator.detect(text)
            detected_lang = detection.lang
            confidence = detection.confidence
            
            logger.debug(f"Detected language: {detected_lang} (confidence: {confidence})")
            return detected_lang
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return 'unknown'
    
    def needs_translation(self, text: str) -> bool:
        """
        Check if the text requires translation to English.
        
        Args:
            text: Text to check
            
        Returns:
            True if translation is needed, False otherwise
        """
        if not text or not text.strip():
            return False
        
        detected_lang = self.detect_language(text)
        
        # Need translation if it's Hindi or Marathi
        needs_trans = detected_lang in {'hi', 'mr'}
        
        if needs_trans:
            logger.info(f"Text requires translation from {detected_lang} to English")
        else:
            logger.debug(f"Text is in {detected_lang}, no translation needed")
        
        return needs_trans
    
    def translate_to_english(self, text: str) -> str:
        """
        Translate text to English if needed.
        
        For Hindi/Marathi text, translates to English.
        For English text, returns unchanged.
        For other languages or errors, returns original with warning.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated English text or original text
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for translation")
            return text
        
        try:
            # Detect language first
            detected_lang = self.detect_language(text)
            
            # If already English, return as-is
            if detected_lang == 'en':
                logger.debug("Text is already in English, no translation needed")
                return text
            
            # If Hindi or Marathi, translate
            if detected_lang in {'hi', 'mr'}:
                logger.info(f"Translating from {detected_lang} to English")
                translation = self.translator.translate(text, src=detected_lang, dest='en')
                translated_text = translation.text
                
                # Clean the translated text
                cleaned_text = self._clean_text(translated_text)
                
                logger.info(f"Translation completed successfully")
                return cleaned_text
            
            # For other languages, return original with warning
            logger.warning(f"Unsupported language detected: {detected_lang}. Keeping original text.")
            return f"[UNTRANSLATED-{detected_lang.upper()}] {text}"
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # Return original text with error marker
            return f"[TRANSLATION-ERROR] {text}"
    
    def process_transcript(self, transcript: str) -> str:
        """
        Process a full transcript, translating non-English sections.
        
        Handles paragraph-by-paragraph translation to maintain context
        and improve translation quality.
        
        Args:
            transcript: Full transcript text
            
        Returns:
            Processed transcript with translations
        """
        if not transcript or not transcript.strip():
            logger.warning("Empty transcript provided for processing")
            return transcript
        
        logger.info("Processing transcript for translation")
        
        # Split into paragraphs (by double newlines or single newlines)
        paragraphs = [p.strip() for p in transcript.split('\n') if p.strip()]
        
        translated_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            logger.debug(f"Processing paragraph {i+1}/{len(paragraphs)}")
            
            # Translate each paragraph
            translated = self.translate_to_english(paragraph)
            translated_paragraphs.append(translated)
        
        # Rejoin with newlines
        result = '\n'.join(translated_paragraphs)
        
        logger.info("Transcript processing completed")
        return result
    
    def _clean_text(self, text: str) -> str:
        """
        Clean translated text to remove artifacts and formatting issues.
        
        Removes:
        - Language detection markers
        - Translation service artifacts
        - Extra whitespace
        - Special formatting characters
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return text
        
        # Remove common translation artifacts
        cleaned = text
        
        # Remove language markers like [hi], [mr], etc.
        cleaned = re.sub(r'\[([a-z]{2})\]', '', cleaned, flags=re.IGNORECASE)
        
        # Remove translation service markers
        cleaned = re.sub(r'\[Translated from [^\]]+\]', '', cleaned, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        # Remove any remaining brackets with language codes
        cleaned = re.sub(r'\([a-z]{2}\)', '', cleaned, flags=re.IGNORECASE)
        
        logger.debug("Text cleaning completed")
        return cleaned
