from dataclasses import dataclass


@dataclass(frozen=True)
class Competitor:
    name: str
    container_image: str

    @classmethod
    def from_raw(cls, raw):
        if isinstance(raw, str):
            return Competitor(raw.split("/")[-1], raw)
        elif isinstance(raw, dict):
            if not "name" in raw or not "image" in raw:
                raise ValueError("Invalid competitor definition")
            return Competitor(raw["name"], raw["image"])
