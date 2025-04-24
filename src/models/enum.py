import enum


class UserRoles(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class VoteType(enum.Enum):
    UPVOTE = "UPVOTE"
    DOWNVOTE = "DOWNVOTE"


class Difficulty(enum.Enum):
    Easy = "Easy"
    Medium = "Medium"
    Hard = "Hard"
    NA = "NA"


class Status(enum.Enum):
    Accepted = "Accepted"
    Rejected = "Rejected"
    Pending = "Pending"
    TimeLimit = "TimeLimit"
