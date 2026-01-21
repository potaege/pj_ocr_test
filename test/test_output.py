

def evaluate_ocr_result(pred: dict, gt: dict, ranks: dict):

    total_weight = 0.0
    total_score = 0.0
    field_scores = {}
    failed_fields = []

    for field, rank in ranks.items():
        weight = 1.0 / rank
        total_weight += weight

        pred_val = pred.get(field)
        gt_val = gt.get(field)


        is_valid = normalize_text(pred_val) == normalize_text(gt_val)

        score = weight if is_valid else 0.0
        total_score += score

        field_scores[field] = {
            "rank": rank,
            "weight": weight,
            "pred": pred_val,
            "gt": gt_val,
            "match": is_valid,
            "score": score
        }

        if not is_valid:
            failed_fields.append(field)

    final_score = total_score / total_weight if total_weight > 0 else 0.0

    return {
        "final_score": round(final_score, 4),
        "field_scores": field_scores,
        "failed_fields": failed_fields
    }


def normalize_text(s):
    if s is None:
        return ""
    s = str(s)
    return (
        s.strip()
         .lower()
         .replace(".", "")
         .replace(" ", "")
    )

