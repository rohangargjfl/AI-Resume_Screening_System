"""
Matching Engine – computes a weighted match score based on 
explicitly extracted technical vs soft skills, blended with baseline TF-IDF text similarity.
Returns both final scores AND detailed breakdowns for explainability.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from feature_extraction import FeatureExtractor


class MatchingEngine:
    """Compute match scores heavily weighted towards technical skills."""

    def __init__(self, text_weight: float = 0.3, skills_weight: float = 0.7):
        self.text_weight = text_weight
        self.skills_weight = skills_weight
        
        # Within the skills portion, technical skills are worth 80%, soft skills 20%
        self.tech_ratio = 0.8
        self.soft_ratio = 0.2
        
        self.extractor = FeatureExtractor()

    def _calculate_skill_score(self, required: list[str], found: list[str]) -> float:
        """Returns percentage (0.0 to 1.0) of required skills that were found."""
        if not required:
            return 1.0  # If none required, they get full points for this section
            
        req_set = {s.lower() for s in required}
        found_set = {s.lower() for s in found}
        
        matched = req_set.intersection(found_set)
        return len(matched) / len(req_set)

    def compute_scores(
        self,
        jd_text: str,
        jd_tech_skills: list[str],
        jd_soft_skills: list[str],
        resumes: list[dict],
        jd_yoe: int = 0,
        weights: dict = None,
    ) -> list[float]:
        """Return list of match scores (0‑100) for each resume using dynamically weighted sum."""
        if not resumes:
            return []

        if weights is None:
            weights = {'tech': 0.60, 'yoe': 0.15, 'context': 0.15, 'soft': 0.10, 'bonus': 0.05}

        # 1. Baseline Text Similarity (TF-IDF)
        all_docs = [jd_text] + [r['text'] for r in resumes]
        tfidf_matrix = self.extractor.tfidf_vectors(all_docs)
        text_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        # 2. Explicit Skill & Experience Matching (Weighted Sum)
        final_scores = []
        for i, resume in enumerate(resumes):
            tech_score = self._calculate_skill_score(jd_tech_skills, resume['technical_skills'])
            soft_score = self._calculate_skill_score(jd_soft_skills, resume['soft_skills'])
            
            resume_yoe = resume.get('years_of_experience', 0)
            if jd_yoe <= 0:
                yoe_score = 1.0
            else:
                yoe_score = min(resume_yoe / jd_yoe, 1.0)
            
            req_set = {s.lower() for s in jd_tech_skills}
            found_set = {s.lower() for s in resume['technical_skills']}
            extra_tech = found_set - req_set
            extra_bonus = min(len(extra_tech) * (weights.get('bonus', 0.05) / 10.0), weights.get('bonus', 0.05))
            
            blended = (
                (tech_score * weights['tech']) +
                (soft_score * weights['soft']) +
                (yoe_score * weights['yoe']) +
                (text_sim[i] * weights['context']) +
                extra_bonus
            )
            
            # Scale to 0-100 and format
            score_100 = min(max(blended * 100, 0.0), 100.0)
            final_scores.append(round(score_100, 2))

        return final_scores

    def compute_scores_detailed(
        self,
        jd_text: str,
        jd_tech_skills: list[str],
        jd_soft_skills: list[str],
        resumes: list[dict],
        jd_yoe: int = 0,
        weights: dict = None,
    ) -> list[dict]:
        """Return detailed score breakdowns including matched, extra missing, and bonuses."""
        if not resumes:
            return []

        if weights is None:
            weights = {'tech': 0.60, 'yoe': 0.15, 'context': 0.15, 'soft': 0.10, 'bonus': 0.05}

        # 1. Baseline Text Similarity (TF-IDF)
        all_docs = [jd_text] + [r['text'] for r in resumes]
        tfidf_matrix = self.extractor.tfidf_vectors(all_docs)
        text_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        results = []
        for i, resume in enumerate(resumes):
            # Compute distinct skill sets
            req_tech = {s.lower() for s in jd_tech_skills}
            found_tech = {s.lower() for s in resume['technical_skills']}
            matched_tech = req_tech.intersection(found_tech)
            extra_tech = found_tech - req_tech
            
            req_soft = {s.lower() for s in jd_soft_skills}
            found_soft = {s.lower() for s in resume['soft_skills']}
            matched_soft = req_soft.intersection(found_soft)

            # Ratios
            tech_match_ratio = len(matched_tech) / len(req_tech) if req_tech else 1.0
            soft_match_ratio = len(matched_soft) / len(req_soft) if req_soft else 1.0
            
            resume_yoe = resume.get('years_of_experience', 0)
            if jd_yoe <= 0:
                yoe_match_ratio = 1.0
            else:
                yoe_match_ratio = min(resume_yoe / jd_yoe, 1.0)
            
            # --- Dynamic Weighting ---
            tech_contrib = tech_match_ratio * weights['tech']
            yoe_contrib = yoe_match_ratio * weights['yoe']
            text_contrib = text_sim[i] * weights['context']
            soft_contrib = soft_match_ratio * weights['soft']
            
            # Bonus points (dynamically capped so it doesn't overpower relevance)
            extra_bonus = min(len(extra_tech) * (weights.get('bonus', 0.05) / 10.0), weights.get('bonus', 0.05))
            
            blended = tech_contrib + soft_contrib + text_contrib + yoe_contrib + extra_bonus
            final = min(max(blended * 100, 0.0), 100.0)
            
            # Combine skill contribs for the breakdown
            skill_contrib = tech_contrib + soft_contrib
            
            results.append({
                'final_score': round(final, 2),
                'text_similarity': round(text_sim[i] * 100, 1),
                'tech_skill_score': round(tech_match_ratio * 100, 1),
                'soft_skill_score': round(soft_match_ratio * 100, 1),
                'yoe_score': round(yoe_match_ratio * 100, 1),
                'combined_skill_score': round((tech_contrib + soft_contrib) * 100, 1),
                'text_contribution': round(text_contrib * 100, 1),
                'skill_contribution': round(skill_contrib * 100, 1),
                'tech_contribution': round(tech_contrib * 100, 1),
                'soft_contribution': round(soft_contrib * 100, 1),
                'yoe_contribution': round(yoe_contrib * 100, 1),
                'extra_skills_bonus': round(extra_bonus * 100, 1),
                'jd_yoe': jd_yoe,
                'resume_yoe': resume_yoe,
            })

        return results
