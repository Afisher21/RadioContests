from Contests import TheSoundJoBros, Bj1000NameGame, StarDisneyland
from ContestHelpers import HandleCompetitionLoop

def main():
    # Build array of current competitions
    competitions = []
    competitions.append(Bj1000NameGame())
    #competitions.append(TheSoundJoBros())
    competitions.append(StarDisneyland())

    # Handle all registerd competitions
    HandleCompetitionLoop(competitions)

if __name__ == '__main__':
    main()
