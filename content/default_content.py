import os

import typer as typer


def create_team_content():
    from wagtail.models import Page

    from team.models import TeamPage

    root_page = Page.get_first_root_node()

    team_content = TeamPage(
        title="Team",
        content="""
        If you drew the organization structure of the PyCon CZ team, you — 
        the attendee would be at the top. 
        The incredible amount of volunteers would follow. There's little or no 
        difference between organizers
        and volunteers, because we all do it in our free time without any claim 
        for wage. Below is a list of our core team members.
        """,
    )
    root_page.add_child(instance=team_content)
    team_content.save_revision().publish()


def create_sponsors_content():
    from wagtail.models import Page

    from sponsors.models import SponsorsOffer

    root_page = Page.get_first_root_node()

    sponsors_content = SponsorsOffer(
        title="Sponsors offer",
        about="""
        The PyConCZ 2019 organizers are pleased to invite your sponsorship of the 
        fifth annual 3-day PyCon conference in Prague, Czech Republic, on 
        10-12 September 2023. Sponsorship presents opportunities to connect you 
        with up to 500 expected attendees.
        """,
        benefits="""
        Sponsorship packages start from 20000 CZK and can include: Partner announced 
        on the PyCon CZ official social media channels, Logo on the conference 
        website, Logo on the intermission slide deck, Roll-up (standing banner) at the 
        venue, Booth at the venue, Promotional items or leaflets in the 
        swag bag of every attendee, Promotional posts, Retweets/reshares on the 
        PyCon CZ official social media channels, Free tickets to the conference, 
        Option to be our exclusive lanyard sponsor.
        """,
        custom_sponsorship="""
        In the case that our sponsorship packages don't fit your needs, you can 
        become diversity sponsor (provide free tickets for target demographic), 
        host or contribute prizes for quiz/competition, or become sponsor of 
        connected event. And of course, if you have your own idea about custom 
        sponsorship, we'd love to hear it!
        """,
        event_summary="""
        Friday, 14 June 2019, to Sunday, 16 June 2019, Gorgeous industrial venue, 
        Friendly environment, 350–500 attendees (professionals, students, and 
        hobbyist Pythonistas alike), Organized by volunteers from the community, 
        full conference days with tracks (both tracks streamed online), full day of 
        workshops and sprints, 30+ diverse, international speakers, Broad range of 
        both technical and community topics, Social events, Food and beverages 
        included in the ticket price.
        """,
        contacts="""
        Mr. Tomáš Orsava, Mr. Jiri Psotka""",
    )
    root_page.add_child(instance=sponsors_content)
    sponsors_content.save_revision().publish()


def create_default_content():
    """
    Creates default WagTail content which is used on localhost only,
    so there is no need to manually add content in WagTail admin
    each time database is dropped.
    """
    import sys

    import django

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, project_root)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    django.setup()

    create_team_content()
    create_sponsors_content()


if __name__ == "__main__":
    typer.run(create_default_content)
