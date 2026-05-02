"""
NLP Processor – uses SpaCy for tokenization, stopword removal,
lemmatization, NER, and skill extraction from predefined lists.
"""

import re

import spacy

from .skills_db import TECHNICAL_SKILLS, SOFT_SKILLS


class NLPProcessor:
    """NLP pipeline for resume / job‑description text."""

    TECHNICAL_SKILLS = TECHNICAL_SKILLS
    SOFT_SKILLS = SOFT_SKILLS

    def __init__(self):
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            from spacy.cli import download
            download('en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')

    # ------------------------------------------------------------------ #
    #  Core NLP
    # ------------------------------------------------------------------ #
    def process(self, text: str) -> dict:
        """Run the full NLP pipeline and return structured results."""
        doc = self.nlp(text)
        tokens = self._tokenize(doc)
        lemmas = self._lemmatize(doc)
        entities = self._extract_entities(doc)
        technical_skills = self._extract_technical_skills(text)
        soft_skills = self._extract_soft_skills(text)
        yoe = self._extract_years_of_experience(text)
        return {
            'tokens': tokens,
            'lemmas': lemmas,
            'entities': entities,
            'technical_skills': sorted(technical_skills),
            'soft_skills': sorted(soft_skills),
            'years_of_experience': yoe,
        }

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _tokenize(doc) -> list[str]:
        """Tokenize and remove stopwords + whitespace."""
        return [
            token.text for token in doc
            if not token.is_stop and not token.is_space and not token.is_punct
        ]

    @staticmethod
    def _lemmatize(doc) -> list[str]:
        """Return lemmatised tokens (no stopwords)."""
        return [
            token.lemma_ for token in doc
            if not token.is_stop and not token.is_space and not token.is_punct
        ]

    @staticmethod
    def _extract_entities(doc) -> list[dict]:
        """Named Entity Recognition."""
        return [
            {'text': ent.text, 'label': ent.label_}
            for ent in doc.ents
        ]

    @classmethod
    def _extract_technical_skills(cls, text: str) -> set[str]:
        text_lower = text.lower()
        found: set[str] = set()
        for skill in cls.TECHNICAL_SKILLS:
            # Use word-boundary regex to avoid false positives
            # e.g. 'c' should not match inside 'communication'
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill)
        return found

    @classmethod
    def _extract_soft_skills(cls, text: str) -> set[str]:
        text_lower = text.lower()
        found: set[str] = set()
        for skill in cls.SOFT_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill)
        return found

    @staticmethod
    def _extract_years_of_experience(text: str) -> int:
        """Extract max years of experience from text using regex or date math."""
        import datetime
        text_lower = text.lower()
        
        # Primary pattern: "5+ years of experience", "3 yrs exp"
        pattern1 = r'\b(\d{1,2})(?:\+)?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)\b'
        matches = re.findall(pattern1, text_lower)
        
        if not matches:
            # Secondary pattern: "Experience: 5+ years"
            pattern2 = r'\b(?:experience|exp)\b.{0,30}?\b(\d{1,2})(?:\+)?\s*(?:years?|yrs?)\b'
            matches = re.findall(pattern2, text_lower)
            
        if matches:
            # Filter out wildly high numbers (e.g. > 40)
            valid_years = [int(m) for m in matches if int(m) <= 40]
            if valid_years:
                return max(valid_years)
                
        # Fallback: Date Math Parser (e.g. "June 2024 - August 2025" which becomes "june 2024 august 2025" after punctuation strip)
        months = r'(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)'
        date_range_month_year = r'\b(' + months + r'\.?\s+\d{4})\s*(?:-|–|to)?\s*(' + months + r'\.?\s+\d{4}|present|current)\b'
        date_range_year_only = r'\b(19\d{2}|20\d{2})\s*(?:-|–|to)?\s*(19\d{2}|20\d{2}|present|current)\b'
        
        total_months = 0
        
        # 1. Parse Month-Year ranges
        month_matches = re.findall(date_range_month_year, text_lower)
        for start_str, end_str in month_matches:
            start_str = start_str.replace('.', '').strip()
            end_str = end_str.replace('.', '').strip()
            
            try:
                start_date = datetime.datetime.strptime(start_str, "%B %Y")
            except Exception:
                try:
                    start_date = datetime.datetime.strptime(start_str, "%b %Y")
                except Exception:
                    continue
                    
            if end_str in ['present', 'current']:
                end_date = datetime.datetime.now()
            else:
                try:
                    end_date = datetime.datetime.strptime(end_str, "%B %Y")
                except Exception:
                    try:
                        end_date = datetime.datetime.strptime(end_str, "%b %Y")
                    except Exception:
                        continue
                        
            if end_date > start_date:
                total_months += (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                
        # 2. Parse Year-only ranges
        year_matches = re.findall(date_range_year_only, text_lower)
        total_years_from_years = 0
        for start_str, end_str in year_matches:
            start_year = int(start_str)
            end_year = datetime.datetime.now().year if end_str in ['present', 'current'] else int(end_str)
            if end_year > start_year:
                total_years_from_years += (end_year - start_year)
                
        calculated_years = max(total_months // 12, total_years_from_years)
        
        # For junior developers with active internships (e.g. 14 months = 1 year, 6 months = 1 year rounded)
        if calculated_years == 0 and total_months >= 6:
            calculated_years = 1
            
        # Prevent education inflation (most BTechs add 4 years) by arbitrarily capping at a realistic fallback if No explicit YoE was declared
        if calculated_years > 5:  
            calculated_years = 0 
            
        return calculated_years
