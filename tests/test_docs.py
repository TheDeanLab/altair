import re
import unittest
import subprocess
import os
from pathlib import Path


class TestDocs(unittest.TestCase):
    def setUp(self):
        self._original_cwd = os.getcwd()
        docs_dir = Path(__file__).resolve().parents[1] / "docs"
        os.chdir(docs_dir)
        print("Current Directory:", os.getcwd())

    def tearDown(self):
        os.chdir(self._original_cwd)

    def test_sphinx_build(self):
        cmd = [
            "make",
            "linkcheck",
        ]

        # Run the build, and print any results.
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)

        # Check that no links are broken.
        assert result.returncode == 0, "Broken links found in Sphinx documentation!"

        # Check that all images are found.
        missing_image_pattern = re.compile(
            r"WARNING: image file not readable", re.IGNORECASE
        )
        match = missing_image_pattern.search(result.stderr)
        self.assertIsNone(
            match,
            "There are missing images in the documentation! "
            "Check Sphinx warnings above.",
        )


if __name__ == "__main__":
    unittest.main()
