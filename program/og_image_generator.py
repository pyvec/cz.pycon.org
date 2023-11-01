from __future__ import annotations

import hashlib
import pathlib
import tempfile
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.template.loader import render_to_string

if TYPE_CHECKING:
    from playwright import sync_api


class ConfigurationError(Exception):
    pass


DEFAULT_IMAGE_SIZE = (1200, 630)


class OgImageGenerator:
    """
    Generates images for social media by rendering a Django template,
    launching Chromium and taking a screenshot.

    The generator must be used as a context manager::

        >>> with OgImageGenerator() as generator:
        ...     # Call multiple times:
        ...     generator.generate_image( ... )

    When the context block is entered, a browser instance is lauched. The browser
    will be terminated when leaving the context block. Generating multiple images
    in the block will speed up things because the browser instance will be re-used.
    """

    def __init__(self):
        self._playwright_ctx: sync_api.PlaywrightContextManager | None = None
        self._playwright_api: sync_api.Playwright | None = None
        self._browser: sync_api.Browser | None = None
        self._temp_dir: tempfile.TemporaryDirectory | None = None

    @property
    def work_dir(self) -> pathlib.Path:
        return pathlib.Path(self._temp_dir.name)

    def generate_image(
        self,
        template_name: str,
        context: dict[str, Any],
        output_path: str | pathlib.Path,
        image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE,
        scale_factor: int = 2,
        include_hash: bool = True,
    ) -> pathlib.Path:
        """
        Render a template with context to a JPEG file. Hash of the rendered HTML file is
        appended at the end of the generated file.
        """
        html_file = self._render_template(template_name, context)
        return self._capture_screenshot(
            html_file, output_path, image_size, scale_factor, include_hash
        )

    def _render_template(
        self, template_name: str, context: dict[str, Any]
    ) -> pathlib.Path:
        rendered_html = render_to_string(template_name, context)
        rendered_html = self._fix_absolute_urls(rendered_html)
        html_file = self.work_dir / "image.html"
        html_file.write_text(rendered_html, encoding="utf-8")
        return html_file

    def _fix_absolute_urls(self, html: str) -> str:
        return html.replace("/static/", "static/").replace("/media/", "media/")

    def _capture_screenshot(
        self,
        html_file: pathlib.Path,
        output_path: str | pathlib.Path,
        image_size: tuple[int, int],
        scale_factor: int,
        include_hash: bool,
    ) -> pathlib.Path:
        # Create parent directory for the image if it does not exist
        output_path = pathlib.Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Add hash of HTML file to the filename
        if include_hash:
            content_hash = self._compute_hash(html_file)
            output_path = output_path.with_stem(f"{output_path.stem}.{content_hash}")

        page = self._browser.new_page(
            viewport={"width": image_size[0], "height": image_size[1]},
            device_scale_factor=scale_factor,
        )
        page.goto(f"file://{html_file.absolute()}")
        page.screenshot(
            path=output_path,
            scale="device",
            type="jpeg",
            quality=60,
        )
        return output_path

    def _compute_hash(self, file_path: pathlib.Path) -> str:
        md5_algo = hashlib.md5()
        md5_algo.update(file_path.read_bytes())
        return md5_algo.hexdigest()[:12]

    def __enter__(self):
        # Try to import playwright at the last possible moment.
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ConfigurationError(
                "playwright library is not installed. Run "
                "`pip install -r requirements-og-generator.txt` "
                "to install all required dependencies."
            )

        self._setup_temp_dir()
        self._playwright_ctx = sync_playwright()
        self._playwright_api = self._playwright_ctx.__enter__()
        self._browser = self._playwright_api.chromium.launch(headless=True)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._browser is not None:
            self._browser.close()
            self._browser = None

        self._playwright_api = None
        if self._playwright_ctx is not None:
            self._playwright_ctx.__exit__(exc_type, exc_val, exc_tb)
            self._playwright_ctx = None

        if self._temp_dir is not None:
            self._temp_dir.cleanup()
            self._temp_dir = None

    def _setup_temp_dir(self):
        self._temp_dir = tempfile.TemporaryDirectory()

        # Symlink all directories listed in the STATICFILES_DIRS
        base_path = settings.BASE_DIR
        for static_dir in settings.STATICFILES_DIRS:
            static_dir_path = pathlib.Path(static_dir)
            relative_dir = static_dir_path.relative_to(base_path)
            link = self.work_dir / relative_dir
            # Make all parent directories
            link.parent.mkdir(parents=True, exist_ok=True)
            # Create symbolic link
            link.symlink_to(static_dir_path, target_is_directory=True)

        # Symlink media directory under /media
        media_link = self.work_dir / "media"
        media_link.symlink_to(settings.MEDIA_ROOT, target_is_directory=True)
