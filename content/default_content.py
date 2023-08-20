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
