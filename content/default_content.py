import os
import sys

import django


def html_to_rich_text(html_content):
    from wagtail.models import Page

    from flex.blocks import RichTextBlock
    from flex.models import FlexPage

    root_page = Page.objects.filter(depth=2).first()
    flex_page = FlexPage(
        title=file_name,
    )
    rich_text_block = RichTextBlock()

    try:
        rich_text_value = rich_text_block.to_python(html_content)
    except TypeError:
        print("Error parsing: " + file_name)
        return
    # subtitle max length is 100
    flex_page.subtitle = original_h1[:100]
    flex_page.body = [("rich_text", rich_text_value)]

    root_page.add_child(instance=flex_page)
    new_page = FlexPage.objects.get(title=file_name)
    n_body = new_page.body
    raw_data = n_body._raw_data
    raw_data[0]["value"]["text"] = html_content
    new_page.save()


path = "./templates/pages/"

files = []
files.append("coc.html")

for file in files:
    # if file is not html file
    if not file.endswith(".html"):
        # skip it
        continue

    html_content = open(path + file, "r").read()

    # file name without extension
    file_name = file.split(".")[0]

    # find first <p> tag and remove everything before it
    # find last </p> tag and remove everything after it
    # find <h1> tag and load everthing inside it
    original_h1 = html_content[
        html_content.find("<h1>") + 4 : html_content.find("</h1>")
    ]

    print("Processing: " + file_name)

    html_content = html_content[
        html_content.find("<p") : html_content.rfind("</p>") + 4
    ]

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, project_root)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    django.setup()

    html_to_rich_text(html_content)
