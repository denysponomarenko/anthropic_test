from typing import Dict, List


def tokenize(text: str, vocab: Dict[str, int]) -> List[int]:
    result = []
    unk = vocab["UNK"]

    i = 0

    while i < len(text):
        best_token = None

        for token in vocab:
            if token == "UNK":
                continue

            if text.startswith(token, i):
                if best_token is None or len(token) > len(best_token):
                    best_token = token

        if best_token is not None:
            result.append(vocab[best_token])
            i += len(best_token)
        else:
            result.append(unk)
            i += 1

    return result
