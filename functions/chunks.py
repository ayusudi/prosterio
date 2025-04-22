from typing import Dict, List

def compile_to_chunk(data: Dict, id: int, pm_email: str) -> List[str]:
    full_name = data["full_name"]
    title = data["title"]
    profile = data["profile"]
    professional_experiences = data["professional_experiences"]
    educations = data["educations"]
    skills = data["skills"]
    distinctions = data["distinctions"]
    certifications = data["certifications"]

    chunks = []

    def add_chunk(title: str, content: str):
        chunks.append(
            {
                "CHUNK_TEXT": f"{title.upper()} of {full_name}\r{content}",
                "NAME": full_name,
                "PM_EMAIL": pm_email,
                "USERID": id,
                "REF": len(chunks) + 1,
            }
        )

    add_chunk(
        "information",
        f"""
title: {title}
summary: {profile}
""",
    )

    if educations:
        list_educations = []
        for education in educations:
            list_educations.append(" ".join(education))
        add_chunk("educations", "\n".join(list_educations))

    if skills:
        add_chunk("skills", "\n".join(skills))

    for experience in professional_experiences:
        add_chunk("professional experience", experience)

    if distinctions:
        add_chunk("distinctions", "\n".join(distinctions))

    if certifications:
        add_chunk("certifications", "\n".join(certifications))
    return chunks
