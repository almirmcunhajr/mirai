from enum import Enum

class Genre(str, Enum):
    ACTION = "action"
    ADVENTURE = "adventure"
    COMEDY = "comedy"
    DRAMA = "drama"
    FANTASY = "fantasy"
    HORROR = "horror"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    SCIENCE_FICTION = "science fiction"
    THRILLER = "thriller"