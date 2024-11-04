from dataclasses import dataclass


@dataclass(frozen=True)
class Competitor:
    name: str
    container_image: str
