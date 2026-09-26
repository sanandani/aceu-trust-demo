"""Transparent illustration of ACE-U features; not a validated assessment model."""


def _dimension(value, explanation, evidence_count):
    return {
        "illustrative_index": None if value is None else round(min(value, 1.0), 2),
        "explanation": explanation,
        "evidence_count": evidence_count,
        "evidence_coverage": "limited" if evidence_count < 3 else "more examples provided",
    }


def calculate_aceu(profile):
    claims = profile.get("claims", [])
    supported = sum(bool(claim.get("artifact")) for claim in claims)
    projects = profile.get("projects", [])
    credentials = profile.get("credential_examples", [])
    peer_support = profile.get("peer_support_examples", [])
    cross_domain = profile.get("cross_domain_projects", [])
    qualifying_cross_domain = sum(
        len(set(item.get("domains", []))) >= 2 for item in cross_domain
    )

    return {
        "authenticity": _dimension(
            supported / len(claims) if claims else None,
            f"{supported} of {len(claims)} example claims have a linked artifact. "
            "This checks example evidence coverage, not whether a person is genuine.",
            len(claims),
        ),
        "credibility": _dimension(
            0.2 * len(projects) + 0.1 * len(credentials)
            if projects or credentials else None,
            f"{len(projects)} documented example projects and "
            f"{len(credentials)} fictional credential examples. "
            "Credentials are not independently verified.",
            len(projects) + len(credentials),
        ),
        "empathy": _dimension(
            0.25 * len(peer_support) if peer_support else None,
            f"{len(peer_support)} substantive peer-support examples supplied. "
            "Missing online activity must not be interpreted as lack of empathy.",
            len(peer_support),
        ),
        "uniqueness": _dimension(
            0.35 * qualifying_cross_domain if cross_domain else None,
            f"{qualifying_cross_domain} example projects span at least two domains. "
            "This is not a population rarity measurement.",
            len(cross_domain),
        ),
    }
