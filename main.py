import os

os.system("pip install -r requirements.txt --quiet")

from orcid.app import orcid
from scholar.app import scholar


def main():
    orcid()
    scholar()


if __name__ == "__main__":
    main()
