from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class ExplanationScope(Enum):
    A = "A"
    B = "B"
    C = "C"


@dataclass
class AnalysisRequest:
    __chapter_url: str
    __explanation_scope: ExplanationScope
    __analysis_role: str = "Constitutional Law Professor"
    __target_audience: Optional[str] = None
    __follow_up_questions: List[str] = field(default_factory=list) # type: ignore

    def __init__(
        self,
        chapter_url: str,
        explanation_scope: ExplanationScope,
        analysis_role: str = "Constitutional Law Professor",
        target_audience: Optional[str] = None,
        follow_up_questions: Optional[List[str]] = None,
    ):
        self.__chapter_url = chapter_url
        self.__explanation_scope = explanation_scope
        self.__analysis_role = analysis_role
        self.__target_audience = target_audience
        self.__follow_up_questions = follow_up_questions or []

    def get_chapter_url(self) -> str:
        return self.__chapter_url

    def get_explanation_scope(self) -> ExplanationScope:
        return self.__explanation_scope

    def get_analysis_role(self) -> str:
        return self.__analysis_role

    def get_target_audience(self) -> Optional[str]:
        return self.__target_audience

    def get_follow_up_questions(self) -> List[str]:
        return self.__follow_up_questions
    
    def __str__(self) -> str:
        return (
            f"AnalysisRequest("
            f"chapter_url='{self.__chapter_url}', "
            f"explanation_scope='{self.__explanation_scope.value}', "
            f"analysis_role='{self.__analysis_role}', "
            f"target_audience='{self.__target_audience}', "
            f"follow_up_questions={self.__follow_up_questions}"
            f")"
        )


class AnalysisRequestMapper:
    @staticmethod
    def from_json(data: Dict[str, Any]) -> AnalysisRequest:
        chapter_url = data["chapterUrl"]

        explanation_scope = ExplanationScope(data["explanationScope"])

        analysis_role = data.get("analysisRole", "Constitutional Law Professor")
        target_audience = data.get("targetAudience")
        follow_up_questions = data.get("followUpQuestions", [])

        return AnalysisRequest(
            chapter_url=chapter_url,
            explanation_scope=explanation_scope,
            analysis_role=analysis_role,
            target_audience=target_audience,
            follow_up_questions=follow_up_questions,
        )