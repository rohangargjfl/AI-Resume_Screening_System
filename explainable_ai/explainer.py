"""
Explainer – for each candidate shows matched skills,
missing skills, detected soft skills, overall match score,
AND a detailed human-readable explanation of WHY they ranked where they did.
"""


class Explainer:
    """Generate explainable reports for candidate–JD matches."""

    @staticmethod
    def explain(
        candidate_name: str,
        match_score: float,
        resume_technical_skills: list[str],
        resume_soft_skills: list[str],
        jd_technical_skills: list[str],
        jd_soft_skills: list[str],
        score_breakdown: dict | None = None,
    ) -> dict:
        """Return an explanation dict for one candidate.
        
        If score_breakdown is provided (from compute_scores_detailed),
        a rich human-readable explanation is generated.
        """

        resume_tech_set = set(resume_technical_skills)
        jd_tech_set = set(jd_technical_skills)
        jd_soft_set = set(jd_soft_skills)
        resume_soft_set = set(resume_soft_skills)

        matched_skills = sorted(resume_tech_set & jd_tech_set)
        missing_skills = sorted(jd_tech_set - resume_tech_set)
        extra_skills = sorted(resume_tech_set - jd_tech_set)
        matched_soft = sorted(resume_soft_set & jd_soft_set)
        missing_soft = sorted(jd_soft_set - resume_soft_set)

        skill_match_ratio = (
            round(len(matched_skills) / len(jd_tech_set) * 100, 1)
            if jd_tech_set else 0.0
        )

        # Build the explanation dict
        result = {
            'candidate_name': candidate_name,
            'match_score': round(match_score, 2),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'extra_skills': extra_skills,
            'detected_soft_skills': sorted(resume_soft_set),
            'matched_soft_skills': matched_soft,
            'missing_soft_skills': missing_soft,
            'total_jd_skills': len(jd_tech_set),
            'total_jd_soft_skills': len(jd_soft_set),
            'skill_match_ratio': skill_match_ratio,
            'total_resume_skills': len(resume_tech_set),
        }

        # Add detailed breakdown if available
        if score_breakdown:
            result['breakdown'] = score_breakdown
            result['explanation'] = Explainer._build_explanation(
                candidate_name, match_score, score_breakdown,
                matched_skills, missing_skills, jd_tech_set,
                matched_soft, resume_soft_set, extra_skills,
            )

        return result

    @staticmethod
    def _build_explanation(
        name, score, breakdown,
        matched_skills, missing_skills, jd_tech_set,
        matched_soft, resume_soft_set, extra_skills,
    ) -> str:
        """Generate a human-readable paragraph explaining the ranking."""
        lines = []
        
        # Overall score summary
        if score >= 75:
            lines.append(f"**{name}** is a strong match with a score of {score:.1f}%.")
        elif score >= 50:
            lines.append(f"**{name}** is a moderate match with a score of {score:.1f}%.")
        elif score >= 30:
            lines.append(f"**{name}** is a partial match with a score of {score:.1f}%.")
        else:
            lines.append(f"**{name}** is a weak match with a score of {score:.1f}%.")
            
        # Experience
        jd_yoe = breakdown.get('jd_yoe', 0)
        resume_yoe = breakdown.get('resume_yoe', 0)
        if jd_yoe > 0:
            if resume_yoe >= jd_yoe:
                lines.append(f"Meets experience requirement ({resume_yoe} yrs / {jd_yoe} yrs requested).")
            else:
                lines.append(f"Falls short on experience ({resume_yoe} yrs / {jd_yoe} yrs requested).")
        
        # Technical skills
        tech_pct = breakdown.get('tech_skill_score', 0)
        if matched_skills:
            lines.append(
                f"They match {len(matched_skills)}/{len(jd_tech_set)} required technical skills "
                f"({tech_pct:.0f}%): {', '.join(matched_skills[:8])}"
                f"{'...' if len(matched_skills) > 8 else ''}."
            )
        else:
            lines.append("They match none of the required technical skills.")
        
        if missing_skills:
            lines.append(
                f"Missing: {', '.join(missing_skills[:6])}"
                f"{'...' if len(missing_skills) > 6 else ''}."
            )
        
        # Extra skills (bonus context)
        if extra_skills:
            lines.append(
                f"Additional skills not in JD: {', '.join(extra_skills[:5])}"
                f"{'...' if len(extra_skills) > 5 else ''}."
            )
        
        # Soft skills
        if matched_soft:
            lines.append(f"Soft skills matched: {', '.join(matched_soft)}.")
        if resume_soft_set:
            soft_pct = breakdown.get('soft_skill_score', 0)
            lines.append(f"Soft skill match: {soft_pct:.0f}%.")
        
        # Score contribution breakdown
        text_c = breakdown.get('text_contribution', 0)
        tech_c = breakdown.get('tech_contribution', 0)
        soft_c = breakdown.get('soft_contribution', 0)
        yoe_c = breakdown.get('yoe_contribution', 0)
        extra_b = breakdown.get('extra_skills_bonus', 0)
        
        breakdown_text = (
            f"Score breakdown: {tech_c:.1f}% from Tech Skills + "
            f"{soft_c:.1f}% from Soft Skills + "
            f"{yoe_c:.1f}% from Experience + "
            f"{text_c:.1f}% from Context Match"
        )
        if extra_b > 0:
            breakdown_text += f" + **{extra_b:.1f}% bonus** for {len(extra_skills)} extra technical skills."
        else:
            breakdown_text += "."
            
        lines.append(breakdown_text)
        
        return " ".join(lines)
