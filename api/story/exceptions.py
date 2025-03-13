class StoryGenerationError(Exception):
    """Raised when story generation fails"""
    pass

class BranchCreationError(Exception):
    """Raised when branch creation fails"""
    pass

class StoryNotFoundError(Exception):
    """Raised when a story is not found in the repository"""
    pass 