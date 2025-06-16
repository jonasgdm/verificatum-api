BRAZILIAN_DIGITS_PER_CONTEST = {
    "vereador": 5,
    "prefeito": 2,
    "deputado_estadual": 5,
    "deputado_federal": 4,
    "senador": 3,
    "governador": 2,
    "presidente": 2,
}


def generate_candidate_codes(option_list):
    result = {}

    for entry in option_list:
        cargo = entry["contest"]
        qtd = entry["candidates"]

        if qtd > 0:
            digits = BRAZILIAN_DIGITS_PER_CONTEST[cargo]
            start = int("9" * digits)
            result[cargo] = [start - j for j in range(qtd)]

    return result
