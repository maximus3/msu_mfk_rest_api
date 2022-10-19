from collections import defaultdict

from pydantic import BaseModel


class CourseResultsCSV(BaseModel):
    keys: list[str]
    results: defaultdict[str, dict[str, str | bool | float]]
