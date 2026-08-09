import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

sys.path.insert(0, os.path.join(BACKEND_DIR, "seed"))

from seed import build_services


def test_service_images_use_local_gallery_assets():
    services = build_services()

    assert services, "Expected seeded services to be generated"

    for service in services:
        image_url = service["image_url"]
        assert image_url.startswith("assets/img/gallery/"), image_url
        assert not image_url.startswith("http"), image_url
