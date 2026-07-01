import re
import statistics

def calculate_heuristic_score(text: str) -> float:
    # 1. Burstiness (Sentence Length Variance)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]
    if len(sentences) < 2:
        return 0.5  # Neutral if not enough data
    
    lengths = [len(s.split()) for s in sentences]
    variance = statistics.stdev(lengths)
    
    # Normalize burstiness: Lower variance (uniform) = higher AI score (closer to 1.0)
    # 0 variance -> 1.0 (AI), 20+ variance -> 0.0 (Human)
    burstiness_score = max(0.0, min(1.0, 1.0 - (variance / 20)))

    # 2. Vocabulary Diversity (Type-Token Ratio)
    tokens = re.findall(r'\w+', text.lower())
    if len(tokens) == 0:
        return 0.5
    ttr = len(set(tokens)) / len(tokens)
    
    # Normalize TTR: Lower ratio (repetitive) = higher AI score (closer to 1.0)
    # 0.5 ratio -> 1.0 (AI), 0.9 ratio -> 0.0 (Human)
    diversity_score = max(0.0, min(1.0, 2.0 - (ttr * 2)))

    # Combined heuristic score
    return (burstiness_score + diversity_score) / 2