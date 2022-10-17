from setuptools import find_packages, setup

setup(
    name="github_poster",
    author="goldenages1989",
    author_email="xiaogang19891001@gmail.com",
    url="https://github.com/goldenages1989/2022",
    license="MIT",
    version="2.3.0",
    description="Make everything a GitHub svg poster and Skyline!",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "svgwrite",
        "pendulum",
        "colour",
    ],
    extras_require={
        "twitter": ["twint_fork"],
        "garmin": ["garminconnect"],
        "gpx": ["gpxpy"],
        "strava": ["stravalib"],
        "github": ["PyGithub"],
        "skyline": ["sdf_fork"],
        "all": [
            "twint_fork",
            "garminconnect",
            "gpxpy",
            "stravalib",
            "PyGithub",
            "sdf_fork",
        ],
    },
    entry_points={
        "console_scripts": ["github_poster = github_poster.cli:main"],
    },
)
