import re

from services.bns_mapping import IPC_BNS_MAP


def classify_sections(text: str):

    detected = []

    suggestions = set()

    crime = "Unknown"

    category = "Unknown"

    confidence = 0.0

    # Find IPC sections

    sections = re.findall(r'\b\d{2,3}[A-Z]?\b', text)

    if "NDPS" in text.upper():
        sections.append("NDPS")

    for sec in sections:

        if sec in IPC_BNS_MAP:

            info = IPC_BNS_MAP[sec]

            detected.append({

                "section": sec,

                "crime": info["crime"],

                "category": info["category"]

            })

            crime = info["crime"]

            category = info["category"]

            confidence = 0.95

            for rel in info["related"]:
                if rel not in sections:
                    suggestions.add(rel)

    return {

        "crime": crime,

        "category": category,

        "confidence": confidence,

        "detected_sections": detected,

        "suggested_sections": list(suggestions)

    }