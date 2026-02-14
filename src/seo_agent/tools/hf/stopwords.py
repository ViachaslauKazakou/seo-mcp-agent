"""Stop words configuration for keyword filtering."""

# Russian stop words (common prepositions, conjunctions, particles, pronouns)
RUSSIAN_STOPWORDS = {
    # Prepositions
    "в", "на", "с", "к", "по", "от", "из", "у", "о", "об", "до", "для",
    "при", "про", "без", "через", "под", "над", "за", "перед", "между",
    
    # Conjunctions
    "и", "а", "но", "или", "да", "что", "как", "если", "чтобы", "когда",
    "потому", "так", "тоже", "также", "либо", "то", "ли",
    
    # Particles
    "не", "ни", "же", "ведь", "уж", "бы", "лишь", "только", "даже",
    
    # Pronouns
    "я", "ты", "он", "она", "оно", "мы", "вы", "они", "мой", "твой",
    "его", "ее", "их", "наш", "ваш", "этот", "тот", "такой", "сам",
    "весь", "всё", "все", "который", "какой", "чей", "кто", "что",
    
    # Common words
    "это", "быть", "есть", "был", "была", "было", "были", "будет", "будут",
    "может", "могут", "имеет", "нет", "да", "тут", "где", "там", "здесь",
    "еще", "уже", "более", "самый", "очень", "один", "два", "три",
}

# English stop words (common prepositions, conjunctions, articles, pronouns)
ENGLISH_STOPWORDS = {
    # Articles
    "a", "an", "the",
    
    # Prepositions
    "in", "on", "at", "to", "for", "of", "with", "from", "by", "about",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "between", "under", "over", "against", "among",
    
    # Conjunctions
    "and", "or", "but", "nor", "yet", "so", "if", "when", "where", "while",
    "because", "since", "unless", "although", "though",
    
    # Pronouns
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us",
    "them", "my", "your", "his", "its", "our", "their", "this", "that",
    "these", "those", "who", "whom", "which", "what", "whose",
    
    # Common verbs
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "can", "must",
    
    # Common words
    "not", "no", "yes", "here", "there", "where", "when", "how", "why",
    "all", "both", "each", "few", "more", "most", "other", "some", "such",
    "than", "too", "very", "one", "two", "three",
}

# Combined stop words for both languages
ALL_STOPWORDS = RUSSIAN_STOPWORDS | ENGLISH_STOPWORDS


def is_stopword(word: str) -> bool:
    """Check if a word is a stop word."""
    return word.lower().strip() in ALL_STOPWORDS


def filter_stopwords(keywords: list[str]) -> list[str]:
    """Filter out stop words from a list of keywords."""
    return [kw for kw in keywords if not is_stopword(kw)]
