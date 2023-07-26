from wagtail import blocks


class RichTextBlock(blocks.StructBlock):
    """RichText"""

    text = blocks.RichTextBlock(required=True, help_text="Add whatever you want")

    class Meta:  # noqa
        template = "flex/rich_text_block.html"
        icon = "edit"
        label = "RichTexts"
