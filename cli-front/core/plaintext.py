def build_plaintext(election_id: str, contest_id: str, candidate_code: int) -> str:
    return f"{election_id}{contest_id}{candidate_code}"
