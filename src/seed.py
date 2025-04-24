import asyncio
from sqlalchemy import delete
from core.db import sessionmanager
from models.association import TopicProblem, ListProblem
from models.bookmark import Bookmark
from models.list import List
from models.problem import Problem
from models.solution import Solution
from models.submission import Submission
from models.testcase import TestCase
from models.topic import Topic
from models.user_solution import UserSolution
from models.user import User
from models.vote_problem import VoteProblem
from models.vote_solution import VoteSolution


async def main():
    async with sessionmanager.session() as session:
        async with session.begin():
            await session.execute(delete(TopicProblem))
            await session.execute(delete(ListProblem))
            await session.execute(delete(Bookmark))
            await session.execute(delete(List))
            await session.execute(delete(Problem))
            await session.execute(delete(Solution))
            await session.execute(delete(Submission))
            await session.execute(delete(TestCase))
            await session.execute(delete(Topic))
            await session.execute(delete(UserSolution))
            await session.execute(delete(User))
            await session.execute(delete(VoteProblem))
            await session.execute(delete(VoteSolution))

    async with sessionmanager.session() as session:
        async with session.begin():
            blind_75 = List(name="Blind 75")
            neetcode_150 = List(name="Neetcode 150")
            cses = List(name="cses")

            session.add_all([blind_75, neetcode_150, cses])

            await session.flush()

            topics = [
                Topic(name="Arrays & Hashing", list_title=neetcode_150),
                Topic(name="Two Pointers", list_title=neetcode_150),
                Topic(name="Sliding Window", list_title=neetcode_150),
                Topic(name="Stack", list_title=neetcode_150),
                Topic(name="Binary Search", list_title=neetcode_150),
                Topic(name="Linked List", list_title=neetcode_150),
                Topic(name="Trees", list_title=neetcode_150),
                Topic(name="Heap", list_title=neetcode_150),
                Topic(name="Backtracking", list_title=neetcode_150),
                Topic(name="Tries", list_title=neetcode_150),
                Topic(name="Graphs", list_title=neetcode_150),
                Topic(name="Advanced Graphs", list_title=neetcode_150),
                Topic(name="1D Dynamic Programming", list_title=neetcode_150),
                Topic(name="2D Dynamic Programming", list_title=neetcode_150),
                Topic(name="Greedy", list_title=neetcode_150),
                Topic(name="Intervals", list_title=neetcode_150),
                Topic(name="Math & Geometry", list_title=neetcode_150),
                Topic(name="Bit Manipulation", list_title=neetcode_150),
            ]

            session.add_all(topics)
            await session.flush()


if __name__ == "__main__":
    asyncio.run(main())
