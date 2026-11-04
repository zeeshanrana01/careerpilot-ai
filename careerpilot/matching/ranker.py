"""Ranking and filtering engine for matched job opportunities."""
from typing import Optional
from careerpilot.domain.models import (
    NormalizedJob,
    CareerProfile,
    JobMatchEvaluation,
    RankedJob,
    WorkplaceType,
)
from careerpilot.storage.repository import JobRepository


class JobRanker:
    """Ranks and filters evaluated jobs using match scores and candidate career preferences."""

    def __init__(self, repository: JobRepository):
        self.repo = repository

    def rank_opportunities(
        self,
        profile: CareerProfile,
        min_score: float = 40.0,
        limit: int = 50,
    ) -> list[RankedJob]:
        """
        Retrieve all matched jobs and apply candidate preference filters:
        - Excluded industries
        - Minimum salary threshold
        - Remote vs On-site requirements
        - Descending score sorting
        """
        raw_matches = self.repo.list_ranked_matches(min_score=min_score)
        
        candidates: list[tuple[float, NormalizedJob, JobMatchEvaluation, bool]] = []
        
        for job, match in raw_matches:
            # Check excluded industries
            if any(ind.lower() in job.description_clean.lower() for ind in profile.preferences.excluded_industries):
                continue
                
            preference_fit = True
            adjusted_score = match.overall_score
            
            # Check remote preference
            if profile.preferences.remote_only and job.workplace_type == WorkplaceType.ONSITE:
                preference_fit = False
                adjusted_score -= 15.0
                
            # Check salary preference
            if profile.preferences.min_acceptable_salary and job.salary and job.salary.max_amount:
                if job.salary.max_amount < profile.preferences.min_acceptable_salary:
                    preference_fit = False
                    adjusted_score -= 10.0
                    
            candidates.append((adjusted_score, job, match, preference_fit))

        # Sort descending by adjusted score
        candidates.sort(key=lambda item: item[0], reverse=True)

        ranked: list[RankedJob] = []
        for idx, (_, job, match, pref_fit) in enumerate(candidates[:limit], start=1):
            ranked.append(
                RankedJob(
                    job=job,
                    evaluation=match,
                    rank=idx,
                    preference_fit=pref_fit,
                )
            )

        return ranked
